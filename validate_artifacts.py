"""Validate artifacts from the latest workflow run in outputs_e2e/."""
import os
import json
import sys

# Auto-discover latest run directory
base = "outputs_e2e"
runs = sorted([d for d in os.listdir(base) if d.startswith("run_")])
assert runs, f"No run directories found in {base}/"
run_dir = os.path.join(base, runs[-1])
print(f"Validating: {run_dir}\n")

with open(f"{run_dir}/workflow_summary.json") as f:
    s = json.load(f)
assert s["scenario"] == "greenfield"
assert s["validation"]["passed"] is True
failed = [t for t in s["tasks"] if t["status"] == "failed"]
assert not failed, f"failed tasks: {failed}"
print(f"[OK] workflow_summary: {len(s['tasks'])} tasks, validation={s['validation']['passed']}")

with open(f"{run_dir}/execution_log.json") as f:
    log = json.load(f)
assert len(log) > 0
print(f"[OK] execution_log: {len(log)} entries")

code_dir = f"{run_dir}/code_generation/app"
for fname in ["main.py", "service.py", "routes.py", "models.py", "repository.py",
              "database.py", "cache.py", "shortener.py", "analytics.py", "config.py"]:
    assert os.path.exists(f"{code_dir}/{fname}"), f"missing {fname}"
print("[OK] code_generation: all 10 app files present")

for fname in ["Dockerfile", "docker-compose.yml", "requirements.txt"]:
    assert os.path.exists(f"{run_dir}/code_generation/{fname}"), f"missing {fname}"
print("[OK] docker artifacts: Dockerfile, docker-compose.yml, requirements.txt")

test_dir = f"{run_dir}/test_generation/tests"
for fpath in ["conftest.py", "unit/test_shortener.py", "unit/test_service.py",
              "integration/test_api.py", "integration/test_analytics.py"]:
    assert os.path.exists(f"{test_dir}/{fpath}"), f"missing test: {fpath}"
print("[OK] test_generation: all 5 test files present")

doc_dir = f"{run_dir}/documentation"
for fname in ["README.md", "ENGINEERING_SUMMARY.md", "RUNBOOK.md"]:
    assert os.path.exists(f"{doc_dir}/{fname}"), f"missing doc: {fname}"
print("[OK] documentation: README.md, ENGINEERING_SUMMARY.md, RUNBOOK.md")

assert os.path.exists(f"{run_dir}/schema_design/output.json")
assert os.path.exists(f"{run_dir}/architecture_design/output.json")
assert os.path.exists(f"{run_dir}/analytics_design/output.json")
print("[OK] schema_design, architecture_design, analytics_design present")

assert len(s["risks"]) == 6
print(f"[OK] risks: {len(s['risks'])} identified")

first = log[0]
for key in ["timestamp", "phase", "level", "message"]:
    assert key in first, f"missing log key: {key}"
print("[OK] structured log format valid")

print("\nAll artifact validations PASSED.")
