"""§6.4 Datasets + §6.5 Images."""

from __future__ import annotations

import pytest

from tests.conformance.conftest import make_project_dataset, upload_blob

pytestmark = pytest.mark.conformance


async def test_create_dataset_and_register_image(conf_client) -> None:
    _pid, did, sha = await make_project_dataset(conf_client, name="ds")
    listing = await conf_client.get(f"/v1/datasets/{did}/images")
    assert listing.status_code == 200
    page = listing.json()
    assert isinstance(page["items"], list)
    assert any(i["content_sha"] == sha for i in page["items"])


async def test_dataset_list_returns_page_shape(conf_client) -> None:
    pid, _, _ = await make_project_dataset(conf_client, name="page")
    listing = await conf_client.get(f"/v1/projects/{pid}/datasets")
    assert listing.status_code == 200
    page = listing.json()
    assert "items" in page  # §3.6 pagination contract
    assert "next_page_token" in page


async def test_image_get_includes_links_block(conf_client) -> None:
    _pid, did, _sha = await make_project_dataset(conf_client, name="links")
    page = (await conf_client.get(f"/v1/datasets/{did}/images")).json()
    image_id = page["items"][0]["image_id"]
    resp = await conf_client.get(f"/v1/images/{image_id}")
    assert resp.status_code == 200
    body = resp.json()
    # §3.5 _links MUST include at minimum a `self` link.
    assert "_links" in body
    assert body["_links"]["self"]["href"].endswith(f"/images/{image_id}")


async def test_image_bytes_returns_payload(conf_client) -> None:
    _pid, did, _ = await make_project_dataset(conf_client, name="bytes")
    page = (await conf_client.get(f"/v1/datasets/{did}/images")).json()
    image_id = page["items"][0]["image_id"]
    resp = await conf_client.get(f"/v1/images/{image_id}/bytes")
    if resp.status_code == 404:
        pytest.skip("server does not implement /images/{id}/bytes (optional)")
    assert resp.status_code == 200
    assert len(resp.content) > 0


async def test_image_thumbnail_is_optional(conf_client) -> None:
    _pid, did, _ = await make_project_dataset(conf_client, name="thumb")
    page = (await conf_client.get(f"/v1/datasets/{did}/images")).json()
    image_id = page["items"][0]["image_id"]
    resp = await conf_client.get(f"/v1/images/{image_id}/thumbnail?size=64")
    if resp.status_code == 404:
        pytest.skip("server does not implement thumbnails (optional)")
    assert resp.status_code == 200
    assert resp.headers.get("content-type", "").startswith("image/")


async def test_image_batch_is_optional(conf_client) -> None:
    _pid, did, _ = await make_project_dataset(conf_client, name="batch")
    sha = await upload_blob(conf_client, b"\xff\xd8\xff\xe0bbb" * 50)
    resp = await conf_client.post(
        f"/v1/datasets/{did}/images:batchCreate",
        json={"requests": [{"name": "extra.jpg", "blob_sha": sha}]},
    )
    if resp.status_code == 404:
        pytest.skip("server does not implement :batchCreate (optional)")
    assert resp.status_code == 201
    body = resp.json()
    assert len(body["images"]) == 1
