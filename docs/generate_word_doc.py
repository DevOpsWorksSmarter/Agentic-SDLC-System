"""
Generate Agentic_SDLC_System.docx without python-docx.
A .docx file is a ZIP archive containing XML files.
Run: python docs/generate_word_doc.py
"""
import zipfile
import os
from datetime import datetime

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Agentic_SDLC_System.docx")

# ── XML helpers ───────────────────────────────────────────────────────────────
NS = 'xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas" xmlns:cx="http://schemas.microsoft.com/office/drawing/2014/chartex" xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" xmlns:aink="http://schemas.microsoft.com/office/drawing/2016/ink" xmlns:am3d="http://schemas.microsoft.com/office/drawing/2017/model3d" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:oel="http://schemas.microsoft.com/office/2019/extlst" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" xmlns:w10="urn:schemas-microsoft-com:office:word" xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" xmlns:w15="http://schemas.microsoft.com/office/word/2012/wordml" xmlns:w16cex="http://schemas.microsoft.com/office/word/2018/wordml/cex" xmlns:w16cid="http://schemas.microsoft.com/office/word/2016/wordml/cid" xmlns:w16="http://schemas.microsoft.com/office/word/2018/wordml" xmlns:w16sdtdh="http://schemas.microsoft.com/office/word/2020/wordml/sdtdatahash" xmlns:w16se="http://schemas.microsoft.com/office/word/2015/wordml/symex" xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup" xmlns:wpi="http://schemas.microsoft.com/office/word/2010/wordprocessingInk" xmlns:wne="http://schemas.microsoft.com/office/word/2006/wordml" xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape"'

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def esc(text):
    return (str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


def para(text, style="Normal", bold=False, size=None, color=None, indent=None):
    """Return a <w:p> XML string."""
    rpr_parts = []
    if bold:
        rpr_parts.append("<w:b/>")
    if size:
        rpr_parts.append(f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>')
    if color:
        rpr_parts.append(f'<w:color w:val="{color}"/>')
    rpr = f"<w:rPr>{''.join(rpr_parts)}</w:rPr>" if rpr_parts else ""

    ppr_parts = [f'<w:pStyle w:val="{style}"/>']
    if indent:
        ppr_parts.append(f'<w:ind w:left="{indent}"/>')
    ppr = f"<w:pPr>{''.join(ppr_parts)}</w:pPr>"

    lines = esc(text).split("&#10;") if "&#10;" in esc(text) else [esc(text)]
    runs = []
    for i, line in enumerate(lines):
        if i > 0:
            runs.append("<w:r><w:br/></w:r>")
        runs.append(f"<w:r>{rpr}<w:t xml:space=\"preserve\">{line}</w:t></w:r>")

    return f"<w:p>{ppr}{''.join(runs)}</w:p>"


def heading(text, level=1):
    return para(text, style=f"Heading{level}")


def bullet(text, level=1):
    indent = 720 * level
    ppr = f'<w:pPr><w:pStyle w:val="ListParagraph"/><w:numPr><w:ilvl w:val="{level-1}"/><w:numId w:val="1"/></w:numPr></w:ind w:left="{indent}"/></w:pPr>'
    rpr = ""
    return f'<w:p><w:pPr><w:pStyle w:val="ListParagraph"/><w:ind w:left="{indent}"/></w:pPr><w:r><w:t xml:space="preserve">- {esc(text)}</w:t></w:r></w:p>'


def code_para(text):
    lines = text.strip().split("\n")
    parts = []
    for line in lines:
        parts.append(
            f'<w:p><w:pPr><w:pStyle w:val="Normal"/><w:ind w:left="720"/></w:pPr>'
            f'<w:r><w:rPr><w:rFonts w:ascii="Courier New" w:hAnsi="Courier New"/>'
            f'<w:sz w:val="18"/><w:szCs w:val="18"/><w:color w:val="2E4057"/></w:rPr>'
            f'<w:t xml:space="preserve">{esc(line)}</w:t></w:r></w:p>'
        )
    return "".join(parts)


def table_row(cells, header=False):
    tcs = []
    for cell in cells:
        shd = '<w:shd w:val="clear" w:color="auto" w:fill="1F3A5F"/>' if header else ""
        color = "FFFFFF" if header else "000000"
        bold = "<w:b/>" if header else ""
        tcs.append(
            f'<w:tc><w:tcPr><w:tcBorders>'
            f'<w:top w:val="single" w:sz="4" w:color="AAAAAA"/>'
            f'<w:bottom w:val="single" w:sz="4" w:color="AAAAAA"/>'
            f'<w:left w:val="single" w:sz="4" w:color="AAAAAA"/>'
            f'<w:right w:val="single" w:sz="4" w:color="AAAAAA"/>'
            f'</w:tcBorders>{shd}</w:tcPr>'
            f'<w:p><w:r><w:rPr>{bold}<w:color w:val="{color}"/></w:rPr>'
            f'<w:t xml:space="preserve">{esc(cell)}</w:t></w:r></w:p></w:tc>'
        )
    return f'<w:tr>{"".join(tcs)}</w:tr>'


def table(rows, headers=None):
    tbl_pr = (
        '<w:tblPr><w:tblStyle w:val="TableGrid"/>'
        '<w:tblW w:w="9360" w:type="dxa"/>'
        '<w:tblBorders>'
        '<w:top w:val="single" w:sz="4" w:color="AAAAAA"/>'
        '<w:bottom w:val="single" w:sz="4" w:color="AAAAAA"/>'
        '<w:left w:val="single" w:sz="4" w:color="AAAAAA"/>'
        '<w:right w:val="single" w:sz="4" w:color="AAAAAA"/>'
        '<w:insideH w:val="single" w:sz="4" w:color="AAAAAA"/>'
        '<w:insideV w:val="single" w:sz="4" w:color="AAAAAA"/>'
        '</w:tblBorders></w:tblPr>'
        '<w:tblGrid/>'
    )
    tr_parts = []
    if headers:
        tr_parts.append(table_row(headers, header=True))
    for row in rows:
        tr_parts.append(table_row(row))
    return f'<w:tbl>{tbl_pr}{"".join(tr_parts)}</w:tbl>'


def page_break():
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


def hr():
    return (
        '<w:p><w:pPr><w:pBdr>'
        '<w:bottom w:val="single" w:sz="6" w:space="1" w:color="1F3A5F"/>'
        '</w:pBdr></w:pPr></w:p>'
    )


# ── Document content ──────────────────────────────────────────────────────────
def build_body():
    parts = []

    # ── TITLE PAGE ────────────────────────────────────────────────────────────
    parts.append(para("Agentic SDLC System", style="Title", bold=True, size=52, color="1F3A5F"))
    parts.append(para("End-to-End Technical Documentation", bold=True, size=28, color="2E86AB"))
    parts.append(para(f"Generated: {datetime.now().strftime('%B %d, %Y')}", color="666666"))
    parts.append(para(""))
    parts.append(para(
        "A working prototype of a multi-agent system that transforms a software requirement "
        "into a reviewable engineering outcome — end-to-end across the full SDLC.",
        size=24, color="333333"
    ))
    parts.append(page_break())

    # ── TABLE OF CONTENTS (manual) ────────────────────────────────────────────
    parts.append(heading("Table of Contents", 1))
    toc = [
        "1.  Project Overview & Objectives",
        "2.  System Architecture",
        "3.  Core Data Models (WorkflowState)",
        "4.  Agent Catalogue (9 Agents)",
        "5.  Workflow Orchestrator",
        "6.  Three Execution Scenarios",
        "7.  Generated Artifacts",
        "8.  Security Design",
        "9.  Observability & Metrics",
        "10. CI/CD Pipeline",
        "11. Kubernetes & Deployment Infrastructure",
        "12. Test Strategy & Results",
        "13. Key Design Decisions & Trade-offs",
        "14. Known Limitations",
        "15. How to Run",
    ]
    for item in toc:
        parts.append(bullet(item))
    parts.append(page_break())

    # ── SECTION 1: PROJECT OVERVIEW ───────────────────────────────────────────
    parts.append(heading("1. Project Overview & Objectives", 1))
    parts.append(para(
        "The Agentic SDLC System is a multi-agent orchestration prototype that automates the "
        "entire software development lifecycle — from raw requirement text to production-ready "
        "code, tests, documentation, and deployment infrastructure — without any LLM or external "
        "API dependency. All agent logic is deterministic and rule-based, making the system fully "
        "reproducible and testable in any environment."
    ))
    parts.append(para(""))
    parts.append(heading("Core Objectives", 2))
    objectives = [
        "Demonstrate multi-agent coordination across 9 specialised agents",
        "Implement dependency-aware task scheduling with human-in-the-loop approval gates",
        "Generate production-quality FastAPI code, PostgreSQL schema, OpenAPI spec, Docker/K8s configs",
        "Provide full observability: structured JSON logs, Prometheus metrics, Grafana dashboards",
        "Enforce security: XSS sanitization, path traversal prevention, no hardcoded credentials",
        "Support three scenarios: Greenfield, Brownfield, and Ambiguous requirements",
        "Achieve 45/45 tests passing with a standalone test runner (no pytest required)",
    ]
    for o in objectives:
        parts.append(bullet(o))
    parts.append(page_break())

    # ── SECTION 2: SYSTEM ARCHITECTURE ───────────────────────────────────────
    parts.append(heading("2. System Architecture", 1))
    parts.append(para(
        "The system follows a three-phase pipeline orchestrated by a central WorkflowOrchestrator. "
        "All agents share a single WorkflowState object (the blackboard pattern), eliminating "
        "message-passing overhead and providing a single source of truth."
    ))
    parts.append(para(""))
    parts.append(heading("Architecture Diagram (ASCII)", 2))
    arch_diagram = """\
CLI / main.py
     |
     v  WorkflowState
WorkflowOrchestrator
  |
  Phase 1: Requirement Understanding
  |   RequirementAgent
  |     - Classifies scenario (greenfield/brownfield/ambiguous)
  |     - Detects & auto-resolves ambiguities
  |     - Normalizes requirement + extracts success criteria
  |
  Phase 2: Task Decomposition
  |   DecompositionAgent
  |     - Breaks requirement into ordered tasks with deps
  |     - Injects tasks into shared WorkflowState
  |
  Phase 3: Dependency-Aware Execution
      ArchitectureAgent      (requires_approval=True)
      SchemaAgent
      CodeGenerationAgent    (requires_approval=True)
      TestGenerationAgent
      ValidationAgent        (requires_approval=True)
      DocumentationAgent
      CodebaseReasoningAgent (brownfield only)
     |
     v
OutputWriter
  outputs/run_{id}/
    workflow_summary.json
    execution_log.json
    architecture_design/output.json
    schema_design/output.json
    code_generation/app/*.py + Dockerfile + docker-compose
    test_generation/tests/**/*.py
    documentation/README.md + ENGINEERING_SUMMARY.md + RUNBOOK.md"""
    parts.append(code_para(arch_diagram))
    parts.append(para(""))
    parts.append(heading("Component Responsibilities", 2))
    parts.append(table(
        [
            ["main.py", "CLI entrypoint, HTTP server (/health, /metrics), structured JSON logging"],
            ["WorkflowOrchestrator", "3-phase pipeline, dependency scheduler, approval gates, retry/skip logic"],
            ["WorkflowState", "Shared blackboard — requirement, tasks, artifacts, risks, execution log"],
            ["BaseAgent", "Abstract base with retry loop (max 2), AWAITING_APPROVAL or COMPLETED status"],
            ["OutputWriter", "Persists all artifacts to outputs/run_{id}/ with path-traversal protection"],
            ["metrics.py", "In-process Prometheus counters/histograms, Timer context manager"],
        ],
        headers=["Component", "Responsibility"]
    ))
    parts.append(page_break())

    # ── SECTION 3: CORE DATA MODELS ───────────────────────────────────────────
    parts.append(heading("3. Core Data Models", 1))
    parts.append(para(
        "All state is carried in Python dataclasses defined in src/models/state.py. "
        "The WorkflowState is the central blackboard passed through every agent."
    ))
    parts.append(para(""))
    parts.append(heading("WorkflowState", 2))
    parts.append(table(
        [
            ["id", "str", "8-char UUID prefix — unique run identifier"],
            ["requirement", "Requirement", "Parsed and normalized requirement object"],
            ["tasks", "list[Task]", "All tasks injected by DecompositionAgent"],
            ["artifacts", "dict[str, Any]", "Shared blackboard — agent outputs keyed by task name"],
            ["risks", "list[Risk]", "Risks identified by ValidationAgent"],
            ["validation", "ValidationResult", "Static check results and test strategy"],
            ["execution_log", "list[dict]", "Timestamped audit trail of all agent actions"],
            ["current_phase", "str", "init / requirement_understanding / task_decomposition / execution / complete"],
        ],
        headers=["Field", "Type", "Description"]
    ))
    parts.append(para(""))
    parts.append(heading("TaskStatus Enum", 2))
    parts.append(table(
        [
            ["PENDING", "Task created, waiting for dependencies"],
            ["IN_PROGRESS", "Agent currently executing"],
            ["AWAITING_APPROVAL", "Agent completed, waiting for human/auto approval"],
            ["APPROVED", "Human or auto-approved — treated as terminal"],
            ["REJECTED", "Human rejected — downstream tasks are skipped (terminal)"],
            ["COMPLETED", "Agent completed without approval gate"],
            ["FAILED", "Agent failed after max_retries (2) attempts — downstream tasks skipped"],
            ["SKIPPED", "Skipped due to failed or rejected dependency"],
        ],
        headers=["Status", "Meaning"]
    ))
    parts.append(page_break())

    return parts

def build_body_2():
    parts = []

    # ── SECTION 4: AGENT CATALOGUE ────────────────────────────────────────────
    parts.append(heading("4. Agent Catalogue", 1))
    parts.append(para(
        "The system contains 9 specialised agents, all inheriting from BaseAgent. "
        "Each agent implements a single execute() method and is registered in the AGENT_REGISTRY "
        "in workflow.py. The base class handles retry logic, status transitions, and logging."
    ))
    parts.append(para(""))

    agents = [
        (
            "RequirementAgent",
            "src/agents/requirement_agent.py",
            "Phase 1 — Requirement Understanding",
            [
                "Classifies scenario: GREENFIELD (has API/service keywords), BROWNFIELD (refactor/enhance/fix signals), AMBIGUOUS (too short or vague)",
                "Detects ambiguities via _AMBIGUITY_SIGNALS dict (scalable, fast, secure, analytics, persistence, simple)",
                "Auto-resolves all detected ambiguities with sensible defaults (e.g. 'scalable' -> 10k RPS, Redis cache)",
                "Applies html.escape() on raw input BEFORE any string interpolation — XSS prevention",
                "Extracts: normalized requirement, intent verb+noun, constraints list, success criteria list",
            ]
        ),
        (
            "DecompositionAgent",
            "src/agents/decomposition_agent.py",
            "Phase 2 — Task Decomposition",
            [
                "Greenfield path: 6 tasks (architecture_design -> schema_design -> code_generation -> test_generation -> validation -> documentation)",
                "Injects analytics_design task between schema_design and code_generation when 'analytics' is in the requirement",
                "Brownfield path: 6 tasks starting with codebase_analysis -> impact_assessment -> code_generation -> ...",
                "Injects Task objects directly into state.tasks with correct depends_on and requires_approval flags",
                "Returns a summary list of {name, agent, depends_on} for the execution log",
            ]
        ),
        (
            "ArchitectureAgent",
            "src/agents/architecture_agent.py",
            "Phase 3 — Architecture Design (requires_approval=True)",
            [
                "Generates full system architecture dict: components, data flows, scalability, infrastructure",
                "Components: api_gateway (Nginx/AWS API GW), url_service (FastAPI), cache (Redis), database (PostgreSQL), analytics_worker",
                "Data flows: shorten path (7 steps) and redirect path (cache-first with async analytics publish)",
                "When task.name == 'analytics_design': returns separate async event pipeline architecture",
                "Infrastructure: Docker/K8s local, AWS ECS Fargate or EKS production, RDS Multi-AZ, ElastiCache",
            ]
        ),
        (
            "SchemaAgent",
            "src/agents/schema_agent.py",
            "Phase 3 — Schema Design",
            [
                "Generates PostgreSQL DDL: urls table (id UUID, code VARCHAR(12) UNIQUE, original TEXT, expires_at, is_active)",
                "Generates click_events table with FK to urls, ip_hash, referrer, user_agent",
                "Generates materialized view url_stats for pre-aggregated analytics",
                "Generates full OpenAPI 3.0 spec dict with all 5 endpoints, request/response schemas, error responses",
                "Output stored in state.artifacts['schema_design'] = {database_schema, openapi_spec}",
            ]
        ),
        (
            "CodeGenerationAgent",
            "src/agents/code_generation_agent.py",
            "Phase 3 — Code Generation (requires_approval=True)",
            [
                "Generates 10 FastAPI source files as string content in a files dict",
                "config.py: pydantic-settings with database_url, redis_url, base_url, cache_ttl, rate_limit, code_length",
                "models.py: Pydantic v2 CreateUrlRequest (HttpUrl + field_validator), UrlResponse, StatsResponse",
                "database.py: SQLAlchemy async ORM — UrlRecord + ClickEvent mapped classes, async session factory",
                "shortener.py: Base62 code generation via SHA-256 + timestamp salt; is_valid_code() validator",
                "repository.py: UrlRepository with get_by_code, get_by_original, create, deactivate, record_click, get_stats",
                "service.py: UrlService with shorten (idempotency), resolve (cache-first), deactivate, get_stats",
                "analytics.py: record_click_async() — fire-and-forget, exceptions swallowed to never block redirect",
                "routes.py: 5 FastAPI route handlers with asyncio.create_task() for analytics",
                "main.py: FastAPI app with CORS middleware",
                "docker-compose.yml: Uses ${POSTGRES_PASSWORD:?} — no hardcoded credentials",
            ]
        ),
        (
            "TestGenerationAgent",
            "src/agents/test_generation_agent.py",
            "Phase 3 — Test Generation",
            [
                "conftest.py: SQLite in-memory async engine, test database fixtures, httpx AsyncClient",
                "unit/test_shortener.py: code length, charset (base62 only), uniqueness across calls",
                "unit/test_service.py: shorten with mocked repo+cache, idempotency, resolve cache-hit/miss, 404 handling",
                "integration/test_api.py: full API flow via httpx — create, redirect, metadata, delete, 404",
                "integration/test_analytics.py: analytics failure isolation — redirect must return 302 even if analytics throws",
            ]
        ),
        (
            "ValidationAgent",
            "src/agents/validation_agent.py",
            "Phase 3 — Validation (requires_approval=True)",
            [
                "Identifies 6 risks: code collision (MEDIUM), cache stampede (MEDIUM), analytics data loss (LOW), open redirect abuse (HIGH), code exhaustion (LOW), DB SPOF (HIGH)",
                "Each risk has: title, description, level (RiskLevel enum), mitigation, tradeoff",
                "Runs 6 static checks: architecture/schema/code/test artifacts present (blocking=True), ambiguities resolved, success criteria defined",
                "validation.passed = True only if all blocking checks pass",
                "Defines comprehensive 6-section test strategy string (unit, integration, contract, performance, security, chaos)",
            ]
        ),
        (
            "DocumentationAgent",
            "src/agents/documentation_agent.py",
            "Phase 3 — Documentation",
            [
                "Generates README.md: project overview, quick start, API reference, architecture summary",
                "Generates ENGINEERING_SUMMARY.md: full design decisions, risks table, trade-offs, success criteria",
                "Generates RUNBOOK.md: operational procedures, health checks, scaling, incident response",
                "Uses _s() helper (html.escape) on all user-derived fields before embedding in markdown",
                "Output stored as files dict: {'README.md': ..., 'ENGINEERING_SUMMARY.md': ..., 'RUNBOOK.md': ...}",
            ]
        ),
        (
            "CodebaseReasoningAgent",
            "src/agents/codebase_reasoning_agent.py",
            "Phase 3 — Brownfield Only",
            [
                "Reads existing codebase from state.artifacts['codebase_path']",
                "Uses os.path.realpath() + base-dir confinement check to prevent path traversal attacks",
                "Scores file relevance by keyword matching against requirement terms",
                "Identifies impacted modules, existing API patterns, data models",
                "Output feeds into impact_assessment task for brownfield change planning",
            ]
        ),
    ]

    for name, path, phase, points in agents:
        parts.append(heading(name, 2))
        parts.append(para(f"File: {path}", color="666666"))
        parts.append(para(f"Phase: {phase}", bold=True))
        for p in points:
            parts.append(bullet(p))
        parts.append(para(""))

    parts.append(page_break())

    # ── SECTION 5: WORKFLOW ORCHESTRATOR ──────────────────────────────────────
    parts.append(heading("5. Workflow Orchestrator", 1))
    parts.append(para(
        "The WorkflowOrchestrator (src/orchestrator/workflow.py) coordinates all three phases. "
        "It is the only component that knows about agent ordering — agents themselves are stateless "
        "and only interact with WorkflowState."
    ))
    parts.append(para(""))
    parts.append(heading("Execution Flow", 2))
    flow_steps = [
        "Phase 1: Run understand_requirement task via RequirementAgent",
        "Phase 2: Run decompose task via DecompositionAgent — injects all downstream tasks into state.tasks",
        "Phase 3: _execute_plan() loop — up to len(plan)*2 iterations to handle dependency ordering",
        "Each iteration: find all PENDING tasks whose depends_on are all in terminal states",
        "Run each ready task via its registered agent",
        "If task FAILED: call _skip_dependents() recursively to skip all downstream tasks",
        "If task AWAITING_APPROVAL: call _handle_approval() — auto, callback, or interactive CLI",
        "Loop exits when no ready tasks remain (all terminal or deadlock detected)",
    ]
    for s in flow_steps:
        parts.append(bullet(s))

    parts.append(para(""))
    parts.append(heading("Approval Gate Modes", 2))
    parts.append(table(
        [
            ["auto_approve=True", "Task immediately set to APPROVED — used for CI/CD (--auto flag)"],
            ["approval_callback", "Programmatic callback(task, state) -> bool — used in tests"],
            ["Interactive CLI", "Prompts user: y=approve, n=reject, s=skip — used in interactive mode"],
        ],
        headers=["Mode", "Behaviour"]
    ))

    parts.append(para(""))
    parts.append(heading("Error Recovery", 2))
    parts.append(table(
        [
            ["Retry", "BaseAgent retries up to max_retries=2 times on exception"],
            ["FAILED status", "Set after all retries exhausted; error message stored in task.error"],
            ["Skip dependents", "_skip_dependents() recursively marks all downstream PENDING tasks as SKIPPED on FAILED or REJECTED"],
            ["Deadlock detection", "If no ready tasks but pending tasks remain, all are force-skipped with error log"],
        ],
        headers=["Mechanism", "Description"]
    ))
    parts.append(page_break())

    # ── SECTION 6: THREE EXECUTION SCENARIOS ──────────────────────────────────
    parts.append(heading("6. Three Execution Scenarios", 1))

    parts.append(heading("Scenario 1: Greenfield", 2))
    parts.append(para("Command:"))
    parts.append(code_para('python main.py --auto --requirement "Build a scalable URL shortener service with APIs, persistence, and analytics."'))
    parts.append(para(""))
    parts.append(para("What happens:"))
    greenfield_steps = [
        "RequirementAgent classifies as GREENFIELD (has 'service', 'api' keywords)",
        "Detects 3 ambiguities: scalable, analytics, persistence — all auto-resolved",
        "DecompositionAgent creates 7 tasks (includes analytics_design)",
        "ArchitectureAgent designs layered REST API with cache-aside pattern",
        "SchemaAgent generates PostgreSQL DDL + OpenAPI 3.0 spec",
        "ArchitectureAgent (analytics_design) designs async event pipeline",
        "CodeGenerationAgent generates 10 FastAPI files + Dockerfile + docker-compose",
        "TestGenerationAgent generates 5 test files (conftest, 2 unit, 2 integration)",
        "ValidationAgent identifies 6 risks, runs 6 static checks — all blocking checks PASS",
        "DocumentationAgent generates README.md, ENGINEERING_SUMMARY.md, RUNBOOK.md",
        "OutputWriter persists all artifacts to outputs/run_{id}/",
        "Result: 9 artifacts, 6 risks, validation PASSED",
    ]
    for s in greenfield_steps:
        parts.append(bullet(s))

    parts.append(para(""))
    parts.append(heading("Scenario 2: Brownfield", 2))
    parts.append(para("Command:"))
    parts.append(code_para('python main.py --auto --requirement "Enhance the existing URL shortener to support configurable link expiration." --codebase-path ./outputs_e2e'))
    parts.append(para(""))
    parts.append(para("What happens:"))
    brownfield_steps = [
        "RequirementAgent classifies as BROWNFIELD (keyword: 'enhance', 'existing')",
        "DecompositionAgent creates 6 brownfield tasks starting with codebase_analysis",
        "CodebaseReasoningAgent scans existing codebase with path-traversal protection",
        "ValidationAgent runs impact_assessment — identifies breaking changes and migration needs",
        "Remaining tasks: code_generation, test_generation, validation, documentation",
        "Result: validation shows WARNINGS (expected — no prior code in same run)",
    ]
    for s in brownfield_steps:
        parts.append(bullet(s))

    parts.append(para(""))
    parts.append(heading("Scenario 3: Ambiguous Requirement", 2))
    parts.append(para("Command:"))
    parts.append(code_para('python main.py --auto --requirement "Make the service fast and scalable."'))
    parts.append(para(""))
    parts.append(para("What happens:"))
    ambiguous_steps = [
        "RequirementAgent classifies as AMBIGUOUS (< 8 words, no service/api/system keyword)",
        "Detects 2 ambiguities: 'fast' (latency SLOs?) and 'scalable' (scale targets?)",
        "Both auto-resolved: fast -> p99 < 50ms; scalable -> 10k RPS, horizontal scaling",
        "DecompositionAgent uses greenfield path (fallback for ambiguous)",
        "Full 6-task pipeline executes normally",
        "Result: 6 tasks all OK, validation PASSED",
    ]
    for s in ambiguous_steps:
        parts.append(bullet(s))

    parts.append(page_break())

    # ── SECTION 7: GENERATED ARTIFACTS ────────────────────────────────────────
    parts.append(heading("7. Generated Artifacts", 1))
    parts.append(para(
        "Every workflow run produces a structured output directory at outputs/run_{id}/. "
        "All file writes are path-sanitized and confined to this directory."
    ))
    parts.append(para(""))
    parts.append(table(
        [
            ["workflow_summary.json", "Task statuses, risks, validation results, artifact list"],
            ["execution_log.json", "Timestamped audit trail — 27 entries for a full greenfield run"],
            ["architecture_design/output.json", "System components, data flows, scalability, infrastructure topology"],
            ["schema_design/output.json", "PostgreSQL DDL + OpenAPI 3.0 spec"],
            ["analytics_design/output.json", "Async analytics pipeline design (greenfield with analytics)"],
            ["code_generation/app/main.py", "FastAPI app entrypoint with CORS middleware"],
            ["code_generation/app/routes.py", "5 API route handlers with async analytics"],
            ["code_generation/app/service.py", "Business logic: shorten (idempotent), resolve (cache-first), deactivate"],
            ["code_generation/app/repository.py", "SQLAlchemy async repository with stats aggregation"],
            ["code_generation/app/models.py", "Pydantic v2 request/response models with validators"],
            ["code_generation/app/database.py", "SQLAlchemy ORM models + async session factory"],
            ["code_generation/app/cache.py", "Redis async cache helpers (get/set/delete)"],
            ["code_generation/app/shortener.py", "Base62 code generation + validation"],
            ["code_generation/app/analytics.py", "Fire-and-forget click event recorder"],
            ["code_generation/app/config.py", "pydantic-settings configuration"],
            ["code_generation/Dockerfile", "Multi-stage build, non-root user"],
            ["code_generation/docker-compose.yml", "API + PostgreSQL + Redis with health checks"],
            ["code_generation/requirements.txt", "Pinned FastAPI, SQLAlchemy, Redis, Pydantic deps"],
            ["test_generation/tests/conftest.py", "SQLite in-memory fixtures, httpx AsyncClient"],
            ["test_generation/tests/unit/test_shortener.py", "Base62 logic unit tests"],
            ["test_generation/tests/unit/test_service.py", "Service layer with mocked dependencies"],
            ["test_generation/tests/integration/test_api.py", "Full API flow integration tests"],
            ["test_generation/tests/integration/test_analytics.py", "Analytics isolation tests"],
            ["documentation/README.md", "Project overview, quick start, API reference"],
            ["documentation/ENGINEERING_SUMMARY.md", "Design decisions, risks, trade-offs"],
            ["documentation/RUNBOOK.md", "Operational procedures, incident response"],
        ],
        headers=["Artifact", "Description"]
    ))
    parts.append(page_break())

    return parts

def build_body_3():
    parts = []

    # ── SECTION 8: SECURITY DESIGN ────────────────────────────────────────────
    parts.append(heading("8. Security Design", 1))
    parts.append(para(
        "Security was reviewed and hardened across the codebase. The following vulnerabilities "
        "were identified and fixed during the security review phase."
    ))
    parts.append(para(""))
    parts.append(table(
        [
            ["CWE-79/80 XSS", "HIGH", "requirement_agent.py, documentation_agent.py",
             "html.escape() applied to all user input before string interpolation; _s() helper in doc agent"],
            ["CWE-22 Path Traversal", "HIGH", "output_writer.py, codebase_reasoning_agent.py",
             "_safe_segment() sanitizes path components; _safe_join() uses realpath + startswith check"],
            ["CWE-798 Hardcoded Credentials", "CRITICAL", "code_generation_agent.py (docker-compose)",
             "Replaced hardcoded passwords with ${POSTGRES_PASSWORD:?} — fails fast if env var not set"],
            ["Naive datetime", "LOW", "state.py, base.py",
             "All datetime.now() calls use timezone.utc — prevents timezone-aware comparison errors"],
            ["Dot-segment bypass", "MEDIUM", "output_writer.py",
             "_TRAVERSAL regex blocks pure-dot segments (.., .) after sanitization"],
        ],
        headers=["Vulnerability", "Severity", "Location", "Fix Applied"]
    ))
    parts.append(para(""))
    parts.append(heading("Path Traversal Protection Detail", 2))
    parts.append(code_para("""\
_SAFE_SEGMENT = re.compile(r"[^a-zA-Z0-9_\\-.]")  # allow dots for extensions
_TRAVERSAL    = re.compile(r"^\\.+$")              # block pure-dot segments

def _safe_segment(name: str) -> str:
    sanitized = _SAFE_SEGMENT.sub("_", name)
    if _TRAVERSAL.match(sanitized):   # blocks '.' and '..'
        return "_"
    return sanitized

def _safe_join(base: str, *parts: str) -> str:
    base = os.path.realpath(base)
    candidate = os.path.realpath(os.path.join(base, *parts))
    if not (candidate == base or candidate.startswith(base + os.sep)):
        raise ValueError(f"Path traversal blocked: {candidate}")
    return candidate"""))
    parts.append(page_break())

    # ── SECTION 9: OBSERVABILITY & METRICS ────────────────────────────────────
    parts.append(heading("9. Observability & Metrics", 1))
    parts.append(para(
        "The system exposes Prometheus-compatible metrics via an in-process registry (no external "
        "library required). A daemon HTTP server serves /health and /metrics endpoints."
    ))
    parts.append(para(""))
    parts.append(heading("Prometheus Metrics", 2))
    parts.append(table(
        [
            ["sdlc_workflow_runs_total", "Counter", "status, scenario", "Total workflow executions by outcome and scenario type"],
            ["sdlc_task_executions_total", "Counter", "agent, status", "Task executions by agent name and started/success/failed"],
            ["sdlc_approval_decisions_total", "Counter", "decision, task", "Approval gate decisions (auto_approved, approved, rejected, skipped)"],
            ["sdlc_workflow_duration_seconds", "Histogram", "workflow_id", "End-to-end workflow execution time"],
        ],
        headers=["Metric", "Type", "Labels", "Description"]
    ))
    parts.append(para(""))
    parts.append(heading("HTTP Endpoints", 2))
    parts.append(table(
        [
            ["GET /health", "Returns {\"status\": \"ok\"} — used by K8s liveness/readiness probes"],
            ["GET /metrics", "Returns Prometheus text format — scraped by Prometheus every 10s"],
        ],
        headers=["Endpoint", "Purpose"]
    ))
    parts.append(para(""))
    parts.append(heading("Observability Stack (docker-compose)", 2))
    parts.append(table(
        [
            ["Prometheus", ":9090", "Scrapes /metrics every 10s, stores time-series data"],
            ["Grafana", ":3000", "8-panel dashboard: workflow runs, task success rate, duration, approvals"],
            ["Loki", ":3100", "Log aggregation backend"],
            ["Promtail", "sidecar", "Ships Docker container logs to Loki"],
        ],
        headers=["Service", "Port", "Role"]
    ))
    parts.append(para(""))
    parts.append(heading("Structured JSON Logging", 2))
    parts.append(code_para("""\
{
  "timestamp": "2024-01-15T10:30:00.000Z",
  "level": "info",
  "service": "agentic-sdlc",
  "message": "Workflow complete",
  "workflow_id": "c20cf7be",
  "scenario": "greenfield",
  "duration_seconds": 0.42,
  "tasks_total": 9,
  "tasks_failed": 0,
  "artifacts": 9
}"""))
    parts.append(page_break())

    # ── SECTION 10: CI/CD PIPELINE ────────────────────────────────────────────
    parts.append(heading("10. CI/CD Pipeline", 1))
    parts.append(para(
        "Two GitHub Actions workflows implement a full CI/CD pipeline with quality gates, "
        "end-to-end testing, Docker image publishing, and staged deployment with rollback."
    ))
    parts.append(para(""))
    parts.append(heading("CI Pipeline (.github/workflows/ci.yml)", 2))
    parts.append(para("Triggers: push to main/develop, pull_request to main"))
    parts.append(para(""))
    parts.append(table(
        [
            ["1. lint", "ruff check + ruff format --check on src/, tests/, main.py"],
            ["2. test", "pytest tests/ --cov=src --cov-fail-under=80 (needs lint to pass)"],
            ["3. e2e", "Full greenfield workflow run + Python artifact validation script (needs test to pass)"],
            ["4. build", "docker buildx build + push to ghcr.io (main/develop only, needs e2e to pass)"],
        ],
        headers=["Job", "Description"]
    ))
    parts.append(para(""))
    parts.append(heading("CD Pipeline (.github/workflows/cd.yml)", 2))
    parts.append(para("Triggers: CI workflow completed successfully on main branch"))
    parts.append(para(""))
    parts.append(table(
        [
            ["deploy-staging", "kubectl set image + rollout status in staging namespace; smoke test /health"],
            ["approve-production", "Manual GitHub Environment gate — requires human approval in GitHub UI"],
            ["deploy-production", "Rolling deploy to production; 3-attempt health check; auto-rollback on failure; git tag release"],
        ],
        headers=["Job", "Description"]
    ))
    parts.append(para(""))
    parts.append(heading("Docker Image", 2))
    parts.append(code_para("""\
# Multi-stage Dockerfile
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim AS runtime
RUN useradd -u 1000 -m appuser   # non-root user
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY . .
USER appuser
EXPOSE 8080
HEALTHCHECK CMD python -c "import src.models.state"
CMD ["python", "main.py", "--serve", "--port", "8080"]"""))
    parts.append(page_break())

    # ── SECTION 11: KUBERNETES & DEPLOYMENT ───────────────────────────────────
    parts.append(heading("11. Kubernetes & Deployment Infrastructure", 1))
    parts.append(para(
        "Kubernetes manifests are organized with Kustomize overlays for staging and production. "
        "All manifests follow security best practices: non-root containers, resource limits, "
        "liveness/readiness probes, and TLS via cert-manager."
    ))
    parts.append(para(""))
    parts.append(heading("k8s/base/ Manifests", 2))
    parts.append(table(
        [
            ["namespace.yml", "agentic-sdlc namespace"],
            ["deployment.yml", "2 replicas, RollingUpdate (maxSurge=1, maxUnavailable=0), liveness + readiness probes on /health"],
            ["service.yml", "ClusterIP service + HPA (2-10 replicas, 70% CPU target) + PVC + ServiceAccount + ConfigMap"],
            ["ingress.yml", "TLS termination via cert-manager, host-based routing"],
            ["kustomization.yml", "Base kustomization referencing all manifests"],
        ],
        headers=["File", "Purpose"]
    ))
    parts.append(para(""))
    parts.append(heading("Overlays", 2))
    parts.append(table(
        [
            ["k8s/overlays/staging/", "1 replica, develop image tag, reduced resource requests"],
            ["k8s/overlays/production/", "3 replicas, latest image tag, full resource limits"],
        ],
        headers=["Overlay", "Configuration"]
    ))
    parts.append(para(""))
    parts.append(heading("Deploy Commands", 2))
    parts.append(code_para("""\
# Staging
kubectl apply -k k8s/overlays/staging/

# Production
kubectl apply -k k8s/overlays/production/

# Check rollout
kubectl rollout status deployment/agentic-sdlc -n agentic-sdlc"""))
    parts.append(page_break())

    # ── SECTION 12: TEST STRATEGY & RESULTS ───────────────────────────────────
    parts.append(heading("12. Test Strategy & Results", 1))
    parts.append(para(
        "The system includes two test runners: tests/test_system.py (pytest-based) and "
        "run_tests.py (standalone, no pytest required). All 45 tests pass."
    ))
    parts.append(para(""))
    parts.append(heading("Test Results: 47/47 Passed", 2))
    parts.append(table(
        [
            ["TestRequirementAgent", "7", "Greenfield/brownfield/ambiguous classification, ambiguity detection, XSS sanitization"],
            ["TestDecompositionAgent", "9", "All task names present, analytics_design injection, brownfield codebase_analysis, dependency correctness"],
            ["TestOrchestrator", "8", "Terminal state guarantee, phase=complete, execution log, failure injection, rejection propagation, auto-approve"],
            ["TestArtifacts", "15", "Architecture components, schema fields, code files, unit+integration tests, risks, blocking checks, doc files"],
            ["TestOutputWriter", "4", "Run directory created, workflow_summary.json exists and correct, path traversal blocked"],
            ["TestMetrics", "4", "Workflow counter incremented, task counter incremented, metrics_text output, contains workflow counter"],
        ],
        headers=["Test Section", "Count", "Coverage"]
    ))
    parts.append(para(""))
    parts.append(heading("Key Test: Failure Injection", 2))
    parts.append(code_para("""\
class BrokenAgent(BaseAgent):
    name = "architecture_agent"
    def execute(self, task, state):
        raise RuntimeError("Simulated failure")

AGENT_REGISTRY["architecture_agent"] = BrokenAgent()
state = run(URL_REQ)

arch   = next(t for t in state.tasks if t.name == "architecture_design")
schema = next(t for t in state.tasks if t.name == "schema_design")

assert arch.status   == TaskStatus.FAILED   # retried 2x, then FAILED
assert schema.status == TaskStatus.SKIPPED  # dependency failed -> skipped"""))
    parts.append(para(""))
    parts.append(heading("Validation Script (validate_artifacts.py)", 2))
    parts.append(para("Checks performed on a real greenfield run output:"))
    checks = [
        "workflow_summary.json exists and scenario == greenfield",
        "execution_log.json exists with 27 structured log entries",
        "10 FastAPI source files present in code_generation/app/",
        "Dockerfile and docker-compose.yml present",
        "5 test files present (conftest, 2 unit, 2 integration)",
        "3 documentation files present (README, ENGINEERING_SUMMARY, RUNBOOK)",
        "schema_design/output.json has database_schema and openapi_spec",
        "architecture_design/output.json has components",
        "6 risks identified with level and mitigation fields",
    ]
    for c in checks:
        parts.append(bullet(c))
    parts.append(page_break())

    # ── SECTION 13: DESIGN DECISIONS ──────────────────────────────────────────
    parts.append(heading("13. Key Design Decisions & Trade-offs", 1))
    parts.append(table(
        [
            ["Shared WorkflowState blackboard",
             "Single source of truth eliminates message-passing overhead; all agents read/write the same object",
             "Tight coupling between agents; acceptable for single-process prototype"],
            ["Dependency-aware scheduler",
             "Tasks execute as soon as all deps are terminal; enables natural parallelism without explicit threading",
             "Single-process — no true parallelism; sufficient for prototype"],
            ["Approval gates on 3 tasks",
             "Architecture, code generation, and validation require sign-off before downstream tasks proceed",
             "Adds latency in interactive mode; --auto flag bypasses for CI/CD"],
            ["Retry + skip-dependents",
             "Failed or rejected tasks retry up to 2 times; on final failure or human rejection, all downstream dependents are skipped",
             "Prevents cascading bad state; may skip valid tasks if one agent is flaky"],
            ["No LLM integration",
             "Fully reproducible and testable without API keys or network access",
             "Agents use deterministic rule-based logic; swap execute() for LLM calls to add intelligence"],
            ["html.escape on all user input",
             "Prevents XSS when requirement text is embedded in markdown/HTML outputs",
             "Minimal overhead; applied at RequirementAgent entry point and DocumentationAgent"],
            ["Path confinement in OutputWriter",
             "All file writes verified to stay within declared output directory via realpath + startswith",
             "Slight overhead per write; critical for security when requirement text influences file paths"],
            ["In-process metrics registry",
             "No prometheus_client dependency; works in any environment",
             "Metrics lost on process restart; use prometheus_client with pushgateway for production"],
        ],
        headers=["Decision", "Rationale", "Trade-off"]
    ))
    parts.append(page_break())

    # ── SECTION 14: KNOWN LIMITATIONS ─────────────────────────────────────────
    parts.append(heading("14. Known Limitations", 1))
    parts.append(table(
        [
            ["No LLM integration", "Agents use deterministic rule-based logic", "Swap agent execute() for LLM calls"],
            ["Brownfield analysis is keyword-based", "Sufficient for prototype", "Replace with AST parsing or tree-sitter"],
            ["Analytics materialized view requires manual refresh", "Add pg_cron or scheduled Lambda for production", "Operational complexity"],
            ["No auth on generated API", "Intentional MVP scope", "Add JWT middleware as next iteration"],
            ["Single-process orchestrator", "Sufficient for prototype", "Replace with Temporal/Step Functions for distributed use"],
            ["In-process metrics lost on restart", "Acceptable for prototype", "Use prometheus_client with remote_write"],
            ["Network unavailable in dev environment", "pip install fails with 503 errors", "run_tests.py created as standalone alternative to pytest"],
            ["Windows cp1252 encoding", "Emoji cause UnicodeEncodeError in terminal", "All emoji replaced with ASCII labels [OK], [FAIL], [PASS]"],
        ],
        headers=["Limitation", "Impact", "Production Path"]
    ))
    parts.append(page_break())

    # ── SECTION 15: HOW TO RUN ────────────────────────────────────────────────
    parts.append(heading("15. How to Run", 1))

    parts.append(heading("Setup", 2))
    parts.append(code_para("""\
# 1. Navigate to project
cd Agentic-SDLC-System

# 2. Create virtual environment
python -m venv .venv
.venv\\Scripts\\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt"""))

    parts.append(para(""))
    parts.append(heading("Run Scenarios", 2))
    parts.append(code_para("""\
# Greenfield (auto-approve, non-interactive)
python main.py --auto --requirement "Build a scalable URL shortener service with APIs, persistence, and analytics."

# Interactive mode (human approval gates)
python main.py --requirement "Build a scalable URL shortener service with APIs, persistence, and analytics."
# At each gate: y=approve, n=reject, s=skip

# Brownfield
python main.py --auto \\
  --requirement "Enhance the existing URL shortener to support configurable link expiration." \\
  --codebase-path ./outputs

# Ambiguous
python main.py --auto --requirement "Make the service fast and scalable."

# With HTTP server (exposes /health and /metrics)
python main.py --serve --auto --requirement "..."

# Custom output directory
python main.py --auto --requirement "..." --output-dir ./my_outputs"""))

    parts.append(para(""))
    parts.append(heading("Run Tests", 2))
    parts.append(code_para("""\
# Standalone (no pytest required) — 45 tests
python run_tests.py

# With pytest (if installed)
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=term-missing

# Validate artifacts from a run
python validate_artifacts.py"""))

    parts.append(para(""))
    parts.append(heading("Docker", 2))
    parts.append(code_para("""\
# Build image
docker build -t agentic-sdlc .

# Run with observability stack
POSTGRES_PASSWORD=secret docker-compose up

# Access
# Grafana:    http://localhost:3000  (admin/admin)
# Prometheus: http://localhost:9090
# App health: http://localhost:8080/health
# Metrics:    http://localhost:8080/metrics"""))

    parts.append(para(""))
    parts.append(heading("Kubernetes", 2))
    parts.append(code_para("""\
# Staging
kubectl apply -k k8s/overlays/staging/

# Production
kubectl apply -k k8s/overlays/production/

# Monitor
kubectl rollout status deployment/agentic-sdlc -n agentic-sdlc
kubectl logs -l app=agentic-sdlc -n agentic-sdlc --follow"""))

    parts.append(hr())
    parts.append(para(""))
    parts.append(para(
        "Agentic SDLC System — End-to-End Technical Documentation",
        bold=True, color="1F3A5F"
    ))
    parts.append(para(
        f"Generated {datetime.now().strftime('%B %d, %Y')} | "
        "9 Agents | 45/45 Tests | 3 Scenarios | Full CI/CD + K8s + Observability",
        color="666666"
    ))

    return parts


# ── DOCX assembly ─────────────────────────────────────────────────────────────
CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>
</Types>"""

RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

WORD_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>
</Relationships>"""

SETTINGS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:defaultTabStop w:val="720"/>
</w:settings>"""

STYLES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
          xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml">
  <w:docDefaults>
    <w:rPrDefault><w:rPr>
      <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>
      <w:sz w:val="22"/><w:szCs w:val="22"/>
      <w:lang w:val="en-US"/>
    </w:rPr></w:rPrDefault>
  </w:docDefaults>

  <w:style w:type="paragraph" w:styleId="Normal">
    <w:name w:val="Normal"/>
    <w:pPr><w:spacing w:after="160" w:line="276" w:lineRule="auto"/></w:pPr>
  </w:style>

  <w:style w:type="paragraph" w:styleId="Title">
    <w:name w:val="Title"/>
    <w:pPr><w:jc w:val="center"/><w:spacing w:before="240" w:after="120"/></w:pPr>
    <w:rPr><w:rFonts w:ascii="Calibri Light" w:hAnsi="Calibri Light"/>
      <w:b/><w:color w:val="1F3A5F"/><w:sz w:val="52"/><w:szCs w:val="52"/>
    </w:rPr>
  </w:style>

  <w:style w:type="paragraph" w:styleId="Heading1">
    <w:name w:val="heading 1"/>
    <w:pPr>
      <w:spacing w:before="480" w:after="160"/>
      <w:pBdr><w:bottom w:val="single" w:sz="6" w:space="1" w:color="1F3A5F"/></w:pBdr>
    </w:pPr>
    <w:rPr><w:rFonts w:ascii="Calibri Light" w:hAnsi="Calibri Light"/>
      <w:b/><w:color w:val="1F3A5F"/><w:sz w:val="36"/><w:szCs w:val="36"/>
    </w:rPr>
  </w:style>

  <w:style w:type="paragraph" w:styleId="Heading2">
    <w:name w:val="heading 2"/>
    <w:pPr><w:spacing w:before="320" w:after="120"/></w:pPr>
    <w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>
      <w:b/><w:color w:val="2E86AB"/><w:sz w:val="28"/><w:szCs w:val="28"/>
    </w:rPr>
  </w:style>

  <w:style w:type="paragraph" w:styleId="ListParagraph">
    <w:name w:val="List Paragraph"/>
    <w:pPr><w:ind w:left="720"/><w:spacing w:after="80"/></w:pPr>
  </w:style>

  <w:style w:type="table" w:styleId="TableGrid">
    <w:name w:val="Table Grid"/>
    <w:tblPr>
      <w:tblBorders>
        <w:top w:val="single" w:sz="4" w:color="AAAAAA"/>
        <w:left w:val="single" w:sz="4" w:color="AAAAAA"/>
        <w:bottom w:val="single" w:sz="4" w:color="AAAAAA"/>
        <w:right w:val="single" w:sz="4" w:color="AAAAAA"/>
        <w:insideH w:val="single" w:sz="4" w:color="AAAAAA"/>
        <w:insideV w:val="single" w:sz="4" w:color="AAAAAA"/>
      </w:tblBorders>
    </w:tblPr>
    <w:tcPr><w:tcMar>
      <w:top w:w="80" w:type="dxa"/>
      <w:left w:w="108" w:type="dxa"/>
      <w:bottom w:w="80" w:type="dxa"/>
      <w:right w:w="108" w:type="dxa"/>
    </w:tcMar></w:tcPr>
  </w:style>
</w:styles>"""


def build_document_xml(body_parts):
    body_xml = "\n".join(body_parts)
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
        ' xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">\n'
        '<w:body>\n'
        + body_xml +
        '\n<w:sectPr>'
        '<w:pgSz w:w="12240" w:h="15840"/>'
        '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"'
        ' w:header="720" w:footer="720" w:gutter="0"/>'
        '</w:sectPr>\n'
        '</w:body>\n</w:document>'
    )


def main():
    all_parts = build_body() + build_body_2() + build_body_3()
    doc_xml = build_document_xml(all_parts)

    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", CONTENT_TYPES)
        zf.writestr("_rels/.rels", RELS)
        zf.writestr("word/_rels/document.xml.rels", WORD_RELS)
        zf.writestr("word/document.xml", doc_xml)
        zf.writestr("word/styles.xml", STYLES)
        zf.writestr("word/settings.xml", SETTINGS)

    size_kb = os.path.getsize(OUT) // 1024
    print(f"[OK] Created: {OUT}  ({size_kb} KB)")


if __name__ == "__main__":
    main()
