# Agentic SDLC System — V7 Assignment Compliance

## Objective
A working multi-agent prototype transforms a software requirement into a reviewable engineering outcome across the SDLC. It is explicitly designed around the assignment's URL-shortener use case and greenfield, brownfield, and ambiguous requirements.

## Requirement-to-implementation matrix
| Assignment requirement | V7 implementation | Evidence |
|---|---|---|
| Understand requirements | RequirementAgent + AIReasoningAgent | normalized intent, assumptions, acceptance criteria |
| Detect ambiguity | ambiguity signals + explicit resolutions | workflow artifacts |
| Decompose work | dependency-aware DecompositionAgent | task graph with dependencies |
| Multi-step orchestration | WorkflowOrchestrator | dependency scheduling, cross-step shared state |
| Error handling/recovery | retries, failure propagation, bounded RepairAgent | execution log + repair_result |
| Greenfield | URL shortener plan | architecture/schema/code/tests/docs |
| Brownfield | codebase analysis + impact assessment | impacted files/data flow/risk |
| Test improvements | unit/integration/resilience strategy | test_generation artifact |
| Production code | FastAPI layered service | generated code package |
| API/schema | OpenAPI + DB schema | schema_design artifact |
| Validation/risk | ValidationAgent + deterministic checks | validation artifact |
| Controlled autonomy | approval gates + release gate | approval decisions + policy |
| Security | SecurityAgent + deterministic guardrails | security_review artifact |
| SRE | SREAgent with SLO/capacity/resilience/observability | sre_review artifact |
| Final output | documentation + evidence chain | ENGINEERING_SUMMARY/RUNBOOK/audit log |

## AI design
The AI layer is optional and production-oriented: set `AI_BASE_URL`, `AI_API_KEY`, and `AI_MODEL` to enable an OpenAI-compatible structured JSON endpoint. Without credentials, deterministic fallbacks keep evaluation reproducible and offline. AI output is advisory and schema-constrained; policy gates remain deterministic.

## SRE design
The SRE review explicitly covers 99.9% availability, p99 latency targets, 10k RPS capacity target, HA PostgreSQL, cache degradation, analytics isolation, resilience tests, metrics, structured logs, traces and operational runbooks.

## Controlled autonomy
Agents can reason and produce artifacts independently, but architecture/code/validation/security/SRE/final engineering decisions are approval-gated. The deterministic release gate blocks release if required evidence is missing.

## Verification
The repository's system test suite passes with 26 tests. The mandatory URL-shortener scenario completes end-to-end with architecture, schema, analytics, code, tests, validation, security, SRE, engineering review, release gate and documentation artifacts.
