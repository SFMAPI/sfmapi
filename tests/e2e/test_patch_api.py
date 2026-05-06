"""PATCH project + PATCH dataset."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.e2e


async def test_patch_project_updates_fields(client) -> None:
    pr = await client.post("/v1/projects", json={"name": "old-name"})
    pid = pr.json()["project_id"]
    resp = await client.patch(
        f"/v1/projects/{pid}",
        json={"name": "new-name", "description": "shiny"},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["name"] == "new-name"
    assert body["description"] == "shiny"
    assert body["_links"]["self"]["href"] == f"/v1/projects/{pid}"


async def test_patch_project_partial_keeps_unset(client) -> None:
    pr = await client.post("/v1/projects", json={"name": "p", "description": "keep me"})
    pid = pr.json()["project_id"]
    resp = await client.patch(f"/v1/projects/{pid}", json={"name": "renamed"})
    assert resp.status_code == 200
    assert resp.json()["description"] == "keep me"


async def test_patch_dataset_updates_camera_and_active_maskset(client) -> None:
    pr = await client.post("/v1/projects", json={"name": "ds-patch"})
    pid = pr.json()["project_id"]
    ds = await client.post(
        f"/v1/projects/{pid}/datasets",
        json={"name": "d1", "source": {"kind": "upload", "entries": []}},
    )
    did = ds.json()["dataset_id"]
    resp = await client.patch(
        f"/v1/projects/{pid}/datasets/{did}",
        json={
            "camera_model": "OPENCV",
            "is_spherical": True,
            "active_maskset_id": "01HZMASKSET00000000000000",
        },
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["camera_model"] == "OPENCV"
    assert body["is_spherical"] is True
    assert body["active_maskset_id"] == "01HZMASKSET00000000000000"
