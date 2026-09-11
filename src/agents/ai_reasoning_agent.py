"""Structured AI reasoning agent. Optional LLM; deterministic fallback keeps CI reproducible."""

from src.agents.base import BaseAgent
from src.models.state import Task, WorkflowState
from src.tools.ai_client import AIClient


class AIReasoningAgent(BaseAgent):
    name = "ai_reasoning_agent"

    def execute(self, task: Task, state: WorkflowState) -> dict:
        req = state.requirement
        fallback = {
            "summary": req.normalized,
            "intent": req.intent,
            "assumptions": [a.resolution for a in req.ambiguities if a.resolution],
            "acceptance_criteria": req.success_criteria,
            "risks": ["Ambiguous scale/latency targets may require confirmation"],
            "confidence": 0.91,
        }
        result = AIClient().complete_json(
            "You are a senior software architect. Return only JSON with summary, intent, assumptions, acceptance_criteria, risks, confidence.",
            req.raw,
            fallback,
        )
        state.artifacts["ai_reasoning"] = result
        return result
