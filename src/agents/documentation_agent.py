"""Documentation Agent.

Generates the final engineering summary, README, and operational runbook
from all accumulated workflow artifacts.
"""

import html

from src.agents.base import BaseAgent
from src.models.state import Task, WorkflowState


def _s(value: str) -> str:
    """Sanitize a string for safe embedding in markdown/HTML output."""
    return html.escape(str(value)) if value else ""


class DocumentationAgent(BaseAgent):
    name = "documentation_agent"

    def execute(self, task: Task, state: WorkflowState) -> dict:
        return {
            "files": {
                "README.md": self._readme(state),
                "ENGINEERING_SUMMARY.md": self._engineering_summary(state),
                "RUNBOOK.md": self._runbook(),
            }
        }

    def _readme(self, state: WorkflowState) -> str:
        req = state.requirement
        return f"""\
# URL Shortener Service

> {_s(req.normalized)}

## Quick Start

```bash
# Clone and start
docker-compose up --build

# Create a short URL
curl -X POST http://localhost:8000/urls \\
  -H "Content-Type: application/json" \\
  -d '{{"url": "https://www.example.com/very/long/path"}}'

# Redirect
curl -L http://localhost:8000/{{code}}

# Get stats
curl http://localhost:8000/urls/{{code}}/stats
```

## Architecture

```
Client → [Nginx] → [FastAPI Service] → [Redis Cache]
                                     ↘ [PostgreSQL]
                                     ↘ [Analytics Worker]
```

## API Reference

| Method | Path | Description |
|--------|------|-------------|
| POST | /urls | Create short URL |
| GET | /{{code}} | Redirect to original |
| GET | /urls/{{code}} | Get URL metadata |
| DELETE | /urls/{{code}} | Deactivate URL |
| GET | /urls/{{code}}/stats | Get click analytics |

## Running Tests

```bash
pip install pytest pytest-asyncio httpx aiosqlite
pytest tests/ -v --tb=short
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| DATABASE_URL | postgresql+asyncpg://... | PostgreSQL connection |
| REDIS_URL | redis://localhost:6379/0 | Redis connection |
| BASE_URL | http://localhost:8000 | Public base URL for short links |
| CACHE_TTL_SECONDS | 86400 | Redis TTL (24h) |
| RATE_LIMIT_PER_MINUTE | 60 | Requests per IP per minute |
"""

    def _engineering_summary(self, state: WorkflowState) -> str:
        req = state.requirement
        risks = state.risks or []
        validation = state.validation

        ambiguity_section = (
            "\n".join(
                f"- **{_s(a.question)}**\n  Resolution: {_s(a.resolution) or 'Unresolved'}"
                for a in req.ambiguities
            )
            or "None detected."
        )

        risk_section = (
            "\n".join(
                f"### {_s(r.title)} [{_s(r.level.value.upper())}]\n{_s(r.description)}\n\n"
                f"**Mitigation:** {_s(r.mitigation)}\n\n**Trade-off:** {_s(r.tradeoff)}"
                for r in risks
            )
            or "No risks identified."
        )

        task_section = "\n".join(
            f"| {_s(t.name)} | {_s(t.agent)} | {_s(t.status.value)} | {_s(', '.join(t.depends_on)) or '—'} |"
            for t in state.tasks
            if t.name not in ("decompose", "documentation")
        )

        checks_section = "\n".join(
            f"- {'[PASS]' if c['passed'] else '[FAIL]'} `{_s(c['name'])}`: {_s(c['detail'])}"
            for c in (validation.checks if validation else [])
        )

        artifacts_section = "\n".join(f"- `{_s(k)}`" for k in state.artifacts)

        return f"""\
# Engineering Summary — {_s(req.intent)}

**Workflow ID:** {_s(state.id)}
**Scenario:** {_s(req.scenario_type.value)}
**Generated:** {_s(state.created_at.isoformat())}

---

## 1. Requirement Analysis

**Raw:** {_s(req.raw)}

**Normalized:** {_s(req.normalized)}

**Intent:** {_s(req.intent)}

**Constraints:**
{chr(10).join(f"- {_s(c)}" for c in req.constraints)}

**Success Criteria:**
{chr(10).join(f"- {_s(c)}" for c in req.success_criteria)}

### Ambiguities Detected & Resolved
{ambiguity_section}

---

## 2. Task Decomposition & Execution

| Task | Agent | Status | Dependencies |
|------|-------|--------|--------------|
{task_section}

---

## 3. Generated Artifacts

{artifacts_section}

---

## 4. Risks & Trade-offs

{risk_section}

---

## 5. Validation

**Overall:** {"[PASSED]" if (validation and validation.passed) else "[WARNINGS]"}

**Coverage Estimate:** {_s(validation.coverage_estimate) if validation else "N/A"}

### Static Checks
{checks_section}

### Test Strategy
```
{validation.test_strategy if validation else "N/A"}
```

---

## 6. Assumptions & Limitations

- **Auth:** No authentication in MVP; add JWT/API key for production
- **Custom domains:** Not supported; single base URL only
- **Analytics latency:** Materialized view refresh is manual; add pg_cron for production
- **Rate limiting:** Configured at app level; move to API Gateway for production scale
- **Code uniqueness:** SHA256 + timestamp salt provides sufficient collision resistance for MVP scale
- **Monitoring:** Structured logging only; add Prometheus metrics for production observability
"""

    def _runbook(self) -> str:
        return """\
# Operational Runbook — URL Shortener Service

## Health Check
```bash
curl http://localhost:8000/health
# Expected: {"status": "ok"}
```

## Scaling
```bash
# Scale API replicas (Docker Compose)
docker-compose up --scale api=3

# Production: update ECS desired count or Kubernetes replicas
```

## Cache Management
```bash
# Flush Redis cache (use with caution)
redis-cli FLUSHDB

# Inspect a specific key
redis-cli GET <code>
```

## Database Maintenance
```bash
# Refresh analytics materialized view
psql -c "REFRESH MATERIALIZED VIEW CONCURRENTLY url_stats;"

# Purge expired URLs (run as scheduled job)
psql -c "UPDATE urls SET is_active=false WHERE expires_at < NOW() AND is_active=true;"
```

## Incident Response

| Symptom | Likely Cause | Action |
|---------|-------------|--------|
| Redirects slow (>200ms) | Redis cache miss / cold start | Check Redis connectivity; warm cache |
| 500 on POST /urls | DB connection pool exhausted | Check DB connections; scale pool |
| Analytics not updating | Worker crash | Restart analytics worker; check queue depth |
| High 404 rate | Cache eviction + DB miss | Investigate code generation collision |

## Rollback
```bash
# Docker Compose rollback
docker-compose down && docker-compose up --build

# Database rollback (Alembic)
alembic downgrade -1
```
"""
