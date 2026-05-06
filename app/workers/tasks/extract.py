"""Feature extraction task.

Materializes the dataset's images, ensures a `database.db`, calls
`pycolmap.extract_features`, returns a result reference. Sealed snapshot
emission is handled by `app.storage.snapshots.SnapshotStore` and is
optional for this stage (DB-only mutation).

The materialization step is what lets the API stay clean: the HTTP
caller only has to know the dataset_id; this task reads the
`materialization` blob the orchestrator put together (kind + image_list
+ blob_shas / image_root / s3 coords) and produces a real local
directory pycolmap can read.
"""

from __future__ import annotations

from pathlib import Path

from app.adapters.registry import get_backend
from app.core.config import get_settings
from app.core.paths import Paths
from app.db.models import Task
from app.workers._materialize import materialize_image_set
from app.workers._task_io import read_state
from app.workers.tasks._registry import task_handler


def _materialize(task: Task, materialization: dict, paths: Paths) -> tuple[Path, list[str]]:
    """Realize the dataset's images under a per-task stage dir."""
    stage = paths.workspace_root / "_stage" / task.task_id
    return materialize_image_set(materialization, stage)


@task_handler("extract")
def run(task: Task) -> dict:
    s = get_settings()
    paths = Paths(s)
    inputs, spec = read_state(task)
    project_id = inputs["project_id"]
    recon_id = inputs["recon_id"]
    materialization = inputs["materialization"]

    image_root, image_list = _materialize(task, materialization, paths)

    rec_root = paths.reconstruction_root(task.tenant_id, project_id, recon_id)
    rec_root.mkdir(parents=True, exist_ok=True)
    db_path = Path(inputs.get("database_path") or (rec_root / "database.db"))
    summary = get_backend().extract_features(
        database_path=db_path,
        image_root=image_root,
        image_list=image_list,
        options={"sift": spec.get("sift") or {}},
    )
    return {"database_path": str(db_path), **summary}
