# Phase 2 — Incremental SfM + Standalone Ops + Diagnostics

**Goal:** Run real reconstructions. Expose all the piecewise pycolmap ops
that real workflows need (BA, triangulate, relocalize, PGO, merge/split,
diagnostics). Paginated reads + binary points format. Streamed exports.

**Success criteria:**
- 4-image fixture → incremental_mapping → SubModel sealed; cameras / images
  / points readable via API; PLY export downloads.
- BA / triangulate / relocalize on existing SubModel produce a new revision
  (parent_submodel_id pointer correct).
- `assess_translation_rigidity()` exposed as diagnostics endpoint.
- Snapshot stream emits `phase_progress` mid-mapping (image registration
  progress visible).

## TDD task list

### 2.1 — Reconstruction + SubModel data model

- [ ] `tests/integration/test_reconstruction_model.py` — Reconstruction has
      N SubModels (`sparse/0`, `sparse/1`...). SubModel has
      `parent_submodel_id` for revisions. Cache key includes
      `dataset_snapshot_hash` (manifest hash at time of run).
- [ ] Implement: alembic 0003 (`reconstruction`, `submodel`).

### 2.2 — Mapping task: incremental

- [ ] `tests/e2e/test_incremental_map.py` (`needs_pycolmap`):
  - 8-image fixture → incremental_mapping → at least one sub-model
    written; sealed snapshot exists; `summary()` JSON has expected
    fields.
  - `IncrementalSpec` Pydantic model (`version=1`) maps to
    pycolmap options inside adapter only. Cache hit on resubmit.
- [ ] `tests/integration/test_mapping_callbacks.py` — callbacks emit
      `incremental_init`, `incremental_register {current,total}`,
      `incremental_ba` events. `snapshot_frames_freq` triggers a sealed
      snapshot.
- [ ] Implement: `app/workers/tasks/map.py`, `IncrementalSpec` schema,
      callback wiring.

### 2.3 — MappingInput checkpoints

- [ ] `tests/integration/test_mapping_input_checkpoint.py` — between two
      stages, `MappingInput.save(path)` and `.load(path)` round-trip.
      Used as the canonical handoff format. (`PCMAPIN\0` v1 from
      colmap_mod.)
- [ ] Implement: helpers in `app/adapters/colmap_adapter.py`.

### 2.4 — Standalone bundle adjustment

- [ ] `tests/e2e/test_bundle_adjust.py`:
  - `POST /v1/submodels/{smid}/bundle_adjust {BAOptions}` → new
    SubModel revision with `parent_submodel_id = smid`.
  - Cache: same options on same parent → hit.
- [ ] Implement: `app/api/v1/submodels.py`, `app/workers/tasks/ba.py`.

### 2.5 — Standalone triangulate

- [ ] `tests/e2e/test_triangulate.py` — re-triangulate against a fresh
      database; new revision points3D count differs from parent.
- [ ] Implement: `app/workers/tasks/triangulate.py`.

### 2.6 — Relocalization

- [ ] `tests/e2e/test_relocalize.py` (`needs_pycolmap`):
  - Existing reconstruction + N new images already in DB →
    `POST /v1/submodels/{smid}/relocalize {image_ids}` →
    revision with the new images registered.
  - Wraps `relocalize_images` / `relocalize_images_from_cache`.
- [ ] Implement: `app/workers/tasks/relocalize.py`.

### 2.7 — Pose graph optimization

- [ ] `tests/e2e/test_pgo.py`:
  - `POST /v1/submodels/{smid}/pose_graph_optimize` → revision; wraps
    `optimize_pose_graph` (linear_solver_type hardcoded
    ITERATIVE_SCHUR per colmap_mod CLAUDE).
- [ ] Implement: `app/workers/tasks/pgo.py`.

### 2.8 — Merge / split

- [ ] `tests/e2e/test_merge_split.py`:
  - Reconstruction with 3 sub-models → merge two → new SubModel.
  - `split_reconstruction_by_bboxes` produces N children.
- [ ] Implement: corresponding endpoints + tasks.

### 2.9 — Diagnostics

- [ ] `tests/integration/test_diagnostics.py`:
  - SubModel diagnostics returns
    `{rigidity, mean_reproj_err, num_reg_images, num_points3D,
      num_submodels, track_len_histogram, reproj_err_histogram}`.
  - Rigidity from `assess_translation_rigidity()`:
    `sigma_0/1/2, anisotropy, planarity, near_degenerate`.
- [ ] Implement: `app/services/reconstruction_service.py::diagnostics()`,
      route on `submodels.py`.

### 2.10 — Paginated reads (binary points)

- [ ] `tests/unit/test_points_binary.py` — encode/decode round-trips. 32 B
      header magic = `SFMP3D\0\0`; 26 B record little-endian.
- [ ] `tests/integration/test_points_pagination.py`:
  - `GET /v1/submodels/{smid}/snapshots/{seq}/points` returns content
    type `application/x-sfm-points-v1`.
  - HTTP `Range: bytes=32-... ` returns subrange.
  - `?preview=true` returns the precomputed
    `points_preview.bin` (decimated).
- [ ] Implement: `app/schemas/points_binary.py` (encoder/decoder),
      `app/storage/snapshots.py::seal()` writes both `points.bin` and
      `points_preview.bin` + `points.meta.json`.

### 2.11 — Cameras / images / rigs / frames / observations reads

- [ ] `tests/integration/test_submodel_reads.py`:
  - `GET .../cameras` returns full list as JSON (small).
  - `GET .../images?cursor=&limit=` cursor-paginates.
  - `GET .../rigs`, `GET .../frames` reflect rig/frame model.
  - `GET .../observations?image_id=` returns the image's track.
- [ ] Implement: encoded into `snapshots/{seq}/{cameras,images,...}.json`
      at seal time; read directly from disk.

### 2.12 — Export

- [ ] `tests/e2e/test_export.py`:
  - `format=ply|nvm|colmap_text|colmap_bin` — for small fixture, exports
    download with correct content-type and non-trivial size.
  - Exports stream with `StreamingResponse`; large file does not OOM
    (assert constant memory).
- [ ] Implement: `app/api/v1/submodels.py::export`,
      `app/workers/tasks/export.py` (writes export under
      `snapshots/{seq}/exports/`).

### 2.13 — DB-mutating ops (first-class)

- [ ] `tests/e2e/test_db_mutate.py`:
  - `DELETE /v1/datasets/{did}/images/{name}` removes image + its
    features/matches from `database.db` (via `pycolmap.Database`).
  - `POST /v1/datasets/{did}/match_subset {image_ids}` re-matches a
    subset.
- [ ] Implement: routes + tasks + adapter wrappers.

## Definition of done

All boxes ticked. A real 8-image fixture runs end-to-end:
features → matches → verify → incremental_mapping → bundle_adjust →
relocalize (with 2 extra images) → diagnostics → export PLY. SSE shows
progress at each phase boundary; sealed snapshots accumulate.
