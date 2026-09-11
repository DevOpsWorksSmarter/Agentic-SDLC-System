"""Deterministic final release gate. AI reviews advise; policy decides."""
from src.agents.base import BaseAgent
from src.agents.repair_agent import RepairAgent
from src.models.state import Task, WorkflowState

class ReleaseGateAgent(BaseAgent):
    name='release_gate_agent'
    def execute(self, task: Task, state: WorkflowState) -> dict:
        checks=[]
        for key,label in [('architecture_design','architecture'),('schema_design','api/schema'),('code_generation','code'),('test_generation','tests'),('validation','validation'),('security_review','security'),('sre_review','sre'),('engineering_review','engineering')]:
            checks.append({'name':label,'passed':key in state.artifacts,'blocking':True})
        failures=[c for c in checks if not c['passed']]
        decision='release' if not failures else 'blocked'
        result={'decision':decision,'checks':checks,'failures':failures,'human_approval_required':True,'policy':'No release when a blocking evidence artifact is missing.'}
        state.artifacts['release_gate']=result
        return result
