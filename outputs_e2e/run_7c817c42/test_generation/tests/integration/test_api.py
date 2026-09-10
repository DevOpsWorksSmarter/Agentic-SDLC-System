import pytest
from unittest.mock import patch, AsyncMock


@pytest.mark.asyncio
async def test_health_check(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_create_url_returns_201(client):
    with patch("app.service.cache_set", new_callable=AsyncMock),          patch("app.service.cache_get", new_callable=AsyncMock, return_value=None):
        resp = await client.post("/urls", json={"url": "https://www.example.com/some/long/path"})
    assert resp.status_code == 201
    data = resp.json()
    assert "code" in data
    assert "short_url" in data
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_create_url_idempotent(client):
    with patch("app.service.cache_set", new_callable=AsyncMock),          patch("app.service.cache_get", new_callable=AsyncMock, return_value=None):
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
    with patch("app.service.cache_set", new_callable=AsyncMock),          patch("app.service.cache_get", new_callable=AsyncMock, return_value=None):
        create_resp = await client.post("/urls", json={"url": "https://redirect-target.example.com"})
    assert create_resp.status_code == 201
    code = create_resp.json()["code"]

    with patch("app.service.cache_get", new_callable=AsyncMock, return_value="https://redirect-target.example.com"),          patch("app.analytics.record_click_async", new_callable=AsyncMock):
        redirect_resp = await client.get(f"/{code}", follow_redirects=False)
    assert redirect_resp.status_code == 302
    assert redirect_resp.headers["location"] == "https://redirect-target.example.com"


@pytest.mark.asyncio
async def test_delete_url(client):
    with patch("app.service.cache_set", new_callable=AsyncMock),          patch("app.service.cache_get", new_callable=AsyncMock, return_value=None):
        create_resp = await client.post("/urls", json={"url": "https://to-delete.example.com"})
    code = create_resp.json()["code"]

    with patch("app.service.cache_delete", new_callable=AsyncMock):
        del_resp = await client.delete(f"/urls/{code}")
    assert del_resp.status_code == 204


@pytest.mark.asyncio
async def test_get_metadata(client):
    with patch("app.service.cache_set", new_callable=AsyncMock),          patch("app.service.cache_get", new_callable=AsyncMock, return_value=None):
        create_resp = await client.post("/urls", json={"url": "https://metadata.example.com"})
    code = create_resp.json()["code"]

    meta_resp = await client.get(f"/urls/{code}")
    assert meta_resp.status_code == 200
    assert meta_resp.json()["code"] == code


@pytest.mark.asyncio
async def test_invalid_url_returns_422(client):
    resp = await client.post("/urls", json={"url": "not-a-valid-url"})
    assert resp.status_code == 422
