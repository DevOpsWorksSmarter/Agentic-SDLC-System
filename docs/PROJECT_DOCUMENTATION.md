# Agentic SDLC System — Complete Project Documentation

**Version:** 1.0.0 | **Author:** Engineering | **Last Updated:** 2025

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Agent Design](#3-agent-design)
4. [Workflow Orchestration](#4-workflow-orchestration)
5. [Generated Artifacts](#5-generated-artifacts)
6. [Deployment Guide](#6-deployment-guide)
7. [CI/CD Pipeline](#7-cicd-pipeline)
8. [Kubernetes Infrastructure](#8-kubernetes-infrastructure)
9. [Observability Stack](#9-observability-stack)
10. [Security Controls](#10-security-controls)
11. [Testing Strategy](#11-testing-strategy)
12. [Example Scenarios](#12-example-scenarios)
13. [Risks and Trade-offs](#13-risks-and-trade-offs)
14. [Assumptions and Limitations](#14-assumptions-and-limitations)
15. [Operational Runbook](#15-operational-runbook)

---

## 1. Project Overview

The Agentic SDLC System is a **multi-agent workflow orchestrator** that transforms a plain-English software requirement into a complete, reviewable engineering outcome — end-to-end across the full Software Development Lifecycle.

### What It Does

Given a requirement like:
> *"Build a scalable URL shortener service with APIs, persistence, and analytics."*

The system automatically:
1. **Understands** the requirement — classifies scenario type, detects ambiguities, resolves them with sensible defaults
2. **Decomposes** it into structured, dependency-ordered tasks
3. **Executes** each task through a specialised agent with human approval gates at critical checkpoints
4. **Generates** production-quality code, API contracts, database schemas, tests, and documentation
5. **Validates** all outputs — identifies risks, trade-offs, and defines a test strategy
6. **Persists** all artifacts to a structured output directory

### Key Differentiators

| Property | Description |
|----------|-------------|
| **Controlled Autonomy** | Agents execute independently; humans approve architecture, code, and validation |
| **Dependency-Aware Scheduling** | Tasks run as soon as all dependencies are terminal — not just sequentially |
| **Error Recovery** | Failed or rejected tasks retry up to 2 times on failure; on final failure or human rejection, all downstream dependents are skipped |
| **Three Scenario Types** | Greenfield, Brownfield, and Ambiguous requirements all handled |
| **Zero External Dependencies** | Fully deterministic, no LLM API keys or network required |
| **Production-Ready Output** | Generated FastAPI service is deployable with Docker Compose out of the box |

---

## 2. System Architecture

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                          CLI / main.py                               │
│              --auto  --requirement "..."  --serve                    │
└───────────────────────────────┬──────────────────────────────────────┘
                                │ WorkflowState (shared mutable object)
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      WorkflowOrchestrator                            │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  Phase 1: Requirement Understanding                          │    │
│  │    RequirementAgent                                          │    │
│  │    • Classify: greenfield / brownfield / ambiguous           │    │
│  │    • Detect ambiguities → auto-resolve with defaults         │    │
│  │    • Normalize requirement + extract success criteria        │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                │                                     │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  Phase 2: Task Decomposition                                 │    │
│  │    DecompositionAgent                                        │    │
│  │    • Break requirement into ordered tasks with dependencies  │    │
│  │    • Inject tasks into WorkflowState                         │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                │                                     │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  Phase 3: Dependency-Aware Execution                         │    │
│  │                                                              │    │
│  │  ArchitectureAgent ──────────────────► [APPROVAL GATE]      │    │
│  │       │                                                      │    │
│  │  SchemaAgent ◄── depends on architecture                    │    │
│  │       │                                                      │    │
│  │  AnalyticsDesignAgent ◄── depends on schema                 │    │
│  │       │                                                      │    │
│  │  CodeGenerationAgent ◄── depends on schema+analytics        │    │
│  │       │                               [APPROVAL GATE]       │    │
│  │  TestGenerationAgent ◄── depends on code                    │    │
│  │       │                                                      │    │
│  │  ValidationAgent ◄── depends on tests                       │    │
│  │       │                               [APPROVAL GATE]       │    │
│  │  DocumentationAgent ◄── depends on validation               │    │
│  └─────────────────────────────────────────────────────────────┘    │
└───────────────────────────────┬──────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│                         OutputWriter                                 │
│   outputs/run_{id}/                                                  │
│   ├── workflow_summary.json      ← task statuses, risks, validation  │
│   ├── execution_log.json         ← timestamped audit trail           │
│   ├── architecture_design/       ← components, data flows, infra     │
│   ├── schema_design/             ← PostgreSQL DDL + OpenAPI 3.0      │
│   ├── analytics_design/          ← async pipeline design             │
│   ├── code_generation/app/       ← 10 FastAPI source files           │
│   ├── test_generation/tests/     ← unit + integration test suites    │
│   └── documentation/             ← README + engineering summary      │
└──────────────────────────────────────────────────────────────────────┘
```

### Component Inventory

| Component | File | Responsibility |
|-----------|------|----------------|
| WorkflowState | `src/models/state.py` | Shared mutable state — single source of truth |
| WorkflowOrchestrator | `src/orchestrator/workflow.py` | Dependency scheduling, approval gates, error recovery |
| RequirementAgent | `src/agents/requirement_agent.py` | Classify, detect ambiguities, normalize |
| DecompositionAgent | `src/agents/decomposition_agent.py` | Break into ordered tasks |
| ArchitectureAgent | `src/agents/architecture_agent.py` | System design + analytics pipeline |
| SchemaAgent | `src/agents/schema_agent.py` | PostgreSQL DDL + OpenAPI 3.0 spec |
| CodeGenerationAgent | `src/agents/code_generation_agent.py` | 10 FastAPI files + Docker artifacts |
| TestGenerationAgent | `src/agents/test_generation_agent.py` | Unit + integration test suites |
| ValidationAgent | `src/agents/validation_agent.py` | Risk identification + static checks |
| DocumentationAgent | `src/agents/documentation_agent.py` | README + engineering summary + runbook |
| CodebaseReasoningAgent | `src/agents/codebase_reasoning_agent.py` | Brownfield impact analysis |
| OutputWriter | `src/tools/output_writer.py` | Path-safe artifact persistence |
| Metrics | `src/tools/metrics.py` | Prometheus-compatible in-process metrics |
| CLI / HTTP | `main.py` | Entry point, structured logging, /health + /metrics |

---

## 3. Agent Design

### Base Agent Contract

Every agent extends `BaseAgent` and implements a single `execute(task, state)` method:

```python
class BaseAgent(ABC):
    def run(self, task, state) -> Task:
        # Sets status IN_PROGRESS, calls execute(), handles retry loop
        # On success: status = COMPLETED or AWAITING_APPROVAL
        # On failure after max_retries: status = FAILED

    @abstractmethod
    def execute(self, task, state) -> Any:
        # Agent-specific logic — returns output stored in state.artifacts
```

### Retry Logic

- Each task has `max_retries=2` (3 total attempts)
- On each failure the error is logged and the attempt counter incremented
- After all retries exhausted: `status = FAILED` → dependents are skipped

### Approval Gates

Three tasks require human sign-off before downstream work proceeds:

| Task | Why Approval Is Required |
|------|--------------------------|
| `architecture_design` | Architecture decisions are hard to reverse; human must validate before code is generated |
| `code_generation` | Generated code goes into production; human reviews before tests are written |
| `validation` | Final risk sign-off before documentation is published |

In `--auto` mode all gates are auto-approved (CI/CD use case). A rejected task propagates `skip_dependents` identically to a failed task — no orphaned pending tasks remain.

---

## 4. Workflow Orchestration

### Dependency Graph (Greenfield + Analytics)

```
understand_requirement
        │
    decompose
        │
  architecture_design ──────────────────────────────────┐
        │                                               │
   schema_design                                analytics_design
        │                                               │
        └───────────────────┬───────────────────────────┘
                            │
                    code_generation
                            │
                    test_generation
                            │
                      validation
                            │
                     documentation
```

### Scheduler Algorithm

```
while iterations < max:
    ready = [t for t in plan if t.PENDING and all deps are TERMINAL]
    if not ready:
        if any PENDING tasks remain → deadlock → skip them
        break
    for task in ready:
        run(task)
        if task.FAILED or task.REJECTED → skip_dependents(task)
```

Terminal states: `COMPLETED`, `APPROVED`, `SKIPPED`, `REJECTED`

### Cross-Step Coordination

`WorkflowState.artifacts` is the shared blackboard:
- `ArchitectureAgent` writes `artifacts["architecture_design"]`
- `SchemaAgent` reads it to align schema with architecture decisions
- `CodeGenerationAgent` reads schema to generate correct models
- `ValidationAgent` reads all artifacts to run static checks
- `DocumentationAgent` reads everything to produce the engineering summary

---

## 5. Generated Artifacts

### URL Shortener Service (Mandatory Use Case)

The system generates a complete, deployable FastAPI service:

```
code_generation/
├── app/
│   ├── config.py        ← pydantic-settings, reads from .env
│   ├── models.py        ← Pydantic request/response models
│   ├── database.py      ← SQLAlchemy async ORM (PostgreSQL)
│   ├── cache.py         ← Redis async cache helpers
│   ├── shortener.py     ← Base62 code generation (SHA256 + timestamp salt)
│   ├── repository.py    ← DB access layer (get, create, deactivate, stats)
│   ├── service.py       ← Business logic (shorten, resolve, deactivate)
│   ├── analytics.py     ← Fire-and-forget async click recording
│   ├── routes.py        ← FastAPI route handlers
│   └── main.py          ← FastAPI app with CORS middleware
├── Dockerfile           ← python:3.12-slim
├── docker-compose.yml   ← API + PostgreSQL + Redis
└── requirements.txt
```

### API Endpoints

| Method | Path | Description | Status Codes |
|--------|------|-------------|--------------|
| POST | `/urls` | Create short URL | 201, 400, 409, 422, 429 |
| GET | `/{code}` | Redirect to original | 302, 404, 410 |
| GET | `/urls/{code}` | Get URL metadata | 200, 404 |
| DELETE | `/urls/{code}` | Deactivate URL | 204, 404 |
| GET | `/urls/{code}/stats` | Click analytics | 200, 404 |
| GET | `/health` | Health check | 200 |

### Database Schema

```sql
CREATE TABLE urls (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code        VARCHAR(12) NOT NULL UNIQUE,
    original    TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at  TIMESTAMPTZ,
    is_active   BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE click_events (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url_id      UUID NOT NULL REFERENCES urls(id) ON DELETE CASCADE,
    clicked_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ip_hash     VARCHAR(64),
    referrer    TEXT,
    user_agent  TEXT
);
```

---

## 6. Deployment Guide

### Prerequisites

- Docker 24+ and Docker Compose v2
- Python 3.12+ (for local runs)
- kubectl 1.29+ (for Kubernetes)

### Local Run (No Docker)

```bash
# 1. Clone and set up
git clone https://github.com/your-org/agentic-sdlc-system
cd Agentic-SDLC-System
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux
pip install -r requirements.txt

# 2. Run mandatory use case (auto-approve, non-interactive)
python main.py --auto \
  --requirement "Build a scalable URL shortener service with APIs, persistence, and analytics."

# 3. Outputs written to: outputs/run_{id}/
```

### Docker (Single Container)

```bash
# Build
docker build -t agentic-sdlc:latest .

# Run with default use case
docker run --rm -v $(pwd)/outputs:/app/outputs agentic-sdlc:latest

# Run with custom requirement
docker run --rm \
  -v $(pwd)/outputs:/app/outputs \
  agentic-sdlc:latest \
  python main.py --auto --requirement "Your requirement here"

# Run with HTTP server (health + metrics)
docker run --rm -p 8080:8080 \
  -v $(pwd)/outputs:/app/outputs \
  agentic-sdlc:latest \
  python main.py --auto --serve \
  --requirement "Build a scalable URL shortener service with APIs, persistence, and analytics."
```

### Docker Compose (Full Stack with Observability)

```bash
# Start everything: orchestrator + Prometheus + Grafana + Loki
docker-compose up --build

# Access:
#   Grafana:    http://localhost:3000  (admin / admin)
#   Prometheus: http://localhost:9090
#   Loki:       http://localhost:3100

# Run a specific scenario
docker-compose run --rm agentic-sdlc \
  python main.py --auto \
  --requirement "Build a scalable URL shortener service with APIs, persistence, and analytics."
```

### Kubernetes

```bash
# Apply base manifests
kubectl apply -k k8s/base/

# Deploy to staging
kubectl apply -k k8s/overlays/staging/

# Deploy to production
kubectl apply -k k8s/overlays/production/

# Check rollout
kubectl rollout status deployment/agentic-sdlc -n agentic-sdlc

# View logs
kubectl logs -l app=agentic-sdlc -n agentic-sdlc --follow

# Port-forward for local access
kubectl port-forward svc/agentic-sdlc 8080:80 -n agentic-sdlc
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Logging verbosity |
| `OUTPUT_DIR` | `outputs` | Artifact output directory |
| `PYTHONUNBUFFERED` | `1` | Flush stdout immediately (required for Docker logs) |

---

## 7. CI/CD Pipeline

### Pipeline Overview

```
Push to main/develop
        │
        ▼
┌───────────────┐
│  lint         │  ruff check + ruff format --check
└───────┬───────┘
        │
        ▼
┌───────────────┐
│  test         │  pytest tests/ --cov=src --cov-fail-under=80
└───────┬───────┘
        │
        ▼
┌───────────────┐
│  e2e          │  python main.py --auto + artifact validation
└───────┬───────┘
        │
        ▼
┌───────────────┐
│  build        │  docker buildx + push to ghcr.io (main/develop only)
└───────┬───────┘
        │ (CD workflow triggers on CI success)
        ▼
┌───────────────┐
│ deploy-staging│  kubectl set image → rollout status → smoke test
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ approve-prod  │  Manual approval gate (GitHub Environments)
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ deploy-prod   │  Rolling deploy → health check → auto-rollback on failure
└───────────────┘
```

### GitHub Secrets Required

| Secret | Description |
|--------|-------------|
| `GITHUB_TOKEN` | Auto-provided — used for GHCR push |
| `KUBE_CONFIG_STAGING` | Base64-encoded kubeconfig for staging cluster |
| `KUBE_CONFIG_PRODUCTION` | Base64-encoded kubeconfig for production cluster |

### Rollback Strategy

- **Automatic**: If production health check fails after deploy, `kubectl rollout undo` is triggered automatically
- **Manual**: `kubectl rollout undo deployment/agentic-sdlc -n agentic-sdlc`

---

## 8. Kubernetes Infrastructure

### Resource Layout

```
Namespace: agentic-sdlc
├── Deployment: agentic-sdlc        (2-10 replicas via HPA)
├── Service: agentic-sdlc           (ClusterIP → port 80)
├── Ingress: agentic-sdlc           (TLS via cert-manager)
├── HPA: agentic-sdlc               (CPU 70% / Memory 80%)
├── PVC: agentic-sdlc-outputs       (10Gi ReadWriteMany)
├── ServiceAccount: agentic-sdlc
└── ConfigMap: agentic-sdlc-config
```

### Scaling Policy

| Trigger | Action |
|---------|--------|
| CPU > 70% | Scale up (max 10 replicas) |
| Memory > 80% | Scale up |
| CPU < 70% for 5 min | Scale down (min 2 replicas) |

### Zero-Downtime Deployment

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1        # One extra pod during rollout
    maxUnavailable: 0  # Never reduce below desired count
```

### Health Probes

- **Liveness**: Verifies Python environment is intact (import check)
- **Readiness**: Verifies orchestrator can be instantiated (import check)

---

## 9. Observability Stack

### Components

| Tool | Role | Port |
|------|------|------|
| Prometheus | Metrics collection and storage | 9090 |
| Grafana | Dashboards and alerting | 3000 |
| Loki | Log aggregation | 3100 |
| Promtail | Log shipping from Docker containers | — |

### Metrics Emitted

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `sdlc_workflow_runs_total` | Counter | `status`, `scenario` | Total workflow executions |
| `sdlc_workflow_duration_seconds` | Histogram | `workflow_id` | End-to-end workflow duration |
| `sdlc_task_executions_total` | Counter | `agent`, `status` | Per-agent task execution count |
| `sdlc_approval_decisions_total` | Counter | `decision`, `task` | Human/auto approval decisions |

### Structured Log Format

Every log line is a JSON object:

```json
{
  "timestamp": "2025-01-01T12:00:00.000Z",
  "level": "info",
  "service": "agentic-sdlc",
  "message": "Workflow complete",
  "workflow_id": "abc12345",
  "scenario": "greenfield",
  "duration_seconds": 1.23,
  "tasks_total": 9,
  "tasks_failed": 0,
  "artifacts": 9
}
```

### Grafana Dashboard

Access at `http://localhost:3000` (admin/admin):
- Workflow run count and success rate
- Average workflow duration
- Task execution breakdown by agent
- Task failure rate over time
- Scenario distribution (greenfield/brownfield/ambiguous)
- Approval gate decision breakdown
- Live log stream from Loki

---

## 10. Security Controls

| Control | Implementation |
|---------|----------------|
| XSS Prevention | `html.escape()` applied to all user input before embedding in markdown/HTML outputs |
| Path Traversal | `_safe_join()` resolves and confines all file writes to the declared output directory |
| Hardcoded Credentials | Docker Compose uses `${POSTGRES_PASSWORD:?must be set}` — fails fast if not provided |
| Non-Root Container | Dockerfile creates `appuser` (UID 1000) and runs as non-root |
| Timezone-Aware Datetimes | All timestamps use `datetime.now(timezone.utc)` — no naive datetime objects |
| Input Validation | Requirement text is sanitized before any string interpolation |
| Minimal Image | Multi-stage Docker build — runtime image is `python:3.12-slim` with no build tools |

---

## 11. Testing Strategy

### Test Pyramid

```
         ┌─────────────────┐
         │   E2E Tests      │  GitHub Actions: full workflow run + artifact validation
         ├─────────────────┤
         │  System Tests    │  run_tests.py: 47 tests across 6 test sections
         ├─────────────────┤
         │  Unit Tests      │  Per-agent logic with mocked dependencies
         └─────────────────┘
```

### System Test Classes

| Class | Tests | What It Covers |
|-------|-------|----------------|
| `TestRequirementAgent` | 7 | Classification, ambiguity detection, XSS sanitization |
| `TestDecompositionAgent` | 9 | Task structure, dependency correctness, analytics injection |
| `TestOrchestrator` | 8 | Terminal state guarantee, failure propagation, rejection propagation, auto-approve |
| `TestArtifacts` | 15 | Presence and structure of all generated outputs |
| `TestOutputWriter` | 4 | Directory creation, summary correctness, path traversal blocking |
| `TestMetrics` | 4 | Counter increments, metrics text output |

### Running Tests

```bash
# Standalone runner (no pytest required) — 47/47 tests
python run_tests.py

# All system tests (requires pytest)
pytest tests/ -v

# Specific class
pytest tests/test_system.py::TestOrchestrator -v

# With coverage (requires pytest-cov)
pytest tests/ --cov=src --cov-report=term-missing --cov-fail-under=80

# Failure injection test
pytest tests/test_system.py::TestOrchestrator::test_failed_task_skips_dependents -v
```

### Coverage Target

- System tests: **>80%** line coverage on `src/`
- CI enforces `--cov-fail-under=80`
- Standalone: `python run_tests.py` — **47/47 tests**, no external dependencies required

---

## 12. Example Scenarios

### Scenario 1: Greenfield — URL Shortener

```bash
python main.py --auto \
  --requirement "Build a scalable URL shortener service with APIs, persistence, and analytics."
```

**Result:**
- Scenario: `greenfield`
- Ambiguities detected: 3 (`scalable`, `analytics`, `persistence`) — all auto-resolved
- Tasks: 9 (architecture → schema → analytics → code → tests → validation → docs)
- Artifacts: 9 (including 10 FastAPI source files, OpenAPI spec, PostgreSQL DDL)
- Validation: PASSED, 6 risks identified

### Scenario 2: Brownfield — Add Link Expiry

```bash
python main.py --auto \
  --requirement "Enhance the existing URL shortener to support configurable link expiration." \
  --codebase-path ./outputs
```

**Result:**
- Scenario: `brownfield`
- Tasks: codebase_analysis → impact_assessment → code_generation → tests → validation → docs
- Codebase analysis scans existing outputs, scores file relevance, identifies impacted modules
- Breaking change risk assessed before code generation begins

### Scenario 3: Ambiguous — "Make It Fast"

```bash
python main.py --auto --requirement "Make the service fast and scalable."
```

**Result:**
- Scenario: `ambiguous`
- Ambiguities: 2 (`fast`, `scalable`) — auto-resolved:
  - `fast` → "p99 redirect latency < 50ms via cache-first lookup"
  - `scalable` → "Target: 10k RPS, horizontal scaling via stateless services + Redis cache"
- Workflow proceeds with resolved constraints

---

## 13. Risks and Trade-offs

| Risk | Level | Mitigation | Trade-off |
|------|-------|------------|-----------|
| Code collision under high concurrency | MEDIUM | DB unique constraint or advisory lock | Locking reduces throughput |
| Cache stampede on cold start | MEDIUM | Probabilistic early expiration / single-flight | Adds complexity |
| Analytics data loss on worker crash | LOW | Durable queue (Redis Streams / SQS) for production | Adds operational overhead |
| Open redirect abuse | HIGH | URL reputation check (Google Safe Browsing) + rate limiting | +50ms on shorten path |
| Short code exhaustion | LOW | 7-char base62 = ~3.5B codes; monitor utilization | Longer codes reduce aesthetics |
| PostgreSQL single point of failure | HIGH | AWS RDS Multi-AZ with automatic failover | Doubles DB cost |

---

## 14. Assumptions and Limitations

| Item | Detail |
|------|--------|
| No LLM integration | Agents use deterministic rule-based logic — fully reproducible without API keys. Swap `execute()` for LLM calls to add intelligence. |
| Brownfield analysis is keyword-based | Sufficient for prototype. Replace with AST parsing or tree-sitter for production. |
| No authentication on generated API | Intentional MVP scope. Add JWT/API key middleware as next iteration. |
| Single-process orchestrator | Sufficient for prototype. Replace with Temporal or AWS Step Functions for distributed production use. |
| Analytics materialized view | Manual refresh required. Add `pg_cron` or scheduled Lambda for production. |
| Rate limiting at app level | Move to API Gateway or Nginx for production scale. |

---

## 15. Operational Runbook

### Health Check

```bash
# Local
curl http://localhost:8080/health
# Expected: {"status":"ok"}

# Kubernetes
kubectl exec -n agentic-sdlc deploy/agentic-sdlc -- \
  python -c "from src.models.state import WorkflowState; print('ok')"
```

### View Metrics

```bash
# Local
curl http://localhost:8080/metrics

# Kubernetes port-forward
kubectl port-forward svc/agentic-sdlc 8080:80 -n agentic-sdlc
curl http://localhost:8080/metrics
```

### View Logs

```bash
# Docker Compose
docker-compose logs -f agentic-sdlc

# Kubernetes
kubectl logs -l app=agentic-sdlc -n agentic-sdlc --follow

# Grafana Loki (UI)
# http://localhost:3000 → Explore → Loki → {service="agentic-sdlc"}
```

### Rollback

```bash
# Kubernetes
kubectl rollout undo deployment/agentic-sdlc -n agentic-sdlc
kubectl rollout status deployment/agentic-sdlc -n agentic-sdlc

# Docker Compose
docker-compose down && docker-compose up --build
```

### Scale

```bash
# Kubernetes manual scale
kubectl scale deployment/agentic-sdlc --replicas=5 -n agentic-sdlc

# Docker Compose
docker-compose up --scale agentic-sdlc=3
```

### Incident Response

| Symptom | Likely Cause | Action |
|---------|-------------|--------|
| Workflow stuck in `in_progress` | Agent exception not caught | Check logs; restart pod |
| All tasks `skipped` | First task failed | Check `execution_log.json` for root cause |
| `Path traversal blocked` error | Malformed artifact key | Sanitize input; check `_safe_segment()` |
| High memory usage | Large codebase scan (brownfield) | Limit `--codebase-path` scope |
| Metrics not appearing in Grafana | Prometheus scrape failing | Check `http://prometheus:9090/targets` |
