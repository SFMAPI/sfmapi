"""CLI smoke tests via Click's CliRunner + respx HTTP mocks."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import respx
from click.testing import CliRunner
from httpx import Response

from sfmapi_client.cli.main import cli

BASE = "http://api.test"


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


def _common(*args: str, json_out: bool = False) -> list[str]:
    out = ["--base-url", BASE, "--api-key", "sfm_test"]
    if json_out:
        out.append("--json")
    out.extend(args)
    return out


@respx.mock
def test_health_check(runner: CliRunner) -> None:
    respx.get(f"{BASE}/healthz").mock(
        return_value=Response(200, json={"status": "ok"}),
    )
    r = runner.invoke(cli, _common("health", "check", json_out=True))
    assert r.exit_code == 0, r.output
    assert json.loads(r.output) == {"status": "ok"}


@respx.mock
def test_projects_create_table_output(runner: CliRunner) -> None:
    respx.post(f"{BASE}/v1/projects").mock(
        return_value=Response(
            201,
            json={
                "project_id": "P" * 26,
                "tenant_id": "default",
                "name": "alpha",
                "description": None,
                "created_at": "2026-05-02T00:00:00Z",
            },
        ),
    )
    r = runner.invoke(cli, _common("projects", "create", "alpha"))
    assert r.exit_code == 0, r.output
    assert "alpha" in r.output


@respx.mock
def test_projects_list_renders_rows(runner: CliRunner) -> None:
    respx.get(f"{BASE}/v1/projects").mock(
        return_value=Response(
            200,
            json={
                "items": [
                    {
                        "project_id": "P" * 26,
                        "tenant_id": "default",
                        "name": "alpha",
                        "description": None,
                        "created_at": "2026-05-02T00:00:00Z",
                    }
                ],
                "next_page_token": None,
                "total": None,
            },
        ),
    )
    r = runner.invoke(cli, _common("projects", "list"))
    assert r.exit_code == 0, r.output
    assert "alpha" in r.output


@respx.mock
def test_uploads_file_prints_sha(tmp_path: Path, runner: CliRunner) -> None:
    payload = b"\xff\xd8\xff\xe0test-bytes"
    p = tmp_path / "img.jpg"
    p.write_bytes(payload)

    respx.post(f"{BASE}/v1/uploads").mock(
        return_value=Response(
            201,
            json={
                "upload_id": "U" * 26,
                "state": "open",
                "expected_size": len(payload),
                "received_bytes": 0,
                "blob_sha": None,
                "expires_at": "2026-05-03T00:00:00Z",
            },
        ),
    )
    respx.patch(f"{BASE}/v1/uploads/{'U' * 26}").mock(
        return_value=Response(
            200,
            json={
                "upload_id": "U" * 26,
                "state": "received",
                "expected_size": len(payload),
                "received_bytes": len(payload),
                "blob_sha": None,
                "expires_at": "2026-05-03T00:00:00Z",
            },
        ),
    )
    import hashlib

    sha = hashlib.sha256(payload).hexdigest()
    respx.post(f"{BASE}/v1/uploads/{'U' * 26}:finalize").mock(
        return_value=Response(
            200,
            json={
                "upload_id": "U" * 26,
                "state": "finalized",
                "expected_size": len(payload),
                "received_bytes": len(payload),
                "blob_sha": sha,
                "expires_at": "2026-05-03T00:00:00Z",
            },
        ),
    )

    r = runner.invoke(cli, _common("uploads", "file", str(p)))
    assert r.exit_code == 0, r.output
    assert sha in r.output


@respx.mock
def test_pipelines_run_default_incremental(runner: CliRunner) -> None:
    respx.post(f"{BASE}/v1/projects/PR/pipelines/incremental").mock(
        return_value=Response(
            202,
            json={
                "job_id": "J" * 26,
                "task_ids": ["T" * 26] * 4,
                "recon_id": "R" * 26,
            },
        ),
    )
    r = runner.invoke(
        cli,
        _common(
            "pipelines",
            "run",
            "PR",
            "--dataset-id",
            "DS",
            json_out=True,
        ),
    )
    assert r.exit_code == 0, r.output
    body = json.loads(r.output)
    assert body["recon_id"] == "R" * 26


@respx.mock
def test_jobs_get_renders_tasks(runner: CliRunner) -> None:
    respx.get(f"{BASE}/v1/jobs/J1").mock(
        return_value=Response(
            200,
            json={
                "job_id": "J1",
                "tenant_id": "default",
                "project_id": "PR",
                "recipe": "incremental",
                "status": "running",
                "cancel_requested": False,
                "cancel_force": False,
                "created_at": "2026-05-02T00:00:00Z",
                "tasks": [
                    {
                        "task_id": "T1" * 13,
                        "job_id": "J1",
                        "kind": "extract",
                        "status": "succeeded",
                        "cache_key": "abcd" * 16,
                        "inputs_hash": "x" * 64,
                        "params_hash": "y" * 64,
                        "outputs_ref": {"num_keypoints": 1024},
                    }
                ],
            },
        ),
    )
    r = runner.invoke(cli, _common("jobs", "get", "J1"))
    assert r.exit_code == 0, r.output
    assert "extract" in r.output
    assert "succeeded" in r.output


@respx.mock
def test_snapshots_get_writes_file(tmp_path: Path, runner: CliRunner) -> None:
    body = b"hello-snapshot"
    respx.get(f"{BASE}/v1/reconstructions/R1/snapshots/3/cameras.json").mock(
        return_value=Response(200, content=body),
    )
    out = tmp_path / "cam.json"
    r = runner.invoke(
        cli, _common("snapshots", "get", "R1", "3", "cameras.json", "--out", str(out))
    )
    assert r.exit_code == 0, r.output
    assert out.read_bytes() == body
