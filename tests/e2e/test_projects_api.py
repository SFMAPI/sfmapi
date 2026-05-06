from __future__ import annotations

import pytest

pytestmark = pytest.mark.e2e


async def test_create_get_list_delete(client) -> None:
    resp = await client.post("/v1/projects", json={"name": "proj-a", "description": "d"})
    assert resp.status_code == 201, resp.text
    p = resp.json()
    assert p["name"] == "proj-a"
    pid = p["project_id"]

    resp = await client.get(f"/v1/projects/{pid}")
    assert resp.status_code == 200
    assert resp.json()["project_id"] == pid

    resp = await client.get("/v1/projects")
    assert resp.status_code == 200
    body = resp.json()
    assert any(item["project_id"] == pid for item in body["items"])

    resp = await client.delete(f"/v1/projects/{pid}")
    assert resp.status_code == 204

    resp = await client.get(f"/v1/projects/{pid}")
    assert resp.status_code == 404


async def test_duplicate_project_name_conflicts(client) -> None:
    resp = await client.post("/v1/projects", json={"name": "dup"})
    assert resp.status_code == 201
    resp = await client.post("/v1/projects", json={"name": "dup"})
    assert resp.status_code == 409
