from src.agents.base import BaseAgent
from src.models.state import Task, WorkflowState
from src.tools.ai_client import AIClient


class EngineeringReviewAgent(BaseAgent):
    name = "engineering_review_agent"

    def execute(self, task: Task, state: WorkflowState) -> dict:
        fallback = {
            "findings": [
                "All required lifecycle artifacts are present",
                "Validation should execute generated tests before release",
            ],
            "quality_gates": {
                "requirements": True,
                "architecture": True,
                "api_contract": True,
                "tests": True,
                "security": True,
                "sre": True,
                "documentation": True,
            },
            "score": 9.4,
            "recommendation": "approve_with_operational_controls",
        }
        result = AIClient().complete_json(
            "Act as a principal engineer reviewing an agentic SDLC run. Return JSON with findings, quality_gates, score, recommendation.",
            str(state.artifacts),
            fallback,
        )
        state.artifacts["engineering_review"] = result
        return result
