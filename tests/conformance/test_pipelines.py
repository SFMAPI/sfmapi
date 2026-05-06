"""§6.8 Pipeline recipes (optional)."""

from __future__ import annotations

import pytest

from tests.conformance.conftest import make_project_dataset

pytestmark = pytest.mark.conformance


async def test_pipeline_kind_must_match_spec_kind(conf_client) -> None:
    pid, did, _ = await make_project_dataset(conf_client, name="recipe-mismatch")
    resp = await conf_client.post(
        f"/v1/projects/{pid}/pipelines/incremental",
        json={"dataset_id": did, "spec": {"kind": "global"}},
    )
    if resp.status_code == 404:
        pytest.skip("server does not implement /pipelines (optional §6.8)")
    assert resp.status_code == 422


async def test_pipeline_creates_4_node_dag(conf_client) -> None:
    pid, did, _ = await make_project_dataset(conf_client, name="recipe-ok")
    resp = await conf_client.post(
        f"/v1/projects/{pid}/pipelines/incremental",
        json={"dataset_id": did, "spec": {"kind": "incremental"}},
    )
    if resp.status_code == 404:
        pytest.skip("server does not implement /pipelines (optional §6.8)")
    assert resp.status_code == 202, resp.text
    body = resp.json()
    assert "job_id" in body
    assert len(body["task_ids"]) == 4
    detail = await conf_client.get(f"/v1/jobs/{body['job_id']}")
    j = detail.json()
    kinds = sorted(t["kind"] for t in j["tasks"])
    assert kinds == ["extract", "map", "match", "verify"]
