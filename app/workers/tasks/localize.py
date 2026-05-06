"""Localize a single query image against a reconstruction.

Materializes the query image to a local path, then dispatches to
``backend.localize_from_memory(...)``. The returned dict matches the
:class:`app.schemas.api.scene.LocalizationResult` wire shape and is
written to the task's ``outputs_ref_json`` so clients can read it via
``GET /v1/jobs/{job_id}``.
"""

from __future__ import annotations

import contextlib
import os
import shutil
from pathlib import Path

from app.adapters.registry import get_backend
from app.core.config import get_settings
from app.core.errors import ValidationError
from app.core.paths import Paths
from app.db.models import Task
from app.storage.blobs import get_blob_store
from app.workers._task_io import read_state
from app.workers.tasks._registry import task_handler


def _materialize_query(blob_sha: str | None, query_path: str | None, stage: Path) -> Path:
    """Resolve the query image bytes to a local path. ``blob_sha`` (a
    content-addressed upload) takes precedence over an absolute
    ``query_path`` (worker-trusted local file)."""
    stage.mkdir(parents=True, exist_ok=True)
    if blob_sha:
        try:
            src = get_blob_store().local_path(blob_sha)
        except Exception as e:
            raise ValidationError(f"blob_sha {blob_sha} not in blob store") from e
        dst = stage / f"{blob_sha}.jpg"
        if not dst.exists():
            try:
                os.link(src, dst)
            except OSError:
                shutil.copy2(src, dst)
        return dst
    if query_path:
        p = Path(query_path)
        if not p.is_file():
            raise ValidationError(f"query_path {query_path} not found on worker")
        return p
    raise ValidationError("localize: blob_sha or query_path is required")


@task_handler("localize")
def run(task: Task) -> dict:
    inputs, spec = read_state(task)
    sparse_dir = Path(inputs["sparse_dir"])
    blob_sha = inputs.get("blob_sha")
    query_path = inputs.get("query_path")

    paths = Paths(get_settings())
    stage = paths.workspace_root / "_localize_stage" / task.task_id
    img_path = _materialize_query(blob_sha, query_path, stage)
    try:
        return get_backend().localize_from_memory(
            sparse_dir=sparse_dir, query_image=img_path, spec=spec
        )
    finally:
        with contextlib.suppress(OSError):
            shutil.rmtree(stage)
