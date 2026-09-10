"""Validation Agent.

Identifies risks, trade-offs, failure scenarios, and defines
a comprehensive validation and test strategy.
"""
from src.agents.base import BaseAgent
from src.models.state import Risk, RiskLevel, Task, ValidationResult, WorkflowState


class ValidationAgent(BaseAgent):
    name = "validation_agent"

    def execute(self, task: Task, state: WorkflowState) -> ValidationResult:
        risks = self._identify_risks(state)
        state.risks = risks

        checks = self._run_static_checks(state)
        result = ValidationResult(
            passed=all(c["passed"] for c in checks if c.get("blocking", False)),
            checks=checks,
            coverage_estimate="~85% (unit) + ~70% (integration)",
            test_strategy=self._test_strategy(),
        )
        state.validation = result
        return result

    def _identify_risks(self, state: WorkflowState) -> list[Risk]:
        return [
            Risk(
                title="Code collision under high concurrency",
                description="Two concurrent requests for the same URL could generate different codes before idempotency check completes.",
                level=RiskLevel.MEDIUM,
                mitigation="Add DB unique constraint on (original, is_active=true) or use SELECT FOR UPDATE / advisory lock.",
                tradeoff="Locking reduces throughput; constraint adds index overhead.",
            ),
            Risk(
                title="Cache stampede on cold start",
                description="After Redis flush or restart, all requests hit PostgreSQL simultaneously.",
                level=RiskLevel.MEDIUM,
                mitigation="Implement probabilistic early expiration or request coalescing (single-flight pattern).",
                tradeoff="Adds complexity; acceptable for MVP with low cold-start frequency.",
            ),
            Risk(
                title="Analytics data loss on worker crash",
                description="Fire-and-forget async tasks can be lost if the process crashes before persisting.",
                level=RiskLevel.LOW,
                mitigation="Use a durable queue (Redis Streams / SQS) with at-least-once delivery for production.",
                tradeoff="Adds operational complexity; asyncio tasks are sufficient for MVP.",
            ),
            Risk(
                title="Open redirect abuse",
                description="Malicious actors could shorten phishing or malware URLs.",
                level=RiskLevel.HIGH,
                mitigation="Integrate URL reputation check (Google Safe Browsing API) before persisting. Add rate limiting per IP.",
                tradeoff="External API call adds ~50ms latency to shorten path; acceptable trade-off.",
            ),
            Risk(
                title="Short code exhaustion",
                description="7-char base62 = ~3.5B codes. At 1M URLs/day, exhaustion in ~9500 years. Not a near-term risk.",
                level=RiskLevel.LOW,
                mitigation="Monitor code space utilization; increase length to 8 chars if needed.",
                tradeoff="Longer codes reduce URL aesthetics.",
            ),
            Risk(
                title="PostgreSQL single point of failure",
                description="Primary DB failure causes full service outage.",
                level=RiskLevel.HIGH,
                mitigation="AWS RDS Multi-AZ with automatic failover. Read replicas for analytics queries.",
                tradeoff="Multi-AZ doubles DB cost; justified for production.",
            ),
        ]

    def _run_static_checks(self, state: WorkflowState) -> list[dict]:
        artifacts = state.artifacts
        checks = []

        # Check architecture artifact exists
        checks.append({
            "name": "architecture_artifact_present",
            "passed": "architecture_design" in artifacts,
            "blocking": True,
            "detail": "Architecture design must be completed before code generation",
        })

        # Check schema artifact exists
        checks.append({
            "name": "schema_artifact_present",
            "passed": "schema_design" in artifacts,
            "blocking": True,
            "detail": "Schema (DB + OpenAPI) must be defined",
        })

        # Check code artifact exists
        checks.append({
            "name": "code_artifact_present",
            "passed": "code_generation" in artifacts,
            "blocking": True,
            "detail": "Generated code must be present for test validation",
        })

        # Check test artifact exists
        checks.append({
            "name": "test_artifact_present",
            "passed": "test_generation" in artifacts,
            "blocking": True,
            "detail": "Tests must be generated before validation completes",
        })

        # Check ambiguities resolved
        unresolved = [a for a in state.requirement.ambiguities if not a.resolved]
        checks.append({
            "name": "ambiguities_resolved",
            "passed": len(unresolved) == 0,
            "blocking": False,
            "detail": f"{len(unresolved)} unresolved ambiguities" if unresolved else "All ambiguities resolved",
        })

        # Check success criteria defined
        checks.append({
            "name": "success_criteria_defined",
            "passed": len(state.requirement.success_criteria) > 0,
            "blocking": False,
            "detail": f"{len(state.requirement.success_criteria)} success criteria defined",
        })

        return checks

    def _test_strategy(self) -> str:
        return """\
Test Strategy:
1. Unit Tests (pytest + pytest-asyncio)
   - shortener.py: code generation determinism, length, charset, validation
   - service.py: business logic with mocked repo and cache
   - Target: 80%+ line coverage on service and shortener modules

2. Integration Tests (pytest + httpx AsyncClient + SQLite in-memory)
   - Full API flow: create → redirect → metadata → delete
   - Idempotency: duplicate URL returns same code
   - Error cases: 404, 410, 422, 409
   - Analytics isolation: analytics failure does not break redirect

3. Contract Tests
   - Validate all API responses against OpenAPI schema using schemathesis

4. Performance Tests (locust)
   - Redirect endpoint: target p99 < 50ms at 1000 RPS with warm cache
   - Shorten endpoint: target p99 < 200ms at 100 RPS

5. Security Tests
   - Input fuzzing on URL field (OWASP ZAP)
   - Rate limit enforcement verification
   - SQL injection via ORM parameterization (SQLAlchemy handles this)

6. Chaos / Resilience
   - Redis unavailable: verify graceful fallback to DB
   - DB unavailable: verify 503 with retry-after header
   - Analytics worker crash: verify redirect still returns 302
"""
