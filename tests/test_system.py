"""System-level tests for the Agentic SDLC orchestrator pipeline."""
import pytest

from src.models.state import Requirement, TaskStatus, WorkflowState
from src.orchestrator.workflow import WorkflowOrchestrator


def make_state(requirement: str) -> WorkflowState:
    return WorkflowState(requirement=Requirement(raw=requirement))


def run(requirement: str) -> WorkflowState:
    state = make_state(requirement)
    WorkflowOrchestrator(auto_approve=True).run(state)
    return state


# ── Requirement Agent ────────────────────────────────────────────────────────

class TestRequirementAgent:
    def test_greenfield_classification(self):
        state = run("Build a scalable URL shortener service with APIs, persistence, and analytics.")
        assert state.requirement.scenario_type.value == "greenfield"

    def test_brownfield_classification(self):
        state = run("Refactor the existing URL shortener to improve performance.")
        assert state.requirement.scenario_type.value == "brownfield"

    def test_ambiguous_classification(self):
        state = run("Make it fast.")
        assert state.requirement.scenario_type.value == "ambiguous"

    def test_ambiguities_detected_and_resolved(self):
        state = run("Build a scalable URL shortener service with APIs, persistence, and analytics.")
        assert len(state.requirement.ambiguities) > 0
        assert all(a.resolved for a in state.requirement.ambiguities)

    def test_success_criteria_populated(self):
        state = run("Build a scalable URL shortener service with APIs, persistence, and analytics.")
        assert len(state.requirement.success_criteria) >= 3

    def test_raw_input_sanitized_in_normalized(self):
        state = run("Build <script>alert('xss')</script> a service.")
        assert "<script>" not in state.requirement.normalized


# ── Decomposition Agent ──────────────────────────────────────────────────────

class TestDecompositionAgent:
    def test_greenfield_produces_expected_tasks(self):
        state = run("Build a scalable URL shortener service with APIs, persistence, and analytics.")
        task_names = [t.name for t in state.tasks]
        for expected in ["architecture_design", "schema_design", "code_generation",
                         "test_generation", "validation", "documentation"]:
            assert expected in task_names

    def test_analytics_task_injected_when_mentioned(self):
        state = run("Build a scalable URL shortener service with APIs, persistence, and analytics.")
        assert any(t.name == "analytics_design" for t in state.tasks)

    def test_brownfield_produces_codebase_analysis_task(self):
        state = run("Refactor the existing URL shortener to improve performance.")
        assert any(t.name == "codebase_analysis" for t in state.tasks)

    def test_dependencies_are_respected(self):
        state = run("Build a scalable URL shortener service with APIs, persistence, and analytics.")
        task_map = {t.name: t for t in state.tasks}
        code_task = task_map.get("code_generation")
        assert code_task is not None
        assert "schema_design" in code_task.depends_on


# ── Orchestrator ─────────────────────────────────────────────────────────────

class TestOrchestrator:
    def test_all_tasks_reach_terminal_state(self):
        state = run("Build a scalable URL shortener service with APIs, persistence, and analytics.")
        terminal = {TaskStatus.COMPLETED, TaskStatus.APPROVED, TaskStatus.SKIPPED, TaskStatus.FAILED}
        non_terminal = [t for t in state.tasks if t.status not in terminal]
        assert non_terminal == [], f"Non-terminal tasks: {[t.name for t in non_terminal]}"

    def test_workflow_phase_reaches_complete(self):
        state = run("Build a scalable URL shortener service with APIs, persistence, and analytics.")
        assert state.current_phase == "complete"

    def test_execution_log_populated(self):
        state = run("Build a scalable URL shortener service with APIs, persistence, and analytics.")
        assert len(state.execution_log) > 0

    def test_failed_task_skips_dependents(self):
        """Inject a broken agent and verify dependents are skipped."""
        from src.agents.base import BaseAgent
        from src.models.state import Task
        from src.orchestrator.workflow import AGENT_REGISTRY

        class BrokenAgent(BaseAgent):
            name = "architecture_agent"
            def execute(self, task: Task, state: WorkflowState):
                raise RuntimeError("Simulated failure")

        original = AGENT_REGISTRY["architecture_agent"]
        AGENT_REGISTRY["architecture_agent"] = BrokenAgent()
        try:
            state = run("Build a scalable URL shortener service with APIs, persistence, and analytics.")
            arch_task = next(t for t in state.tasks if t.name == "architecture_design")
            assert arch_task.status == TaskStatus.FAILED
            schema_task = next(t for t in state.tasks if t.name == "schema_design")
            assert schema_task.status == TaskStatus.SKIPPED
        finally:
            AGENT_REGISTRY["architecture_agent"] = original

    def test_auto_approve_skips_interactive_gate(self):
        state = run("Build a scalable URL shortener service with APIs, persistence, and analytics.")
        approval_tasks = [t for t in state.tasks if t.requires_approval]
        for t in approval_tasks:
            assert t.status in {TaskStatus.APPROVED, TaskStatus.SKIPPED, TaskStatus.FAILED}

    def test_rejected_task_skips_dependents(self):
        """A human-rejected task must skip all downstream dependents."""
        state = make_state("Build a scalable URL shortener service with APIs, persistence, and analytics.")
        # Reject architecture_design via callback
        def reject_arch(task, _state):
            return task.name != "architecture_design"  # reject only arch
        WorkflowOrchestrator(auto_approve=False, approval_callback=reject_arch).run(state)
        arch = next(t for t in state.tasks if t.name == "architecture_design")
        schema = next(t for t in state.tasks if t.name == "schema_design")
        assert arch.status == TaskStatus.REJECTED
        assert schema.status == TaskStatus.SKIPPED


