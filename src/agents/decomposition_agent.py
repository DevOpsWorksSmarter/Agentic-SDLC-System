"""Task Decomposition Agent.

Breaks a normalized requirement into structured, ordered tasks with
explicit dependencies and assigned agents.
"""

from src.agents.base import BaseAgent
from src.models.state import ScenarioType, Task, TaskStatus, WorkflowState


class DecompositionAgent(BaseAgent):
    name = "decomposition_agent"

    def execute(self, task: Task, state: WorkflowState) -> list[dict]:
        req = state.requirement
        scenario = req.scenario_type

        if scenario == ScenarioType.BROWNFIELD:
            tasks = self._brownfield_tasks()
        else:
            tasks = self._greenfield_tasks(req)

        # Inject into state
        state.tasks = [
            t for t in state.tasks if t.name == "decompose"
        ]  # keep orchestrator seed task
        for td in tasks:
            t = Task(
                name=td["name"],
                description=td["description"],
                agent=td["agent"],
                depends_on=td.get("depends_on", []),
                requires_approval=td.get("requires_approval", False),
                status=TaskStatus.PENDING,
            )
            state.tasks.append(t)

        state.log(self.name, f"Decomposed into {len(tasks)} tasks")
        return [
            {
                "name": t["name"],
                "agent": t["agent"],
                "depends_on": t.get("depends_on", []),
            }
            for t in tasks
        ]

    def _greenfield_tasks(self, req) -> list[dict]:
        tasks = [
            {
                "name": "architecture_design",
                "description": "Design system architecture: components, data flow, API surface, infra topology",
                "agent": "architecture_agent",
                "depends_on": [],
                "requires_approval": True,
            },
            {
                "name": "schema_design",
                "description": "Define database schema and API contracts (OpenAPI spec)",
                "agent": "schema_agent",
                "depends_on": ["architecture_design"],
            },
            {
                "name": "code_generation",
                "description": "Generate production-quality service code from schema and architecture",
                "agent": "code_generation_agent",
                "depends_on": ["schema_design"],
                "requires_approval": True,
            },
            {
                "name": "test_generation",
                "description": "Generate unit and integration tests for all generated code",
                "agent": "test_generation_agent",
                "depends_on": ["code_generation"],
            },
            {
                "name": "validation",
                "description": "Validate outputs: risks, trade-offs, test strategy, guardrails",
                "agent": "validation_agent",
                "depends_on": ["test_generation"],
                "requires_approval": True,
            },
            {
                "name": "documentation",
                "description": "Generate engineering summary, README, and operational runbook",
                "agent": "documentation_agent",
                "depends_on": ["validation"],
            },
        ]

        # Add analytics tasks if requirement mentions analytics
        if "analytic" in req.raw.lower():
            tasks.insert(
                3,
                {
                    "name": "analytics_design",
                    "description": "Design async analytics pipeline: event capture, aggregation, query API",
                    "agent": "architecture_agent",
                    "depends_on": ["schema_design"],
                },
            )
            # Update code_generation dependency
            for t in tasks:
                if t["name"] == "code_generation":
                    t["depends_on"].append("analytics_design")

        return tasks

    def _brownfield_tasks(self) -> list[dict]:
        return [
            {
                "name": "codebase_analysis",
                "description": "Analyze existing codebase: impacted modules, APIs, data flows",
                "agent": "codebase_reasoning_agent",
                "depends_on": [],
                "requires_approval": True,
            },
            {
                "name": "impact_assessment",
                "description": "Assess change impact: breaking changes, migration needs, risk surface",
                "agent": "validation_agent",
                "depends_on": ["codebase_analysis"],
            },
            {
                "name": "code_generation",
                "description": "Generate targeted code changes based on impact assessment",
                "agent": "code_generation_agent",
                "depends_on": ["impact_assessment"],
                "requires_approval": True,
            },
            {
                "name": "test_generation",
                "description": "Generate regression and new tests covering the change surface",
                "agent": "test_generation_agent",
                "depends_on": ["code_generation"],
            },
            {
                "name": "validation",
                "description": "Validate changes against existing contracts and risk surface",
                "agent": "validation_agent",
                "depends_on": ["test_generation"],
                "requires_approval": True,
            },
            {
                "name": "documentation",
                "description": "Generate change summary, migration guide, and updated docs",
                "agent": "documentation_agent",
                "depends_on": ["validation"],
            },
        ]
