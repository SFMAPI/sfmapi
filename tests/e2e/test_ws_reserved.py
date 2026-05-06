from __future__ import annotations

import pytest

pytestmark = pytest.mark.e2e


async def test_ws_get_hint_returns_endpoint_info(client) -> None:
    """The plain GET on the WS path returns a hint pointing at the
    real WebSocket URL — used by curl-based discoverability."""
    resp = await client.get("/ws/v1/jobs/some-id")
    assert resp.status_code == 200
    body = resp.json()
    assert body["kind"] == "ws_endpoint"
    assert body["ws_url"] == "/ws/v1/jobs/some-id"
