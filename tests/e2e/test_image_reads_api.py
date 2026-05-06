"""Image bytes / thumbnail / EXIF + bulk add endpoints."""

from __future__ import annotations

import io
from pathlib import Path

import pytest
from PIL import Image as PILImage

pytestmark = pytest.mark.e2e


def _jpeg_bytes(size: int = 64) -> bytes:
    im = PILImage.new("RGB", (size, size), color=(120, 60, 30))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=80)
    return buf.getvalue()


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


async def _make_dataset_with_image(client, payload: bytes) -> tuple[str, str]:
    pid = await _create_project(client, f"img-{len(payload)}")
    sha = await _upload_one(client, payload)
    ds = await client.post(
        f"/v1/projects/{pid}/datasets",
        json={
            "name": "ds",
            "source": {
                "kind": "upload",
                "entries": [{"name": "a.jpg", "blob_sha": sha}],
            },
        },
    )
    did = ds.json()["dataset_id"]
    img = await client.post(f"/v1/datasets/{did}/images", json={"name": "a.jpg", "blob_sha": sha})
    return did, img.json()["image_id"]


async def test_get_image_metadata_includes_links(client) -> None:
    payload = _jpeg_bytes()
    _, image_id = await _make_dataset_with_image(client, payload)
    resp = await client.get(f"/v1/images/{image_id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["image_id"] == image_id
    links = body["_links"]
    assert links["self"]["href"] == f"/v1/images/{image_id}"
    assert links["bytes"]["href"] == f"/v1/images/{image_id}/bytes"
    assert links["thumbnail"]["href"] == f"/v1/images/{image_id}/thumbnail"


async def test_delete_image_by_id_removes_metadata_and_listing(client) -> None:
    payload = _jpeg_bytes()
    did, image_id = await _make_dataset_with_image(client, payload)
    resp = await client.delete(f"/v1/images/{image_id}")
    assert resp.status_code == 204, resp.text

    missing = await client.get(f"/v1/images/{image_id}")
    assert missing.status_code == 404

    listing = await client.get(f"/v1/datasets/{did}/images")
    assert listing.status_code == 200
    assert listing.json()["items"] == []


async def test_get_image_bytes_returns_payload_with_etag(client) -> None:
    payload = _jpeg_bytes()
    _, image_id = await _make_dataset_with_image(client, payload)
    resp = await client.get(f"/v1/images/{image_id}/bytes")
    assert resp.status_code == 200
    assert resp.content == payload
    assert resp.headers["content-type"] == "image/jpeg"
    etag = resp.headers["etag"]
    assert etag

    cached = await client.get(f"/v1/images/{image_id}/bytes", headers={"If-None-Match": etag})
    assert cached.status_code == 304


async def test_thumbnail_renders_and_caches(client, tmp_path: Path) -> None:
    payload = _jpeg_bytes(size=200)
    _, image_id = await _make_dataset_with_image(client, payload)
    resp = await client.get(f"/v1/images/{image_id}/thumbnail?size=64")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "image/jpeg"
    out = PILImage.open(io.BytesIO(resp.content))
    assert max(out.size) == 64
    etag = resp.headers["etag"]
    cached = await client.get(
        f"/v1/images/{image_id}/thumbnail?size=64",
        headers={"If-None-Match": etag},
    )
    assert cached.status_code == 304


async def test_thumbnail_size_above_max_rejected(client) -> None:
    payload = _jpeg_bytes()
    _, image_id = await _make_dataset_with_image(client, payload)
    resp = await client.get(f"/v1/images/{image_id}/thumbnail?size=99999")
    assert resp.status_code == 422


async def test_exif_returns_dict(client) -> None:
    payload = _jpeg_bytes()
    _, image_id = await _make_dataset_with_image(client, payload)
    resp = await client.get(f"/v1/images/{image_id}/exif")
    assert resp.status_code == 200
    assert isinstance(resp.json(), dict)


async def test_batch_create_inserts_all(client) -> None:
    pid = await _create_project(client, "batch-test")
    shas = [await _upload_one(client, _jpeg_bytes(size=32 + i)) for i in range(3)]
    ds = await client.post(
        f"/v1/projects/{pid}/datasets",
        json={"name": "ds", "source": {"kind": "upload", "entries": []}},
    )
    did = ds.json()["dataset_id"]
    requests = [{"name": f"img_{i}.jpg", "blob_sha": s} for i, s in enumerate(shas)]
    resp = await client.post(
        f"/v1/datasets/{did}/images:batchCreate",
        json={"requests": requests},
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert len(body["images"]) == 3
    listing = await client.get(f"/v1/datasets/{did}/images")
    assert len(listing.json()["items"]) == 3


async def test_batch_empty_rejected(client) -> None:
    pid = await _create_project(client, "batch-empty")
    ds = await client.post(
        f"/v1/projects/{pid}/datasets",
        json={"name": "ds", "source": {"kind": "upload", "entries": []}},
    )
    did = ds.json()["dataset_id"]
    resp = await client.post(
        f"/v1/datasets/{did}/images:batchCreate",
        json={"requests": []},
    )
    assert resp.status_code == 422
