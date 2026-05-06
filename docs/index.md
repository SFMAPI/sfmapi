# sfmapi

> **A generic HTTP/REST API for Structure-from-Motion tasks.**
> Backend-agnostic by design — any SfM engine that conforms to the
> [spec](spec.md) can serve it (pycolmap, OpenSfM, hloc, custom
> forks). Sealed-snapshot progress, content-addressed storage,
> multi-tenant from day 1.

::::{grid} 2
:gutter: 3

:::{grid-item-card} 🚀 Five-minute install
:link: guides/quickstart
:link-type: doc

`uv pip install`, `alembic upgrade`, `uvicorn`. SQLite on disk,
filesystem blobs, in-process worker. No Docker, no Redis.
:::

:::{grid-item-card} 🐚 Curl tour
:link: reference/curl_tour
:link-type: doc

Project → upload → dataset → register image → recipe pipeline →
poll → read sealed snapshot. End-to-end in shell.
:::

:::{grid-item-card} 🔌 Implement a backend
:link: guides/backend_implementations
:link-type: doc

sfmapi ships no engine. Make `pycolmap`, OpenSfM, hloc, or your
own fork power the API in one `register_backend()` call.
:::

:::{grid-item-card} 📡 REST API reference
:link: reference/api
:link-type: doc

Resource model, endpoint groups, request/response schemas. The
canonical machine-readable contract is the
[OpenAPI page](reference/openapi.md).
:::

:::{grid-item-card} 🧠 Architecture
:link: guides/architecture
:link-type: doc

How the web tier, orchestrator, workers, and snapshot store fit
together. Why the boundaries exist.
:::

:::{grid-item-card} 📜 Spec
:link: spec
:link-type: doc

`SFMAPI-SPEC.md` — the v1 surface as a standard other tools can
implement. Resource model, conventions, conformance rules.
:::

::::

## What's inside

```{toctree}
:caption: Guides
:maxdepth: 2

guides/quickstart
guides/backend_implementations
guides/architecture
guides/storage
guides/jobs_and_progress
guides/multitenancy
guides/deployment
guides/contributing
```

```{toctree}
:caption: Reference
:maxdepth: 2

reference/api
reference/openapi
reference/auth
reference/curl_tour
reference/errors
reference/configuration
reference/cli
```

```{toctree}
:caption: Server modules
:maxdepth: 1

server/orchestrator
server/storage
server/workers
server/adapters
server/services
```

```{toctree}
:caption: Python SDK
:maxdepth: 2

sdk/index
sdk/sync
sdk/async
sdk/models
sdk/errors
```

```{toctree}
:caption: Decisions & proposals
:maxdepth: 1

guides/decisions
guides/aip_audit_2026
guides/oneshot_streaming_proposal
guides/resume_unification_proposal
guides/sealed_snapshots_on_s3_proposal
guides/rls_postgres_tenancy_proposal
guides/streaming_slam_proposal
```

```{toctree}
:caption: Project
:maxdepth: 1

spec
changelog
GitHub repository <https://github.com/sfmapi/sfmapi>
```

## Status

Pre-release. Wire surface, orchestration shell, three SDKs (Python,
TypeScript, C++) on the `main` branch, dual-DB (SQLite + Postgres)
parity, full CI matrix green, AGPL-3.0-or-later licensed.

This repository ships no concrete SfM backend on purpose — it's the
contract. Backend implementations (pycolmap, OpenSfM, hloc, custom
forks) live in their own packages and register at startup with
`register_backend()`. See the
[decision register](guides/decisions.md) for the locked
architectural decisions and [the changelog](changelog.md) for what
landed in each release.
