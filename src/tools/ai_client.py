"""Optional structured LLM adapter with deterministic offline fallback."""
import json
import os
import urllib.request


class AIClient:
    def __init__(self):
        self.base_url = os.getenv("AI_BASE_URL", "").rstrip("/")
        self.api_key = os.getenv("AI_API_KEY", "")
        self.model = os.getenv("AI_MODEL", "gpt-4o-mini")
        self.enabled = bool(self.base_url and self.api_key)

    def complete_json(self, system: str, user: str, fallback: dict) -> dict:
        if not self.enabled:
            return fallback
        payload = json.dumps(
            {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "temperature": 0,
                "response_format": {"type": "json_object"},
            }
        ).encode()
        req = urllib.request.Request(
            self.base_url + "/chat/completions",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                body = json.loads(r.read().decode())
            return json.loads(body["choices"][0]["message"]["content"])
        except Exception:
            return fallback
