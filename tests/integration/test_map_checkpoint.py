"""Test the mapping task's checkpoint handshake without pycolmap.

We monkey-patch the colmap_adapter's lazy import to a fake `pycolmap`
module that mimics the surface needed by `_run_incremental`:
  - `IncrementalPipelineOptions`, `IncrementalPipeline`,
    `ReconstructionManager`, `MappingInput`, `PipelineCallback`.

The fake pipeline registers N synthetic images and invokes the
`NEXT_IMAGE_REG_CALLBACK` once per image. With `checkpoint_every=2` and
6 registrations, we expect 3 checkpoints to land under
`jobs/{job_id}/checkpoints/`.

This exercises the same control flow that the real pycolmap pipeline
goes through, so the test is meaningful even without a CUDA build.
"""

from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest

from app.core.ids import new_id
from app.db.models import Job, Project, RuntimeVersion, Task
from app.storage.mapping_input import list_checkpoints
from app.workers.tasks import map as map_task

pytestmark = pytest.mark.integration


def _build_fake_pycolmap(captured: list[Path]) -> types.SimpleNamespace:
    class FakePipelineCallback:
        NEXT_IMAGE_REG_CALLBACK = "next_image_reg"

    class FakeMappingInput:
        def __init__(self) -> None:
            self._payload = b""

        def from_pipeline(self, pipeline) -> None:
            self._payload = b"PCMAPIN\x00data"

        def save_to_bytes(self) -> bytes:
            return self._payload or b"PCMAPIN\x00fallback"

        def save(self, path: str) -> None:
            Path(path).write_bytes(self._payload or b"PCMAPIN\x00fallback")

        @staticmethod
        def load(path: str) -> FakeMappingInput:
            mi = FakeMappingInput()
            mi._payload = Path(path).read_bytes()
            return mi

    class FakeReconstructionManager:
        def __init__(self) -> None:
            self._models: list[FakeReconstruction] = []

        def __iter__(self):
            return iter(self._models)

        def __bool__(self) -> bool:
            return bool(self._models)

        def add(self, rec) -> None:
            self._models.append(rec)

    class FakeReconstruction:
        def __init__(self, n_imgs: int = 0, n_pts: int = 0) -> None:
            self.num_reg_images = n_imgs
            self.num_points3D = n_pts

    class FakePipeline:
        def __init__(self, *, options, image_path, database_path, reconstruction_manager) -> None:
            self.options = options
            self.rm = reconstruction_manager
            self._cbs: dict[str, list] = {}

        def add_callback(self, kind: str, cb) -> None:
            self._cbs.setdefault(kind, []).append(cb)

        def set_mapping_input(self, mi) -> None:
            captured.append(Path("(loaded mapping input)"))

        def run(self) -> None:
            for i in range(6):
                for cb in self._cbs.get(FakePipelineCallback.NEXT_IMAGE_REG_CALLBACK, []):
                    cb(i)
            self.rm.add(FakeReconstruction(n_imgs=6, n_pts=120))

        def write(self, output_path: str) -> None:
            Path(output_path).mkdir(parents=True, exist_ok=True)
            (Path(output_path) / "0").mkdir(parents=True, exist_ok=True)
            (Path(output_path) / "0" / "marker.txt").write_text("ok")

    class FakeOptions:
        pass

    fake = types.SimpleNamespace(
        IncrementalPipeline=FakePipeline,
        IncrementalPipelineOptions=FakeOptions,
        ReconstructionManager=FakeReconstructionManager,
        MappingInput=FakeMappingInput,
        PipelineCallback=FakePipelineCallback,
    )
    return fake


