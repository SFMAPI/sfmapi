# sfmapi point-cloud viewer (example)

A small Vite + Three.js single-page app that uses
[`@sfmapi/client`](../../) to fetch a sealed snapshot's `points.bin`
and render it as an orbitable point cloud.

## Run locally

```bash
cd clients/typescript          # build the SDK once first (the example
npm install                    # uses a `file:` dep on @sfmapi/client)
npm run build

cd examples/viewer
npm install
npm run dev                    # http://localhost:5173
```

In the page header, fill in:

- **API base** — e.g. `http://localhost:8080`
- **Reconstruction** — a 26-char `recon_id`
- **Snapshot** — auto-populated; pick a seq
- **API key** — only needed when `auth_mode=api_key`

Click **Load** for the full `points.bin`, or **Preview** for the
decimated `points_preview.bin`. Controls: drag = orbit, right-drag =
pan, wheel = zoom, <kbd>R</kbd> = reset camera, <kbd>F</kbd> = fit.

## What it demonstrates

- Using `@sfmapi/client` from a browser (no Node-isms).
- Decoding the `application/x-sfm-points-v1` binary format with a
  vanilla `DataView` parser (`src/binary.ts`).
- sRGB-to-linear color conversion so Three.js' color management
  doesn't double-encode.
- Auto-fit-to-cloud camera framing.

## CORS

If your sfmapi web container is on a different origin than the viewer
during dev, add a permissive CORS middleware. The default deploy does
not enable CORS — that's a deliberate choice so production tenants
front the API with their own gateway.

For a local dev session, the simplest fix is to run the viewer behind
the same origin as the API (`vite build && cp -r dist /workspaces/...`)
or to add this to `app/main.py` in dev only:

```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```
