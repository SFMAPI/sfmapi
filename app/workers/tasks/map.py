"""Mapping task — incremental | global | hierarchical | spherical.

Dispatches to ``backend.run_mapping(kind=...)`` and then runs the
sfmapi-side post-processing: per-submodel snapshot emit, primary-
submodel emit at the flat ``sparse/`` root for the legacy snapshot
read endpoint, and a sealed snapshot.

Resume support is internal to the backend — the colmap_mod backend
writes ``MappingInput`` checkpoints into ``jobs/{job_id}/checkpoints/``
and resumes from the latest one when the same task re-runs. Other
backends may use their own checkpoint format; the interface here just
threads ``job_dir`` through.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.adapters.registry import get_backend
from app.core.config import get_settings
from app.core.errors import ValidationError
from app.core.paths import Paths
from app.db.models import Task
from app.storage.snapshot_emit import emit_snapshot_files
from app.storage.snapshots import SnapshotStore
from app.workers._task_io import read_state


def _num_reg_images(rec: Any) -> int:
    """Backends may expose ``num_reg_images`` as a method (real
    pycolmap.Reconstruction) or as an attribute (test stubs)."""
    nr = getattr(rec, "num_reg_images", 0)
    return int(nr() if callable(nr) else nr)


def run(task: Task) -> dict:
    paths = Paths(get_settings())
    inputs, spec = read_state(task)
    project_id = inputs["project_id"]
    recon_id = inputs["recon_id"]
    db_path = Path(inputs["database_path"])
    image_root = Path(inputs["image_root"])
    job_id = inputs.get("job_id") or task.job_id
    pose_priors = inputs.get("pose_priors") or {}

    rec_root = paths.reconstruction_root(task.tenant_id, project_id, recon_id)
    sparse_root = rec_root / "sparse"
    sparse_root.mkdir(parents=True, exist_ok=True)
    job_dir = paths.job_root(task.tenant_id, project_id, job_id)
    job_dir.mkdir(parents=True, exist_ok=True)

    kind = spec.get("kind", "incremental")
    if kind not in ("incremental", "global", "hierarchical", "spherical"):
        raise ValidationError(f"Unknown mapping kind: {kind!r}")

    summaries, recs = get_backend().run_mapping(
        kind=kind,
        db_path=db_path,
        image_root=image_root,
        sparse_root=sparse_root,
        job_dir=job_dir,
        spec=spec,
        pose_priors=pose_priors,
    )

    # Convert each in-memory Reconstruction into the JSON+binary files
    # the API serves; the largest one is also written flat at sparse_root
    # so legacy `GET /snapshots/{seq}/{name}` callers see a sensible
    # default. Multi-submodel breakdown is preserved under sparse/<idx>/.
    if recs:
        for idx, rec in enumerate(recs):
            emit_snapshot_files(rec, sparse_root / str(idx))
        primary = max(recs, key=_num_reg_images)
        emit_snapshot_files(primary, sparse_root)

    snapshots = SnapshotStore(rec_root)
    seq = (snapshots.latest() or 0) + 1
    sealed = snapshots.seal(seq=seq, source_dir=sparse_root, summary={"models": summaries})
    return {
        "snapshot_seq": seq,
        "snapshot_path": str(sealed),
        "models": summaries,
        "job_dir": str(job_dir),
    }
