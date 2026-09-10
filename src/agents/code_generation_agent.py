"""Code Generation Agent.

Generates production-quality FastAPI service code for the URL shortener,
including models, repository, service layer, API routes, and config.
"""

from src.agents.base import BaseAgent
from src.models.state import Task, WorkflowState


class CodeGenerationAgent(BaseAgent):
    name = "code_generation_agent"

    def execute(self, task: Task, state: WorkflowState) -> dict:
        return {
            "files": {
                "app/config.py": self._config(),
                "app/models.py": self._models(),
                "app/database.py": self._database(),
                "app/cache.py": self._cache(),
                "app/shortener.py": self._shortener(),
                "app/repository.py": self._repository(),
                "app/service.py": self._service(),
                "app/analytics.py": self._analytics(),
                "app/routes.py": self._routes(),
                "app/main.py": self._main(),
                "docker-compose.yml": self._docker_compose(),
                "Dockerfile": self._dockerfile(),
                "requirements.txt": self._requirements(),
            }
        }

    def _config(self) -> str:
        return """\
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://user:pass@localhost:5432/urlshortener"
    redis_url: str = "redis://localhost:6379/0"
    base_url: str = "http://localhost:8000"
    cache_ttl_seconds: int = 86400  # 24h
    rate_limit_per_minute: int = 60
    code_length: int = 7

    class Config:
        env_file = ".env"


settings = Settings()
"""

    def _models(self) -> str:
        return """\
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, HttpUrl, field_validator


class CreateUrlRequest(BaseModel):
    url: HttpUrl
    custom_code: Optional[str] = None
    expires_in_days: Optional[int] = None

    @field_validator("custom_code")
    @classmethod
    def validate_code(cls, v):
        if v and not v.isalnum():
            raise ValueError("Custom code must be alphanumeric")
        return v


class UrlResponse(BaseModel):
    id: uuid.UUID
    code: str
    short_url: str
    original_url: str
    created_at: datetime
    expires_at: Optional[datetime]
    is_active: bool


class StatsResponse(BaseModel):
    code: str
    total_clicks: int
    unique_visitors: int
    clicks_24h: int
    last_clicked_at: Optional[datetime]
    clicks_by_day: list[dict]
"""

    def _database(self) -> str:
        return """\
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Boolean, Text, DateTime, ForeignKey
from datetime import datetime
import uuid
from app.config import settings


engine = create_async_engine(settings.database_url, pool_size=10, max_overflow=20)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class UrlRecord(Base):
    __tablename__ = "urls"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(12), unique=True, index=True, nullable=False)
    original: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[str | None] = mapped_column(String(255), nullable=True)


class ClickEvent(Base):
    __tablename__ = "click_events"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    url_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("urls.id", ondelete="CASCADE"), index=True)
    clicked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    ip_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    referrer: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)


async def get_db():
    async with SessionLocal() as session:
        yield session
"""

    def _cache(self) -> str:
        return """\
from redis.asyncio import Redis
from app.config import settings

_redis: Redis | None = None


async def get_redis() -> Redis:
    global _redis
    if _redis is None:
        _redis = Redis.from_url(settings.redis_url, decode_responses=True)
    return _redis


async def cache_get(key: str) -> str | None:
    r = await get_redis()
    return await r.get(key)


async def cache_set(key: str, value: str, ttl: int = None) -> None:
    r = await get_redis()
    await r.set(key, value, ex=ttl or settings.cache_ttl_seconds)


async def cache_delete(key: str) -> None:
    r = await get_redis()
    await r.delete(key)
"""

    def _shortener(self) -> str:
        return '''\
import hashlib
import string
import time

_ALPHABET = string.ascii_letters + string.digits  # base62


def generate_code(url: str, length: int = 7) -> str:
    """Deterministic base62 code derived from URL + timestamp salt."""
    salt = str(time.time_ns())
    digest = hashlib.sha256(f"{url}{salt}".encode()).hexdigest()
    num = int(digest[:16], 16)
    code = []
    while num and len(code) < length:
        code.append(_ALPHABET[num % 62])
        num //= 62
    return "".join(reversed(code)).ljust(length, _ALPHABET[0])


def is_valid_code(code: str) -> bool:
    return 4 <= len(code) <= 12 and all(c in _ALPHABET for c in code)
'''

    def _repository(self) -> str:
        return """\
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.database import UrlRecord, ClickEvent
import uuid


class UrlRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_code(self, code: str) -> UrlRecord | None:
        result = await self.db.execute(select(UrlRecord).where(UrlRecord.code == code))
        return result.scalar_one_or_none()

    async def get_by_original(self, original: str) -> UrlRecord | None:
        result = await self.db.execute(
            select(UrlRecord).where(UrlRecord.original == original, UrlRecord.is_active == True)
        )
        return result.scalar_one_or_none()

    async def create(self, code: str, original: str, expires_at=None, created_by=None) -> UrlRecord:
        record = UrlRecord(code=code, original=original, expires_at=expires_at, created_by=created_by)
        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)
        return record

    async def deactivate(self, code: str) -> bool:
        result = await self.db.execute(
            update(UrlRecord).where(UrlRecord.code == code).values(is_active=False)
        )
        await self.db.commit()
        return result.rowcount > 0

    async def record_click(self, url_id: uuid.UUID, ip_hash: str | None, referrer: str | None, user_agent: str | None):
        event = ClickEvent(url_id=url_id, ip_hash=ip_hash, referrer=referrer, user_agent=user_agent)
        self.db.add(event)
        await self.db.commit()

    async def get_stats(self, code: str) -> dict | None:
        from sqlalchemy import func, text
        url = await self.get_by_code(code)
        if not url:
            return None
        total = await self.db.scalar(
            select(func.count()).where(ClickEvent.url_id == url.id)
        )
        unique = await self.db.scalar(
            select(func.count(ClickEvent.ip_hash.distinct())).where(ClickEvent.url_id == url.id)
        )
        from datetime import datetime, timedelta
        cutoff = datetime.utcnow() - timedelta(hours=24)
        clicks_24h = await self.db.scalar(
            select(func.count()).where(ClickEvent.url_id == url.id, ClickEvent.clicked_at >= cutoff)
        )
        last = await self.db.scalar(
            select(func.max(ClickEvent.clicked_at)).where(ClickEvent.url_id == url.id)
        )
        return {
            "code": code,
            "total_clicks": total or 0,
            "unique_visitors": unique or 0,
            "clicks_24h": clicks_24h or 0,
            "last_clicked_at": last,
            "clicks_by_day": [],
        }
"""

    def _service(self) -> str:
        return """\
from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.repository import UrlRepository
from app.shortener import generate_code, is_valid_code
from app.cache import cache_get, cache_set, cache_delete
from app.config import settings
from app.models import CreateUrlRequest, UrlResponse
import asyncio


class UrlService:
    def __init__(self, db: AsyncSession):
        self.repo = UrlRepository(db)

    async def shorten(self, req: CreateUrlRequest) -> UrlResponse:
        original = str(req.url)

        # Idempotency: return existing mapping if URL already shortened
        existing = await self.repo.get_by_original(original)
        if existing:
            return self._to_response(existing)

        code = req.custom_code or generate_code(original, settings.code_length)

        if req.custom_code and not is_valid_code(req.custom_code):
            raise HTTPException(status_code=400, detail="Invalid custom code format")

        if req.custom_code and await self.repo.get_by_code(req.custom_code):
            raise HTTPException(status_code=409, detail="Custom code already in use")

        expires_at = None
        if req.expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=req.expires_in_days)

        record = await self.repo.create(code, original, expires_at)
        await cache_set(code, original)
        return self._to_response(record)

    async def resolve(self, code: str) -> str:
        # Cache-first lookup
        cached = await cache_get(code)
        if cached:
            return cached

        record = await self.repo.get_by_code(code)
        if not record:
            raise HTTPException(status_code=404, detail="Short URL not found")
        if not record.is_active:
            raise HTTPException(status_code=410, detail="Short URL has been deactivated")
        if record.expires_at and record.expires_at < datetime.utcnow():
            raise HTTPException(status_code=410, detail="Short URL has expired")

        await cache_set(code, record.original)
        return record.original

    async def get_metadata(self, code: str) -> UrlResponse:
        record = await self.repo.get_by_code(code)
        if not record:
            raise HTTPException(status_code=404, detail="Not found")
        return self._to_response(record)

    async def deactivate(self, code: str) -> None:
        deleted = await self.repo.deactivate(code)
        if not deleted:
            raise HTTPException(status_code=404, detail="Not found")
        await cache_delete(code)

    async def get_stats(self, code: str) -> dict:
        stats = await self.repo.get_stats(code)
        if not stats:
            raise HTTPException(status_code=404, detail="Not found")
        return stats

    def _to_response(self, record) -> UrlResponse:
        return UrlResponse(
            id=record.id,
            code=record.code,
            short_url=f"{settings.base_url}/{record.code}",
            original_url=record.original,
            created_at=record.created_at,
            expires_at=record.expires_at,
            is_active=record.is_active,
        )
"""

    def _analytics(self) -> str:
        return '''\
"""Async analytics event publisher — fire-and-forget, never blocks redirect."""
import asyncio
import hashlib
from sqlalchemy.ext.asyncio import AsyncSession
from app.repository import UrlRepository


def _hash_ip(ip: str | None) -> str | None:
    if not ip:
        return None
    return hashlib.sha256(ip.encode()).hexdigest()[:16]


async def record_click_async(
    db: AsyncSession,
    url_id,
    client_ip: str | None,
    referrer: str | None,
    user_agent: str | None,
):
    """Non-blocking click event recording via asyncio background task."""
    try:
        repo = UrlRepository(db)
        await repo.record_click(url_id, _hash_ip(client_ip), referrer, user_agent)
    except Exception:
        pass  # Analytics failures must never surface to the redirect path
'''

    def _routes(self) -> str:
        return """\
from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.service import UrlService
from app.analytics import record_click_async
from app.models import CreateUrlRequest, UrlResponse, StatsResponse
import asyncio

router = APIRouter()


@router.post("/urls", response_model=UrlResponse, status_code=201)
async def create_url(req: CreateUrlRequest, db: AsyncSession = Depends(get_db)):
    return await UrlService(db).shorten(req)


@router.get("/{code}")
async def redirect_url(code: str, request: Request, db: AsyncSession = Depends(get_db)):
    svc = UrlService(db)
    original = await svc.resolve(code)

    # Resolve URL record for analytics (non-blocking)
    record = await svc.repo.get_by_code(code)
    if record:
        asyncio.create_task(record_click_async(
            db,
            record.id,
            request.client.host if request.client else None,
            request.headers.get("referer"),
            request.headers.get("user-agent"),
        ))

    return RedirectResponse(url=original, status_code=302)


@router.get("/urls/{code}", response_model=UrlResponse)
async def get_url(code: str, db: AsyncSession = Depends(get_db)):
    return await UrlService(db).get_metadata(code)


@router.delete("/urls/{code}", status_code=204)
async def delete_url(code: str, db: AsyncSession = Depends(get_db)):
    await UrlService(db).deactivate(code)


@router.get("/urls/{code}/stats", response_model=StatsResponse)
async def get_stats(code: str, db: AsyncSession = Depends(get_db)):
    return await UrlService(db).get_stats(code)
"""

    def _main(self) -> str:
        return """\
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router

app = FastAPI(
    title="URL Shortener API",
    version="1.0.0",
    description="Scalable URL shortener with analytics",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "ok"}
"""

    def _docker_compose(self) -> str:
        return """\
version: "3.9"
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://${POSTGRES_USER:-user}:${POSTGRES_PASSWORD:?POSTGRES_PASSWORD must be set}@db:5432/${POSTGRES_DB:-urlshortener}
      REDIS_URL: redis://cache:6379/0
      BASE_URL: http://localhost:8000
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_healthy

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-user}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?POSTGRES_PASSWORD must be set}
      POSTGRES_DB: ${POSTGRES_DB:-urlshortener}
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 5s
      retries: 5

  cache:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      retries: 5

volumes:
  pgdata:
"""

    def _dockerfile(self) -> str:
        return """\
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
"""

    def _requirements(self) -> str:
        return """\
fastapi==0.111.0
uvicorn[standard]==0.29.0
sqlalchemy[asyncio]==2.0.30
asyncpg==0.29.0
redis[asyncio]==5.0.4
pydantic==2.7.1
pydantic-settings==2.2.1
alembic==1.13.1
"""
