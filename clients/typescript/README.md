# @sfmapi/client

Typed TypeScript SDK for [sfmapi](https://github.com/sfmapi/sfmapi).

Works in browsers (modern fetch + ReadableStream) and Node ≥ 20.

```bash
npm install @sfmapi/client
# or
pnpm add @sfmapi/client
```

## Usage

```ts
import { SfmApiClient, IncrementalSpec } from "@sfmapi/client";

const c = new SfmApiClient({
  baseUrl: "http://localhost:8080",
  apiKey: process.env.SFMAPI_KEY,
});

const proj = await c.createProject({ name: "my-proj" });

// Upload a File / Blob / Uint8Array — chunked under the hood.
const sha = await c.uploadBytes(await file.arrayBuffer(), {
  contentType: "image/jpeg",
});

const ds = await c.createDataset(proj.project_id, {
  name: "ds",
  source: {
    kind: "upload",
    entries: [{ name: "a.jpg", blob_sha: sha }],
  },
});

const job = await c.runPipeline(proj.project_id, {
  dataset_id: ds.dataset_id,
  image_root: "/data",
  image_list: ["a.jpg"],
  spec: { kind: "incremental", version: 1 } satisfies IncrementalSpec,
});

// Stream progress events
for await (const event of c.streamEvents(job.job_id)) {
  console.log(event.kind, "phase=", event.phase);
}
```

## Errors

Every non-2xx HTTP response throws a typed subclass of `SfmApiError`:

| HTTP | Class |
|---|---|
| 403 | `AuthError` |
| 404 | `NotFoundError` |
| 409 | `ConflictError` |
| 413 / 429 | `QuotaExceededError` |
| 422 | `ValidationError` |
| 503 | `PycolmapUnavailableError` |
| 507 | `StorageError` |

Each error carries `.statusCode`, `.problem` (parsed
`application/problem+json`), and `.response` (the raw `Response`).

## Browser usage notes

- `streamEvents()` uses `fetch`'s `ReadableStream`. All evergreen
  browsers support this.
- `uploadBytes()` accepts `ArrayBuffer | Uint8Array | Blob | File`.
- Pass `globalThis.AbortSignal` via `{ signal }` in any method options
  to cancel.

## Versioning

The SDK pins to the major version of the server's REST API (`/v1`).
Minor server bumps are non-breaking by contract.