async def test_incremental_writes_checkpoints(session, monkeypatch, tmp_path: Path) -> None:
    captured: list[Path] = []
    fake = _build_fake_pycolmap(captured)
    monkeypatch.setitem(sys.modules, "pycolmap", fake)

    from app.adapters import colmap_adapter
    from app.core.config import get_settings

    monkeypatch.setattr(get_settings(), "pycolmap_available", True)
    monkeypatch.setattr(colmap_adapter, "_require_pycolmap", lambda: fake)

    rv = RuntimeVersion(
        rv_id=new_id(),
        colmap_sha="x",
        baxx_sha="x",
        cudss_ver="x",
        cuda_arch="x",
        sam_model_sha="x",
        seed="0",
    )
    p = Project(tenant_id="default", name="map-cp")
    session.add_all([rv, p])
    await session.flush()
    j = Job(tenant_id="default", project_id=p.project_id, recipe="incremental")
    session.add(j)
    await session.flush()

    inputs = {
        "project_id": p.project_id,
        "recon_id": new_id(),
        "database_path": str(tmp_path / "database.db"),
        "image_root": str(tmp_path / "images"),
        "job_id": j.job_id,
    }
    spec = {"kind": "incremental", "checkpoint_every": 2}
    t = Task(
        task_id=new_id(),
        tenant_id="default",
        job_id=j.job_id,
        kind="map",
        inputs_hash="i",
        params_hash="p",
        runtime_version_id=rv.rv_id,
        cache_key=new_id(),
        task_state_json={"inputs": inputs, "spec": spec},
    )
    session.add(t)
    await session.commit()

    # Make sure source dir exists so the snapshot copy step doesn't error.
    (tmp_path / "images").mkdir(parents=True, exist_ok=True)

    result = map_task.run(t)
    assert result["models"][0]["num_reg_images"] == 6

    from app.core.paths import Paths

    job_dir = Paths().job_root("default", p.project_id, j.job_id)
    cps = list_checkpoints(job_dir)
    assert len(cps) == 3, [c.seq for c in cps]
    assert cps[0].seq == 1
    assert cps[-1].summary["registered"] == 6
    assert cps[0].path.read_bytes().startswith(b"PCMAPIN\x00")


async def test_incremental_resumes_from_latest_checkpoint(
    session, monkeypatch, tmp_path: Path
) -> None:
    captured: list[Path] = []
    fake = _build_fake_pycolmap(captured)
    monkeypatch.setitem(sys.modules, "pycolmap", fake)
    from app.adapters import colmap_adapter
    from app.core.config import get_settings

    monkeypatch.setattr(get_settings(), "pycolmap_available", True)
    monkeypatch.setattr(colmap_adapter, "_require_pycolmap", lambda: fake)

    rv = RuntimeVersion(
        rv_id=new_id(),
        colmap_sha="x",
        baxx_sha="x",
        cudss_ver="x",
        cuda_arch="x",
        sam_model_sha="x",
        seed="0",
    )
    p = Project(tenant_id="default", name="map-resume")
    session.add_all([rv, p])
    await session.flush()
    j = Job(tenant_id="default", project_id=p.project_id, recipe="incremental")
    session.add(j)
    await session.flush()

    from app.core.paths import Paths
    from app.storage.mapping_input import write_checkpoint

    job_dir = Paths().job_root("default", p.project_id, j.job_id)
    write_checkpoint(job_dir, seq=42, payload=b"PCMAPIN\x00preexisting", summary={"registered": 42})

    inputs = {
        "project_id": p.project_id,
        "recon_id": new_id(),
        "database_path": str(tmp_path / "database.db"),
        "image_root": str(tmp_path / "images"),
        "job_id": j.job_id,
    }
    spec = {"kind": "incremental", "checkpoint_every": 100}
    t = Task(
        task_id=new_id(),
        tenant_id="default",
        job_id=j.job_id,
        kind="map",
        inputs_hash="i",
        params_hash="p",
        runtime_version_id=rv.rv_id,
        cache_key=new_id(),
        task_state_json={"inputs": inputs, "spec": spec},
    )
    session.add(t)
    await session.commit()
    (tmp_path / "images").mkdir(parents=True, exist_ok=True)

    map_task.run(t)
    # set_mapping_input got called -> the captured marker is appended.
    assert captured, "expected resume to call set_mapping_input"
