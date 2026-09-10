"""Architecture Agent.

Produces a structured architecture design including components,
data flows, API surface, and infrastructure topology.
"""
from src.agents.base import BaseAgent
from src.models.state import Task, WorkflowState


class ArchitectureAgent(BaseAgent):
    name = "architecture_agent"

    def execute(self, task: Task, state: WorkflowState) -> dict:
        req = state.requirement
        raw = req.raw.lower()

        if task.name == "analytics_design":
            return self._analytics_architecture()

        return self._core_architecture(raw)

    def _core_architecture(self, raw: str) -> dict:
        return {
            "system_name": "URL Shortener Service",
            "pattern": "Layered REST API with cache-aside and async event pipeline",
            "components": {
                "api_gateway": {
                    "role": "Entry point — rate limiting, TLS termination, routing",
                    "technology": "Nginx / AWS API Gateway",
                },
                "url_service": {
                    "role": "Core business logic — shorten, resolve, validate URLs",
                    "technology": "Python FastAPI (stateless, horizontally scalable)",
                    "endpoints": [
                        "POST /urls          → create short URL",
                        "GET  /{code}        → redirect to original URL",
                        "GET  /urls/{code}   → get URL metadata",
                        "DELETE /urls/{code} → deactivate URL",
                        "GET  /urls/{code}/stats → get click analytics",
                    ],
                },
                "cache": {
                    "role": "Hot-path lookup cache — code → original_url mapping",
                    "technology": "Redis (TTL-based eviction, 24h default)",
                    "strategy": "Cache-aside: read cache first, fallback to DB, populate on miss",
                },
                "database": {
                    "role": "Durable store for URL records and analytics events",
                    "technology": "PostgreSQL",
                    "tables": ["urls", "click_events"],
                },
                "analytics_worker": {
                    "role": "Async consumer of click events — aggregates stats",
                    "technology": "Background task queue (asyncio / Celery)",
                    "pattern": "Fire-and-forget publish on redirect; worker persists to DB",
                },
            },
            "data_flow": {
                "shorten": [
                    "Client → POST /urls",
                    "Validate URL format and length",
                    "Check DB for existing mapping (idempotency)",
                    "Generate unique 7-char base62 code",
                    "Persist to PostgreSQL",
                    "Populate Redis cache",
                    "Return short URL",
                ],
                "redirect": [
                    "Client → GET /{code}",
                    "Lookup code in Redis (cache hit → 302 redirect, ~1ms)",
                    "On cache miss → lookup PostgreSQL → populate Redis → 302 redirect",
                    "Publish click event to async queue (non-blocking)",
                    "Return 404 if code not found",
                ],
            },
            "scalability": {
                "stateless_api": "Multiple API replicas behind load balancer",
                "cache_layer": "Redis reduces DB load by ~95% for hot URLs",
                "db_scaling": "Read replicas for analytics queries; primary for writes",
                "async_analytics": "Decoupled from redirect path — no latency impact",
            },
            "infrastructure": {
                "containerization": "Docker + Docker Compose (local); Kubernetes (production)",
                "deployment": "AWS ECS Fargate or EKS",
                "database": "AWS RDS PostgreSQL (Multi-AZ)",
                "cache": "AWS ElastiCache Redis",
                "monitoring": "Prometheus + Grafana; structured JSON logs",
            },
        }

    def _analytics_architecture(self) -> dict:
        return {
            "pattern": "Async event-driven analytics pipeline",
            "components": {
                "event_publisher": {
                    "role": "Publishes click events on each redirect (fire-and-forget)",
                    "implementation": "asyncio background task or Redis pub/sub",
                },
                "event_consumer": {
                    "role": "Consumes events and persists to click_events table",
                    "implementation": "Celery worker or asyncio consumer loop",
                },
                "aggregation": {
                    "role": "Pre-aggregated stats via DB views or scheduled rollup",
                    "metrics": ["total_clicks", "unique_visitors", "clicks_by_day", "top_referrers"],
                },
            },
            "guarantees": "At-least-once delivery; idempotent event writes via event_id dedup",
            "isolation": "Analytics failures do not affect redirect availability",
        }
