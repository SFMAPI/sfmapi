"""Mesh generation — Poisson / Delaunay.

Calls ``backend.generate_mesh(...)`` and seals a fresh snapshot with
``mesh.ply`` + ``mesh.json`` (per :class:`app.schemas.api.scene.MeshFile`).
"""

from __future__ import annotations

import json
from pathlib import Path

from app.adapters.registry import get_backend
from app.core.errors import ValidationError
from app.db.models import Task
from app.schemas.api.scene import MeshFile, MeshSummary
from app.storage._atomic import write_text as _atomic_write_text
from app.storage.snapshot_emit import emit_snapshot_files
from app.storage.snapshots import SnapshotStore
from app.workers._task_io import read_state


def run(task: Task) -> dict:
    inputs, spec = read_state(task)
    rec_root = Path(inputs["reconstruction_root"])
    sparse_dir = Path(inputs["sparse_dir"])
    method = (spec.get("method") or "poisson").lower()
    options = spec.get("options") or {}

    if not sparse_dir.is_dir():
        raise ValidationError(f"sparse dir does not exist: {sparse_dir}")

    out_dir = rec_root / "_mesh" / task.task_id
    out_dir.mkdir(parents=True, exist_ok=True)

    # Reuse the latest sealed snapshot's dense fused.bin if present (Poisson
    # gives much better results from dense point clouds than sparse ones).
    dense_fused = None
    snapshots = SnapshotStore(rec_root)
    latest_seq = snapshots.latest()
    if latest_seq is not None:
        candidate = snapshots.path_for(latest_seq) / "dense" / "fused.bin"
        if candidate.is_file():
            dense_fused = candidate

    mesh_path = out_dir / "mesh.ply"
    summary_dict = get_backend().generate_mesh(
        sparse_dir=sparse_dir,
        dense_fused_path=dense_fused,
        output_path=mesh_path,
        method=method,
        options=options,
    )

    summary = MeshSummary(**summary_dict)
    manifest = MeshFile(summary=summary)
    _atomic_write_text(
        out_dir / "mesh.json",
        json.dumps(manifest.model_dump(by_alias=True, mode="json"), indent=2, sort_keys=True),
    )

    # Also emit the snapshot scene files so the new snapshot is a complete
    # readable unit (cameras/images/points + the mesh sidecar).
    rec = get_backend().read_reconstruction(sparse_dir)
    emit_snapshot_files(rec, out_dir)

    seq = (snapshots.latest() or 0) + 1
    sealed = snapshots.seal(
        seq=seq,
        source_dir=out_dir,
        summary={"phase": "mesh", "method": method, **summary_dict},
    )
    return {
        "snapshot_seq": seq,
        "snapshot_path": str(sealed),
        "mesh_path": str(mesh_path),
        **summary_dict,
    }
