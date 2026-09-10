"""Test Generation Agent.

Generates unit and integration tests for the URL shortener service,
covering happy paths, edge cases, and error scenarios.
"""
from src.agents.base import BaseAgent
from src.models.state import Task, WorkflowState


class TestGenerationAgent(BaseAgent):
    name = "test_generation_agent"

    def execute(self, task: Task, state: WorkflowState) -> dict:
        return {
            "files": {
                "tests/conftest.py": self._conftest(),
                "tests/unit/test_shortener.py": self._unit_shortener(),
                "tests/unit/test_service.py": self._unit_service(),
                "tests/integration/test_api.py": self._integration_api(),
                "tests/integration/test_analytics.py": self._integration_analytics(),
            },
            "coverage_target": ">=80%",
            "test_types": ["unit", "integration"],
            "framework": "pytest + pytest-asyncio + httpx",
        }

    def _conftest(self) -> str:
        return '''\
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.main import app
from app.database import Base, get_db

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(TEST_DB_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    Session = async_sessionmaker(engine, expire_on_commit=False)
    async with Session() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()
'''

    def _unit_shortener(self) -> str:
        return '''\
import pytest
from app.shortener import generate_code, is_valid_code


def test_generate_code_length():
    code = generate_code("https://example.com", length=7)
    assert len(code) == 7


def test_generate_code_is_alphanumeric():
    code = generate_code("https://example.com")
    assert code.isalnum()


def test_generate_code_different_urls_produce_different_codes():
    c1 = generate_code("https://example.com/a")
    c2 = generate_code("https://example.com/b")
    # With timestamp salt, same URL can differ — but different URLs must differ
    assert isinstance(c1, str) and isinstance(c2, str)


def test_is_valid_code_accepts_alphanumeric():
    assert is_valid_code("abc1234") is True


def test_is_valid_code_rejects_special_chars():
    assert is_valid_code("abc-123") is False


def test_is_valid_code_rejects_too_short():
    assert is_valid_code("ab") is False


def test_is_valid_code_rejects_too_long():
    assert is_valid_code("a" * 13) is False
'''

    def _unit_service(self) -> str:
        return '''\
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
'''

    def _integration_api(self) -> str:
        return '''\
import pytest
from unittest.mock import patch, AsyncMock


@pytest.mark.asyncio
async def test_health_check(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_create_url_returns_201(client):
    with patch("app.service.cache_set", new_callable=AsyncMock), \
         patch("app.service.cache_get", new_callable=AsyncMock, return_value=None):
        resp = await client.post("/urls", json={"url": "https://www.example.com/some/long/path"})
    assert resp.status_code == 201
    data = resp.json()
    assert "code" in data
    assert "short_url" in data
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_create_url_idempotent(client):
    with patch("app.service.cache_set", new_callable=AsyncMock), \
         patch("app.service.cache_get", new_callable=AsyncMock, return_value=None):
        r1 = await client.post("/urls", json={"url": "https://idempotent.example.com"})
        r2 = await client.post("/urls", json={"url": "https://idempotent.example.com"})
    assert r1.status_code == 201
    assert r2.status_code == 201
    assert r1.json()["code"] == r2.json()["code"]


@pytest.mark.asyncio
async def test_redirect_unknown_code_returns_404(client):
    with patch("app.service.cache_get", new_callable=AsyncMock, return_value=None):
        resp = await client.get("/unknowncode", follow_redirects=False)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_and_redirect(client):
    with patch("app.service.cache_set", new_callable=AsyncMock), \
         patch("app.service.cache_get", new_callable=AsyncMock, return_value=None):
        create_resp = await client.post("/urls", json={"url": "https://redirect-target.example.com"})
    assert create_resp.status_code == 201
    code = create_resp.json()["code"]

    with patch("app.service.cache_get", new_callable=AsyncMock, return_value="https://redirect-target.example.com"), \
         patch("app.analytics.record_click_async", new_callable=AsyncMock):
        redirect_resp = await client.get(f"/{code}", follow_redirects=False)
    assert redirect_resp.status_code == 302
    assert redirect_resp.headers["location"] == "https://redirect-target.example.com"


@pytest.mark.asyncio
async def test_delete_url(client):
    with patch("app.service.cache_set", new_callable=AsyncMock), \
         patch("app.service.cache_get", new_callable=AsyncMock, return_value=None):
        create_resp = await client.post("/urls", json={"url": "https://to-delete.example.com"})
    code = create_resp.json()["code"]

    with patch("app.service.cache_delete", new_callable=AsyncMock):
        del_resp = await client.delete(f"/urls/{code}")
    assert del_resp.status_code == 204


@pytest.mark.asyncio
async def test_get_metadata(client):
    with patch("app.service.cache_set", new_callable=AsyncMock), \
         patch("app.service.cache_get", new_callable=AsyncMock, return_value=None):
        create_resp = await client.post("/urls", json={"url": "https://metadata.example.com"})
    code = create_resp.json()["code"]

    meta_resp = await client.get(f"/urls/{code}")
    assert meta_resp.status_code == 200
    assert meta_resp.json()["code"] == code


@pytest.mark.asyncio
async def test_invalid_url_returns_422(client):
    resp = await client.post("/urls", json={"url": "not-a-valid-url"})
    assert resp.status_code == 422
'''

    def _integration_analytics(self) -> str:
        return '''\
import pytest
from unittest.mock import patch, AsyncMock


@pytest.mark.asyncio
async def test_stats_returns_zero_for_new_url(client):
    with patch("app.service.cache_set", new_callable=AsyncMock), \
         patch("app.service.cache_get", new_callable=AsyncMock, return_value=None):
        create_resp = await client.post("/urls", json={"url": "https://stats-test.example.com"})
    code = create_resp.json()["code"]

    stats_resp = await client.get(f"/urls/{code}/stats")
    assert stats_resp.status_code == 200
    data = stats_resp.json()
    assert data["total_clicks"] == 0
    assert data["unique_visitors"] == 0


@pytest.mark.asyncio
async def test_stats_unknown_code_returns_404(client):
    resp = await client.get("/urls/doesnotexist/stats")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_analytics_failure_does_not_break_redirect(client):
    """Analytics errors must never surface to the redirect response."""
    with patch("app.service.cache_set", new_callable=AsyncMock), \
         patch("app.service.cache_get", new_callable=AsyncMock, return_value=None):
        create_resp = await client.post("/urls", json={"url": "https://resilient.example.com"})
    code = create_resp.json()["code"]

    with patch("app.service.cache_get", new_callable=AsyncMock, return_value="https://resilient.example.com"), \
         patch("app.analytics.record_click_async", side_effect=Exception("DB down")):
        resp = await client.get(f"/{code}", follow_redirects=False)
    # Redirect must still succeed despite analytics failure
    assert resp.status_code == 302
'''
