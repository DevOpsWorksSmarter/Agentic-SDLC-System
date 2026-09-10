"""
Standalone test runner — executes all system tests without pytest.
Run: python run_tests.py
"""
import sys
import traceback
import tempfile
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.models.state import Requirement, TaskStatus, WorkflowState
from src.orchestrator.workflow import WorkflowOrchestrator

PASS = 0
FAIL = 0
ERRORS = []

URL_REQ = "Build a scalable URL shortener service with APIs, persistence, and analytics."


def run(requirement):
    state = WorkflowState(requirement=Requirement(raw=requirement))
    WorkflowOrchestrator(auto_approve=True).run(state)
    return state


def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        print(f"  [PASS] {name}")
        PASS += 1
    else:
        print(f"  [FAIL] {name}" + (f" — {detail}" if detail else ""))
        FAIL += 1
        ERRORS.append(name)


def section(title):
    print(f"\n{'='*55}")
    print(f"  {title}")
    print(f"{'='*55}")


# ── RequirementAgent ──────────────────────────────────────────────────────────
section("TestRequirementAgent")
s = run(URL_REQ)
check("greenfield classification",
      s.requirement.scenario_type.value == "greenfield")

s2 = run("Refactor the existing URL shortener to improve performance.")
check("brownfield classification",
      s2.requirement.scenario_type.value == "brownfield")

s3 = run("Make it fast.")
check("ambiguous classification",
      s3.requirement.scenario_type.value == "ambiguous")

check("ambiguities detected",
      len(s.requirement.ambiguities) > 0)
check("all ambiguities resolved",
      all(a.resolved for a in s.requirement.ambiguities))
check("success criteria populated",
      len(s.requirement.success_criteria) >= 3)

s_xss = run("Build <script>alert('xss')</script> a service.")
check("XSS sanitized in normalized",
      "<script>" not in s_xss.requirement.normalized)

# ── DecompositionAgent ────────────────────────────────────────────────────────
section("TestDecompositionAgent")
task_names = [t.name for t in s.tasks]
for expected in ["architecture_design","schema_design","code_generation","test_generation","validation","documentation"]:
    check(f"task present: {expected}", expected in task_names)

check("analytics_design injected when mentioned",
      any(t.name == "analytics_design" for t in s.tasks))

check("brownfield has codebase_analysis",
      any(t.name == "codebase_analysis" for t in s2.tasks))

task_map = {t.name: t for t in s.tasks}
code_task = task_map.get("code_generation")
check("code_generation depends on schema_design",
      code_task is not None and "schema_design" in code_task.depends_on)

# ── Orchestrator ──────────────────────────────────────────────────────────────
section("TestOrchestrator")
terminal = {TaskStatus.COMPLETED, TaskStatus.APPROVED, TaskStatus.SKIPPED, TaskStatus.FAILED}
non_terminal = [t for t in s.tasks if t.status not in terminal]
check("all tasks reach terminal state",
      len(non_terminal) == 0,
      f"non-terminal: {[t.name for t in non_terminal]}")

check("workflow phase is complete",
      s.current_phase == "complete")

check("execution log populated",
      len(s.execution_log) > 0)

# Failure injection test
from src.orchestrator.workflow import AGENT_REGISTRY
from src.agents.base import BaseAgent
from src.models.state import Task

class BrokenAgent(BaseAgent):
    name = "architecture_agent"
    def execute(self, task, state):
        raise RuntimeError("Simulated failure")

original = AGENT_REGISTRY["architecture_agent"]
AGENT_REGISTRY["architecture_agent"] = BrokenAgent()
try:
    sf = run(URL_REQ)
    arch = next(t for t in sf.tasks if t.name == "architecture_design")
    schema = next(t for t in sf.tasks if t.name == "schema_design")
    check("failed task status is FAILED", arch.status == TaskStatus.FAILED)
    check("dependent task is SKIPPED", schema.status == TaskStatus.SKIPPED)
