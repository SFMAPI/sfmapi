from __future__ import annotations

import hashlib

import pytest

pytestmark = pytest.mark.e2e


async def test_upload_init_patch_finalize(client) -> None:
    payload = b"hello-sfmapi-bytes-12345" * 1000
    expected_sha = hashlib.sha256(payload).hexdigest()
    init = await client.post(
        "/v1/uploads",
        json={"expected_size": len(payload), "expected_sha": expected_sha},
        headers={"Idempotency-Key": "abc"},
    )
    assert init.status_code == 201, init.text
    upload_id = init.json()["upload_id"]

    chunk_size = 4096
    offset = 0
    while offset < len(payload):
        chunk = payload[offset : offset + chunk_size]
        last = offset + len(chunk) - 1
        resp = await client.patch(
            f"/v1/uploads/{upload_id}",
            content=chunk,
            headers={"Content-Range": f"bytes {offset}-{last}/{len(payload)}"},
        )
        assert resp.status_code == 200, resp.text
        offset += len(chunk)

    fin = await client.post(f"/v1/uploads/{upload_id}:finalize")
    assert fin.status_code == 200, fin.text
    body = fin.json()
    assert body["state"] == "finalized"
    assert body["blob_sha"] == expected_sha


async def test_idempotency_returns_same_upload(client) -> None:
    a = await client.post(
        "/v1/uploads",
        json={"expected_size": 16},
        headers={"Idempotency-Key": "kkk"},
    )
    b = await client.post(
        "/v1/uploads",
        json={"expected_size": 16},
        headers={"Idempotency-Key": "kkk"},
    )
    assert a.status_code == 201
    assert b.status_code == 201
    assert a.json()["upload_id"] == b.json()["upload_id"]


async def test_resume_chunk_after_status(client) -> None:
    payload = b"x" * 64
    init = await client.post("/v1/uploads", json={"expected_size": len(payload)})
    upload_id = init.json()["upload_id"]
    half = payload[:32]
    resp = await client.patch(
        f"/v1/uploads/{upload_id}",
        content=half,
        headers={"Content-Range": f"bytes 0-31/{len(payload)}"},
    )
    assert resp.status_code == 200
    status = await client.get(f"/v1/uploads/{upload_id}")
    assert status.json()["received_bytes"] == 32

    second = payload[32:]
    resp = await client.patch(
        f"/v1/uploads/{upload_id}",
        content=second,
        headers={"Content-Range": f"bytes 32-63/{len(payload)}"},
    )
    assert resp.status_code == 200
    fin = await client.post(f"/v1/uploads/{upload_id}:finalize")
    assert fin.json()["state"] == "finalized"


async def test_finalize_rejects_sha_mismatch(client) -> None:
    payload = b"abcdefgh"
    init = await client.post(
        "/v1/uploads",
        json={
            "expected_size": len(payload),
            "expected_sha": "0" * 64,
        },
    )
    upload_id = init.json()["upload_id"]
    await client.patch(
        f"/v1/uploads/{upload_id}",
        content=payload,
        headers={"Content-Range": f"bytes 0-{len(payload) - 1}/{len(payload)}"},
    )
    fin = await client.post(f"/v1/uploads/{upload_id}:finalize")
    assert fin.status_code == 422, fin.text