# ── Artifacts ────────────────────────────────────────────────────────────────

class TestArtifacts:
    def test_architecture_artifact_has_components(self):
        state = run("Build a scalable URL shortener service with APIs, persistence, and analytics.")
        arch = state.artifacts.get("architecture_design", {})
        assert "components" in arch

    def test_schema_artifact_has_db_and_openapi(self):
        state = run("Build a scalable URL shortener service with APIs, persistence, and analytics.")
        schema = state.artifacts.get("schema_design", {})
        assert "database_schema" in schema
        assert "openapi_spec" in schema

    def test_code_artifact_has_required_files(self):
        state = run("Build a scalable URL shortener service with APIs, persistence, and analytics.")
        code = state.artifacts.get("code_generation", {})
        files = code.get("files", {})
        for expected in ["app/main.py", "app/service.py", "app/routes.py", "app/models.py"]:
            assert expected in files, f"Missing generated file: {expected}"

    def test_test_artifact_has_unit_and_integration(self):
        state = run("Build a scalable URL shortener service with APIs, persistence, and analytics.")
        tests = state.artifacts.get("test_generation", {})
        files = tests.get("files", {})
        assert any("unit" in k for k in files)
        assert any("integration" in k for k in files)

    def test_validation_artifact_has_risks(self):
        state = run("Build a scalable URL shortener service with APIs, persistence, and analytics.")
        assert len(state.risks) > 0

    def test_validation_checks_all_pass(self):
        state = run("Build a scalable URL shortener service with APIs, persistence, and analytics.")
        assert state.validation is not None
        blocking_failures = [
            c for c in state.validation.checks
            if c.get("blocking") and not c["passed"]
        ]
        assert blocking_failures == [], f"Blocking checks failed: {blocking_failures}"

    def test_documentation_artifact_has_all_files(self):
        state = run("Build a scalable URL shortener service with APIs, persistence, and analytics.")
        docs = state.artifacts.get("documentation", {})
        files = docs.get("files", {})
        for expected in ["README.md", "ENGINEERING_SUMMARY.md", "RUNBOOK.md"]:
            assert expected in files


# ── Output Writer ─────────────────────────────────────────────────────────────

class TestOutputWriter:
    def test_write_outputs_creates_run_directory(self, tmp_path):
        from src.tools.output_writer import write_outputs
        state = run("Build a scalable URL shortener service with APIs, persistence, and analytics.")
        out_dir = write_outputs(state, base_dir=str(tmp_path))
        assert out_dir.startswith(str(tmp_path))
        import os
        assert os.path.isdir(out_dir)

    def test_write_outputs_creates_summary(self, tmp_path):
        import json
        import os

        from src.tools.output_writer import write_outputs
        state = run("Build a scalable URL shortener service with APIs, persistence, and analytics.")
        out_dir = write_outputs(state, base_dir=str(tmp_path))
        summary_path = os.path.join(out_dir, "workflow_summary.json")
        assert os.path.exists(summary_path)
        with open(summary_path) as f:
            summary = json.load(f)
        assert summary["workflow_id"] == state.id

    def test_path_traversal_blocked(self, tmp_path):
        from src.tools.output_writer import _safe_join
        with pytest.raises(ValueError, match="Path traversal blocked"):
            _safe_join(str(tmp_path), "../../etc/passwd")
