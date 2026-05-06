# Phase 4 — Global / Hierarchical / Spherical + VLAD + Recipes

**Goal:** Surface the rest of pycolmap's mapping backends. Cubemap
rendering for spherical. Pipeline recipe sugar.

**Success criteria:**
- `global_mapper`, `hierarchical_mapper`, `panorama_mapping`,
  `spherical_mapping` all callable via the same submodel-producing
  interface.
- `IncrementalVLADIndex` exposed for incremental matching.
- `POST /v1/projects/{pid}/pipelines/{recipe}` chains the right Tasks for
  each recipe.

## TDD task list

### 4.1 — GlobalSpec / HierarchicalSpec

- [ ] `tests/unit/test_pipeline_spec_variants.py` — discriminated union
      accepts each variant; unknown `kind` rejected.
- [ ] `tests/e2e/test_global_map.py` (`needs_pycolmap`) — small fixture
      (>=15 images for GP threshold per colmap_mod) → global_mapper run.
- [ ] `tests/e2e/test_hierarchical_map.py` (`needs_pycolmap`).
- [ ] Implement: `IncrementalSpec | GlobalSpec | HierarchicalSpec |
      SphericalSpec` discriminated union; tasks dispatch by `kind`.

### 4.2 — Spherical / panorama

- [ ] `tests/e2e/test_panorama_map.py` (`needs_pycolmap`) — small
      panoramic fixture (or synthesized cubemap). Wraps
      `panorama_mapping`.
- [ ] `tests/integration/test_spherical_camera_route.py` — Dataset with
      `is_spherical=true` routes to spherical extract/match path.
- [ ] `tests/e2e/test_cubemap_endpoints.py`:
  - `POST /v1/datasets/{did}/render_cubemap` — wraps
    `render_spherical_cubemap_images`.
  - `POST /v1/reconstructions/{rid}/convert_to_cubemap` — wraps
    `convert_spherical_reconstruction_to_cubemap`.
- [ ] Implement: tasks + routes.

### 4.3 — VLAD index

- [ ] `tests/e2e/test_vlad_index.py` — `POST /v1/datasets/{did}/vlad_index
      {images}` builds incrementally; status retrievable.
- [ ] Implement: `app/workers/tasks/vlad.py`.

### 4.4 — Recipe endpoint

- [ ] `tests/e2e/test_pipeline_recipe.py`:
  - `POST /v1/projects/{pid}/pipelines/incremental {dataset_id, ...}`
    creates a Job whose DAG is
    extract → match → verify → incremental_map → ba.
  - Each Task's cache_key is independent; resubmitting with one param
    changed re-runs only the affected suffix.
- [ ] Implement: `app/api/v1/pipelines.py`, recipe builders in
      `app/orchestrator/recipes.py`.

### 4.5 — Advanced helpers

- [ ] Wrap `two_pass_reconstruction`, `adaptive_reconstruction`,
      `match_and_verify_adaptive` as recipes (no new tasks; just specific
      DAG shapes).

## Definition of done

All boxes ticked. Each of `incremental | global | hierarchical | spherical`
recipes runs an appropriate fixture end-to-end.
