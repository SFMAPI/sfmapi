# Contributing

## Dev loop

```bash
uv venv
uv pip install -e ".[dev]"
cp .env.example .env
uv run alembic upgrade head
uv run pytest -q
uv run uvicorn app.main:app --reload
```

## Running tests under both DB engines

```bash
bash scripts/test_dual_db.sh                      # SQLite + (Postgres if SFMAPI_DB_URL_PG set or docker available)
bash scripts/test_postgres_local.sh               # ephemeral Postgres in docker
```

## Lint + type

```bash
uv run ruff check app tests
uv run ruff format --check app tests
uv run mypy app
```

## Smoke-testing the deploy

```bash
bash scripts/smoke.sh                # bring up compose, walk API, tear down
bash scripts/smoke.sh --keep         # leave stack up on success
```

## Conventional commits

Commit titles drive the changelog (release-drafter). Use:

| Prefix | Maps to release-drafter category |
|---|---|
| `feat:` / `feat(scope):` | 🚀 Features |
| `fix:` / `fix(scope):` | 🐛 Fixes |
| `perf:` | ⚡ Performance |
| `refactor:` / `chore:` | 🛠 Internal |
| `deps:` / `chore(deps):` | 📦 Dependencies |
| `docs:` | 📚 Docs |
| `ci:` | 🤖 CI |
| `feat!:` / `BREAKING CHANGE:` in body | 💥 Breaking |

`scripts/smoke.sh` and the dual-DB tests are the merge gates; if
either is red, the PR doesn't land.

## Adding a new endpoint

1. Pydantic schema under `app/schemas/api/`.
2. Service function under `app/services/`.
3. Route under `app/api/v1/`, mounted from `app/main.py`.
4. Test under `tests/e2e/` (and `tests/integration/` if it touches
   storage).
5. Update the [API reference](../reference/api.md).
6. If it submits a Task, add the per-task module under
   `app/workers/tasks/` and register it in `app/workers/runner.py`.

The web tier still must not import pycolmap / torch / cv2; the
`test_app_does_not_import_pycolmap_or_torch` unit test enforces that.

## Adding a new pycolmap binding

1. Add the entry-point function in `app/adapters/colmap_adapter.py`
   (lazy import only).
2. If it needs a worker task, add it under `app/workers/tasks/`.
3. Test the adapter with `pytest -m needs_pycolmap` on a CUDA host
   (the GH Actions `worker-tests` workflow does this nightly).
