"""Pose graph optimization."""

from __future__ import annotations

from pathlib import Path

from app.adapters.backend import require_backend_method
from app.db.models import Task
from app.storage.pose_graph_emit import emit_pose_graph_file
from app.workers._task_io import read_state, stage_output_dir
from app.workers.backend_resolver import backend_for_stage
from app.workers.tasks._registry import task_handler


@task_handler("pgo")
def run(task: Task) -> dict:
    inputs, spec = read_state(task)
    out_path = stage_output_dir(root=inputs["reconstruction_root"], task=task, name="pgo")
    backend = backend_for_stage(spec)
    pose_graph_optimize = require_backend_method(
        backend,
        "pose_graph_optimize",
        capability="pgo.optimize",
    )
    read_reconstruction = require_backend_method(
        backend,
        "read_reconstruction",
        capability="pgo.optimize",
        reason="Pose-graph optimization needs read_reconstruction() to emit the sidecar.",
    )
    result = pose_graph_optimize(
        model_path=Path(inputs["model_path"]),
        output_path=out_path,
        spec=spec,
    )
    # The pose-graph sidecar is sfmapi-side post-processing — not
    # something a backend's optimize() call needs to know about. Read
    # the freshly-written model back through the backend so the emitter
    # gets a duck-typed reconstruction it can walk.
    rec = read_reconstruction(out_path)
    emit_pose_graph_file(rec, out_path)
    return result
