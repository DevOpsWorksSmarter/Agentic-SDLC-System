"""Slides 6-10 for Agentic SDLC presentation."""
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

DARK_BG    = RGBColor(0x1A, 0x1A, 0x2E)
ACCENT     = RGBColor(0x00, 0xD4, 0xFF)
ACCENT2    = RGBColor(0xFF, 0x6B, 0x35)
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_GRAY = RGBColor(0xCC, 0xCC, 0xCC)
GREEN      = RGBColor(0x00, 0xC8, 0x5A)
YELLOW     = RGBColor(0xFF, 0xD7, 0x00)
RED        = RGBColor(0xFF, 0x4C, 0x4C)
CARD_BG    = RGBColor(0x16, 0x21, 0x3E)


def add_slides_6_to_10(prs, slide, bg, box, txt, accent_bar):

    # ── SLIDE 6: Workflow Orchestration ──────────────────────────────────────
    sl = slide()
    bg(sl)
    accent_bar(sl, y=0.55)
    txt(sl, "WORKFLOW ORCHESTRATION", 0.4, 0.1, 12.5, 0.5,
        size=28, bold=True, color=WHITE)

    txt(sl, "Dependency-Aware Scheduler — not simple sequential execution",
        0.4, 0.65, 12.5, 0.4, size=15, color=ACCENT, bold=True)

    # Dependency graph visual
    nodes = [
        (0.5, 1.2, "understand_requirement", ACCENT),
        (0.5, 2.1, "decompose", ACCENT),
        (0.5, 3.0, "architecture_design", ACCENT2),
        (0.5, 3.9, "schema_design", GREEN),
        (4.5, 3.9, "analytics_design", GREEN),
        (2.3, 4.8, "code_generation", YELLOW),
        (2.3, 5.6, "test_generation", ACCENT),
        (2.3, 6.3, "validation", RED),
    ]
    for nx, ny, name, color in nodes:
        box(sl, nx, ny, 3.5, 0.55, fill=CARD_BG, line_color=color, line_width=Pt(1.5))
        txt(sl, name, nx + 0.1, ny + 0.08, 3.3, 0.4, size=11, bold=True, color=color)

    # Arrows (text-based)
    arrows = [(1.7, 1.8), (1.7, 2.7), (1.7, 3.6), (3.7, 4.5), (3.7, 5.3), (3.7, 6.0)]
    for ax, ay in arrows:
        txt(sl, "|", ax, ay, 0.3, 0.35, size=14, color=LIGHT_GRAY, align=PP_ALIGN.CENTER)

    # Right side: scheduler algorithm
    box(sl, 8.5, 0.85, 4.6, 6.3, fill=CARD_BG)
    txt(sl, "SCHEDULER ALGORITHM", 8.65, 0.9, 4.3, 0.4,
        size=13, bold=True, color=ACCENT)
    algo = (
        "while iterations < max:\n\n"
        "  ready = tasks where:\n"
        "    status == PENDING\n"
        "    AND all deps are TERMINAL\n\n"
        "  if not ready:\n"
        "    if pending tasks exist:\n"
        "      -> deadlock detected\n"
        "      -> skip remaining\n"
        "    break\n\n"
        "  for task in ready:\n"
        "    run(task)\n"
        "    if FAILED or REJECTED:\n"
        "      skip_dependents(task)"
    )
    txt(sl, algo, 8.65, 1.4, 4.3, 5.5, size=10, color=LIGHT_GRAY)

    # Terminal states legend
    for i, (label, color) in enumerate([
        ("COMPLETED", GREEN), ("APPROVED", ACCENT), ("SKIPPED", YELLOW), ("REJECTED", RED)
    ]):
        box(sl, 0.5 + i * 2.6, 7.0, 2.3, 0.35, fill=color)
        txt(sl, label, 0.5 + i * 1.95, 7.0, 1.8, 0.35,
            size=11, bold=True, color=DARK_BG, align=PP_ALIGN.CENTER)

    # ── SLIDE 7: Generated Artifacts ─────────────────────────────────────────
    sl = slide()
    bg(sl)
    accent_bar(sl, y=0.55)
    txt(sl, "GENERATED ARTIFACTS — URL SHORTENER", 0.4, 0.1, 12.5, 0.5,
        size=26, bold=True, color=WHITE)

    # Code files
    box(sl, 0.3, 0.75, 4.0, 6.5, fill=CARD_BG)
    txt(sl, "CODE (10 files)", 0.45, 0.8, 3.7, 0.4,
        size=13, bold=True, color=YELLOW)
    code_files = [
        "app/config.py     pydantic-settings",
        "app/models.py     Pydantic schemas",
        "app/database.py   SQLAlchemy ORM",
        "app/cache.py      Redis helpers",
        "app/shortener.py  Base62 generator",
        "app/repository.py DB access layer",
        "app/service.py    Business logic",
        "app/analytics.py  Async click events",
        "app/routes.py     FastAPI handlers",
        "app/main.py       App entrypoint",
        "Dockerfile        python:3.12-slim",
        "docker-compose.yml API+PG+Redis",
        "requirements.txt",
    ]
    for i, f in enumerate(code_files):
        txt(sl, f"  {f}", 0.45, 1.3 + i * 0.43, 3.7, 0.38, size=10, color=LIGHT_GRAY)

    # Schema
    box(sl, 4.5, 0.75, 4.0, 3.0, fill=CARD_BG)
    txt(sl, "SCHEMA", 4.65, 0.8, 3.7, 0.4, size=13, bold=True, color=ACCENT)
    schema_items = [
        "PostgreSQL DDL",
        "  urls table (UUID, code, original,",
        "  expires_at, is_active)",
        "  click_events table (url_id FK,",
        "  ip_hash, referrer, user_agent)",
        "  Materialized view: url_stats",
        "OpenAPI 3.0 spec",
        "  5 endpoints fully documented",
        "  Request/response schemas",
    ]
    for i, s in enumerate(schema_items):
        txt(sl, s, 4.65, 1.3 + i * 0.47, 3.7, 0.4, size=10, color=LIGHT_GRAY)

    # Tests
    box(sl, 4.5, 3.9, 4.0, 3.35, fill=CARD_BG)
    txt(sl, "TESTS", 4.65, 3.95, 3.7, 0.4, size=13, bold=True, color=GREEN)
    test_items = [
        "tests/conftest.py  SQLite in-memory",
        "unit/test_shortener.py  7 tests",
        "unit/test_service.py    5 tests",
        "integration/test_api.py 8 tests",
        "integration/test_analytics.py 3 tests",
        "Coverage target: >= 80%",
    ]
    for i, t in enumerate(test_items):
        txt(sl, f"  {t}", 4.65, 4.45 + i * 0.45, 3.7, 0.38, size=10, color=LIGHT_GRAY)

    # Docs
    box(sl, 8.7, 0.75, 4.3, 6.5, fill=CARD_BG)
    txt(sl, "DOCUMENTATION", 8.85, 0.8, 4.0, 0.4,
        size=13, bold=True, color=ACCENT2)
    doc_items = [
        "README.md",
        "  Quick start, API reference,",
        "  env vars, architecture diagram",
        "",
        "ENGINEERING_SUMMARY.md",
        "  Requirement analysis",
        "  Task decomposition table",
        "  All artifacts listed",
        "  6 risks with mitigations",
        "  Validation results",
        "  Assumptions & limitations",
        "",
        "RUNBOOK.md",
        "  Health check commands",
        "  Scaling procedures",
        "  Incident response table",
        "  Rollback steps",
    ]
    for i, d in enumerate(doc_items):
        txt(sl, d, 8.85, 1.3 + i * 0.33, 4.0, 0.3, size=10, color=LIGHT_GRAY)

    # ── SLIDE 8: CI/CD Pipeline ───────────────────────────────────────────────
    sl = slide()
    bg(sl)
    accent_bar(sl, y=0.55)
    txt(sl, "CI/CD PIPELINE", 0.4, 0.1, 12.5, 0.5,
        size=28, bold=True, color=WHITE)

    stages = [
        ("LINT", ACCENT, "ruff check\nruff format --check"),
        ("TEST", GREEN, "pytest --cov=src\n--cov-fail-under=80"),
        ("E2E", YELLOW, "Full workflow run\nArtifact validation"),
        ("BUILD", ACCENT2, "docker buildx\nPush to ghcr.io"),
        ("STAGING", ACCENT, "kubectl set image\nSmoke test"),
        ("APPROVE", RED, "Manual gate\nGitHub Environments"),
        ("PROD", GREEN, "Rolling deploy\nAuto-rollback"),
    ]

    for i, (name, color, detail) in enumerate(stages):
        bx = 0.3 + i * 1.85
        box(sl, bx, 1.1, 1.65, 1.8, fill=CARD_BG, line_color=color, line_width=Pt(2))
        txt(sl, name, bx, 1.15, 1.65, 0.5,
            size=13, bold=True, color=color, align=PP_ALIGN.CENTER)
        txt(sl, detail, bx + 0.05, 1.7, 1.55, 1.1, size=9,
            color=LIGHT_GRAY, align=PP_ALIGN.CENTER)
        if i < 6:
            txt(sl, "->", bx + 1.65, 1.8, 0.2, 0.4,
                size=14, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)

    # Details
    details = [
        ("Trigger", "Push to main/develop triggers CI.\nCD triggers on CI success (main only)."),
        ("Image Registry", "GitHub Container Registry (ghcr.io)\nTagged: branch, sha-{short}, latest"),
        ("Rollback", "Auto: health check fails -> kubectl rollout undo\nManual: kubectl rollout undo deployment/..."),
        ("Secrets", "GITHUB_TOKEN (auto)\nKUBE_CONFIG_STAGING\nKUBE_CONFIG_PRODUCTION"),
    ]
    for i, (title, detail) in enumerate(details):
        col = i % 2
        row = i // 2
        bx = 0.3 + col * 6.5
        by = 3.3 + row * 2.0
        box(sl, bx, by, 6.2, 1.8, fill=CARD_BG)
        txt(sl, title, bx + 0.15, by + 0.1, 5.9, 0.4,
            size=13, bold=True, color=ACCENT)
        txt(sl, detail, bx + 0.15, by + 0.55, 5.9, 1.1, size=11, color=LIGHT_GRAY)

    # ── SLIDE 9: Kubernetes & Observability ───────────────────────────────────
    sl = slide()
    bg(sl)
    accent_bar(sl, y=0.55)
    txt(sl, "KUBERNETES & OBSERVABILITY", 0.4, 0.1, 12.5, 0.5,
        size=28, bold=True, color=WHITE)

    # K8s left
    box(sl, 0.3, 0.75, 5.8, 6.5, fill=CARD_BG)
    txt(sl, "KUBERNETES INFRASTRUCTURE", 0.45, 0.8, 5.5, 0.4,
        size=13, bold=True, color=ACCENT)
    k8s_items = [
        ("Namespace", "agentic-sdlc"),
        ("Deployment", "2-10 replicas (HPA)"),
        ("Strategy", "RollingUpdate: maxSurge=1, maxUnavailable=0"),
        ("HPA Triggers", "CPU > 70%  |  Memory > 80%"),
        ("Service", "ClusterIP -> port 80"),
        ("Ingress", "TLS via cert-manager + nginx"),
        ("PVC", "10Gi ReadWriteMany for outputs"),
        ("Liveness", "Python import check every 30s"),
        ("Readiness", "Orchestrator import check every 10s"),
        ("Security", "runAsNonRoot: true, runAsUser: 1000"),
        ("Overlays", "staging (1 replica) / production (3 replicas)"),
        ("Kustomize", "Base + staging/production overlays"),
    ]
    for i, (k, v) in enumerate(k8s_items):
        txt(sl, k, 0.45, 1.35 + i * 0.45, 2.0, 0.38,
            size=10, bold=True, color=ACCENT2)
        txt(sl, v, 2.5, 1.35 + i * 0.45, 3.5, 0.38, size=10, color=LIGHT_GRAY)

    # Observability right
    box(sl, 6.4, 0.75, 6.6, 6.5, fill=CARD_BG)
    txt(sl, "OBSERVABILITY STACK", 6.55, 0.8, 6.3, 0.4,
        size=13, bold=True, color=ACCENT)

    obs_tools = [
        ("Prometheus :9090", ACCENT, "Scrapes /metrics every 10s\nStores 15 days of time-series"),
        ("Grafana :3000", GREEN, "Pre-built dashboard\nWorkflow runs, task rates, logs"),
        ("Loki :3100", YELLOW, "Log aggregation\nStructured JSON log ingestion"),
        ("Promtail", ACCENT2, "Ships Docker container logs\nto Loki automatically"),
    ]
    for i, (name, color, detail) in enumerate(obs_tools):
        by = 1.35 + i * 1.4
        box(sl, 6.55, by, 6.2, 1.2, fill=DARK_BG, line_color=color, line_width=Pt(1))
        txt(sl, name, 6.7, by + 0.05, 3.0, 0.4, size=12, bold=True, color=color)
        txt(sl, detail, 6.7, by + 0.5, 5.9, 0.6, size=10, color=LIGHT_GRAY)

    metrics = [
        "sdlc_workflow_runs_total {status, scenario}",
        "sdlc_workflow_duration_seconds {workflow_id}",
        "sdlc_task_executions_total {agent, status}",
        "sdlc_approval_decisions_total {decision, task}",
    ]
    txt(sl, "METRICS EMITTED", 6.55, 6.95, 6.3, 0.35,
        size=11, bold=True, color=ACCENT)

    # ── SLIDE 10: Security & Testing ─────────────────────────────────────────
    sl = slide()
    bg(sl)
    accent_bar(sl, y=0.55)
    txt(sl, "SECURITY & TESTING", 0.4, 0.1, 12.5, 0.5,
        size=28, bold=True, color=WHITE)

    # Security
    box(sl, 0.3, 0.75, 6.0, 6.5, fill=CARD_BG)
    txt(sl, "SECURITY CONTROLS", 0.45, 0.8, 5.7, 0.4,
        size=14, bold=True, color=RED)
    sec_items = [
        ("XSS Prevention", "html.escape() on all user input before\nembedding in markdown/HTML outputs"),
        ("Path Traversal", "_safe_join() resolves + confines all writes\nto declared output directory"),
        ("No Hardcoded Creds", "docker-compose uses ${POSTGRES_PASSWORD:?}\nFails fast if not set"),
        ("Non-Root Container", "Dockerfile: runAsUser=1000 (appuser)\nNo build tools in runtime image"),
        ("Timezone-Aware", "All timestamps: datetime.now(timezone.utc)\nNo naive datetime objects"),
        ("Input Validation", "Requirement sanitized before any\nstring interpolation into outputs"),
        ("Multi-Stage Build", "Builder stage separate from runtime\npython:3.12-slim — minimal attack surface"),
    ]
    for i, (title, detail) in enumerate(sec_items):
        by = 1.35 + i * 0.75
        txt(sl, title, 0.45, by, 2.2, 0.35, size=11, bold=True, color=ACCENT2)
        txt(sl, detail, 2.7, by, 3.5, 0.65, size=10, color=LIGHT_GRAY)

    # Testing
    box(sl, 6.6, 0.75, 6.4, 6.5, fill=CARD_BG)
    txt(sl, "TESTING STRATEGY", 6.75, 0.8, 6.1, 0.4,
        size=14, bold=True, color=GREEN)
    test_classes = [
        ("TestRequirementAgent", "7 tests",
         "Classification, ambiguity detection, XSS sanitization"),
        ("TestDecompositionAgent", "9 tests",
         "Task structure, dependency correctness, analytics injection"),
        ("TestOrchestrator", "8 tests",
         "Terminal state guarantee, failure/rejection propagation, auto-approve"),
        ("TestArtifacts", "15 tests",
         "Presence and structure of all generated outputs"),
        ("TestOutputWriter", "4 tests",
         "Directory creation, summary, path traversal blocking"),
        ("TestMetrics", "4 tests",
         "Counter increments, metrics text output"),
    ]
    for i, (cls, count, detail) in enumerate(test_classes):
        by = 1.1 + i * 0.9
        box(sl, 6.75, by, 6.1, 0.8, fill=DARK_BG,
            line_color=GREEN, line_width=Pt(1))
        txt(sl, cls, 6.9, by + 0.05, 3.5, 0.3, size=11, bold=True, color=GREEN)
        txt(sl, count, 10.5, by + 0.05, 1.2, 0.3,
            size=11, bold=True, color=YELLOW, align=PP_ALIGN.RIGHT)
        txt(sl, detail, 6.9, by + 0.4, 5.8, 0.35, size=10, color=LIGHT_GRAY)

    txt(sl, "Total: 47/47 passed  |  python run_tests.py  |  Coverage target: >= 80%",
        6.75, 6.95, 6.1, 0.35, size=11, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)
