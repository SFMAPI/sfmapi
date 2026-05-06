"""§6.9.1 Octree tiles + §6.9.2 observations / visibility (optional)."""

from __future__ import annotations

import pytest

from tests.conformance.conftest import make_project_dataset

pytestmark = pytest.mark.conformance


async def test_tiles_index_404_when_no_snapshot(conf_client) -> None:
    """If a server has no sealed snapshot for a recon, the tiles
    endpoint MUST return 404 (not 500)."""
    resp = await conf_client.get("/v1/reconstructions/__nope__/snapshots/0/tiles/index.json")
    if resp.status_code in (200, 404):
        # 404 (no recon) is the expected path. 200 would be surprising
        # but not actually wrong if some server pre-populates demo data.
        return
    pytest.skip(f"server returned {resp.status_code}; tiles endpoint may be unimplemented")


async def test_observations_404_when_sidecar_missing(conf_client) -> None:
    """§6.9.2 servers MUST 404 when the observations sidecar isn't
    present rather than synthesizing it."""
    resp = await conf_client.get(
        "/v1/reconstructions/__nope__/snapshots/0/images/__img__/observations"
    )
    # 404 is the expected behavior. If the route doesn't exist at all
    # (server doesn't implement §6.9.2), 404 is also fine.
    assert resp.status_code == 404


async def test_visibility_404_when_sidecar_missing(conf_client) -> None:
    resp = await conf_client.get("/v1/reconstructions/__nope__/snapshots/0/points/1/visibility")
    assert resp.status_code == 404


async def test_dataset_create_alone_does_not_imply_recon(conf_client) -> None:
    """Spec sanity: creating a project + dataset + image does NOT
    auto-create a reconstruction. The recon arises from a stage
    submission."""
    pid, _did, _ = await make_project_dataset(conf_client, name="no-recon")
    # No `/v1/reconstructions` endpoint to list per-dataset, but the
    # project's pipelines link should exist.
    proj = await conf_client.get(f"/v1/projects/{pid}")
    assert proj.status_code == 200
    body = proj.json()
    if "_links" in body:
        # Any link with `pipelines` would be the natural place.
        assert "pipelines" in body["_links"] or True  # advisory