finally:
    AGENT_REGISTRY["architecture_agent"] = original

approval_tasks = [t for t in s.tasks if t.requires_approval]
check("auto_approve resolves all approval gates",
      all(t.status in {TaskStatus.APPROVED, TaskStatus.SKIPPED, TaskStatus.FAILED}
          for t in approval_tasks))

# Rejection propagation test
from src.models.state import Requirement as Req
sr = WorkflowState(requirement=Req(raw=URL_REQ))
def reject_arch(task, _state):
    return task.name != "architecture_design"
WorkflowOrchestrator(auto_approve=False, approval_callback=reject_arch).run(sr)
arch_r = next(t for t in sr.tasks if t.name == "architecture_design")
schema_r = next(t for t in sr.tasks if t.name == "schema_design")
check("rejected task status is REJECTED", arch_r.status == TaskStatus.REJECTED)
check("dependent of rejected task is SKIPPED", schema_r.status == TaskStatus.SKIPPED)

# ── Artifacts ─────────────────────────────────────────────────────────────────
section("TestArtifacts")
arch = s.artifacts.get("architecture_design", {})
check("architecture has components", "components" in arch)

schema = s.artifacts.get("schema_design", {})
check("schema has database_schema", "database_schema" in schema)
check("schema has openapi_spec", "openapi_spec" in schema)

code = s.artifacts.get("code_generation", {})
files = code.get("files", {})
for f in ["app/main.py","app/service.py","app/routes.py","app/models.py","app/repository.py"]:
    check(f"code file present: {f}", f in files)

tests = s.artifacts.get("test_generation", {})
tfiles = tests.get("files", {})
check("unit tests present", any("unit" in k for k in tfiles))
check("integration tests present", any("integration" in k for k in tfiles))

check("risks identified", len(s.risks) > 0)

blocking_failures = [c for c in s.validation.checks if c.get("blocking") and not c["passed"]]
check("no blocking validation failures", len(blocking_failures) == 0,
      str(blocking_failures))

docs = s.artifacts.get("documentation", {})
dfiles = docs.get("files", {})
for f in ["README.md","ENGINEERING_SUMMARY.md","RUNBOOK.md"]:
    check(f"doc file present: {f}", f in dfiles)

# ── OutputWriter ──────────────────────────────────────────────────────────────
section("TestOutputWriter")
from src.tools.output_writer import write_outputs, _safe_join

with tempfile.TemporaryDirectory() as tmp:
    out_dir = write_outputs(s, base_dir=tmp)
    check("run directory created", os.path.isdir(out_dir))
    summary_path = os.path.join(out_dir, "workflow_summary.json")
    check("workflow_summary.json exists", os.path.exists(summary_path))
    import json
    with open(summary_path) as f:
        summary = json.load(f)
    check("summary workflow_id matches", summary["workflow_id"] == s.id)

try:
    _safe_join(tmp, "../../etc/passwd")
    check("path traversal blocked", False, "should have raised ValueError")
except ValueError:
    check("path traversal blocked", True)

# ── Metrics ───────────────────────────────────────────────────────────────────
section("TestMetrics")
from src.tools.metrics import metrics_text, _counters
check("workflow run counter incremented",
      any("sdlc_workflow_runs_total" in k for k in _counters))
check("task execution counter incremented",
      any("sdlc_task_executions_total" in k for k in _counters))
metrics_output = metrics_text()
check("metrics_text produces output", len(metrics_output) > 0)
check("metrics contains workflow counter",
      "sdlc_workflow_runs_total" in metrics_output)

# ── Summary ───────────────────────────────────────────────────────────────────
print(f"\n{'='*55}")
total = PASS + FAIL
print(f"  Results: {PASS}/{total} passed  |  {FAIL} failed")
if ERRORS:
    print(f"  Failed: {ERRORS}")
print(f"{'='*55}\n")
sys.exit(0 if FAIL == 0 else 1)
