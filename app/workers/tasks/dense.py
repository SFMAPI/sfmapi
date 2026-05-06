"""Dense MVS — undistort → patch_match_stereo → stereo_fusion.

Dispatches the whole dense pipeline to ``backend.dense_pipeline(...)``,
which produces the sealed-snapshot directory layout (sparse-model
emit at the top, ``dense/`` subdirectory with the per-image depth /
normal maps in sfmapi wire formats and a ``fused.bin`` dense cloud).
The worker just seals the directory.
"""

from __future__ import annotations

from pathlib import Path

from app.adapters.registry import get_backend
from app.core.errors import ValidationError
from app.db.models import Task
from app.storage.snapshots import SnapshotStore
from app.workers._task_io import read_state


def run(task: Task) -> dict:
    inputs, spec = read_state(task)
    rec_root = Path(inputs["reconstruction_root"])
    sparse_dir = Path(inputs["sparse_dir"])
    image_root = Path(inputs["image_root"])
    if not sparse_dir.is_dir():
        raise ValidationError(f"sparse dir does not exist: {sparse_dir}")
    if not image_root.is_dir():
        raise ValidationError(f"image_root does not exist: {image_root}")

    workspace = rec_root / "_dense" / task.task_id
    workspace.mkdir(parents=True, exist_ok=True)
    out_dir = rec_root / "_dense_seal" / task.task_id
    out_dir.mkdir(parents=True, exist_ok=True)

    result = get_backend().dense_pipeline(
        sparse_dir=sparse_dir,
        image_root=image_root,
        workspace=workspace,
        out_dir=out_dir,
        spec=spec,
    )

    snapshots = SnapshotStore(rec_root)
    seq = (snapshots.latest() or 0) + 1
    sealed = snapshots.seal(
        seq=seq,
        source_dir=out_dir,
        summary={
            "phase": "dense",
            "num_depth_maps": result.get("num_depth_maps", 0),
            "fused_points": result.get("fused_points", 0),
        },
    )
    return {
        "snapshot_seq": seq,
        "snapshot_path": str(sealed),
        "num_depth_maps": result.get("num_depth_maps", 0),
        "fused_points": result.get("fused_points", 0),
    }
