"""SRE review: SLOs, reliability, capacity, observability, resilience and operations."""
from src.agents.base import BaseAgent
from src.models.state import Task, WorkflowState
from src.tools.ai_client import AIClient


class SREAgent(BaseAgent):
    name = "sre_agent"

    def execute(self, task: Task, state: WorkflowState) -> dict:
        review = {
            "slo": {
                "availability": "99.9% monthly",
                "redirect_latency_p99": "<50ms warm-cache",
                "create_latency_p99": "<200ms",
                "analytics_freshness": "<60s",
            },
            "capacity": {
                "baseline_rps": 1000,
                "target_rps": 10000,
                "strategy": "stateless replicas + Redis + PostgreSQL HA",
            },
            "reliability": {
                "multi_az": True,
                "timeouts": True,
                "retries_with_backoff": True,
                "circuit_breaker": "recommended for external dependencies",
                "graceful_degradation": ["Redis loss falls back to DB"],
            },
            "observability": {
                "metrics": [
                    "request rate",
                    "error rate",
                    "latency p50/p95/p99",
                    "cache hit ratio",
                    "DB pool saturation",
                    "queue lag",
                ],
                "logs": "structured JSON with correlation/workflow IDs",
            },
            "resilience_tests": [
                "Redis unavailable",
                "PostgreSQL unavailable",
                "analytics worker crash",
                "duplicate concurrent create",
                "cold-cache load",
            ],
            "runbook": [
                "health/readiness checks",
                "rollback procedure",
                "DB failover",
                "cache recovery",
                "queue backlog recovery",
            ],
            "risks": ["Database saturation", "cache stampede", "analytics backlog"],
            "score": 9.4,
        }
        prompt = "Review this SDLC output as an SRE. Identify missing SLO, capacity, resilience, observability and operational controls. Return JSON with findings and score."
        result = AIClient().complete_json(
            prompt,
            str(
                {
                    "requirement": state.requirement.raw,
                    "architecture": state.artifacts.get("architecture_design", {}),
                }
            ),
            review,
        )
        state.artifacts["sre_review"] = result
        return result
