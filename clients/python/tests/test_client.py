"""SDK tests using respx to mock httpx.

We only assert the SDK's request shape and response parsing; the server
contract itself is covered by the sfmapi tests.
"""

from __future__ import annotations

import hashlib

import pytest
import respx
from httpx import Response

from sfmapi_client import (
    AsyncSfmApiClient,
    FeaturesSpec,
    IncrementalSpec,
    NotFoundError,
    SfmApiClient,
    ValidationError,
)


BASE = "http://api.test"


def _project_payload(name: str = "p") -> dict:
    return {
        "project_id": "01" * 13,
        "tenant_id": "default",
        "name": name,
        "description": None,
        "created_at": "2026-05-02T00:00:00Z",
    }


@respx.mock
def test_sync_create_project_sets_auth_header() -> None:
    route = respx.post(f"{BASE}/v1/projects").mock(
        return_value=Response(201, json=_project_payload("alpha"))
    )
    with SfmApiClient(BASE, api_key="sfm_test") as c:
        p = c.create_project("alpha")
    assert p.name == "alpha"
    assert route.calls.last.request.headers["Authorization"] == "Bearer sfm_test"
    assert route.calls.last.request.read() != b""  # body sent


@respx.mock
def test_sync_404_raises_not_found() -> None:
    respx.get(f"{BASE}/v1/projects/missing").mock(
        return_value=Response(
            404,
            json={
                "type": "https://sfmapi/errors/not_found",
                "title": "Resource not found",
                "status": 404,
                "detail": "Project missing not found",
            },
            headers={"content-type": "application/problem+json"},
        )
    )
    with SfmApiClient(BASE) as c, pytest.raises(NotFoundError) as ei:
        c.get_project("missing")
    assert ei.value.status_code == 404
    assert "missing" in str(ei.value)


@respx.mock
def test_sync_upload_bytes_full_handshake() -> None:
    payload = b"\xff\xd8\xff\xe0" + b"x" * 256
    sha = hashlib.sha256(payload).hexdigest()

    init = respx.post(f"{BASE}/v1/uploads").mock(
        return_value=Response(
            201,
            json={
                "upload_id": "U1" * 13,
                "state": "open",
                "expected_size": len(payload),
                "received_bytes": 0,
                "blob_sha": None,
                "expires_at": "2026-05-03T00:00:00Z",
            },
        )
    )
    patch = respx.patch(f"{BASE}/v1/uploads/{'U1' * 13}").mock(
        return_value=Response(
            200,
            json={
                "upload_id": "U1" * 13,
                "state": "received",
                "expected_size": len(payload),
                "received_bytes": len(payload),
                "blob_sha": None,
                "expires_at": "2026-05-03T00:00:00Z",
            },
        )
    )
    finalize = respx.post(f"{BASE}/v1/uploads/{'U1' * 13}:finalize").mock(
        return_value=Response(
            200,
            json={
                "upload_id": "U1" * 13,
                "state": "finalized",
                "expected_size": len(payload),
                "received_bytes": len(payload),
                "blob_sha": sha,
                "expires_at": "2026-05-03T00:00:00Z",
            },
        )
    )

    with SfmApiClient(BASE) as c:
        result = c.upload_bytes(payload)
    assert result == sha
    assert init.called and patch.called and finalize.called

    init_req = init.calls.last.request
    body = init_req.read().decode()
    assert f'"expected_size":{len(payload)}' in body.replace(" ", "")
    assert sha in body  # client passes the precomputed sha


@respx.mock
def test_run_pipeline_routes_to_kind_path() -> None:
    job = {
        "job_id": "JJ" * 13,
        "task_ids": ["T1" * 13, "T2" * 13, "T3" * 13, "T4" * 13],
        "recon_id": "R1" * 13,
    }
    route = respx.post(f"{BASE}/v1/projects/PR/pipelines/incremental").mock(
        return_value=Response(202, json=job)
    )
    with SfmApiClient(BASE) as c:
        result = c.run_pipeline(
            "PR",
            dataset_id="DS",
            spec=IncrementalSpec(),
            features=FeaturesSpec(use_gpu=False),
        )
    assert result.recon_id == "R1" * 13
    assert len(result.task_ids) == 4
    body = route.calls.last.request.read().decode()
    assert '"kind":"incremental"' in body.replace(" ", "")


@respx.mock
def test_validation_error_propagates() -> None:
    respx.post(f"{BASE}/v1/datasets/DS/matches").mock(
        return_value=Response(
            422,
            json={"title": "Validation error", "status": 422, "detail": "vocab missing"},
            headers={"content-type": "application/problem+json"},
        )
    )
    with SfmApiClient(BASE) as c, pytest.raises(ValidationError):
        c.submit_matches("DS", pairs={"strategy": "vocabtree"})


# ----- async -----------------------------------------------------------------


@pytest.mark.asyncio
@respx.mock
async def test_async_create_project_round_trip() -> None:
    respx.post(f"{BASE}/v1/projects").mock(
        return_value=Response(201, json=_project_payload("beta"))
    )
    async with AsyncSfmApiClient(BASE, api_key="sfm_async") as c:
        p = await c.create_project("beta")
    assert p.name == "beta"


@pytest.mark.asyncio
@respx.mock
async def test_async_resume_job() -> None:
    respx.post(f"{BASE}/v1/jobs/J1:resume").mock(
        return_value=Response(
            202,
            json={
                "job_id": "J1",
                "tenant_id": "default",
                "project_id": "PR",
                "recipe": "incremental",
                "status": "pending",
                "cancel_requested": False,
                "cancel_force": False,
                "created_at": "2026-05-02T00:00:00Z",
            },
        )
    )
    async with AsyncSfmApiClient(BASE) as c:
        j = await c.resume_job("J1")
    assert j.status == "pending"
