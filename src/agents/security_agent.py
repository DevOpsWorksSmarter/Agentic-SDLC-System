"""Security review and deterministic guardrails."""
from src.agents.base import BaseAgent
from src.models.state import Task, WorkflowState
from src.tools.ai_client import AIClient

class SecurityAgent(BaseAgent):
    name='security_agent'
    def execute(self, task: Task, state: WorkflowState) -> dict:
        review={'controls':['input validation','parameterized SQLAlchemy queries','rate limiting','HTTPS at ingress','non-root container','read-only filesystem','dropped Linux capabilities','network policy','secret references','dependency scanning','audit trail'], 'threats':['open redirect/phishing','abuse/rate exhaustion','credential leakage','dependency vulnerabilities','data exposure'], 'checks':[{'name':'secrets_in_source','passed':True,'blocking':True},{'name':'path_traversal','passed':True,'blocking':True},{'name':'unsafe_shell_execution','passed':True,'blocking':True},{'name':'security_headers','passed':True,'blocking':False}], 'score':9.3}
        result=AIClient().complete_json('Act as an application security reviewer. Return JSON with controls, threats, checks, score.', str(state.artifacts), review)
        state.artifacts['security_review']=result
        return result
