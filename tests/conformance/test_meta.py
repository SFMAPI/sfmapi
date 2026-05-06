"""§6.1 Health / meta + §11 spec discovery."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.conformance


async def test_healthz_returns_200(conf_client) -> None:
    resp = await conf_client.get("/healthz")
    assert resp.status_code == 200, resp.text


async def test_readyz_returns_200_or_503(conf_client) -> None:
    resp = await conf_client.get("/readyz")
    assert resp.status_code in (200, 503), resp.text


async def test_version_returns_required_fields(conf_client) -> None:
    resp = await conf_client.get("/version")
    assert resp.status_code == 200
    body = resp.json()
    # Per §6.1 the field set is implementation-defined but the engine
    # discovery fields here are the de-facto contract for any sfmapi
    # implementation that wraps a SfM engine.
    assert "sfmapi" in body or "server" in body


async def test_spec_endpoint_identifies_implementation(conf_client) -> None:
    """§11. A conforming server MUST expose `/spec` so clients can
    identify which standard + version the server implements."""
    resp = await conf_client.get("/spec")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body.get("spec") == "sfmapi"
    assert isinstance(body.get("spec_version"), str)
    assert body.get("openapi_url"), "spec response should advertise an openapi_url"


async def test_openapi_document_is_3x(conf_client) -> None:
    resp = await conf_client.get("/openapi.json")
    assert resp.status_code == 200
    body = resp.json()
    assert str(body.get("openapi", "")).startswith("3.")
