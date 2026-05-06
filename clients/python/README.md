# sfmapi-client

Typed Python SDK for [sfmapi](https://github.com/sfmapi/sfmapi),
plus the `sfmapi` CLI.

```bash
pip install "sfmapi-client[cli]"     # SDK + the `sfmapi` command
pip install sfmapi-client            # SDK only
```

## CLI

```bash
export SFMAPI_BASE_URL=http://localhost:8080
export SFMAPI_KEY=sfm_xxx          # only when auth_mode=api_key

sfmapi health version
sfmapi projects create my-proj
sfmapi uploads dir ./images        # prints `name<TAB>sha` per file
sfmapi datasets create <pid> ds1 \
    --entry a.jpg:<sha> --entry b.jpg:<sha>
sfmapi pipelines run <pid> \
    --dataset-id <did> --image-root /data \
    --image a.jpg --image b.jpg --kind incremental
sfmapi jobs watch <job_id>
sfmapi jobs events <job_id>        # SSE tail
sfmapi snapshots list <recon_id>
sfmapi snapshots get <recon_id> <seq> points.bin --out cloud.bin
```

Add `--json` (between the program name and the subcommand) to get raw
JSON instead of Rich-rendered tables — convenient for scripting.

## Sync usage

```python
from sfmapi_client import SfmApiClient, IncrementalSpec

with SfmApiClient("http://localhost:8080", api_key="sfm_xxx") as c:
    proj = c.create_project("photogrammetry")
    sha  = c.upload_bytes(open("a.jpg", "rb").read(), content_type="image/jpeg")
    ds   = c.create_dataset(
        proj.project_id,
        name="dataset-1",
        source={"kind": "upload",
                "entries": [{"name": "a.jpg", "blob_sha": sha}]},
        camera_model="SIMPLE_RADIAL",
    )
    job = c.run_pipeline(
        proj.project_id,
        dataset_id=ds.dataset_id,
        image_root="/data/images",
        image_list=["a.jpg"],
        spec=IncrementalSpec(),
    )
    print("job_id:", job.job_id)
    detail = c.get_job(job.job_id)
    print("status:", detail.status, "tasks:", [(t.kind, t.status) for t in detail.tasks])
```

## Async usage

```python
import asyncio
from sfmapi_client import AsyncSfmApiClient, FeaturesSpec

async def main():
    async with AsyncSfmApiClient("http://localhost:8080") as c:
        proj = await c.create_project("p")
        sha  = await c.upload_bytes(b"...")
        ds   = await c.create_dataset(proj.project_id, name="ds",
                                      source={"kind": "upload", "entries": []})
        job = await c.submit_features(
            ds.dataset_id, spec=FeaturesSpec(use_gpu=False),
            image_root="/data", image_list=["a.jpg"],
        )
        async for event in c.stream_events(job.job_id):
            print(event)

asyncio.run(main())
```

## Errors

All HTTP errors raise typed exceptions:

| HTTP | Exception |
|---|---|
| 403 | `AuthError` |
| 404 | `NotFoundError` |
| 409 | `ConflictError` |
| 413 / 429 | `QuotaExceededError` |
| 422 | `ValidationError` |
| 503 | `PycolmapUnavailableError` |
| 507 | `StorageError` |
| other 4xx/5xx | `SfmApiError` |

Each exception carries `status_code`, `problem` (parsed
`application/problem+json` body), and the original `httpx.Response`.

## Streaming progress events

`stream_events(job_id, last_event_id=...)` yields parsed `ProgressEvent`
dicts (see server-side schema). The `last_event_id` parameter triggers
SSE replay so reconnects don't drop history.
