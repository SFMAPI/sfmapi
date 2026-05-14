"""Standalone bundle adjustment — produces a new SubModel revision.

Supports two algorithms via ``spec.mode`` (see
:class:`app.schemas.pipeline_spec.BundleAdjustmentSpec`):

  - ``standard`` (default): single solve over all parameters.
  - ``two_stage``: a poses-only pass, then a full unlock pass —
    requires the backend to expose ``two_stage_bundle_adjustment``
    (capability ``ba.two_stage``).
"""

from __future__ import annotations

from pathlib import Path

from app.adapters.backend import require_backend_method
from app.core.capabilities import require as require_capability
from app.db.models import Task
from app.workers._task_io import read_state
from app.workers.backend_resolver import backend_for_stage
from app.workers.options import stage_options
from app.workers.tasks._registry import task_handler


@task_handler("ba")
def run(task: Task) -> dict:
    inputs, spec = read_state(task)
    mode = (spec.get("mode") or "standard").lower()
    if mode == "two_stage":
        require_capability("ba.two_stage")
    backend = backend_for_stage(spec)
    bundle_adjustment = require_backend_method(
        backend,
        "bundle_adjustment",
        capability="ba.two_stage" if mode == "two_stage" else "ba.standard",
    )
    return bundle_adjustment(
        model_path=Path(inputs["model_path"]),
        output_path=Path(inputs["output_path"]),
        spec=stage_options(spec),
    )
