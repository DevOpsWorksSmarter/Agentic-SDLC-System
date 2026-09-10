"""Output Writer.

Persists all generated artifacts from the workflow state
to the outputs directory in a structured layout.
"""
import json
import os
import re

from src.models.state import WorkflowState

_SAFE_SEGMENT = re.compile(r"[^a-zA-Z0-9_\-.]")  # allow dots for file extensions
_TRAVERSAL = re.compile(r"^\.+$")  # block pure dot segments like '.' and '..'


def _safe_segment(name: str) -> str:
    """Sanitize a single path segment to prevent traversal."""
    sanitized = _SAFE_SEGMENT.sub("_", name)
    # Block segments that are purely dots after sanitization
    if _TRAVERSAL.match(sanitized):
        return "_"
    return sanitized


def _safe_join(base: str, *parts: str) -> str:
    """Join and resolve path, raising if result escapes base directory."""
    base = os.path.realpath(base)
    candidate = os.path.realpath(os.path.join(base, *parts))
    if not (candidate == base or candidate.startswith(base + os.sep)):
        raise ValueError(f"Path traversal blocked: {candidate}")
    return candidate


def write_outputs(state: WorkflowState, base_dir: str = "outputs") -> str:
    if not state or not state.id:
        raise ValueError("Invalid workflow state")

    base_dir = os.path.realpath(base_dir)
    run_dir = _safe_join(base_dir, f"run_{_safe_segment(state.id)}")
    os.makedirs(run_dir, exist_ok=True)

    for artifact_name, artifact_data in state.artifacts.items():
        safe_artifact = _safe_segment(artifact_name)
        artifact_dir = _safe_join(run_dir, safe_artifact)

        if isinstance(artifact_data, dict) and "files" in artifact_data:
            for filepath, content in artifact_data["files"].items():
                # Sanitize each path component individually
                safe_parts = [_safe_segment(p) for p in filepath.replace("\\", "/").split("/") if p]
                if not safe_parts:
                    continue
                full_path = _safe_join(artifact_dir, *safe_parts)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content)
        else:
            os.makedirs(artifact_dir, exist_ok=True)
            out_path = _safe_join(artifact_dir, "output.json")
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(artifact_data, f, indent=2, default=str)

    log_path = _safe_join(run_dir, "execution_log.json")
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(state.execution_log, f, indent=2, default=str)

    summary = {
        "workflow_id": state.id,
        "scenario": state.requirement.scenario_type.value,
        "requirement": state.requirement.raw,
        "tasks": [
            {
                "name": t.name,
                "agent": t.agent,
                "status": t.status.value,
                "depends_on": t.depends_on,
                "error": t.error,
                "retry_count": t.retry_count,
            }
            for t in state.tasks
        ],
        "risks": [
            {
                "title": r.title,
                "level": r.level.value,
                "mitigation": r.mitigation,
                "tradeoff": r.tradeoff,
            }
            for r in state.risks
        ],
        "validation": {
            "passed": state.validation.passed if state.validation else None,
            "coverage_estimate": state.validation.coverage_estimate if state.validation else None,
            "checks": state.validation.checks if state.validation else [],
        },
        "artifacts_generated": list(state.artifacts.keys()),
    }
    summary_path = _safe_join(run_dir, "workflow_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)

    return run_dir
