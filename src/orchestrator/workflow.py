"""Workflow Orchestrator.

Coordinates multi-agent execution with:
- Dependency-aware task scheduling
- Human-in-the-loop approval gates
- Error handling and retry logic
- Cross-step state propagation
"""
from src.agents.architecture_agent import ArchitectureAgent
from src.agents.code_generation_agent import CodeGenerationAgent
from src.agents.codebase_reasoning_agent import CodebaseReasoningAgent
from src.agents.decomposition_agent import DecompositionAgent
from src.agents.documentation_agent import DocumentationAgent
from src.agents.requirement_agent import RequirementAgent
from src.agents.schema_agent import SchemaAgent
from src.agents.test_generation_agent import TestGenerationAgent
from src.agents.validation_agent import ValidationAgent
from src.models.state import Task, TaskStatus, WorkflowState
from src.tools.metrics import Timer, inc

AGENT_REGISTRY = {
    "requirement_agent": RequirementAgent(),
    "decomposition_agent": DecompositionAgent(),
    "architecture_agent": ArchitectureAgent(),
    "schema_agent": SchemaAgent(),
    "code_generation_agent": CodeGenerationAgent(),
    "test_generation_agent": TestGenerationAgent(),
    "validation_agent": ValidationAgent(),
    "codebase_reasoning_agent": CodebaseReasoningAgent(),
    "documentation_agent": DocumentationAgent(),
}

_SEED_TASKS = ("understand_requirement", "decompose")
_TERMINAL = {TaskStatus.COMPLETED, TaskStatus.APPROVED, TaskStatus.SKIPPED, TaskStatus.REJECTED}


class WorkflowOrchestrator:
    def __init__(self, auto_approve: bool = False, approval_callback=None):
        self.auto_approve = auto_approve
        self.approval_callback = approval_callback

    def run(self, state: WorkflowState) -> WorkflowState:
        state.log("orchestrator", f"Starting workflow {state.id}")
        _timer = Timer("sdlc_workflow_duration_seconds", {"workflow_id": state.id})
        _timer.__enter__()

        # Phase 1: Requirement Understanding
        state.current_phase = "requirement_understanding"
        self._run_task(Task(name="understand_requirement", agent="requirement_agent"), state)

        # Phase 2: Task Decomposition
        state.current_phase = "task_decomposition"
        self._run_task(Task(name="decompose", agent="decomposition_agent"), state)

        # Phase 3: Execute decomposed plan in dependency order
        state.current_phase = "execution"
        self._execute_plan(state)

        state.current_phase = "complete"
        state.log("orchestrator", f"Workflow {state.id} complete")
        _timer.__exit__(None, None, None)
        inc("sdlc_workflow_runs_total", {"status": "complete", "scenario": state.requirement.scenario_type.value})
        return state

    def _execute_plan(self, state: WorkflowState):
        plan = [t for t in state.tasks if t.name not in _SEED_TASKS]
        max_iterations = len(plan) * 2

        for _ in range(max_iterations):
            ready = self._ready_tasks(plan, state)
            if not ready:
                pending = [t for t in plan if t.status == TaskStatus.PENDING]
                if pending:
                    state.log("orchestrator", f"Deadlock — skipping: {[t.name for t in pending]}", level="error")
                    for t in pending:
                        t.status = TaskStatus.SKIPPED
                break

            for task in ready:
                self._run_task(task, state)
                if task.status in {TaskStatus.FAILED, TaskStatus.REJECTED}:
                    self._skip_dependents(task, plan, state)

    def _ready_tasks(self, tasks: list[Task], state: WorkflowState) -> list[Task]:
        return [
            t for t in tasks
            if t.status == TaskStatus.PENDING
            and all(
                any(s.name == dep and s.status in _TERMINAL for s in state.tasks)
                for dep in t.depends_on
            )
        ]

    def _run_task(self, task: Task, state: WorkflowState):
        inc("sdlc_task_executions_total", {"agent": task.agent, "status": "started"})
        agent = AGENT_REGISTRY.get(task.agent)
        if not agent:
            task.status = TaskStatus.FAILED
            task.error = f"No agent registered: {task.agent}"
            state.log("orchestrator", task.error, level="error")
            return

        agent.run(task, state)

        if task.output is not None:
            state.artifacts[task.name] = task.output

        status = "failed" if task.status == TaskStatus.FAILED else "success"
        inc("sdlc_task_executions_total", {"agent": task.agent, "status": status})
        if task.status == TaskStatus.AWAITING_APPROVAL:
            self._handle_approval(task, state)

    def _handle_approval(self, task: Task, state: WorkflowState):
        state.log("orchestrator", f"Awaiting approval: {task.name}")

        if self.auto_approve:
            task.status = TaskStatus.APPROVED
            inc("sdlc_approval_decisions_total", {"decision": "auto_approved", "task": task.name})
            state.log("orchestrator", f"Auto-approved: {task.name}")
            return

        if self.approval_callback:
            approved = self.approval_callback(task, state)
            task.status = TaskStatus.APPROVED if approved else TaskStatus.REJECTED
            if not approved:
                task.error = "Rejected by reviewer"
            state.log("orchestrator", f"Callback decision for {task.name}: {task.status.value}")
            return

        # Interactive CLI gate
        print(f"\n{'='*60}")
        print(f"[APPROVAL GATE] Task: {task.name}  |  Agent: {task.agent}")
        print(f"Description: {task.description}")
        print(f"{'='*60}")
        choice = input("Approve? [y=yes / n=reject / s=skip]: ").strip().lower()
        if choice == "y":
            task.status = TaskStatus.APPROVED
        elif choice == "s":
            task.status = TaskStatus.SKIPPED
        else:
            task.status = TaskStatus.REJECTED
            task.error = "Rejected by human reviewer"
        state.log("orchestrator", f"Human decision for {task.name}: {task.status.value}")

    def _skip_dependents(self, failed: Task, tasks: list[Task], state: WorkflowState):
        for t in tasks:
            if failed.name in t.depends_on and t.status == TaskStatus.PENDING:
                t.status = TaskStatus.SKIPPED
                t.error = f"Dependency '{failed.name}' failed"
                state.log("orchestrator", f"Skipped {t.name} — dependency failed", level="warn")
                self._skip_dependents(t, tasks, state)
