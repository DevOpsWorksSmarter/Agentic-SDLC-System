"""Requirement Understanding Agent.

Interprets raw requirements, identifies ambiguities, normalizes into
a structured engineering problem, and classifies scenario type.
"""

import html
import re

from src.agents.base import BaseAgent
from src.models.state import Ambiguity, Requirement, ScenarioType, Task, WorkflowState

_BROWNFIELD_SIGNALS = {
    "refactor",
    "migrate",
    "fix",
    "bug",
    "enhance",
    "improve",
    "update",
    "existing",
    "legacy",
    "optimize",
    "extend",
}

_AMBIGUITY_SIGNALS = {
    "scalable": "What scale is expected? (RPS, data volume, geographic distribution)",
    "fast": "What are the latency SLOs? (p50, p99 targets)",
    "secure": "What security standards apply? (OWASP, SOC2, internal policy)",
    "analytics": "What analytics are required? (click counts, geo, referrer, time-series?)",
    "persistence": "What persistence backend is preferred? (SQL, NoSQL, Redis, cloud-managed?)",
    "simple": "What does 'simple' mean in this context? (API surface, ops complexity, UX?)",
}


class RequirementAgent(BaseAgent):
    name = "requirement_agent"

    def execute(self, task: Task, state: WorkflowState) -> Requirement:
        raw = state.requirement.raw
        # Sanitize raw input before any string interpolation into outputs
        safe_raw = html.escape(raw.strip())
        lower = raw.lower()

        scenario = self._classify_scenario(lower)
        ambiguities = self._detect_ambiguities(lower)
        normalized = self._normalize(safe_raw, scenario)
        intent = self._extract_intent(raw)
        constraints = self._extract_constraints(lower)
        success_criteria = self._derive_success_criteria(lower)

        req = state.requirement
        req.normalized = normalized
        req.intent = intent
        req.scenario_type = scenario
        req.ambiguities = ambiguities
        req.constraints = constraints
        req.success_criteria = success_criteria
        return req

    def _classify_scenario(self, text: str) -> ScenarioType:
        if any(kw in text for kw in _BROWNFIELD_SIGNALS):
            return ScenarioType.BROWNFIELD
        if len(text.split()) < 8 or not any(
            c in text for c in ["api", "service", "system", "app"]
        ):
            return ScenarioType.AMBIGUOUS
        return ScenarioType.GREENFIELD

    def _detect_ambiguities(self, text: str) -> list[Ambiguity]:
        found = []
        for keyword, question in _AMBIGUITY_SIGNALS.items():
            if keyword in text:
                resolution = self._default_resolution(keyword)
                found.append(
                    Ambiguity(
                        question=question,
                        resolution=resolution,
                        resolved=resolution is not None,
                    )
                )
        return found

    def _default_resolution(self, keyword: str) -> str | None:
        defaults = {
            "scalable": "Target: 10k RPS, horizontal scaling via stateless services + Redis cache",
            "analytics": "Track: click count, unique visitors, referrer, user-agent, timestamp per URL",
            "persistence": "Primary: PostgreSQL for URL records; Redis for hot-path caching",
            "fast": "p99 redirect latency < 50ms via cache-first lookup",
            "secure": "Input validation, rate limiting, no open redirect, HTTPS-only",
            "simple": "RESTful API with minimal surface area; no auth required for MVP",
        }
        return defaults.get(keyword)

    def _normalize(self, safe_raw: str, scenario: ScenarioType) -> str:
        return (
            f"[{scenario.value.upper()}] {safe_raw} "
            f"— Normalized: Design and implement a production-ready system addressing "
            f"the stated requirement with clear API contracts, persistence layer, "
            f"test coverage, and operational documentation."
        )

    def _extract_intent(self, raw: str) -> str:
        verbs = re.findall(
            r"\b(build|create|implement|design|add|fix|refactor|migrate|extend)\b",
            raw.lower(),
        )
        primary_verb = verbs[0] if verbs else "implement"
        nouns = re.findall(
            r"\b(service|api|system|feature|module|endpoint|database|cache)\b",
            raw.lower(),
        )
        primary_noun = nouns[0] if nouns else "solution"
        return f"Primary intent: {primary_verb} a {primary_noun} that satisfies the stated requirement."

    def _extract_constraints(self, text: str) -> list[str]:
        constraints = ["RESTful API design", "Stateless service layer"]
        if "scalab" in text:
            constraints.append("Horizontal scalability required")
        if "analytic" in text:
            constraints.append(
                "Analytics must not impact redirect latency (async write path)"
            )
        if "persist" in text or "storage" in text or "database" in text:
            constraints.append("Durable persistence with crash recovery")
        return constraints

    def _derive_success_criteria(self, text: str) -> list[str]:
        criteria = [
            "All API endpoints return correct HTTP status codes",
            "Unit test coverage >= 80%",
            "Integration tests cover happy path and error cases",
        ]
        if "url" in text or "short" in text:
            criteria += [
                "Short URL redirects to original URL within p99 < 50ms",
                "Duplicate long URLs return the same short code",
                "Invalid short codes return 404",
            ]
        if "analytic" in text:
            criteria.append(
                "Click events are recorded asynchronously without blocking redirect"
            )
        return criteria
