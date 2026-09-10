"""Codebase Reasoning Agent (Brownfield).

Analyzes an existing codebase to identify impacted modules, APIs,
data flows, and change surface for brownfield requirements.
"""

import os

from src.agents.base import BaseAgent
from src.models.state import Task, WorkflowState

_SKIP_DIRS = {"__pycache__", "node_modules", ".git", "venv", ".venv"}


class CodebaseReasoningAgent(BaseAgent):
    name = "codebase_reasoning_agent"

    def execute(self, task: Task, state: WorkflowState) -> dict:
        raw_path = state.artifacts.get("codebase_path", ".")
        # Resolve and validate the codebase path before any file access
        codebase_path = os.path.realpath(raw_path)
        if not os.path.isdir(codebase_path):
            return {"error": f"Codebase path is not a directory: {codebase_path}"}
        return self._analyze(codebase_path, state.requirement.raw)

    def _analyze(self, base: str, requirement: str) -> dict:
        file_map = self._scan_files(base)
        impacted = self._identify_impacted(file_map, requirement)
        return {
            "scanned_files": len(file_map),
            "file_map": file_map,
            "impacted_modules": impacted,
            "change_surface": self._estimate_change_surface(impacted),
            "breaking_change_risk": self._assess_breaking_risk(impacted),
            "migration_needed": self._needs_migration(requirement),
            "recommendations": self._recommendations(impacted, requirement),
        }

    def _scan_files(self, base: str) -> dict:
        file_map = {}
        for root, dirs, files in os.walk(base):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in _SKIP_DIRS]
            for f in files:
                if not f.endswith((".py", ".yaml", ".yml", ".json", ".sql")):
                    continue
                abs_path = os.path.realpath(os.path.join(root, f))
                # Confine to base directory — skip symlinks that escape
                if not abs_path.startswith(base + os.sep) and abs_path != base:
                    continue
                rel = os.path.relpath(abs_path, base)
                file_map[rel] = self._summarize_file(abs_path)
        return file_map

    def _summarize_file(self, filepath: str) -> dict:
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as fh:
                lines = fh.readlines()
            classes = [ln.strip() for ln in lines if ln.strip().startswith("class ")]
            functions = [
                ln.strip()
                for ln in lines
                if ln.strip().startswith("def ") or ln.strip().startswith("async def ")
            ]
            return {
                "lines": len(lines),
                "classes": classes[:10],
                "functions": functions[:20],
            }
        except Exception:
            return {"lines": 0, "classes": [], "functions": []}

    def _identify_impacted(self, file_map: dict, requirement: str) -> list[dict]:
        keywords = requirement.lower().split()
        impacted = []
        for filepath, summary in file_map.items():
            score = sum(1 for kw in keywords if kw in filepath.lower())
            score += sum(
                1
                for fn in summary.get("functions", [])
                if any(kw in fn.lower() for kw in keywords)
            )
            if score > 0:
                impacted.append(
                    {
                        "file": filepath,
                        "relevance_score": score,
                        "functions": summary.get("functions", []),
                        "classes": summary.get("classes", []),
                    }
                )
        return sorted(impacted, key=lambda x: x["relevance_score"], reverse=True)[:10]

    def _estimate_change_surface(self, impacted: list) -> str:
        n = len(impacted)
        if n == 0:
            return "minimal"
        if n <= 3:
            return "small (1-3 files)"
        if n <= 7:
            return "medium (4-7 files)"
        return "large (8+ files)"

    def _assess_breaking_risk(self, impacted: list) -> str:
        api_files = [m for m in impacted if "route" in m["file"] or "api" in m["file"]]
        schema_files = [
            m for m in impacted if "model" in m["file"] or "schema" in m["file"]
        ]
        if api_files or schema_files:
            return "HIGH — API or schema changes detected; review for breaking changes"
        return "LOW — Internal implementation changes only"

    def _needs_migration(self, requirement: str) -> bool:
        signals = {"schema", "database", "column", "table", "migrate", "rename", "drop"}
        return any(kw in requirement.lower() for kw in signals)

    def _recommendations(self, impacted: list, requirement: str) -> list[str]:
        recs = [
            "Run full regression test suite before and after changes",
            "Review impacted API contracts for backward compatibility",
        ]
        if self._needs_migration(requirement):
            recs.append("Create Alembic migration script; test rollback procedure")
        if len(impacted) > 5:
            recs.append("Consider feature flag to gate changes in production")
        return recs
