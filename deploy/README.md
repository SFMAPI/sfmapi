# sfmapi deployment

Two pieces:

1. **Web + Redis + Postgres** — `docker compose` (this dir). No GPU.
2. **Worker** — Windows service via `nssm`, runs against the host's
   CUDA stack + the `pycolmap` wheel built from `../colmap_mod`. Connects
   to the Redis + Postgres exposed by docker compose (or to a remote
   pair).

The two halves are deliberately decoupled: the web tier scales out
independently, and a single Postgres + Redis can serve N GPU hosts.

## 1. Bring up web + redis + postgres

```bash
cp deploy/.env.example deploy/.env
# edit deploy/.env: set SFMAPI_PG_PASS, SFMAPI_AUTH_MODE, etc.
docker compose -f deploy/docker-compose.yml --env-file deploy/.env up -d
```

The web container runs `alembic upgrade head` on start, then serves
`uvicorn app.main:app` on `:8080`. `/healthz`, `/readyz`, `/version`,
`/metrics` are exposed.

Issue an API key (in `api_key` mode):

```bash
curl -sX POST http://localhost:8080/v1/admin/api-keys \
    -H 'Content-Type: application/json' \
    -d '{"tenant_id":"my-tenant","name":"oncall"}'
```

## 2. Install the worker on a GPU host (Windows)

Prereqs:
- The host has the same CUDA / cuDSS stack the `colmap_mod` wheel was
  built against.
- A venv at the repo root with `pycolmap` + `sfmapi` installed editable:

  ```powershell
  uv venv
  CMAKE_GENERATOR=Ninja uv pip install -e ..\colmap_mod
  uv pip install -e ".[dev]"
  ```

- `nssm` is on `PATH` (https://nssm.cc/).

Install (Administrator):

```powershell
.\deploy\install-worker.ps1 `
    -ServiceName sfmapi-worker `
    -DbUrl "postgresql+psycopg://sfm:secret@db.internal:5432/sfmapi" `
    -RedisUrl "redis://redis.internal:6379/0" `
    -GpuUuid "0"
```

Multi-GPU host? One service per GPU, distinct service names:

```powershell
.\deploy\install-worker.ps1 -ServiceName sfmapi-worker-0 -GpuUuid "0"
.\deploy\install-worker.ps1 -ServiceName sfmapi-worker-1 -GpuUuid "1"
```

Each service writes `logs\<ServiceName>.std{out,err}.log` next to the
repo. Tail with:

```powershell
Get-Content -Wait .\logs\sfmapi-worker.stdout.log
```

Uninstall:

```powershell
.\deploy\uninstall-worker.ps1 -ServiceName sfmapi-worker
```

## Multi-host scale-out

- Run `docker compose` once on a control plane host (or replace
  postgres + redis with managed services).
- Install the worker service on each GPU host pointing at the central
  `SFMAPI_DB_URL` + `SFMAPI_REDIS_URL`.
- The fair-share scheduler (Phase 5.2) interleaves work across tenants;
  per-host concurrency-1 is enforced by ARQ default settings.

## Smoke test the deploy

Once Docker is running:

```bash
bash scripts/smoke.sh                 # bring up, run flow, tear down
bash scripts/smoke.sh --keep          # leave stack up on success
SFMAPI_WEB_PORT=18080 bash scripts/smoke.sh
```

Or on Windows:

```powershell
.\scripts\smoke.ps1
.\scripts\smoke.ps1 -Keep -WebPort 18080
```

Steps the script verifies:
healthz → version → metrics surface → create project → chunked upload
(init / PATCH / finalize) → create dataset (upload source) → register
image → list images → idempotency-key replay returns same upload_id.

On failure, the script prints the last 80 lines of the `web` container
logs before tearing the stack down (unless `--keep` / `-Keep`).

## Troubleshooting

- **Worker won't start**: `arq.exe` missing from venv → re-run
  `uv pip install -e .`.
- **`/healthz` 503 from web**: check container logs; usually the
  postgres dependency is still starting (compose `condition: healthy`
  should prevent this).
- **No tasks running**: confirm the worker can reach Redis
  (`redis-cli -h <host> ping` from the worker host).
- **CUDA OOM mid-mapping**: check
  `Get-Content .\logs\<svc>.stderr.log`; reduce `sift_max_num_features`
  or drop `max_image_size` in the `IncrementalSpec`.
