"""Job + SSE endpoints — Phase 1.

The stage endpoints derive the image source + database path from the
dataset itself (per the v1 cleanup), so each test that submits a
features/match/verify job has to register at least one image first.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.e2e


async def _upload(client, payload: bytes) -> str:
    init = await client.post("/v1/uploads", json={"expected_size": len(payload)})
    upload_id = init.json()["upload_id"]
    await client.patch(
        f"/v1/uploads/{upload_id}",
        content=payload,
        headers={"Content-Range": f"bytes 0-{len(payload) - 1}/{len(payload)}"},
    )
    fin = await client.post(f"/v1/uploads/{upload_id}:finalize")
    return fin.json()["blob_sha"]


async def _project_with_image(client, name: str) -> tuple[str, str]:
    pr = await client.post("/v1/projects", json={"name": name})
    pid = pr.json()["project_id"]
    sha = await _upload(client, b"\xff\xd8\xff\xe0imagebytes")
    ds = await client.post(
        f"/v1/projects/{pid}/datasets",
        json={
            "name": "ds",
            "source": {"kind": "upload", "entries": [{"name": "a.jpg", "blob_sha": sha}]},
        },
    )
    did = ds.json()["dataset_id"]
    await client.post(f"/v1/datasets/{did}/images", json={"name": "a.jpg", "blob_sha": sha})
    return pid, did


async def test_features_returns_202(client) -> None:
    _, did = await _project_with_image(client, "p-feat")
    resp = await client.post(
        f"/v1/datasets/{did}/features",
        json={"spec": {"sift_max_num_features": 4096, "use_gpu": False}},
    )
    assert resp.status_code == 202, resp.text
    body = resp.json()
    assert "job_id" in body
    assert "task_ids" in body
    job_id = body["job_id"]
    detail = await client.get(f"/v1/jobs/{job_id}")
    assert detail.status_code == 200
    j = detail.json()
    assert j["recipe"] == "features"
    assert len(j["tasks"]) == 1


async def test_features_rejects_empty_dataset(client) -> None:
    """A dataset with no images can't be featured — the API says so up
    front rather than letting the job fail mid-flight."""
    pr = await client.post("/v1/projects", json={"name": "p-empty"})
    pid = pr.json()["project_id"]
    ds = await client.post(
        f"/v1/projects/{pid}/datasets",
        json={"name": "ds", "source": {"kind": "upload", "entries": []}},
    )
    did = ds.json()["dataset_id"]
    resp = await client.post(f"/v1/datasets/{did}/features", json={"spec": {}})
    assert resp.status_code == 422
    assert "images" in resp.text.lower()


async def test_cancel_sets_flag(client) -> None:
    _, did = await _project_with_image(client, "p-cancel")
    resp = await client.post(f"/v1/datasets/{did}/features", json={"spec": {"use_gpu": False}})
    job_id = resp.json()["job_id"]
    cancel = await client.post(f"/v1/jobs/{job_id}:cancel")
    assert cancel.status_code == 200
    assert cancel.json()["cancel_requested"] is True

    cancel2 = await client.post(f"/v1/jobs/{job_id}:cancel?force=true")
    assert cancel2.json()["cancel_force"] is True


async def test_matches_requires_vocab_tree_for_vocabtree_strategy(client) -> None:
    _, did = await _project_with_image(client, "p-match")
    resp = await client.post(
        f"/v1/datasets/{did}/matches",
        json={"pairs": {"strategy": "vocabtree"}},
    )
    assert resp.status_code == 422


async def test_verify_returns_202(client) -> None:
    _, did = await _project_with_image(client, "p-verify")
    resp = await client.post(f"/v1/datasets/{did}/verify", json={"spec": {}})
    assert resp.status_code == 202
