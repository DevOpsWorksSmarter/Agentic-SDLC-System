"""Base agent with retry, error handling, and approval gate support."""

from abc import ABC, abstractmethod
from datetime import datetime, timezone

from src.models.state import Task, TaskStatus, WorkflowState


class BaseAgent(ABC):
    name: str = "base"

    def run(self, task: Task, state: WorkflowState) -> Task:
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.now(timezone.utc)
        state.log(self.name, f"Starting task: {task.name}")

        for attempt in range(task.max_retries + 1):
            try:
                task.output = self.execute(task, state)
                task.status = (
                    TaskStatus.AWAITING_APPROVAL
                    if task.requires_approval
                    else TaskStatus.COMPLETED
                )
                task.completed_at = datetime.now(timezone.utc)
                state.log(self.name, f"Completed task: {task.name}")
                return task
            except Exception as e:
                task.retry_count = attempt + 1
                task.error = str(e)
                state.log(self.name, f"Attempt {attempt + 1} failed: {e}", level="warn")
                if attempt == task.max_retries:
                    task.status = TaskStatus.FAILED
                    state.log(
                        self.name,
                        f"Task failed after {task.max_retries + 1} attempts: {task.name}",
                        level="error",
                    )
        return task

    @abstractmethod
    def execute(self, task: Task, state: WorkflowState) -> any:
        """Execute agent logic and return output."""
