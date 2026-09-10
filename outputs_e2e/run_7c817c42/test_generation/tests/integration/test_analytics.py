import pytest
from unittest.mock import patch, AsyncMock


@pytest.mark.asyncio
async def test_stats_returns_zero_for_new_url(client):
    with patch("app.service.cache_set", new_callable=AsyncMock),          patch("app.service.cache_get", new_callable=AsyncMock, return_value=None):
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
    with patch("app.service.cache_set", new_callable=AsyncMock),          patch("app.service.cache_get", new_callable=AsyncMock, return_value=None):
        create_resp = await client.post("/urls", json={"url": "https://resilient.example.com"})
    code = create_resp.json()["code"]

    with patch("app.service.cache_get", new_callable=AsyncMock, return_value="https://resilient.example.com"),          patch("app.analytics.record_click_async", side_effect=Exception("DB down")):
        resp = await client.get(f"/{code}", follow_redirects=False)
    # Redirect must still succeed despite analytics failure
    assert resp.status_code == 302
