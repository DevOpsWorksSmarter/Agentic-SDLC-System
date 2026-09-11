# Agentic SDLC System

A working prototype of a multi-agent system that transforms a software requirement into a reviewable engineering outcome — end-to-end across the full SDLC.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLI / main.py                            │
└────────────────────────────┬────────────────────────────────────┘
                             │ WorkflowState
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   WorkflowOrchestrator                          │
│                                                                 │
│  Phase 1: Requirement Understanding                             │
│    └─► RequirementAgent                                         │
│         • Classifies scenario (greenfield/brownfield/ambiguous) │
│         • Detects & auto-resolves ambiguities                   │
│         • Normalizes requirement + extracts success criteria    │
│                                                                 │
│  Phase 2: Task Decomposition                                    │
│    └─► DecompositionAgent                                       │
│         • Breaks requirement into ordered tasks with deps       │
│         • Injects tasks into shared WorkflowState              │
│                                                                 │
│  Phase 3: Dependency-Aware Execution                            │
│    ├─► ArchitectureAgent      (requires_approval=True)          │
│    ├─► SchemaAgent                                              │
│    ├─► CodeGenerationAgent    (requires_approval=True)          │
│    ├─► TestGenerationAgent                                      │
│    ├─► ValidationAgent        (requires_approval=True)          │
│    ├─► DocumentationAgent                                       │
│    └─► CodebaseReasoningAgent (brownfield only)                 │
│                                                                 │
│  Quality Plane: AI Reasoning → Security → SRE → Engineering    │
│                 Review → Deterministic Release Gate            │
│                                                                 │
│  Human-in-the-Loop Gates: approval_callback or interactive CLI  │
│  Error Recovery: retry (max 2) → skip dependents on failure     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      OutputWriter                               │
│   outputs/run_{id}/                                             │
│   ├── workflow_summary.json                                     │
│   ├── execution_log.json                                        │
│   ├── architecture_design/output.json                           │
│   ├── schema_design/output.json                                 │
│   ├── code_generation/app/*.py + Dockerfile + docker-compose    │
│   ├── test_generation/tests/**/*.py                             │
│   └── documentation/README.md + ENGINEERING_SUMMARY.md         │
└─────────────────────────────────────────────────────────────────┘
```

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Shared `WorkflowState` | Single source of truth passed through all agents; enables cross-step coordination without message passing overhead |
| Dependency-aware scheduler | Tasks execute as soon as all deps are terminal; enables parallelism without explicit thread management |
| Approval gates on key tasks | Architecture, code generation, and validation require human sign-off before downstream tasks proceed |
| Retry + skip-dependents | Failed or rejected tasks retry up to 2 times on failure; on final failure or human rejection, all downstream dependents are skipped to prevent cascading bad state |
| `auto_approve` flag | Enables full CI/CD pipeline execution without interactive prompts |
| `html.escape` on all user input | Prevents XSS when requirement text is embedded in markdown/HTML outputs |
| Path confinement in OutputWriter | All file writes are resolved and verified to stay within the declared output directory |
| `REJECTED` is terminal | Human rejection at an approval gate propagates skip-dependents identically to a task failure, preventing orphaned pending tasks |

---

## Setup

```bash
# 1. Clone / navigate to project
cd Agentic-SDLC-System

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Running the System

### Mandatory Use Case — URL Shortener (auto-approve, non-interactive)
```bash
python main.py --auto --requirement "Build a scalable URL shortener service with APIs, persistence, and analytics."
```

### Interactive Mode (with human approval gates)
```bash
python main.py --requirement "Build a scalable URL shortener service with APIs, persistence, and analytics."
# At each approval gate: y=approve, n=reject, s=skip
```

### Brownfield Scenario
```bash
python main.py --auto \
  --requirement "Enhance the existing URL shortener to support configurable link expiration." \
  --codebase-path ./outputs
```

### Ambiguous Requirement
```bash
python main.py --auto --requirement "Make the service fast and scalable."
```

### Custom Output Directory
```bash
python main.py --auto --requirement "..." --output-dir ./my_outputs
```

---

## Running Tests

```bash
# All system tests
pytest tests/ -v

# Specific test class
pytest tests/test_system.py::TestOrchestrator -v

# With coverage
pip install pytest-cov
pytest tests/ --cov=src --cov-report=term-missing
```

---

## Example Scenarios

See [`examples/scenarios.json`](examples/scenarios.json) for full input/output specifications for:
- **Greenfield**: URL shortener from scratch
- **Brownfield**: Add expiry to existing service
- **Ambiguous**: "Make it fast and scalable" — demonstrates ambiguity detection and auto-resolution

---

## Generated Outputs (per run)

```
outputs/run_{id}/
├── workflow_summary.json          # Task statuses, risks, validation results
├── execution_log.json             # Timestamped audit trail of all agent actions
├── architecture_design/
│   └── output.json                # System components, data flows, infra topology
├── schema_design/
│   └── output.json                # PostgreSQL DDL + OpenAPI 3.0 spec
├── analytics_design/
│   └── output.json                # Async analytics pipeline design
├── code_generation/
│   ├── app/
│   │   ├── main.py                # FastAPI app entrypoint
│   │   ├── routes.py              # API route handlers
│   │   ├── service.py             # Business logic layer
│   │   ├── repository.py          # Database access layer
│   │   ├── models.py              # Pydantic request/response models
│   │   ├── database.py            # SQLAlchemy ORM models + session
│   │   ├── cache.py               # Redis cache helpers
│   │   ├── shortener.py           # Base62 code generation
│   │   ├── analytics.py           # Async click event recording
│   │   └── config.py              # Settings via pydantic-settings
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── requirements.txt
├── test_generation/
│   └── tests/
│       ├── conftest.py
│       ├── unit/
│       │   ├── test_shortener.py
│       │   └── test_service.py
│       └── integration/
│           ├── test_api.py
│           └── test_analytics.py
└── documentation/
    ├── README.md
    ├── ENGINEERING_SUMMARY.md     # Full engineering summary with risks & trade-offs
    └── RUNBOOK.md                 # Operational runbook
```

---

## Testing Approach

### System Tests (`tests/test_system.py`)
- **RequirementAgent** (7 tests): scenario classification, ambiguity detection, XSS sanitization
- **DecompositionAgent** (9 tests): task structure, dependency correctness, analytics task injection
- **Orchestrator** (8 tests): terminal state guarantee, dependency ordering, failure propagation, rejection propagation, auto-approve
- **Artifacts** (15 tests): presence and structure of all generated outputs
- **OutputWriter** (4 tests): directory creation, summary correctness, path traversal blocking
- **Metrics** (4 tests): counter increments, metrics text output

### Generated App Tests (in `outputs/run_{id}/test_generation/`)
- **Unit**: shortener logic, service layer with mocked dependencies
- **Integration**: full API flow via httpx AsyncClient + SQLite in-memory
- **Analytics isolation**: analytics failure must never break redirect

### Known Limitations & Trade-offs

| Limitation | Trade-off |
|------------|-----------|
| Optional LLM integration | Set `AI_BASE_URL`, `AI_API_KEY`, and `AI_MODEL` for structured JSON reasoning; deterministic fallback keeps CI reproducible and offline |
| Brownfield codebase analysis is keyword-based | Sufficient for prototype; replace with AST parsing or tree-sitter for production |
| Analytics materialized view requires manual refresh | Add `pg_cron` or a scheduled Lambda for production |
| No auth on generated API | Intentional MVP scope; add JWT middleware as next iteration |
| Single-process orchestrator | Sufficient for prototype; replace with Temporal/Step Functions for distributed production use |
