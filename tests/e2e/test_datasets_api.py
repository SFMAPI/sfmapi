from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.e2e


async def _create_project(client, name: str) -> str:
    r = await client.post("/v1/projects", json={"name": name})
    return r.json()["project_id"]


async def _upload_one(client, payload: bytes) -> str:
    init = await client.post("/v1/uploads", json={"expected_size": len(payload)})
    upload_id = init.json()["upload_id"]
    await client.patch(
        f"/v1/uploads/{upload_id}",
        content=payload,
        headers={"Content-Range": f"bytes 0-{len(payload) - 1}/{len(payload)}"},
    )
    fin = await client.post(f"/v1/uploads/{upload_id}:finalize")
    return fin.json()["blob_sha"]


async def test_create_dataset_from_uploads(client) -> None:
    pid = await _create_project(client, "p1")
    sha_a = await _upload_one(client, b"\xff\xd8\xff\xe0aaaaa")
    sha_b = await _upload_one(client, b"\xff\xd8\xff\xe0bbbbb")

    resp = await client.post(
        f"/v1/projects/{pid}/datasets",
        json={
            "name": "ds1",
            "source": {
                "kind": "upload",
                "entries": [
                    {"name": "a.jpg", "blob_sha": sha_a},
                    {"name": "b.jpg", "blob_sha": sha_b},
                ],
            },
            "camera_model": "OPENCV",
            "is_spherical": False,
        },
    )
    assert resp.status_code == 201, resp.text
    d = resp.json()
    assert d["name"] == "ds1"
    assert d["camera_model"] == "OPENCV"
    assert d["manifest_hash"] == ""

    add = await client.post(
        f"/v1/datasets/{d['dataset_id']}/images",
        json={"name": "a.jpg", "blob_sha": sha_a},
    )
    assert add.status_code == 201, add.text

    list_imgs = await client.get(f"/v1/datasets/{d['dataset_id']}/images")
    assert list_imgs.status_code == 200
    assert len(list_imgs.json()["items"]) == 1


async def test_create_dataset_from_local(client, tmp_path: Path) -> None:
    img = tmp_path / "img.jpg"
    img.write_bytes(b"\xff\xd8\xff\xe0" + b"x" * 1024)

    pid = await _create_project(client, "p2")
    resp = await client.post(
        f"/v1/projects/{pid}/datasets",
        json={
            "name": "ds-local",
            "source": {"kind": "local", "root": str(tmp_path)},
            "camera_model": "SIMPLE_RADIAL",
            "is_spherical": True,
        },
    )
    assert resp.status_code == 201, resp.text
    d = resp.json()
    assert d["is_spherical"] is True


async def test_dataset_unique_per_project(client) -> None:
    pid = await _create_project(client, "p3")
    body = {
        "name": "same",
        "source": {"kind": "upload", "entries": []},
    }
    a = await client.post(f"/v1/projects/{pid}/datasets", json=body)
    b = await client.post(f"/v1/projects/{pid}/datasets", json=body)
    assert a.status_code == 201
    assert b.status_code == 409
