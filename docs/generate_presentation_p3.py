"""Slides 11-14 for Agentic SDLC presentation."""
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


def add_slides_11_to_14(prs, slide, bg, box, txt, accent_bar):

    # ── SLIDE 11: Three Scenarios ─────────────────────────────────────────────
    sl = slide()
    bg(sl)
    accent_bar(sl, y=0.55)
    txt(sl, "THREE EXAMPLE SCENARIOS", 0.4, 0.1, 12.5, 0.5,
        size=28, bold=True, color=WHITE)

    scenarios = [
        (
            "GREENFIELD",
            ACCENT,
            "Build a scalable URL shortener service\nwith APIs, persistence, and analytics.",
            [
                "Scenario: greenfield",
                "Ambiguities: 3 detected, 3 resolved",
                "  scalable -> 10k RPS, Redis cache",
                "  analytics -> click/referrer/UA tracking",
                "  persistence -> PostgreSQL + Redis",
                "Tasks: 9 (incl. analytics_design)",
                "Artifacts: 9 generated",
                "Validation: PASSED",
                "Risks: 6 identified",
            ]
        ),
        (
            "BROWNFIELD",
            ACCENT2,
            "Enhance the existing URL shortener to\nsupport configurable link expiration.",
            [
                "Scenario: brownfield",
                "Ambiguities: 0",
                "Tasks: codebase_analysis ->",
                "  impact_assessment ->",
                "  code_generation ->",
                "  test_generation ->",
                "  validation -> documentation",
                "Codebase scanned: scores relevance",
                "Breaking change risk: assessed",
            ]
        ),
        (
            "AMBIGUOUS",
            YELLOW,
            "Make the service fast and scalable.",
            [
                "Scenario: ambiguous",
                "Ambiguities: 2 detected, 2 resolved",
                "  fast -> p99 < 50ms cache-first",
                "  scalable -> 10k RPS horizontal",
                "Workflow proceeds with resolved",
                "  constraints as if greenfield",
                "Demonstrates: system never blocks",
                "  on vague requirements",
            ]
        ),
    ]

    for i, (name, color, req, results) in enumerate(scenarios):
        bx = 0.3 + i * 4.35
        box(sl, bx, 0.75, 4.1, 6.5, fill=CARD_BG, line_color=color, line_width=Pt(2))
        box(sl, bx, 0.75, 4.1, 0.55, fill=color)
        txt(sl, name, bx, 0.75, 4.1, 0.55,
            size=15, bold=True, color=DARK_BG, align=PP_ALIGN.CENTER)
        txt(sl, "Requirement:", bx + 0.15, 1.4, 3.8, 0.3,
            size=10, bold=True, color=color)
        txt(sl, req, bx + 0.15, 1.75, 3.8, 0.75, size=10, color=LIGHT_GRAY)
        txt(sl, "Result:", bx + 0.15, 2.6, 3.8, 0.3,
            size=10, bold=True, color=color)
        for j, r in enumerate(results):
            txt(sl, r, bx + 0.15, 2.95 + j * 0.42, 3.8, 0.38, size=10, color=WHITE)

    # ── SLIDE 12: Risks & Trade-offs ─────────────────────────────────────────
    sl = slide()
    bg(sl)
    accent_bar(sl, y=0.55)
    txt(sl, "RISKS & TRADE-OFFS", 0.4, 0.1, 12.5, 0.5,
        size=28, bold=True, color=WHITE)

    risks = [
        ("Code Collision", "MEDIUM", YELLOW,
         "Concurrent requests may generate different codes before idempotency check.",
         "DB unique constraint or SELECT FOR UPDATE advisory lock."),
        ("Cache Stampede", "MEDIUM", YELLOW,
         "Redis flush causes all requests to hit PostgreSQL simultaneously.",
         "Probabilistic early expiration or single-flight request coalescing."),
        ("Analytics Data Loss", "LOW", GREEN,
         "Fire-and-forget async tasks lost if process crashes before persisting.",
         "Durable queue (Redis Streams / SQS) with at-least-once delivery."),
        ("Open Redirect Abuse", "HIGH", RED,
         "Malicious actors could shorten phishing or malware URLs.",
         "Google Safe Browsing API check + rate limiting per IP."),
        ("Code Exhaustion", "LOW", GREEN,
         "7-char base62 = ~3.5B codes. At 1M/day: 9500 years.",
         "Monitor utilization; increase to 8 chars if needed."),
        ("DB Single Point of Failure", "HIGH", RED,
         "Primary DB failure causes full service outage.",
         "AWS RDS Multi-AZ with automatic failover + read replicas."),
    ]

    for i, (title, level, color, desc, mitigation) in enumerate(risks):
        col = i % 2
        row = i // 2
        bx = 0.3 + col * 6.5
        by = 0.85 + row * 2.1
        box(sl, bx, by, 6.2, 1.9, fill=CARD_BG, line_color=color, line_width=Pt(1.5))
        txt(sl, title, bx + 0.15, by + 0.1, 4.0, 0.38, size=13, bold=True, color=WHITE)
        box(sl, bx + 4.3, by + 0.1, 1.7, 0.35, fill=color)
        txt(sl, level, bx + 4.3, by + 0.1, 1.7, 0.35,
            size=11, bold=True, color=DARK_BG, align=PP_ALIGN.CENTER)
        txt(sl, desc, bx + 0.15, by + 0.55, 5.9, 0.5, size=10, color=LIGHT_GRAY)
        txt(sl, f"Mitigation: {mitigation}", bx + 0.15, by + 1.1, 5.9, 0.65,
            size=10, color=color)

    # ── SLIDE 13: Deployment Architecture ────────────────────────────────────
    sl = slide()
    bg(sl)
    accent_bar(sl, y=0.55)
    txt(sl, "DEPLOYMENT ARCHITECTURE", 0.4, 0.1, 12.5, 0.5,
        size=28, bold=True, color=WHITE)

    # Local
    box(sl, 0.3, 0.75, 3.8, 3.0, fill=CARD_BG, line_color=ACCENT, line_width=Pt(1.5))
    txt(sl, "LOCAL", 0.45, 0.8, 3.5, 0.4, size=13, bold=True, color=ACCENT)
    local_items = [
        "python main.py --auto",
        "  No dependencies required",
        "  Outputs to ./outputs/run_{id}/",
        "",
        "python main.py --serve",
        "  + HTTP /health + /metrics",
        "",
        "docker-compose up --build",
        "  + Prometheus :9090",
        "  + Grafana :3000",
        "  + Loki :3100",
    ]
    for i, item in enumerate(local_items):
        txt(sl, item, 0.45, 1.3 + i * 0.3, 3.5, 0.28, size=9, color=LIGHT_GRAY)

    # Docker
    box(sl, 4.3, 0.75, 4.0, 3.0, fill=CARD_BG, line_color=ACCENT2, line_width=Pt(1.5))
    txt(sl, "DOCKER", 4.45, 0.8, 3.7, 0.4, size=13, bold=True, color=ACCENT2)
    docker_items = [
        "Multi-stage build",
        "  Stage 1: builder (gcc + pip)",
        "  Stage 2: python:3.12-slim",
        "Non-root user (appuser:1000)",
        "HEALTHCHECK every 30s",
        "Outputs volume mounted",
        "Image: ghcr.io/org/agentic-sdlc",
        "Tags: branch, sha-{short}, latest",
    ]
    for i, item in enumerate(docker_items):
        txt(sl, item, 4.45, 1.3 + i * 0.3, 3.7, 0.28, size=9, color=LIGHT_GRAY)

    # Kubernetes
    box(sl, 8.5, 0.75, 4.5, 3.0, fill=CARD_BG, line_color=GREEN, line_width=Pt(1.5))
    txt(sl, "KUBERNETES", 8.65, 0.8, 4.2, 0.4, size=13, bold=True, color=GREEN)
    k8s_items = [
        "kubectl apply -k k8s/overlays/production",
        "Namespace: agentic-sdlc",
        "Deployment: 2-10 replicas (HPA)",
        "RollingUpdate: zero downtime",
        "Ingress: TLS + cert-manager",
        "Kustomize overlays:",
        "  staging: 1 replica, develop tag",
        "  production: 3 replicas, latest",
    ]
    for i, item in enumerate(k8s_items):
        txt(sl, item, 8.65, 1.3 + i * 0.3, 4.2, 0.28, size=9, color=LIGHT_GRAY)

    # Observability stack diagram
    box(sl, 0.3, 4.0, 12.7, 3.2, fill=CARD_BG)
    txt(sl, "OBSERVABILITY STACK", 0.45, 4.05, 12.4, 0.4,
        size=13, bold=True, color=ACCENT)

    obs = [
        ("Agentic SDLC\n:8080", ACCENT, 0.5),
        ("Prometheus\n:9090", YELLOW, 3.2),
        ("Grafana\n:3000", GREEN, 5.9),
        ("Loki\n:3100", ACCENT2, 8.6),
        ("Promtail", LIGHT_GRAY, 11.3),
    ]
    for name, color, bx in obs:
        box(sl, bx, 4.6, 2.2, 1.5, fill=DARK_BG, line_color=color, line_width=Pt(1.5))
        txt(sl, name, bx, 4.6, 2.2, 1.5,
            size=12, bold=True, color=color, align=PP_ALIGN.CENTER)

    arrows_obs = [2.7, 5.4, 8.1, 10.8]
    for ax in arrows_obs:
        txt(sl, "->", ax, 5.1, 0.5, 0.4,
            size=14, bold=True, color=LIGHT_GRAY, align=PP_ALIGN.CENTER)

    txt(sl, "Structured JSON logs -> Promtail -> Loki -> Grafana",
        0.45, 6.3, 12.4, 0.35, size=11, color=LIGHT_GRAY, align=PP_ALIGN.CENTER)
    txt(sl, "Prometheus metrics -> Grafana dashboards (workflow runs, task rates, durations)",
        0.45, 6.65, 12.4, 0.35, size=11, color=LIGHT_GRAY, align=PP_ALIGN.CENTER)

    # ── SLIDE 14: Summary & Closing ───────────────────────────────────────────
    sl = slide()
    bg(sl)
    accent_bar(sl, y=0.0, color=ACCENT)
    accent_bar(sl, y=7.44, color=ACCENT)
    box(sl, 0, 0, 0.08, 7.5, fill=ACCENT)

    txt(sl, "SUMMARY", 0.3, 0.3, 12.5, 0.6,
        size=36, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

    pillars = [
        ("End-to-End Workflow", ACCENT,
         "Requirement -> Architecture -> Schema -> Code\n-> Tests -> Validation -> Documentation"),
        ("Controlled Autonomy", ACCENT2,
         "9 agents execute independently.\n3 human approval gates at critical checkpoints."),
        ("Production Quality", GREEN,
         "10 FastAPI files, OpenAPI 3.0, PostgreSQL DDL,\nunit + integration tests, Docker + K8s ready."),
        ("Secure by Design", RED,
         "XSS prevention, path traversal blocking,\nnon-root container, no hardcoded credentials."),
        ("Full Observability", YELLOW,
         "Prometheus metrics, Grafana dashboards,\nLoki log aggregation, structured JSON logs."),
        ("Three Scenarios", ACCENT,
         "Greenfield, Brownfield, Ambiguous —\nall handled with auto-resolution of ambiguities."),
    ]

    for i, (title, color, detail) in enumerate(pillars):
        col = i % 3
        row = i // 2
        bx = 0.4 + col * 4.3
        by = 1.2 + row * 2.5
        box(sl, bx, by, 4.0, 2.2, fill=CARD_BG, line_color=color, line_width=Pt(2))
        txt(sl, title, bx + 0.15, by + 0.12, 3.7, 0.45,
            size=14, bold=True, color=color)
        txt(sl, detail, bx + 0.15, by + 0.65, 3.7, 1.3, size=11, color=LIGHT_GRAY)

    txt(sl, "github.com/your-org/agentic-sdlc-system",
        0.3, 7.0, 12.7, 0.38, size=13, color=ACCENT, align=PP_ALIGN.CENTER)
