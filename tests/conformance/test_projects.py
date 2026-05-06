"""§6.2 Projects."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.conformance


async def test_project_lifecycle(conf_client) -> None:
    # Create
    create = await conf_client.post("/v1/projects", json={"name": "conf-lifecycle"})
    assert create.status_code == 201, create.text
    body = create.json()
    pid = body["project_id"]
    assert isinstance(pid, str)
    assert len(pid) >= 8
    assert body["name"] == "conf-lifecycle"
    assert "tenant_id" in body
    assert "created_at" in body

    # Get
    get = await conf_client.get(f"/v1/projects/{pid}")
    assert get.status_code == 200
    assert get.json()["project_id"] == pid

    # List shape
    listing = await conf_client.get("/v1/projects")
    assert listing.status_code == 200
    page = listing.json()
    assert isinstance(page.get("items"), list)
    assert any(item["project_id"] == pid for item in page["items"])

    # PATCH
    patch = await conf_client.patch(f"/v1/projects/{pid}", json={"description": "from-conformance"})
    if patch.status_code != 404:  # PATCH is RECOMMENDED, not required by §6.2
        assert patch.status_code == 200
        assert patch.json()["description"] == "from-conformance"

    # Delete
    delete = await conf_client.delete(f"/v1/projects/{pid}")
    assert delete.status_code in (204, 200)
    missing = await conf_client.get(f"/v1/projects/{pid}")
    assert missing.status_code == 404


async def test_project_create_409_on_duplicate(conf_client) -> None:
    a = await conf_client.post("/v1/projects", json={"name": "conf-dup"})
    assert a.status_code == 201
    b = await conf_client.post("/v1/projects", json={"name": "conf-dup"})
    assert b.status_code == 409


async def test_project_get_unknown_returns_404(conf_client) -> None:
    resp = await conf_client.get("/v1/projects/__definitely_not_a_real_id__")
    assert resp.status_code == 404
    body = resp.json()
    # §3.4 RFC 7807 shape
    assert "title" in body
    assert body.get("status") == 404
