# Configuration

All settings are env-vars prefixed with `SFMAPI_`. They're parsed by a
single Pydantic `Settings` class:

```{eval-rst}
.. autoclass:: app.core.config.Settings
   :members:
   :no-index:
```

## Common bundles

### Single-host dev (default)

```bash
SFMAPI_ENV=dev
SFMAPI_DB_URL=sqlite+aiosqlite:///./sfmapi.db
SFMAPI_AUTH_MODE=none
SFMAPI_INLINE_TASKS=false
```

### Production (web tier in docker compose)

```bash
SFMAPI_ENV=prod
SFMAPI_DB_URL=postgresql+psycopg://sfm:secret@postgres:5432/sfmapi
SFMAPI_REDIS_URL=redis://redis:6379/0
SFMAPI_WORKSPACE_ROOT=/workspaces
SFMAPI_AUTH_MODE=api_key
SFMAPI_PYCOLMAP_AVAILABLE=false
SFMAPI_LOG_LEVEL=INFO
```

### Worker (Windows + CUDA)

```bash
SFMAPI_DB_URL=postgresql+psycopg://sfm:secret@db.internal:5432/sfmapi
SFMAPI_REDIS_URL=redis://redis.internal:6379/0
SFMAPI_PYCOLMAP_AVAILABLE=true
SFMAPI_COLMAP_SHA=<sha>
SFMAPI_BAXX_SHA=<sha>
SFMAPI_CUDA_ARCH=120
SFMAPI_LEASE_TTL_SECONDS=30
SFMAPI_INLINE_TASKS=false
CUDA_VISIBLE_DEVICES=0
```

## Notable knobs

| Env var | Default | What it does |
|---|---|---|
| `SFMAPI_INLINE_TASKS` | false | Run tasks in-process (test mode) |
| `SFMAPI_LEASE_TTL_SECONDS` | 30 | Per-task lease TTL |
| `SFMAPI_JANITOR_INTERVAL_SECONDS` | 10 | Reclaim expired leases |
| `SFMAPI_SNAPSHOT_KEEP_LAST` | 3 | GC keeps last N + final |
| `SFMAPI_UPLOAD_CHUNK_MAX_BYTES` | 8 MiB | Max single PATCH chunk |
| `SFMAPI_UPLOAD_EXPIRY_HOURS` | 24 | Open uploads GC'd after this |
