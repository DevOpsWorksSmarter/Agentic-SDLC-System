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
