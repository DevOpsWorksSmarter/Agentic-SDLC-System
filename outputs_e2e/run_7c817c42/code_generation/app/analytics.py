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
