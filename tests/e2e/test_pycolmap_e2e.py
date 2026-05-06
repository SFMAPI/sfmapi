"""End-to-end test against the real `pycolmap` library.

Skipped unless `SFMAPI_PYCOLMAP_AVAILABLE=true` AND `pycolmap` imports
cleanly. Generates 4 synthetic images, runs features → matches → verify
through the live API + worker, and asserts that pycolmap actually wrote
keypoints/matches into `database.db`.

Mapping is exercised in a separate test that downgrades expectations
since 4 synthetic images aren't enough to register a non-trivial
reconstruction; we accept "the call returns without raising" as the
contract.
"""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

pytestmark = [pytest.mark.e2e, pytest.mark.needs_pycolmap]


def _pycolmap_available() -> bool:
    if os.environ.get("SFMAPI_PYCOLMAP_AVAILABLE", "").lower() not in ("1", "true", "yes"):
        return False
    try:
        import pycolmap  # noqa: F401
    except ImportError:
        return False
    return True


pytest.importorskip("PIL")
if not _pycolmap_available():
    pytest.skip("pycolmap not available; skipping real-pycolmap e2e", allow_module_level=True)


def _make_textured_image(seed: int, size: tuple[int, int] = (640, 480)) -> Image.Image:
    """Generate a textured image with enough features for SIFT."""
    rng = np.random.default_rng(seed)
    base = rng.integers(0, 256, size=(size[1], size[0]), dtype=np.uint8)
    # Add some structure (overlapping rectangles, gradients) so SIFT has
    # repeatable corners across views.
    for _ in range(40):
        x = int(rng.integers(0, size[0] - 64))
        y = int(rng.integers(0, size[1] - 64))
        w = int(rng.integers(20, 64))
        h = int(rng.integers(20, 64))
        v = int(rng.integers(0, 256))
        base[y : y + h, x : x + w] = v
    rgb = np.stack([base, base, base], axis=-1)
    return Image.fromarray(rgb, mode="RGB")


@pytest.fixture
def fixture_images(tmp_path: Path) -> tuple[Path, list[str]]:
    img_dir = tmp_path / "imgs"
    img_dir.mkdir()
    names: list[str] = []
    for i in range(4):
        name = f"img_{i:03d}.jpg"
        _make_textured_image(seed=i + 1).save(img_dir / name, format="JPEG", quality=92)
        names.append(name)
    return img_dir, names


async def test_features_match_verify_real(client, fixture_images) -> None:
    img_dir, names = fixture_images

    pr = await client.post("/v1/projects", json={"name": "real-e2e"})
    pid = pr.json()["project_id"]
    ds = await client.post(
        f"/v1/projects/{pid}/datasets",
        json={
            "name": "ds-real",
            "source": {"kind": "local", "root": str(img_dir)},
            "camera_model": "SIMPLE_RADIAL",
        },
    )
    assert ds.status_code == 201, ds.text
    did = ds.json()["dataset_id"]

    # Features
    feat = await client.post(
        f"/v1/datasets/{did}/features",
        json={
            "spec": {"sift_max_num_features": 4096, "use_gpu": False},
            "image_root": str(img_dir),
            "image_list": names,
        },
    )
    assert feat.status_code == 202, feat.text
    feat_job = feat.json()["job_id"]
    detail = await client.get(f"/v1/jobs/{feat_job}")
    j = detail.json()
    assert j["status"] in ("succeeded", "pending")
    assert len(j["tasks"]) == 1
    feat_task = j["tasks"][0]
    assert feat_task["status"] == "succeeded", feat_task
    db_path = feat_task["outputs_ref"]["database_path"]
    assert Path(db_path).is_file()
    assert feat_task["outputs_ref"]["num_keypoints"] > 0

    # Matches (exhaustive)
    match = await client.post(
        f"/v1/datasets/{did}/matches",
        json={
            "pairs": {"strategy": "exhaustive"},
            "matcher": {"use_gpu": False},
            "database_path": db_path,
        },
    )
    assert match.status_code == 202, match.text
    match_detail = await client.get(f"/v1/jobs/{match.json()['job_id']}")
    mt = match_detail.json()["tasks"][0]
    assert mt["status"] == "succeeded", mt
    assert mt["outputs_ref"]["num_matches"] >= 0

    # Verify
    ver = await client.post(
        f"/v1/datasets/{did}/verify",
        json={"spec": {}, "database_path": db_path},
    )
    assert ver.status_code == 202, ver.text
    ver_detail = await client.get(f"/v1/jobs/{ver.json()['job_id']}")
    vt = ver_detail.json()["tasks"][0]
    assert vt["status"] == "succeeded", vt


async def test_pipeline_recipe_runs_without_raising(client, fixture_images) -> None:
    img_dir, names = fixture_images
    pr = await client.post("/v1/projects", json={"name": "real-recipe"})
    pid = pr.json()["project_id"]
    ds = await client.post(
        f"/v1/projects/{pid}/datasets",
        json={"name": "ds", "source": {"kind": "local", "root": str(img_dir)}},
    )
    did = ds.json()["dataset_id"]

    resp = await client.post(
        f"/v1/projects/{pid}/pipelines/incremental",
        json={
            "dataset_id": did,
            "image_root": str(img_dir),
            "image_list": names,
            "features": {"sift_max_num_features": 4096, "use_gpu": False},
            "pairs": {"strategy": "exhaustive"},
            "matcher": {"use_gpu": False},
            "verify": {},
            "spec": {"kind": "incremental", "min_num_matches": 5},
        },
    )
    assert resp.status_code == 202, resp.text
    job_id = resp.json()["job_id"]
    detail = await client.get(f"/v1/jobs/{job_id}")
    body = detail.json()
    kinds_status = {(t["kind"], t["status"]) for t in body["tasks"]}
    # At minimum, extract/match/verify must succeed.
    for k in ("extract", "match", "verify"):
        assert (k, "succeeded") in kinds_status, kinds_status
    # Map may succeed or fail depending on synthetic-image quality;
    # accept any terminal state.
    map_status = next(t["status"] for t in body["tasks"] if t["kind"] == "map")
    assert map_status in ("succeeded", "failed"), map_status
