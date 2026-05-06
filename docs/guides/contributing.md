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

The web tier must not import any engine library (pycolmap, torch,
cv2, segment_anything, ...); the
`test_app_does_not_import_pycolmap_or_torch` unit test enforces that
boundary.

## Adding a new backend or backend method

sfmapi ships no concrete SfM backend; engine packages live in their
own repos and satisfy ``app.adapters.backend.SfmBackend``.

1. Implement the protocol in your backend package; raise
   ``CapabilityUnavailableError`` for ops you don't support and
   advertise the supported subset via ``capabilities()``.
2. Register the factory at app startup:
   ``register_backend("name", MyBackend)``.
3. If a new wire op is needed (a method not yet on the protocol),
   add it here in `app/adapters/backend.py` and surface a worker
   task under `app/workers/tasks/`. Worker tasks call backends only
   through ``get_backend()``, never via direct import.
