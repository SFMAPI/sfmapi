"""Geometric verification task."""

from __future__ import annotations

import contextlib
from pathlib import Path

from app.adapters.registry import get_backend
from app.db.models import Task
from app.storage.two_view_emit import export_two_view_geometries
from app.workers._task_io import read_state
from app.workers.tasks._registry import task_handler


@task_handler("verify")
def run(task: Task) -> dict:
    inputs, spec = read_state(task)
    db_path = Path(inputs["database_path"])
    backend = get_backend()
    summary = backend.verify_matches(database_path=db_path, options=spec)

    # Export the verified two-view geometries as a wire-stable JSON sidecar
    # next to the database. Best-effort: failure here doesn't fail verify.
    out: dict = {"database_path": str(db_path), **summary}
    with contextlib.suppress(Exception):
        written = export_two_view_geometries(
            backend.iter_two_view_geometries(database_path=db_path), db_path.parent
        )
        out["two_view_geometries_path"] = str(written)
    return out
