"""Core state models for the Agentic SDLC System."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
import uuid
from datetime import datetime, timezone


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ScenarioType(Enum):
    GREENFIELD = "greenfield"
    BROWNFIELD = "brownfield"
    AMBIGUOUS = "ambiguous"


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Ambiguity:
    question: str
    resolution: Optional[str] = None
    resolved: bool = False


@dataclass
class Requirement:
    raw: str
    normalized: str = ""
    intent: str = ""
    scenario_type: ScenarioType = ScenarioType.GREENFIELD
    ambiguities: list[Ambiguity] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    success_criteria: list[str] = field(default_factory=list)


@dataclass
class Task:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    agent: str = ""
    depends_on: list[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    output: Any = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 2
    requires_approval: bool = False
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class Risk:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    description: str = ""
    level: RiskLevel = RiskLevel.MEDIUM
    mitigation: str = ""
    tradeoff: str = ""


@dataclass
class ValidationResult:
    passed: bool = True
    checks: list[dict] = field(default_factory=list)
    coverage_estimate: str = ""
    test_strategy: str = ""


@dataclass
class WorkflowState:
    """Central state object passed through the entire workflow."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    requirement: Optional[Requirement] = None
    tasks: list[Task] = field(default_factory=list)
    artifacts: dict[str, Any] = field(default_factory=dict)
    risks: list[Risk] = field(default_factory=list)
    validation: Optional[ValidationResult] = None
    execution_log: list[dict] = field(default_factory=list)
    current_phase: str = "init"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def get_task(self, task_id: str) -> Optional[Task]:
        return next((t for t in self.tasks if t.id == task_id), None)

    def get_task_by_name(self, name: str) -> Optional[Task]:
        return next((t for t in self.tasks if t.name == name), None)

    def log(self, phase: str, message: str, level: str = "info"):
        self.execution_log.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "phase": phase,
            "level": level,
            "message": message
        })
