# Phase 1 — Orchestrator + Workers + Features/Match/Verify

**Goal:** End-to-end async job execution with sealed-snapshot progress.
First real pycolmap calls: feature extraction, matching, verification.

**Success criteria:**
- `POST /v1/datasets/{did}/features` returns `202 + job_url`; worker runs
  `pycolmap.extract_features`; events stream via SSE.
- Crash a worker mid-job → janitor reclaims; lease handoff works.
- Cooperative cancel works between phases; `?force=true` hard-kills.
- Cache hit: identical `inputs_hash + params_hash + runtime_version` returns
  the prior `outputs_ref` without re-running.

## TDD task list

### 1.1 — Job + Task DAG model

- [ ] `tests/unit/test_dag.py`:
  - Build a DAG `extract → match → verify` from a single
    `FeaturesJob` request; topological order valid; cycle detection
    rejects bad input.
  - Each Task has `inputs_hash`, `params_hash`, `runtime_version_id`,
    `cache_key`. Same inputs/params/rv → same cache_key.
- [ ] `tests/integration/test_task_persistence.py` — write Tasks; query by
      `(job_id, kind, status)`; depends_on serialization round-trips.
- [ ] Implement: tables `job`, `task` in alembic 0002; `app/orchestrator/dag.py`.

### 1.2 — Cache lookup

- [ ] `tests/integration/test_cache_lookup.py`:
  - First run: task enqueued, executes, writes `outputs_ref`.
  - Second run with same cache_key: short-circuits to existing
    `outputs_ref` without enqueue (assert no ARQ job created).
  - Different `runtime_version_id` invalidates: re-enqueues.
- [ ] Implement: `app/orchestrator/scheduler.py::lookup_or_enqueue()`.

### 1.3 — ARQ executor + per-task module

- [ ] `tests/integration/test_arq_runner.py` — start an in-process ARQ
      worker; submit a no-op task; assert task transitions
      `pending → running → succeeded`; lease refreshed during execution.
- [ ] Implement: `app/workers/runner.py` (ARQ Settings with one async fn
      `run_task(ctx, task_id)` that loads the task and dispatches by
      `kind` to a sync handler in `app/workers/tasks/`).

### 1.4 — Supervisor + subprocess fork-per-task

- [ ] `tests/integration/test_supervisor_subprocess.py`:
  - Run a task that consumes 100 MB; assert child exits cleanly.
  - Run a task that sigsegvs; supervisor reaps, marks task
    `failed_cuda`, worker stays alive.
  - Run a task and SIGKILL the child mid-run; supervisor marks
    `cancelled_dirty`.
- [ ] Implement: `app/workers/supervisor.py`. Use `multiprocessing.Process`
      with a `spawn` context; pass task_id and config via pipe; child
      exits via `os._exit`.

### 1.5 — Lease + janitor

- [ ] `tests/integration/test_lease_janitor.py`:
  - Worker A acquires lease; B cannot.
  - Sleep past `LEASE_TTL`; janitor reclaims A's tasks; B can acquire.
  - Janitor never reclaims tasks whose worker is heartbeating.
- [ ] Implement: `app/orchestrator/janitor.py`, `app/orchestrator/lease.py`.

### 1.6 — Cancellation

- [ ] `tests/integration/test_cancel.py`:
  - Cooperative: task with two phases; cancel between → status
    `cancelled`, no further phase runs.
  - Hard-kill: cancel `?force=true` mid-phase; supervisor SIGKILLs;
    status `cancelled_dirty`.
  - CUDA-style fake: simulate a phase that ignores the cancel flag for
    20s; force kill terminates it within `KILL_GRACE` (default 2s).
- [ ] Implement: `app/orchestrator/cancel.py` (DB flag + check helper +
      kill protocol).

### 1.7 — Sealed snapshots

- [ ] `tests/integration/test_snapshots.py`:
  - Worker writes `snapshots/.tmp_{seq}/...`, then `os.replace` to
    `snapshots/{seq}`; API can list seqs and read content of sealed seq.
  - Concurrent reader during seal does not see partial state (assert
    no `ENOENT`/torn data).
  - GC keeps last 3 + final.
- [ ] Implement: `app/storage/snapshots.py` (writer with atomic seal),
      `app/api/v1/submodels.py` GET endpoints (placeholders for Phase 2
      data, but the snapshot machinery is here).

### 1.8 — ProgressEvent + SSE replay

- [ ] `tests/unit/test_progress_event_schema.py` — discriminated union
      validates each kind; unknown kind rejected; schema_version pinned.
- [ ] `tests/integration/test_sse_replay.py`:
  - Worker emits 5 events to `events.jsonl`; SSE client reads all.
  - Client sets `Last-Event-ID: 2`; only events 3-5 replayed; live tail
    works after replay.
  - Server restart: ring buffer survives (events.jsonl on disk).
- [ ] Implement: `app/schemas/progress_event.py`, `app/workers/events.py`,
      `app/api/v1/jobs.py::stream_events` using `sse_starlette`.

### 1.9 — Adapter scaffolding

- [ ] `tests/unit/test_colmap_adapter_lazy.py` — importing
      `app.adapters.colmap_adapter` does not import `pycolmap`. Calling
      any function raises `PycolmapUnavailableError` if
      `SFMAPI_PYCOLMAP_AVAILABLE=false`.
- [ ] Implement: `app/adapters/colmap_adapter.py` with lazy loader and
      version probe (`get_runtime_versions()`).

### 1.10 — `POST /datasets/{did}/features`

- [ ] `tests/e2e/test_features_endpoint.py` (mocked adapter):
  - POST with `FeaturesSpec` returns 202 + job url.
  - Job runs (mocked); database.db materialized under reconstruction
    workspace; events stream; final status `succeeded`.
  - Re-POST same spec returns cached result.
- [ ] `tests/e2e/test_features_endpoint_real.py` (`needs_pycolmap`):
  - Use 4 small fixture images; run real `extract_features`; assert
    keypoints written to `database.db`.
- [ ] Implement: `app/api/v1/datasets.py` (features route),
      `app/workers/tasks/extract.py`,
      `app/schemas/api/features_spec.py`.

### 1.11 — `POST /datasets/{did}/matches`

- [ ] `tests/e2e/test_matches_endpoint.py`:
  - Modes: exhaustive | sequential | spatial | vocabtree (vocab_tree
    path required for vocabtree).
  - Cache: same matches spec on same database → cache hit.
- [ ] `tests/e2e/test_matches_real.py` (`needs_pycolmap`).
- [ ] Implement: `app/api/v1/datasets.py` (matches route),
      `app/workers/tasks/match.py`.

### 1.12 — `POST /datasets/{did}/verify`

- [ ] `tests/e2e/test_verify_endpoint.py` — wraps `verify_matches_batch`.
- [ ] Implement: `app/workers/tasks/verify.py`.

### 1.13 — `POST /datasets/{did}/vlad_index` (optional in Phase 1)

- [ ] Defer to Phase 4 unless trivial; keep stub.

## Definition of done

All boxes ticked. With `SFMAPI_PYCOLMAP_AVAILABLE=true`, a 4-image fixture
runs end-to-end through features → matches → verify, with SSE streaming the
progress.
