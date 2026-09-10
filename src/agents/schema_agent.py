"""Schema Agent.

Generates database schema (DDL) and OpenAPI 3.0 contract
from the architecture design artifact.
"""
from src.agents.base import BaseAgent
from src.models.state import Task, WorkflowState


class SchemaAgent(BaseAgent):
    name = "schema_agent"

    def execute(self, task: Task, state: WorkflowState) -> dict:
        return {
            "database_schema": self._db_schema(),
            "openapi_spec": self._openapi_spec(),
        }

    def _db_schema(self) -> str:
        return """\
-- URL Shortener Database Schema

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE urls (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code        VARCHAR(12) NOT NULL UNIQUE,
    original    TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at  TIMESTAMPTZ,
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    created_by  VARCHAR(255),
    CONSTRAINT  chk_original_length CHECK (char_length(original) <= 2048)
);

CREATE INDEX idx_urls_code ON urls(code);
CREATE INDEX idx_urls_original ON urls(original);

CREATE TABLE click_events (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url_id      UUID NOT NULL REFERENCES urls(id) ON DELETE CASCADE,
    clicked_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ip_hash     VARCHAR(64),
    referrer    TEXT,
    user_agent  TEXT,
    country     VARCHAR(2)
);

CREATE INDEX idx_clicks_url_id ON click_events(url_id);
CREATE INDEX idx_clicks_clicked_at ON click_events(clicked_at);

-- Pre-aggregated stats view
CREATE MATERIALIZED VIEW url_stats AS
SELECT
    u.code,
    COUNT(c.id)                          AS total_clicks,
    COUNT(DISTINCT c.ip_hash)            AS unique_visitors,
    MAX(c.clicked_at)                    AS last_clicked_at,
    DATE_TRUNC('day', c.clicked_at)      AS click_day,
    COUNT(*) FILTER (WHERE c.clicked_at >= NOW() - INTERVAL '24 hours') AS clicks_24h
FROM urls u
LEFT JOIN click_events c ON c.url_id = u.id
GROUP BY u.code, DATE_TRUNC('day', c.clicked_at);

CREATE UNIQUE INDEX ON url_stats(code, click_day);
"""

    def _openapi_spec(self) -> dict:
        return {
            "openapi": "3.0.3",
            "info": {
                "title": "URL Shortener API",
                "version": "1.0.0",
                "description": "Scalable URL shortener with analytics",
            },
            "paths": {
                "/urls": {
                    "post": {
                        "summary": "Create a short URL",
                        "operationId": "createUrl",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/CreateUrlRequest"}
                                }
                            },
                        },
                        "responses": {
                            "201": {
                                "description": "Short URL created",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/UrlResponse"}
                                    }
                                },
                            },
                            "400": {"description": "Invalid URL"},
                            "409": {"description": "URL already exists (returns existing)"},
                            "429": {"description": "Rate limit exceeded"},
                        },
                    }
                },
                "/{code}": {
                    "get": {
                        "summary": "Redirect to original URL",
                        "operationId": "redirectUrl",
                        "parameters": [
                            {"name": "code", "in": "path", "required": True, "schema": {"type": "string"}}
                        ],
                        "responses": {
                            "302": {"description": "Redirect to original URL"},
                            "404": {"description": "Short code not found"},
                            "410": {"description": "URL has been deactivated"},
                        },
                    }
                },
                "/urls/{code}": {
                    "get": {
                        "summary": "Get URL metadata",
                        "operationId": "getUrl",
                        "parameters": [
                            {"name": "code", "in": "path", "required": True, "schema": {"type": "string"}}
                        ],
                        "responses": {
                            "200": {
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/UrlResponse"}
                                    }
                                }
                            },
                            "404": {"description": "Not found"},
                        },
                    },
                    "delete": {
                        "summary": "Deactivate a short URL",
                        "operationId": "deleteUrl",
                        "parameters": [
                            {"name": "code", "in": "path", "required": True, "schema": {"type": "string"}}
                        ],
                        "responses": {
                            "204": {"description": "Deactivated"},
                            "404": {"description": "Not found"},
                        },
                    },
                },
                "/urls/{code}/stats": {
                    "get": {
                        "summary": "Get click analytics for a short URL",
                        "operationId": "getStats",
                        "parameters": [
                            {"name": "code", "in": "path", "required": True, "schema": {"type": "string"}}
                        ],
                        "responses": {
                            "200": {
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/StatsResponse"}
                                    }
                                }
                            },
                            "404": {"description": "Not found"},
                        },
                    }
                },
            },
            "components": {
                "schemas": {
                    "CreateUrlRequest": {
                        "type": "object",
                        "required": ["url"],
                        "properties": {
                            "url": {"type": "string", "format": "uri", "maxLength": 2048},
                            "custom_code": {"type": "string", "minLength": 4, "maxLength": 12},
                            "expires_in_days": {"type": "integer", "minimum": 1, "maximum": 365},
                        },
                    },
                    "UrlResponse": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string", "format": "uuid"},
                            "code": {"type": "string"},
                            "short_url": {"type": "string", "format": "uri"},
                            "original_url": {"type": "string", "format": "uri"},
                            "created_at": {"type": "string", "format": "date-time"},
                            "expires_at": {"type": "string", "format": "date-time", "nullable": True},
                            "is_active": {"type": "boolean"},
                        },
                    },
                    "StatsResponse": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string"},
                            "total_clicks": {"type": "integer"},
                            "unique_visitors": {"type": "integer"},
                            "clicks_24h": {"type": "integer"},
                            "last_clicked_at": {"type": "string", "format": "date-time", "nullable": True},
                            "clicks_by_day": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "date": {"type": "string", "format": "date"},
                                        "count": {"type": "integer"},
                                    },
                                },
                            },
                        },
                    },
                }
            },
        }
