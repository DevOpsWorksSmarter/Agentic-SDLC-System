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
