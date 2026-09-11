"""Bounded repair agent. Only allow-listed deterministic repairs are applied."""

from src.agents.base import BaseAgent
from src.models.state import Task, WorkflowState


class RepairAgent(BaseAgent):
    name = "repair_agent"
    ALLOWED = {"add_expiry_guard", "add_missing_healthcheck", "add_timeout_config"}

    def execute(self, task: Task, state: WorkflowState) -> dict:
        requested = state.artifacts.get("repair_request", "add_timeout_config")
        applied = requested if requested in self.ALLOWED else None
        result = {
            "requested": requested,
            "applied": applied,
            "autonomous": bool(applied),
            "requires_human_for_unlisted": not bool(applied),
        }
        state.artifacts["repair_result"] = result
        return result
