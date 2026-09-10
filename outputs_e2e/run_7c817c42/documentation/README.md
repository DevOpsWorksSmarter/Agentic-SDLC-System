# URL Shortener Service

> [GREENFIELD] Build a scalable URL shortener service with APIs, persistence, and analytics. — Normalized: Design and implement a production-ready system addressing the stated requirement with clear API contracts, persistence layer, test coverage, and operational documentation.

## Quick Start

```bash
# Clone and start
docker-compose up --build

# Create a short URL
curl -X POST http://localhost:8000/urls \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.example.com/very/long/path"}'

# Redirect
curl -L http://localhost:8000/{code}

# Get stats
curl http://localhost:8000/urls/{code}/stats
```

## Architecture

```
Client → [Nginx] → [FastAPI Service] → [Redis Cache]
                                     ↘ [PostgreSQL]
                                     ↘ [Analytics Worker]
```

## API Reference

| Method | Path | Description |
|--------|------|-------------|
| POST | /urls | Create short URL |
| GET | /{code} | Redirect to original |
| GET | /urls/{code} | Get URL metadata |
| DELETE | /urls/{code} | Deactivate URL |
| GET | /urls/{code}/stats | Get click analytics |

## Running Tests

```bash
pip install pytest pytest-asyncio httpx aiosqlite
pytest tests/ -v --tb=short
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| DATABASE_URL | postgresql+asyncpg://... | PostgreSQL connection |
| REDIS_URL | redis://localhost:6379/0 | Redis connection |
| BASE_URL | http://localhost:8000 | Public base URL for short links |
| CACHE_TTL_SECONDS | 86400 | Redis TTL (24h) |
| RATE_LIMIT_PER_MINUTE | 60 | Requests per IP per minute |
