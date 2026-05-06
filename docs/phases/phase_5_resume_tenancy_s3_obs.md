# Phase 5 — Resume + Tenant Enforcement + S3 + Observability

**Goal:** Production-shape. Full resume from `MappingInput`. Auth + quotas
enforced. S3 source GA. Prometheus metrics + structured logging.

## TDD task list

### 5.1 — Full resume

- [ ] `tests/e2e/test_resume.py`:
  - Long mapping job killed mid-way; `POST /v1/jobs/{jid}/resume` picks
    up from last `MappingInput` checkpoint; final result equivalent to
    uninterrupted run (modulo seed).
- [ ] Implement: `app/orchestrator/resume.py`; checkpoints written by
      mapping task; resume rebuilds Task DAG starting at last completed
      checkpoint.

### 5.2 — Auth (API keys)

- [ ] `tests/e2e/test_auth_api_keys.py`:
  - `SFMAPI_AUTH_MODE=api_key`: requests without `Authorization` →
    401; with valid key → tenant resolved from key row.
  - Per-tenant key rotation, revocation.
- [ ] Implement: alembic 0006 (`api_key`), `app/core/tenancy.py` upgraded
      `current_tenant` to read from key.

### 5.3 — Quota enforcement

- [ ] `tests/integration/test_quotas.py`:
  - storage quota hit → 413 on next upload.
  - gpu_seconds quota hit → 429 on next job submit.
- [ ] Implement: `app/services/quota_service.py`, hooks at upload + job
      enqueue + write paths.

### 5.4 — Fair-share scheduler

- [ ] `tests/integration/test_fair_share.py` — two tenants submit 10 jobs
      each; scheduler interleaves so no tenant is starved beyond
      `max_consecutive_jobs_per_tenant` (default 2).
- [ ] Implement: `app/orchestrator/scheduler.py` upgraded with priority +
      tenant fairness.

### 5.5 — S3 source GA

- [ ] `tests/integration/test_s3_source.py` (uses `moto`):
  - List, ETag verify, lazy download, LRU eviction at budget.
  - Cache shared across projects in same tenant.
- [ ] Implement: `app/sources/s3.py` (replace stub).

### 5.6 — Prometheus metrics

- [ ] `tests/integration/test_metrics.py`:
  - `/metrics` exposes `sfmapi_job_duration_seconds`,
    `sfmapi_queue_depth`, `sfmapi_active_jobs`,
    `sfmapi_storage_bytes`, `sfmapi_worker_lease_age_seconds`.
- [ ] Implement: `prometheus-client` integration in app + workers.

### 5.7 — Structured logging hardening

- [ ] `tests/unit/test_logging_fields.py` — every log line has
      `tenant_id, project_id, job_id, task_id, phase` when applicable.
      Per-job log file `jobs/{jid}/log.jsonl` mirrors aggregate.
- [ ] Implement: `app/core/logging.py` (structlog) wired into FastAPI +
      ARQ + supervisor.

### 5.8 — Snapshot/job GC

- [ ] `tests/integration/test_gc.py`:
  - Old completed job past TTL → snapshots and dense outputs dropped;
    manifest preserved.
  - Pinned project not GC'd.
- [ ] Implement: GC task scheduled by ARQ cron.

### 5.9 — WebSocket for cancel/peek

- [ ] `tests/e2e/test_ws_jobs.py`:
  - Connect `/ws/v1/jobs/{jid}`; receive events; send cancel via socket.
- [ ] Implement: `app/api/v1/ws_jobs.py` (route prefix already reserved
      from Phase 0).

## Definition of done

All boxes ticked. A multi-tenant test scenario runs end-to-end: two tenants,
quota limits, S3-sourced datasets, full mapping with mid-run resume,
Prometheus scraping clean, logs structured.
