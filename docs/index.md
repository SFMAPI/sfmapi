# sfmapi

> A FastAPI service that wraps a custom [pycolmap](https://github.com/opsiclear/colmap_mod)
> for Structure-from-Motion, plus image segmentation and masking. Sealed-snapshot
> progress, content-addressed storage, multi-tenant from day 1.

::::{grid} 2
:gutter: 3

:::{grid-item-card} 🚀 Get started
:link: guides/quickstart
:link-type: doc

Stand up the docker-compose stack, install a worker on a GPU host,
issue an API key, fire off a reconstruction.
:::

:::{grid-item-card} 🐚 5-minute curl tour
:link: reference/curl_tour
:link-type: doc

Project → upload → dataset → register image → recipe pipeline →
poll → read sealed snapshot. End-to-end in shell.
:::

:::{grid-item-card} 📡 REST API reference
:link: reference/api
:link-type: doc

Resource model, endpoint groups, request/response schemas. The
canonical machine-readable contract is the [OpenAPI page](reference/openapi.md).
:::

:::{grid-item-card} 🔐 Authentication
:link: reference/auth
:link-type: doc

`auth_mode=none` (default, dev) vs `auth_mode=api_key` (multi-tenant).
Issuing keys, revocation, tenant boundaries.
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
guides/architecture
guides/storage
guides/jobs_and_progress
guides/multitenancy
guides/deployment
guides/contributing
```

```{toctree}
:caption: Phase task breakdowns
:maxdepth: 1

phases/phase_0_skeleton
phases/phase_1_orchestrator_features_match
phases/phase_2_incremental_sfm
phases/phase_3_segmentation
phases/phase_4_global_spherical
phases/phase_5_resume_tenancy_s3_obs
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

Production-shape but young: 94 tests passing on `main`, four CI
workflows, dual-DB (SQLite + Postgres) parity, full Phase 0–5
implementation. See [the changelog](changelog.md) for what landed in
each release.
