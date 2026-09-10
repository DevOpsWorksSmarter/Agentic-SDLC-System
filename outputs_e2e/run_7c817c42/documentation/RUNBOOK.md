# Operational Runbook — URL Shortener Service

## Health Check
```bash
curl http://localhost:8000/health
# Expected: {"status": "ok"}
```

## Scaling
```bash
# Scale API replicas (Docker Compose)
docker-compose up --scale api=3

# Production: update ECS desired count or Kubernetes replicas
```

## Cache Management
```bash
# Flush Redis cache (use with caution)
redis-cli FLUSHDB

# Inspect a specific key
redis-cli GET <code>
```

## Database Maintenance
```bash
# Refresh analytics materialized view
psql -c "REFRESH MATERIALIZED VIEW CONCURRENTLY url_stats;"

# Purge expired URLs (run as scheduled job)
psql -c "UPDATE urls SET is_active=false WHERE expires_at < NOW() AND is_active=true;"
```

## Incident Response

| Symptom | Likely Cause | Action |
|---------|-------------|--------|
| Redirects slow (>200ms) | Redis cache miss / cold start | Check Redis connectivity; warm cache |
| 500 on POST /urls | DB connection pool exhausted | Check DB connections; scale pool |
| Analytics not updating | Worker crash | Restart analytics worker; check queue depth |
| High 404 rate | Cache eviction + DB miss | Investigate code generation collision |

## Rollback
```bash
# Docker Compose rollback
docker-compose down && docker-compose up --build

# Database rollback (Alembic)
alembic downgrade -1
```
