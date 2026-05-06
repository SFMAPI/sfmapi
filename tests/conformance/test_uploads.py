"""§6.3 Chunked uploads + §3.7 idempotency."""

from __future__ import annotations

import hashlib

import pytest

pytestmark = pytest.mark.conformance


async def test_full_upload_flow_and_sha_match(conf_client) -> None:
    payload = b"\xff\xd8\xff\xe0conformance" * 100
    expected_sha = hashlib.sha256(payload).hexdigest()
    init = await conf_client.post(
        "/v1/uploads",
        json={"expected_size": len(payload), "expected_sha": expected_sha},
    )
    assert init.status_code == 201
    body = init.json()
    upload_id = body["upload_id"]
    assert body["state"] in ("open", "pending")

    # PATCH chunk in two halves to exercise resume
    half = len(payload) // 2
    a = await conf_client.patch(
        f"/v1/uploads/{upload_id}",
        content=payload[:half],
        headers={"Content-Range": f"bytes 0-{half - 1}/{len(payload)}"},
    )
    assert a.status_code == 200
    b = await conf_client.patch(
        f"/v1/uploads/{upload_id}",
        content=payload[half:],
        headers={"Content-Range": f"bytes {half}-{len(payload) - 1}/{len(payload)}"},
    )
    assert b.status_code == 200

    fin = await conf_client.post(f"/v1/uploads/{upload_id}:finalize", json={})
    assert fin.status_code == 200
    assert fin.json()["blob_sha"] == expected_sha


async def test_idempotency_key_returns_same_upload_id(conf_client) -> None:
    """§3.7 same Idempotency-Key MUST yield the same upload_id."""
    body = {"expected_size": 64}
    headers = {"Idempotency-Key": "conf-idem-key-1"}
    a = await conf_client.post("/v1/uploads", json=body, headers=headers)
    assert a.status_code == 201
    b = await conf_client.post("/v1/uploads", json=body, headers=headers)
    assert b.status_code == 201
    assert a.json()["upload_id"] == b.json()["upload_id"]


async def test_finalize_rejects_sha_mismatch(conf_client) -> None:
    payload = b"abcdefgh"
    init = await conf_client.post(
        "/v1/uploads",
        json={"expected_size": len(payload), "expected_sha": "0" * 64},
    )
    upload_id = init.json()["upload_id"]
    await conf_client.patch(
        f"/v1/uploads/{upload_id}",
        content=payload,
        headers={"Content-Range": f"bytes 0-{len(payload) - 1}/{len(payload)}"},
    )
    fin = await conf_client.post(f"/v1/uploads/{upload_id}:finalize", json={})
    assert fin.status_code == 422
