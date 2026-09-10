"""Agentic SDLC System — CLI Entrypoint.

Usage:
    python main.py --auto --requirement "..."
    python main.py --serve                        # HTTP mode: /run + /metrics + /health
    python main.py --requirement "..." --auto     # CI/CD non-interactive mode
"""

import argparse
import json
import logging
import sys
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

from src.models.state import Requirement, WorkflowState
from src.orchestrator.workflow import WorkflowOrchestrator
from src.tools.metrics import inc, metrics_text
from src.tools.output_writer import write_outputs

# ── Structured JSON logger ────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(message)s")
_log = logging.getLogger("agentic-sdlc")


def _emit(level: str, message: str, **extra):
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": level,
        "service": "agentic-sdlc",
        "message": message,
        **extra,
    }
    print(json.dumps(record), flush=True)


# ── HTTP server for /health and /metrics ─────────────────────────────────────
class _Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass  # suppress default access log

    def do_GET(self):
        if self.path == "/health":
            body = b'{"status":"ok"}'
            self._respond(200, "application/json", body)
        elif self.path == "/metrics":
            body = metrics_text().encode()
            self._respond(200, "text/plain; version=0.0.4", body)
        else:
            self._respond(404, "text/plain", b"not found")

    def _respond(self, code: int, content_type: str, body: bytes):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def start_http_server(port: int = 8080):
    server = HTTPServer(("0.0.0.0", port), _Handler)
    t = Thread(target=server.serve_forever, daemon=True)
    t.start()
    _emit("info", f"HTTP server listening on :{port} (/health, /metrics)")
    return server


# ── CLI ───────────────────────────────────────────────────────────────────────
def parse_args():
    parser = argparse.ArgumentParser(description="Agentic SDLC System")
    parser.add_argument("--requirement", "-r", type=str, help="Requirement string")
    parser.add_argument(
        "--auto", action="store_true", help="Auto-approve all human gates"
    )
    parser.add_argument(
        "--codebase-path",
        type=str,
        default=".",
        help="Path to existing codebase (brownfield)",
    )
    parser.add_argument(
        "--output-dir", type=str, default="outputs", help="Output directory"
    )
    parser.add_argument(
        "--serve", action="store_true", help="Start HTTP server then run workflow"
    )
    parser.add_argument(
        "--port", type=int, default=8080, help="HTTP server port (default: 8080)"
    )
    return parser.parse_args()


def get_requirement(args) -> str:
    if args.requirement:
        return args.requirement
    print("\n" + "=" * 60)
    print("  Agentic SDLC System")
    print("=" * 60)
    print("Enter your software requirement (press Enter twice to submit):\n")
    lines = []
    while True:
        line = input()
        if line == "" and lines:
            break
        lines.append(line)
    return " ".join(lines).strip()


def print_summary(state: WorkflowState, output_dir: str):
    print("\n" + "=" * 60)
    print(f"  Workflow Complete — ID: {state.id}")
    print("=" * 60)
    print(f"\nScenario:    {state.requirement.scenario_type.value}")
    print(f"Intent:      {state.requirement.intent}")
    print(
        f"\nAmbiguities: {len(state.requirement.ambiguities)} detected, "
        f"{sum(1 for a in state.requirement.ambiguities if a.resolved)} resolved"
    )
    print("\nTask Execution:")
    for t in state.tasks:
        icon = {
            "completed": "[OK]",
            "approved": "[OK]",
            "failed": "[FAIL]",
            "skipped": "[SKIP]",
            "rejected": "[REJ]",
        }.get(t.status.value, "[...]")
        print(
            f"  {icon} {t.name:<30} [{t.status.value}]"
            + (f"  <- {t.error}" if t.error else "")
        )
    print(f"\nArtifacts Generated: {len(state.artifacts)}")
    for k in state.artifacts:
        print(f"  * {k}")
    if state.risks:
        print(f"\nRisks Identified: {len(state.risks)}")
        for r in state.risks:
            print(f"  [{r.level.value.upper():8}] {r.title}")
    if state.validation:
        status = "[PASSED]" if state.validation.passed else "[WARNINGS]"
        print(f"\nValidation: {status}")
        print(f"Coverage Estimate: {state.validation.coverage_estimate}")
    print(f"\nOutputs written to: {output_dir}")
    print("=" * 60 + "\n")


def run_workflow(
    requirement_text: str, auto: bool, codebase_path: str, output_dir: str
):
    state = WorkflowState(requirement=Requirement(raw=requirement_text))
    if codebase_path and codebase_path != ".":
        state.artifacts["codebase_path"] = codebase_path

    _emit(
        "info",
        "Workflow started",
        workflow_id=state.id,
        requirement=requirement_text[:120],
        auto_approve=auto,
    )

    start = time.monotonic()
    try:
        WorkflowOrchestrator(auto_approve=auto).run(state)
    except Exception as e:
        inc("sdlc_workflow_runs_total", {"status": "error"})
        _emit("error", f"Workflow error: {e}", workflow_id=state.id)
        raise

    elapsed = time.monotonic() - start
    _emit(
        "info",
        "Workflow complete",
        workflow_id=state.id,
        scenario=state.requirement.scenario_type.value,
        duration_seconds=round(elapsed, 2),
        tasks_total=len(state.tasks),
        tasks_failed=sum(1 for t in state.tasks if t.status.value == "failed"),
        artifacts=len(state.artifacts),
    )

    output_path = write_outputs(state, base_dir=output_dir)
    return state, output_path


def main():
    args = parse_args()

    if args.serve:
        start_http_server(args.port)

    requirement_text = get_requirement(args)
    if not requirement_text:
        _emit("error", "Requirement cannot be empty")
        sys.exit(1)

    try:
        state, output_dir = run_workflow(
            requirement_text,
            auto=args.auto,
            codebase_path=args.codebase_path,
            output_dir=args.output_dir,
        )
    except KeyboardInterrupt:
        _emit("warn", "Workflow interrupted by user")
        sys.exit(1)

    print_summary(state, output_dir)

    if args.serve:
        _emit("info", "HTTP server still running. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
