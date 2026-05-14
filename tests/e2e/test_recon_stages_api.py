"""Portable reconstruction-scoped stage route contracts.

The stub backend advertises no capabilities, so every stage service
builder's ``require_capability`` gate fires first — before any DB
lookup — and the route returns 501 with the canonical capability
name. That makes these endpoint-contract tests independent of having
a real reconstruction row.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.e2e

_FAKE_RECON = "01HGHOST00000000000000000A"


async def test_bundle_adjust_returns_501_without_capability(client) -> None:
    resp = await client.post(f"/v1/reconstructions/{_FAKE_RECON}:bundleAdjust", json={})
    assert resp.status_code == 501
    assert resp.json()["capability"] == "ba.standard"


async def test_bundle_adjust_mode_selects_capability(client) -> None:
    resp = await client.post(
        f"/v1/reconstructions/{_FAKE_RECON}:bundleAdjust", json={"mode": "rig"}
    )
    assert resp.status_code == 501
    assert resp.json()["capability"] == "ba.rig"


async def test_bundle_adjust_rejects_unknown_field(client) -> None:
    resp = await client.post(f"/v1/reconstructions/{_FAKE_RECON}:bundleAdjust", json={"bogus": 1})
    assert resp.status_code == 422


async def test_triangulate_returns_501_without_capability(client) -> None:
    resp = await client.post(f"/v1/reconstructions/{_FAKE_RECON}:triangulate", json={})
    assert resp.status_code == 501
    assert resp.json()["capability"] == "triangulate.retri"


async def test_pose_graph_optimize_returns_501_without_capability(client) -> None:
    resp = await client.post(f"/v1/reconstructions/{_FAKE_RECON}:poseGraphOptimize", json={})
    assert resp.status_code == 501
    assert resp.json()["capability"] == "pgo.optimize"


async def test_export_returns_501_without_capability(client) -> None:
    resp = await client.post(f"/v1/reconstructions/{_FAKE_RECON}:export", json={})
    assert resp.status_code == 501
    assert resp.json()["capability"] == "export.ply"


async def test_export_format_selects_capability(client) -> None:
    resp = await client.post(f"/v1/reconstructions/{_FAKE_RECON}:export", json={"format": "nvm"})
    assert resp.status_code == 501
    assert resp.json()["capability"] == "export.nvm"


async def test_export_rejects_unknown_format(client) -> None:
    resp = await client.post(f"/v1/reconstructions/{_FAKE_RECON}:export", json={"format": "obj"})
    assert resp.status_code == 422


async def test_relocalize_returns_501_without_capability(client) -> None:
    resp = await client.post(
        f"/v1/reconstructions/{_FAKE_RECON}:relocalize", json={"image_ids": [1, 2]}
    )
    assert resp.status_code == 501
    assert resp.json()["capability"] == "relocalize.images"


async def test_undistort_returns_501_without_capability(client) -> None:
    resp = await client.post(f"/v1/reconstructions/{_FAKE_RECON}:undistort", json={})
    assert resp.status_code == 501
    assert resp.json()["capability"] == "image.undistort"


async def test_undistort_rejects_bad_provider(client) -> None:
    resp = await client.post(
        f"/v1/reconstructions/{_FAKE_RECON}:undistort", json={"provider": "bad provider!"}
    )
    assert resp.status_code == 422
