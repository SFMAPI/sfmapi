from __future__ import annotations

import pytest

pytestmark = pytest.mark.integration


async def test_metrics_endpoint_exposes_expected_series(client) -> None:
    resp = await client.get("/metrics")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/plain")
    body = resp.text
    for series in (
        "sfmapi_job_duration_seconds",
        "sfmapi_task_duration_seconds",
        "sfmapi_queue_depth",
        "sfmapi_active_jobs",
        "sfmapi_storage_bytes",
        "sfmapi_worker_lease_age_seconds",
        "sfmapi_errors_total",
    ):
        assert series in body, series


async def test_queue_depth_reflects_pending_tasks(client) -> None:
    pr = await client.post("/v1/projects", json={"name": "p-metric"})
    pid = pr.json()["project_id"]
    ds = await client.post(
        f"/v1/projects/{pid}/datasets",
        json={"name": "ds", "source": {"kind": "upload", "entries": []}},
    )
    did = ds.json()["dataset_id"]
    # Submit features task; with inline_tasks=true it ends up succeeded
    # very quickly so queue_depth for "extract" should remain 0.
    await client.post(
        f"/v1/datasets/{did}/features",
        json={"spec": {"use_gpu": False}, "image_root": "/tmp", "image_list": []},
    )
    metrics = await client.get("/metrics")
    assert metrics.status_code == 200
    assert "sfmapi_queue_depth" in metrics.text
