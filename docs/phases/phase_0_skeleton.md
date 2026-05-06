# Phase 0 — Skeleton + Storage + CRUD

**Goal:** A FastAPI app that you can `pip install`, migrate, run, and use to
create a project, upload images via chunked upload, and create datasets with
either uploaded blobs or a local-path source. Tenant scaffold + cache hash
plumbing + `runtime_versions` table all wired in. **No SfM yet.**

**Success criteria:**
- `uv run pytest -q` passes under both SQLite and Postgres.
- `uv run uvicorn app.main:app` starts and `/healthz` returns 200.
- `POST /v1/projects` → `POST /v1/uploads` → `PATCH /v1/uploads/{id}` →
  `POST /v1/uploads/{id}:finalize` → `POST /v1/datasets/{did}/images` flow
  works end-to-end.
- Same image bytes uploaded twice deduplicate (blob refcount = 2).
- A `LocalPathSource` referencing a 50 GB folder must register without
  copying any bytes.

## TDD task list

### 0.1 — App bootstrap (test-first)

- [ ] `tests/unit/test_app_starts.py::test_app_starts` — assert app builds and
      `/healthz` returns 200, `/version` returns the expected schema. Should
      run with **no env vars** set (defaults must work).
- [ ] `tests/unit/test_app_starts.py::test_app_does_not_import_pycolmap` —
      assert that importing `app.main` does not import `pycolmap`, `torch`,
      or `cv2`. Use `sys.modules` check.
- [ ] Implement: `app/main.py` (FastAPI app, lifespan, router mount),
      `app/api/v1/health.py` (healthz/readyz/version/metrics stub),
      `app/core/config.py` (pydantic Settings, `SFMAPI_*` prefix, sane
      defaults).

### 0.2 — IDs and hashing

- [ ] `tests/unit/test_ids.py` — ULID is 26 chars, sortable in time order,
      unique under tight loop.
- [ ] `tests/unit/test_hashing.py` — `canonical_json` is stable under key
      reorder, idempotent, returns bytes; `content_address(bytes) -> str`
      returns lowercase hex sha256, 64 chars.
- [ ] Implement: `app/core/ids.py`, `app/core/hashing.py`.

### 0.3 — Database + dual-engine

- [ ] `tests/integration/test_db_dual.py` — fixture parametrizes engine
      (`sqlite_aiosqlite`, `postgres_psycopg`); test `engine.connect()`,
      run `alembic upgrade head`, assert tables exist with `tenant_id`
      column NOT NULL on every domain table.
- [ ] `tests/unit/test_lease_pattern.py` — given two simulated workers,
      only one acquires the lease; expired lease is reclaimable.
- [ ] Implement: `app/db/base.py`, `app/db/session.py`, `app/db/types.py`
      (ULID type, JSONType), `app/db/models.py` (initial tables: tenant,
      project, blob, image_source, dataset, image, upload,
      runtime_version), `alembic/env.py`, `alembic/versions/0001_init.py`.
      Lease helper in `app/orchestrator/cancel.py` (or `lease.py`).

### 0.4 — Tenancy scaffold

- [ ] `tests/unit/test_tenancy.py` — `current_tenant()` returns `'default'`
      when `SFMAPI_AUTH_MODE=none`. `TenantScopedSession` injects
      `tenant_id` filter into queries; missing tenant raises.
- [ ] Implement: `app/core/tenancy.py`. Add a `RowFilteringSession` that
      auto-filters via `with_loader_criteria` based on a context var.

### 0.5 — Blob store

- [ ] `tests/integration/test_blob_store.py`:
  - `put_stream(reader)` returns `(sha, size)`, file at
    `blobs/{sha[:2]}/{sha}` exists, mode is read-only.
  - Same bytes twice → same path; refcount increments to 2.
  - `delete(sha)` decrements refcount; deletes file at 0.
  - Streaming a 100 MB file uses bounded memory (assert resident set or
    just stream chunk-size, not whole file).
- [ ] Implement: `app/storage/blobs.py`. Use `tempfile.NamedTemporaryFile`
      in same FS, `os.replace` to seal.

### 0.6 — Chunked upload

- [ ] `tests/integration/test_uploads.py`:
  - `POST /v1/uploads {expected_size, content_type}` with
    `Idempotency-Key` returns `upload_id`; same key returns same id.
  - `PATCH /v1/uploads/{id}` with `Content-Range: bytes 0-9/20` accepts
    partial content; out-of-range returns 416.
  - Resumable: send chunk 0, restart client, GET status returns received
    bitmap, PATCH chunk 1 succeeds.
  - `POST /v1/uploads/{id}:finalize` with optional
    `X-Content-SHA256` returns `{blob_sha, byte_size}`. Mismatched sha
    rejected.
  - Expired upload state GC'd on a periodic task (test calls GC
    directly).
- [ ] Implement: `app/api/v1/uploads.py`, table `upload`,
      `app/services/upload_service.py`.

### 0.7 — ImageSource: upload + local

- [ ] `tests/unit/test_image_source_upload.py` — `UploadSource` materializes
      to a temp dir by hardlinking from the blob store (fallback to copy
      on Windows where hardlink across volumes fails).
- [ ] `tests/integration/test_image_source_local.py` — `LocalPathSource`
      with a temp dir of 5 fake images. `materialize()` returns the same
      dir (no copy); `fingerprint()` returns deterministic dict; mutating
      a file invalidates the fingerprint.
- [ ] `tests/integration/test_local_50gb_simulated.py` — instead of 50 GB,
      use a sparse file pattern; assert no read-the-whole-file behavior
      (use only stat + sample-hash of head/mid/tail).
- [ ] Implement: `app/sources/{base.py, upload.py, local.py}`.
      `s3.py` is a stub raising `NotImplementedError` (Phase 5).

### 0.8 — Projects / datasets / images CRUD

- [ ] `tests/e2e/test_projects.py` — POST/GET/LIST/DELETE happy paths,
      tenant isolation (a record from a different tenant_id is invisible).
- [ ] `tests/e2e/test_datasets.py` — create dataset with
      `source: {kind: upload, blob_shas: [...]}` and with
      `source: {kind: local, root: ...}`. Camera model, intrinsics_mode,
      is_spherical, rig_config_json fields are persisted.
- [ ] `tests/e2e/test_images.py` — POST image (by blob_sha, name);
      duplicates by `(dataset_id, name)` rejected; listing paginates.
      `dataset.manifest_hash` recomputed on add/delete (deterministic).
- [ ] Implement: `app/api/v1/{projects,datasets,images}.py`,
      `app/services/{project_service,dataset_service,image_service}.py`,
      `app/schemas/api/`.

### 0.9 — runtime_versions

- [ ] `tests/integration/test_runtime_version.py` — at startup, a row is
      ensured for the current
      `(colmap_sha, baxx_sha, cudss_ver, cuda_arch, sam_model_sha, seed)`
      tuple read from settings. Same tuple → same id (no duplicate).
      Different tuple → new id.
- [ ] Implement: `app/services/runtime_version_service.py`, called from
      lifespan.

### 0.10 — Linting / typing / dual-DB CI

- [ ] `scripts/test_dual_db.sh` and `.ps1` — runs pytest under both
      engines, fails if either fails.
- [ ] `mypy app` clean.
- [ ] `ruff check .` and `ruff format --check .` clean.

## Definition of done

All boxes ticked, all tests pass under both SQLite and Postgres, mypy clean,
ruff clean, README quickstart steps reproduce.
