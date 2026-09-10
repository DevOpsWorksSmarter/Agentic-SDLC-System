import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from app.service import UrlService
from app.models import CreateUrlRequest
from fastapi import HTTPException


@pytest_asyncio.fixture
def mock_db():
    return AsyncMock()


@pytest.mark.asyncio
async def test_shorten_returns_existing_for_duplicate_url(mock_db):
    svc = UrlService(mock_db)
    existing = MagicMock(
        id="uuid-1", code="abc1234", original="https://example.com",
        created_at=None, expires_at=None, is_active=True
    )
    svc.repo.get_by_original = AsyncMock(return_value=existing)

    req = CreateUrlRequest(url="https://example.com")
    result = await svc.shorten(req)
    assert result.code == "abc1234"
    svc.repo.create.assert_not_called()


@pytest.mark.asyncio
async def test_shorten_creates_new_url(mock_db):
    svc = UrlService(mock_db)
    svc.repo.get_by_original = AsyncMock(return_value=None)
    svc.repo.get_by_code = AsyncMock(return_value=None)
    new_record = MagicMock(
        id="uuid-2", code="xyz9999", original="https://new.com",
        created_at=None, expires_at=None, is_active=True
    )
    svc.repo.create = AsyncMock(return_value=new_record)

    with patch("app.service.cache_set", new_callable=AsyncMock):
        req = CreateUrlRequest(url="https://new.com")
        result = await svc.shorten(req)
    assert result.original_url == "https://new.com"


@pytest.mark.asyncio
async def test_resolve_raises_404_for_unknown_code(mock_db):
    svc = UrlService(mock_db)
    svc.repo.get_by_code = AsyncMock(return_value=None)
    with patch("app.service.cache_get", new_callable=AsyncMock, return_value=None):
        with pytest.raises(HTTPException) as exc:
            await svc.resolve("unknown")
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_resolve_returns_cached_url(mock_db):
    svc = UrlService(mock_db)
    with patch("app.service.cache_get", new_callable=AsyncMock, return_value="https://cached.com"):
        result = await svc.resolve("abc1234")
    assert result == "https://cached.com"


@pytest.mark.asyncio
async def test_deactivate_raises_404_for_unknown_code(mock_db):
    svc = UrlService(mock_db)
    svc.repo.deactivate = AsyncMock(return_value=False)
    with patch("app.service.cache_delete", new_callable=AsyncMock):
        with pytest.raises(HTTPException) as exc:
            await svc.deactivate("notexist")
    assert exc.value.status_code == 404
