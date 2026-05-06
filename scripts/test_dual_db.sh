#!/usr/bin/env bash
# Run the test suite twice: once on SQLite, once on Postgres.
# CI must pass both. The Postgres run requires SFMAPI_DB_URL_PG set.
set -euo pipefail

echo "=== SQLite ==="
SFMAPI_DB_URL="sqlite+aiosqlite:///./test_sqlite.db" \
    uv run pytest -q -m "not needs_pycolmap and not needs_postgres" "$@"

if [[ -n "${SFMAPI_DB_URL_PG:-}" ]]; then
    echo
    echo "=== Postgres (existing instance) ==="
    SFMAPI_DB_URL="${SFMAPI_DB_URL_PG}" \
        uv run pytest -q -m "not needs_pycolmap" "$@"
elif command -v docker >/dev/null; then
    echo
    echo "=== Postgres (ephemeral docker) ==="
    bash scripts/test_postgres_local.sh "$@"
else
    echo
    echo "(skipping Postgres run; set SFMAPI_DB_URL_PG or install docker)"
fi
