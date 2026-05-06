# sfmapi

FastAPI service wrapping [colmap_mod](../colmap_mod) (custom COLMAP fork with baxx GPU
bundle adjustment, global SfM, native spherical SfM) plus image segmentation/masking.

See [CLAUDE.md](./CLAUDE.md) for architecture, conventions, and the phase task
breakdowns under [`docs/`](./docs/).

## Quickstart

```bash
uv venv
uv pip install -e ".[dev]"
cp .env.example .env
uv run alembic upgrade head
uv run pytest -q
uv run uvicorn app.main:app --reload
```

## Layout

```
app/
  api/v1/        HTTP routes (NEVER imports pycolmap/torch)
  core/          config, tenancy, hashing, paths, ids
  db/            SQLAlchemy models + alembic
  schemas/       pydantic I/O models
  sources/       ImageSource impls (upload | local | s3)
  storage/       blob store, materializer, snapshot writer
  orchestrator/  in-house Job→Task DAG, lease/janitor, cache lookup
  services/      tenant-scoped CRUD, transactions, DAG construction
  workers/       supervisor + per-task ARQ jobs (subprocess fork)
  adapters/      ONLY heavy-dep importers (pycolmap / torch / cv2)
tests/
  unit/          fast, no IO
  integration/   db + filesystem
  e2e/           full app
docs/            phase task breakdowns
```

Both SQLite and Postgres are supported; CI tests both.
