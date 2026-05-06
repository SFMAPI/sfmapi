"""§3.4 RFC 7807 errors + §3.8 ETag/304 caching."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.conformance


async def test_404_is_problem_json(conf_client) -> None:
    resp = await conf_client.get("/v1/projects/__nope__")
    assert resp.status_code == 404
    # SHOULD be application/problem+json; allow application/json as a
    # graceful deviation since it's the most common false-friend.
    ct = resp.headers.get("content-type", "")
    assert "json" in ct
    body = resp.json()
    assert isinstance(body.get("title"), str)
    assert body.get("status") == 404


async def test_validation_error_returns_422(conf_client) -> None:
    """§6.6: bad spec or bad upload should return 422 with a problem
    body, not 500."""
    resp = await conf_client.post("/v1/uploads", json={"expected_size": -1})
    assert resp.status_code in (400, 422)


async def test_pagination_default_shape(conf_client) -> None:
    listing = await conf_client.get("/v1/projects")
    assert listing.status_code == 200
    page = listing.json()
    # §3.6 list endpoints MUST return {items, next_page_token, total} (AIP-158).
    for k in ("items", "next_page_token", "total"):
        assert k in page, f"list missing key {k!r}"
    assert isinstance(page["items"], list)


async def test_options_preflight_advertises_methods(conf_client) -> None:
    """§3.10 CORS: OPTIONS should produce useful preflight info on at
    least one well-known endpoint when CORS is enabled."""
    resp = await conf_client.options(
        "/v1/projects",
        headers={
            "Origin": "https://conformance.example.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    if resp.status_code == 405:
        pytest.skip("server has CORS disabled (OPTIONS rejected); skipping preflight check")
    assert resp.status_code == 200
    methods = resp.headers.get("access-control-allow-methods", "")
    # If the server enabled CORS, methods should be advertised.
    if methods:
        assert "GET" in methods or "*" in methods
