# sfmapi

> A FastAPI service that wraps a custom [pycolmap](https://github.com/opsiclear/colmap_mod)
> for Structure-from-Motion, plus image segmentation and masking. Sealed-snapshot
> progress, content-addressed storage, multi-tenant from day 1.

::::{grid} 2
:gutter: 3

:::{grid-item-card} 📜 Spec
:link: spec
:link-type: doc

`SFMAPI-SPEC.md` — the v1 surface as a standard other tools can
implement. Resource model, conventions, conformance rules.
:::

:::{grid-item-card} 🚀 Get started
:link: guides/quickstart
:link-type: doc

Stand up the docker-compose stack, install a worker on a GPU host,
issue an API key, fire off a reconstruction.
:::

:::{grid-item-card} 🧠 Architecture
:link: guides/architecture
:link-type: doc

How the web tier, orchestrator, workers, and snapshot store fit
together. Why the boundaries exist.
:::

:::{grid-item-card} 📡 REST API reference
:link: reference/api
:link-type: doc

All v1 endpoints, request/response schemas, error model.
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
:caption: Project
:maxdepth: 1

spec
changelog
GitHub repository <https://github.com/opsiclear/sfmapi>
```

## Status

Production-shape but young: 94 tests passing on `main`, four CI
workflows, dual-DB (SQLite + Postgres) parity, full Phase 0–5
implementation. See [the changelog](changelog.md) for what landed in
each release.
