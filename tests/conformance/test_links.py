"""§3.5 HAL-lite `_links` invariant: every linkable resource carries
at minimum a `self` link."""

from __future__ import annotations

import pytest

from tests.conformance.conftest import make_project_dataset

pytestmark = pytest.mark.conformance


async def test_project_has_self_link(conf_client) -> None:
    pr = await conf_client.post("/v1/projects", json={"name": "links-p"})
    body = pr.json()
    if "_links" not in body:
        pytest.skip("server does not surface _links (optional §3.5)")
    assert body["_links"]["self"]["href"].endswith(f"/projects/{body['project_id']}")


async def test_dataset_has_self_link(conf_client) -> None:
    pid, did, _ = await make_project_dataset(conf_client, name="links-ds")
    resp = await conf_client.get(f"/v1/projects/{pid}/datasets/{did}")
    body = resp.json()
    if "_links" not in body:
        pytest.skip("server does not surface _links (optional §3.5)")
    assert body["_links"]["self"]["href"].endswith(f"/datasets/{did}")


async def test_image_has_self_link(conf_client) -> None:
    _pid, did, _ = await make_project_dataset(conf_client, name="links-img")
    page = (await conf_client.get(f"/v1/datasets/{did}/images")).json()
    image_id = page["items"][0]["image_id"]
    resp = await conf_client.get(f"/v1/images/{image_id}")
    if resp.status_code == 404:
        pytest.skip("server does not implement top-level /v1/images/{id}")
    body = resp.json()
    if "_links" not in body:
        pytest.skip("server does not surface _links (optional §3.5)")
    assert body["_links"]["self"]["href"].endswith(f"/images/{image_id}")
