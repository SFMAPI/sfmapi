"""Spec discovery endpoint exposes which standard this server implements."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


async def test_spec_endpoint_shape(client) -> None:
    resp = await client.get("/spec")
    assert resp.status_code == 200
    body = resp.json()
    assert body["spec"] == "sfmapi"
    assert body["spec_version"].startswith("v")
    assert body["openapi_url"].endswith("openapi.json")
    assert "name" in body["server"]
    assert "version" in body["server"]
