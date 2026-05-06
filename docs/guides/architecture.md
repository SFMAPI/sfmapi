# Architecture

sfmapi separates a thin always-on **web tier** from one or more
**workers** that drive a registered SfM backend. The web tier never
imports an engine library (pycolmap, torch, segment_anything, ...) —
those live in backend packages outside this repo, accessed only
through the `SfmBackend` Protocol behind the `app/adapters/`
boundary.

State lives in three durable stores: a SQL DB (SQLite or Postgres),
a content-addressed blob store, and a sealed-snapshot directory
tree per reconstruction.

```{mermaid}
flowchart LR
    subgraph Client
        SDK[Generated SDKs<br/>Python · TypeScript · C++]
        UI[CLI / curl / browser]
    end

    subgraph Web["Web tier (in-process)"]
        API[FastAPI app]
        Inline[Inline queue<br/>standalone mode]
        API --- Inline
    end

    subgraph WorkerPkg["Backend package<br/>(separate repo)"]
        Backend["SfmBackend impl<br/>e.g. ColmapModBackend"]
        Backend --> Engine["pycolmap / OpenSfM /<br/>hloc / custom fork"]
    end

    subgraph Persistence
        DB[(SQLite / Postgres)]
        Blobs[(blobs/&lt;sha&gt;)]
        WS[(workspaces/&lt;tenant&gt;/...)]
    end

    subgraph Multi["Multi-instance only (optional)"]
        Redis[(Redis)]
        Sup["Supervisor + workers<br/>per GPU"]
    end

    SDK --> API
    UI --> API
    API -->|writes| DB
    API -->|writes| Blobs
    API -->|reads sealed| WS

    Inline -.->|standalone| Backend
    Sup -.->|polls + leases| DB
    Sup -.->|consumes| Redis
    Sup -.-> Backend
    Backend -->|reads bytes| Blobs
    Backend -->|writes snapshots/{seq}/| WS
    Backend -->|writes events.jsonl| WS
    API -->|tails events.jsonl| WS
```

## Boundaries

| Layer | Imports | Notes |
|---|---|---|
| `app/api/` | only `app.core`, `app.db`, `app.schemas`, `app.services`, `app.orchestrator` | web process. Must start in <2s. |
| `app/services/` | `app.db`, `app.storage`, `app.orchestrator` | tenant-scoped CRUD, transactions, DAG construction |
| `app/orchestrator/` | `app.db`, `app.workers.runner` | DAG, lease, scheduler, recipes, resume |
| `app/workers/` | `app.adapters` only | per-task lease + heartbeat; calls backend through the registry |
| `app/adapters/` | `SfmBackend` Protocol + registry only | no engine imports — engines ship in their own package |

A test (`tests/unit/test_app_starts.py`) enforces that importing
`app.main` does not pull in any engine library (pycolmap, torch,
cv2, segment_anything, ...). CI fails if any of those leak.

## Why a custom DAG instead of using ARQ chains

ARQ is a great task runner, but its `chain` semantics don't model the
properties we need:

- **Per-task cache lookup**: each Task carries
  `(inputs_hash, params_hash, runtime_version_id) → cache_key`; an
  identical Task that has already produced output short-circuits to
  the cached `outputs_ref` without enqueuing.
- **Cancellation atomicity**: a single DB flag + cooperative check
  inside the worker between phases. Hard-kill = subprocess SIGKILL +
  worker restart, marked `cancelled_dirty`.
- **Resumability**: failed tasks reset to `pending` while succeeded
  tasks stay; the cache key is the contract.

ARQ remains the *executor* — one ARQ job = one Task. The DAG itself
lives in `task` rows and `depends_on_json`.

## Why sealed snapshots

Most SfM engines mutate their working state (a SQLite DB, sparse
reconstruction directory, ...) in place. Reading those while the
worker writes them produces torn protobuf, partial JSON, and
sometimes SIGSEGV. The worker periodically copies the live
working state to `snapshots/.tmp_{seq}/` then `os.replace`s the
directory atomically; the API only ever serves data from sealed
`snapshots/{seq}/` dirs.

```{mermaid}
sequenceDiagram
    participant Worker
    participant Disk
    participant API
    participant Client

    Worker->>Disk: write sparse/0/... (in place)
    loop every 50 image registrations
        Worker->>Disk: copy sparse/ -> snapshots/.tmp_42/
        Worker->>Disk: write snapshots/.tmp_42/.complete
        Worker->>Disk: os.replace(.tmp_42, 00000042)
        Worker->>API: emit ProgressEvent(snapshot_available, seq=42)
    end
    Client->>API: GET /reconstructions/R/snapshots/42/points.bin
    API->>Disk: serve immutable file
    API-->>Client: bytes
```

## Why the runtime version vector

SfM backends ship new builds frequently. A reconstruction cached
against backend SHA `abc` is not equivalent to one cached against
`def`, even if the spec is identical. Each cache key salts in the
backend's `runtime_version_id` — a freeform fingerprint string the
backend computes (typically rolled up from engine commit + auxiliary
library shas + CUDA arch + a deterministic seed). When a worker
upgrade swaps the backend or its underlying engine, cached output
invalidates automatically. sfmapi treats the string as opaque; the
backend defines what goes into it.

## Storage layout

```text
workspaces/{tenant_id}/
  blobs/{aa}/{sha256}                 # uploaded bytes (refcounted)
  _cache/s3/{bucket}/{key-hash}       # global S3 LRU
  projects/{pid}/datasets/{did}/
      manifest.json
      masks/{maskset_id}/...
  projects/{pid}/reconstructions/{rid}/
      database.db                     # backend-private; never read by the API
      sparse/{idx}/                   # live, backend-only
      snapshots/{seq}/{idx}/          # sealed, atomic-rename; API reads these
      latest                          # text file: latest sealed seq
      manifest.json
  projects/{pid}/jobs/{jid}/
      log.jsonl                       # per-job structured log
      events.jsonl                    # ProgressEvent stream (SSE replay)
      checkpoints/{seq}.pcmapin       # MappingInput resume points
```

## Further reading

- [Storage abstraction](storage.md): blob store, ImageSource (upload/local/S3), snapshot writer.
- [Jobs and progress](jobs_and_progress.md): DAG, lease, cancellation, SSE.
- [Multi-tenancy](multitenancy.md): the day-1 scaffold, auth, quotas, fair-share.
- [Server modules](../server/orchestrator.md): autodoc reference.
