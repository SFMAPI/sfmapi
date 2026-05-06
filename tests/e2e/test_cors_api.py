"""CORS middleware respects the configured origin list."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.e2e


async def test_cors_preflight_default_wildcard(client) -> None:
    resp = await client.options(
        "/v1/projects",
        headers={
            "Origin": "https://viewer.example.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert resp.status_code == 200
    # Default config is `*` — middleware echoes either `*` or the origin.
    allow = resp.headers.get("access-control-allow-origin")
    assert allow in ("*", "https://viewer.example.com")
    assert "GET" in resp.headers.get("access-control-allow-methods", "")


async def test_cors_actual_request_exposes_etag(client) -> None:
    resp = await client.get("/healthz", headers={"Origin": "https://viewer.example.com"})
    assert resp.status_code == 200
    expose = resp.headers.get("access-control-expose-headers", "")
    # CORSMiddleware joins exposed-headers with commas.
    assert "ETag" in expose
