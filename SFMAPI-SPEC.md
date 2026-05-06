# SFMAPI Specification

**Version:** `v1.0-draft`
**Status:** Draft. Stable in shape; additive changes only until v2.
**Reference implementation:** [opsiclear/sfmapi](https://github.com/opsiclear/sfmapi)

This document specifies a HTTP / REST + SSE + WebSocket surface for
running Structure-from-Motion (SfM) pipelines as a service. It is
intended to be implementable by any backend; the reference
implementation is one such backend.

The spec is normative when it uses **MUST**, **MUST NOT**, **SHOULD**,
**SHOULD NOT**, and **MAY** as defined by [RFC 2119][rfc2119].

[rfc2119]: https://www.rfc-editor.org/rfc/rfc2119

---

## 1. Goals and non-goals

### 1.1 Goals

- A single REST surface every SfM-aware tool can target, regardless of
  the backend (COLMAP, custom forks, future engines).
- First-class web ergonomics: CORS, ETag, Range, SSE, WebSocket.
- Content-addressed storage so the same dataset never gets re-uploaded
  or re-processed unnecessarily.
- Multi-tenant from the first request: every resource carries a
  `tenant_id` and tenant isolation is server-enforced.
- Job model that supports cancellation, resume, and per-stage caching.
- Decoupled compute: the API surface does not assume a particular
  worker topology.

### 1.2 Non-goals

- This spec does not cover a particular SfM algorithm. It covers the
  *interface* — what a client asks for, what a server returns. The
  backend may use COLMAP, OpenSfM, custom code, etc.
- This spec does not cover infrastructure (deployment topology,
  GPU scheduling, Helm charts).
- This spec does not cover offline / batch SDK ergonomics — those are
  client-side and may be implemented per-language.
- This spec **does not** define a wire format for masks beyond
  "an image format servable by HTTP." (Future revision will.)

---

## 2. Versioning and evolution

- The current version is **`v1`**, served under the `/v1/` URL prefix.
- A `v1` server **MUST** accept `/v1/` requests.
- A server **MAY** add new endpoints, new fields on existing
  responses, new optional request fields, and new enum values without
  bumping the major version, as long as well-behaved older clients
  continue to function.
- A server **MUST NOT** remove existing fields, repurpose enum values,
  change a 2xx response shape, or change the meaning of an HTTP
  method on an existing path within `v1`.
- A server **MUST** ignore unknown request body fields rather than
  rejecting them (forward compatibility with future-revision
  clients).
- A server **MAY** add `x-`-prefixed extension fields anywhere; clients
  **MUST** ignore unrecognised `x-`-prefixed fields.
- The shape of `_links` (§3.5) is part of the spec; the *contents* are
  advisory and may grow.

### 2.1 Backends and capabilities

sfmapi is **a wire standard, not a single implementation**. Different
deployments can be powered by different SfM engines (COLMAP,
COLMAP-mod, OpenMVG, Theia, hloc, custom code) and **MUST NOT** be
required to support every endpoint in this spec.

- A small set of capabilities is **CORE** (project / dataset / image
  CRUD, uploads, jobs, events). Every conforming server **MUST**
  expose these and they always succeed.
- The remaining capabilities are **OPTIONAL** feature flags. A server
  advertises which OPTIONAL flags it supports via
  `GET /v1/capabilities` (see §3.11). Endpoints whose capability is
  not advertised **MUST** return `501 Not Implemented` with a
  problem+json body whose `capability` extra carries the canonical
  feature name.
- Clients **SHOULD** call `/v1/capabilities` once at startup and gate
  UI affordances on the response. Clients **MUST** treat the absence
  of an OPTIONAL key as `false`.

This is what lets sfmapi be a high-level standard rather than a
COLMAP wrapper: the schemas and HTTP shapes don't change between
backends; only the set of advertised capabilities does.

The reference implementation isolates the backend behind a single
Python protocol (`app.adapters.backend.SfmBackend`); see
`app.adapters.colmap_backend.ColmapModBackend` for the colmap_mod
implementation. Adding e.g. an OpenMVG backend is a single
`register_backend("openmvg", OpenMvgBackend)` call — no schema, no
endpoint, and no worker-task signature changes.

---

## 3. Conventions

### 3.1 IDs

Resource IDs **MUST** be opaque strings safe for URL path
inclusion. The reference implementation uses 26-char ULIDs; clients
**MUST NOT** parse the ID format. IDs **MUST** be unique within a
tenant.

### 3.2 Timestamps

All timestamps **MUST** be ISO-8601 / RFC 3339 strings in UTC, e.g.
`"2026-05-02T18:42:01.123Z"`.

### 3.3 Hashes

Content addresses **MUST** be lower-case hex SHA-256 digests
(64 chars).

### 3.4 Errors

A non-2xx response **MUST** be a `application/problem+json`
[RFC 7807][rfc7807] document with at minimum:

```json
{
  "type": "https://sfmapi.github.io/errors/<slug>",
  "title": "Human-readable category",
  "status": 409,
  "detail": "Optional, free-form description",
  "instance": "/v1/projects/abc"
}
```

The HTTP status → error-class mapping the spec defines:

| HTTP | Error class                      |
|------|----------------------------------|
| 400  | `bad_request`                    |
| 403  | `tenant_violation`, `auth`       |
| 404  | `not_found`                      |
| 409  | `conflict`                       |
| 413  | `quota_exceeded` (storage)       |
| 422  | `validation`                     |
| 429  | `quota_exceeded` (rate / GPU-s)  |
| 501  | `pycolmap_unavailable` / `capability_unavailable` |
| 507  | `storage`                        |

Other 4xx/5xx codes **MAY** be used; clients **SHOULD** treat any
non-2xx as an error.

[rfc7807]: https://www.rfc-editor.org/rfc/rfc7807

### 3.5 HAL-lite `_links`

Every resource representation **SHOULD** include a `_links` block
containing at minimum a `self` link, plus zero or more named links
to subresources. Each link is `{"href": "<absolute or root-relative URL>"}`.

```json
{
  "project_id": "...",
  "_links": {
    "self":     { "href": "/v1/projects/abc" },
    "datasets": { "href": "/v1/projects/abc/datasets" }
  }
}
```

Clients **SHOULD** prefer `_links` over hard-coded URL templates when
navigating between resources.

### 3.6 Pagination

List endpoints **MUST** follow [AIP-158][aip158] and return:

```json
{
  "items":           [...],
  "next_page_token": "<opaque string>" | null,
  "total":           <int> | null
}
```

Clients pass `?page_token=` and `?page_size=` to continue. `total`
**MAY** be `null` when counting is expensive. Clients **MUST NOT**
parse the page token.

[aip158]: https://google.aip.dev/158

### 3.7 Idempotency

`POST` endpoints that create a resource **SHOULD** accept an
`Idempotency-Key` request header. If the same key + same tenant is
seen again, the server **MUST** return the original resource (or
upload state) instead of creating a duplicate.

### 3.8 Caching

For immutable resources (sealed snapshots, content-addressed blobs,
finalized uploads), the server **MUST** emit a strong `ETag` and
**MUST** honor `If-None-Match` with a `304 Not Modified` response.

For long-cacheable resources the server **SHOULD** emit
`Cache-Control: public, max-age=<n>, immutable`.

Range requests (`Range: bytes=A-B`) **MUST** be honored on byte
endpoints. The binary points format (§7.1) is fixed-stride for
exactly this reason.

### 3.9 Long-running operations (LROs)

Any endpoint that submits work **MUST** return:

```
HTTP/1.1 202 Accepted
Location: /v1/jobs/<job_id>
Content-Type: application/json

{
  "job_id":   "<id>",
  "task_ids": ["<id>", ...],
  "recon_id": "<id>" | null
}
```

The created `Job` resource is then observable via §6.7.

### 3.11 Capability discovery

```http
GET /v1/capabilities
200 OK
content-type: application/json

{
  "backend": {
    "name":    "colmap_mod",
    "version": "3.13.0.dev",
    "vendor":  "ETH3D / sfmapi"
  },
  "features": {
    "projects.crud":             true,
    "datasets.crud":             true,
    "images.crud":               true,
    "uploads.chunked":           true,
    "jobs.read":                 true,
    "events.sse":                true,
    "spec.read":                 true,

    "features.extract":          true,
    "matches.exhaustive":        true,
    "matches.sequential":        true,
    "matches.spatial":           true,
    "matches.vocabtree":         true,
    "matches.verify":            true,

    "map.incremental":           true,
    "map.global":                true,
    "map.hierarchical":          true,
    "map.spherical":             true,

    "ba.standard":               true,
    "ba.two_stage":              true,
    "triangulate.retri":         true,
    "relocalize.images":         true,
    "pgo.optimize":              true,

    "export.ply":                true,
    "export.nvm":                true,
    "export.colmap_text":        true,
    "export.colmap_bin":         true,

    "dense.patch_match_stereo":  true,
    "dense.stereo_fusion":       true,

    "similarity.dhash":          true,
    "similarity.vlad":           true,

    "localize.from_memory":      true,
    "georegister.sim3":          true,
    "spherical.to_cubemap":      true,
    "spherical.render_cubemap":  true,

    "pose_priors.read_write":    true,
    "segment.sam":               false
  }
}
```

`backend` identifies the SfM engine powering this deployment;
`features` is a flat dict from canonical capability name to bool.
The CORE feature names are listed in §6.1; OPTIONAL feature names
are owned by the spec — backends MAY add extra keys outside the
canonical list but clients **MUST** treat unknown names as opaque.

When a request hits an OPTIONAL feature whose flag is `false`, the
server **MUST** respond:

```http
501 Not Implemented
content-type: application/problem+json

{
  "type":       "https://sfmapi/errors/capability_unavailable",
  "title":      "Capability not available in this deployment",
  "status":     501,
  "detail":     "capability 'dense.patch_match_stereo' not supported by the current backend",
  "capability": "dense.patch_match_stereo"
}
```

### 3.10 CORS

Servers **MUST** support CORS preflight (`OPTIONS *`) and **SHOULD**
expose the following response headers to browsers:
`ETag, Last-Modified, Content-Range, Location, Link`.

---

## 4. Resource model

The spec defines nine first-class nouns:

```text
Tenant
  └── Project              (group of datasets)
        └── Dataset        (set of images + camera/rig metadata)
              ├── ImageSource   (where bytes live; immutable)
              ├── Image*        (one per registered image)
              └── Reconstruction*
                    └── SubModel*    (one per produced sparse/{idx})

Job                        (user-facing intent)
  └── Task*                (DAG node; one per stage)

Snapshot                   (sealed, immutable read view of a SubModel)
```

### 4.1 Project

```json
{
  "project_id":   "01HZ...",
  "tenant_id":    "default",
  "name":         "vacation-2026",
  "description":  null,
  "created_at":   "2026-05-02T...",
  "_links": { "self": {...}, "datasets": {...}, "pipelines": {...} }
}
```

### 4.2 ImageSource

A logical reference to where the bytes live. **Immutable.** To change
where a dataset's bytes come from, create a new dataset.

```json
{ "kind": "upload" }
{ "kind": "local",  "root": "/data/photos", "recursive": true }
{ "kind": "s3",     "bucket": "my-bucket", "prefix": "scenes/a/" }
```

### 4.3 Dataset

```json
{
  "dataset_id":               "01HZ...",
  "tenant_id":                "default",
  "project_id":               "01HZ...",
  "source_id":                "01HZ...",
  "name":                     "trip",
  "camera_model":             "SIMPLE_RADIAL",
  "intrinsics_mode":          "single_camera" | "per_image" | "per_folder",
  "is_spherical":             false,
  "respect_exif_orientation": false,
  "rig_config_json":          { ... } | null,
  "active_maskset_id":        null,
  "manifest_hash":            "<sha256 of sorted (name, content_sha)>",
  "created_at":               "2026-05-02T...",
  "_links": { "self": {...}, "images": {...}, "features": {...}, ... }
}
```

`manifest_hash` is the canonical content address of the dataset's
*image set*. Two datasets with the same manifest_hash are
interchangeable as inputs to any subsequent stage.

### 4.4 Image

```json
{
  "image_id":    "01HZ...",
  "dataset_id":  "01HZ...",
  "name":        "img_001.jpg",
  "content_sha": "<sha256 or 0x00 placeholder for local sources>",
  "source_kind": "upload" | "local" | "s3",
  "rel_path":    "subdir/img_001.jpg" | null,
  "byte_size":   123456 | null,
  "width":       4032 | null,
  "height":      3024 | null,
  "created_at":  "...",
  "_links": { "self": {...}, "bytes": {...}, "thumbnail": {...}, "exif": {...} }
}
```

### 4.5 Reconstruction

A run of a mapping pipeline. Identified by the cache key
`(dataset_snapshot_hash, params_hash, runtime_version_id)`.

```json
{
  "recon_id":               "01HZ...",
  "project_id":             "01HZ...",
  "dataset_id":             "01HZ...",
  "dataset_snapshot_hash":  "<sha256>",
  "spec":                   { ...PipelineSpec },
  "rv_id":                  "<runtime_version_id>",
  "status":                 "pending" | "running" | "succeeded" | "failed",
  "created_at":             "...",
  "_links": { "self": {...}, "submodels": {...}, "snapshots": {...} }
}
```

### 4.6 SubModel

One per produced `sparse/{idx}` directory. A reconstruction may
contain N sub-models. Iterative refinement (BA round, retriangulation,
reloc) produces a **revision** of a SubModel via `parent_submodel_id`.

```json
{
  "submodel_id":         "01HZ...",
  "recon_id":            "01HZ...",
  "idx":                 0,
  "parent_submodel_id":  null,
  "summary":             { "num_reg_images": 12, "num_points3D": 4567, ... },
  "rigidity":            { "sigma_0": ..., "sigma_1": ..., ... } | null,
  "snapshot_seq":        7,
  "sealed_path":         "<server-side path; informational>",
  "created_at":          "...",
  "_links": { "self": {...}, "reconstruction": {...} }
}
```

### 4.7 Job and Task

```json
// Job
{
  "job_id":           "01HZ...",
  "tenant_id":        "default",
  "project_id":       "01HZ...",
  "recipe":           "incremental" | "global" | ... | "features" | "matches" | ...,
  "status":           "pending" | "running" | "succeeded" | "failed" |
                      "cancelled" | "cancelled_dirty",
  "cancel_requested": false,
  "cancel_force":     false,
  "created_at":       "...",
  "started_at":       "..." | null,
  "finished_at":      "..." | null,
  "error_class":      "OOMError" | "CudaContextError" | ... | null,
  "error_message":    "..." | null,
  "_links":           { "self": {...}, "events": {...}, "ws": {...} }
}

// Task (one per DAG node)
{
  "task_id":      "01HZ...",
  "job_id":       "01HZ...",
  "kind":         "extract" | "match" | "verify" | "map" | "ba" |
                  "triangulate" | "relocalize" | "pgo" | "export" | "segment" | "vlad",
  "status":       "<as Job.status>",
  "cache_key":    "<sha256>",
  "inputs_hash":  "<sha256>",
  "params_hash":  "<sha256>",
  "outputs_ref":  { ... } | null
}
```

The `JobDetail` shape is `Job & { tasks: Task[] }`.

### 4.8 Upload

```json
{
  "upload_id":      "01HZ...",
  "state":          "open" | "received" | "finalized",
  "expected_size":  102400,
  "received_bytes": 102400,
  "blob_sha":       "<sha256>" | null,
  "expires_at":     "..."
}
```

### 4.9 Snapshot

A snapshot is **not** a database row; it is a directory of immutable
files keyed by `(reconstruction, seq)`. The server enumerates sealed
seqs and serves files within them. Required filenames are listed in
§7.

---

## 5. Auth

The spec defines two auth modes; servers **MUST** support at least
one.

### 5.1 `none` mode

Every request resolves to a single `default` tenant. Suitable for
local development. Servers in this mode **SHOULD** emit a warning
header `X-SFMAPI-Auth: none` so clients can detect it.

### 5.2 `api_key` mode

Clients pass `Authorization: Bearer <opaque-key>`. The server resolves
the key to a tenant and uses it for every subsequent operation.

Issuing keys is out of scope for this spec; the reference
implementation exposes `POST /v1/admin/api-keys`. Servers **MAY**
expose a different admin path or none at all (manual provisioning).

---

## 6. The endpoint surface

All paths are `v1`-prefixed. Square brackets indicate optional path
segments. **Bold** = required. Italics = optional.

### 6.1 Health and meta

| Method | Path                | Purpose                                 |
|--------|---------------------|-----------------------------------------|
| GET    | `/healthz`          | Liveness — always 200 if process alive  |
| GET    | `/readyz`           | Readiness — DB/queue reachable, ...     |
| GET    | `/version`          | Versions of server + engine             |
| GET    | `/openapi.json`     | OpenAPI 3.1 document                    |
| GET    | `/metrics`          | Prometheus exposition (optional)        |

### 6.2 Projects

| Method  | Path                        | Body / Returns                          |
|---------|-----------------------------|-----------------------------------------|
| POST    | `/v1/projects`              | `{name, description?}` → `Project` (201)|
| GET     | `/v1/projects`              | `Page<Project>`                         |
| GET     | `/v1/projects/{pid}`        | `Project`                               |
| PATCH   | `/v1/projects/{pid}`        | `{name?, description?}` → `Project`     |
| DELETE  | `/v1/projects/{pid}`        | 204                                     |

### 6.3 Uploads (chunked)

| Method  | Path                                     | Body / Headers                                     | Returns        |
|---------|------------------------------------------|----------------------------------------------------|----------------|
| POST    | `/v1/uploads`                            | `{expected_size, content_type?, expected_sha?}` + `Idempotency-Key` | `Upload` (201) |
| GET     | `/v1/uploads/{uid}`                      | —                                                  | `Upload`       |
| PATCH   | `/v1/uploads/{uid}`                      | raw chunk + `Content-Range: bytes A-B/T`           | `Upload`       |
| POST    | `/v1/uploads/{uid}:finalize`             | `{}` or `X-Content-SHA256` header                  | `Upload`       |

After `finalize`, the bytes live at `blob_sha` and can be referenced
from `Image.blob_sha` (§6.5).

### 6.4 Datasets

| Method  | Path                                          | Returns         |
|---------|-----------------------------------------------|-----------------|
| POST    | `/v1/projects/{pid}/datasets`                 | `Dataset` (201) |
| GET     | `/v1/projects/{pid}/datasets`                 | `Page<Dataset>` |
| GET     | `/v1/projects/{pid}/datasets/{did}`           | `Dataset`       |
| PATCH   | `/v1/projects/{pid}/datasets/{did}`           | `Dataset`       |

`POST` body:

```json
{
  "name":                     "trip",
  "source":                   { "kind": "upload" | "local" | "s3", ... },
  "camera_model":             "SIMPLE_RADIAL",
  "intrinsics_mode":          "single_camera",
  "is_spherical":             false,
  "rig_config":               null,
  "respect_exif_orientation": false
}
```

### 6.5 Images

| Method  | Path                                       | Returns       |
|---------|--------------------------------------------|---------------|
| POST    | `/v1/datasets/{did}/images`                | `Image` (201) |
| POST    | `/v1/datasets/{did}/images:batchCreate`    | `BatchCreateImagesResponse` (201) |
| GET     | `/v1/datasets/{did}/images`                | `Page<Image>` |
| DELETE  | `/v1/datasets/{did}/images/{name}`         | 204           |
| GET     | `/v1/images/{image_id}`                    | `Image`       |
| GET     | `/v1/images/{image_id}/bytes`              | image bytes (Range, ETag) |
| GET     | `/v1/images/{image_id}/thumbnail?size=N`   | JPEG (Cache-Control) |
| GET     | `/v1/images/{image_id}/exif`               | JSON          |

`POST .../images:batchCreate` body (AIP-231):

```json
{ "requests": [ { "name": "...", "blob_sha": "..." }, ... ] }
```

Returns `BatchCreateImagesResponse`:

```json
{ "images": [ { "image_id": "...", "name": "...", ... } ] }
```

Servers **MUST** cap batches at 1000 items.

### 6.6 SfM stages

Stage endpoints take only `{spec}`. Image source and database path
are derived server-side from the dataset's `source` and the cached
reconstruction.

| Method | Path                                | Body                  | Returns |
|--------|-------------------------------------|-----------------------|---------|
| POST   | `/v1/datasets/{did}/features`       | `{spec: FeaturesSpec}`| 202 + LRO |
| POST   | `/v1/datasets/{did}/matches`        | `{pairs: PairsSpec, matcher: MatcherSpec}` | 202 + LRO |
| POST   | `/v1/datasets/{did}/verify`         | `{spec: VerifySpec}`  | 202 + LRO |

A dataset with no registered images **MUST** be rejected with 422
*before* a job is created.

### 6.7 Jobs and progress

| Method  | Path                          | Body / Headers                       | Returns             |
|---------|-------------------------------|--------------------------------------|---------------------|
| GET     | `/v1/jobs/{jid}`              | —                                    | `JobDetail`         |
| POST    | `/v1/jobs/{jid}:cancel`       | `?force=true`                        | `Job` (cancel set)  |
| POST    | `/v1/jobs/{jid}:resume`       | —                                    | 202 + `Job`         |
| GET     | `/v1/jobs/{jid}/events`       | `Last-Event-ID: <int>`               | SSE (`ProgressEvent`) |
| GET     | `/ws/v1/jobs/{jid}`           | WebSocket upgrade                    | (see §8)            |

### 6.8 Pipelines (recipe sugar)

| Method | Path                                                | Body                                                | Returns |
|--------|-----------------------------------------------------|-----------------------------------------------------|---------|
| POST   | `/v1/projects/{pid}/pipelines/{recipe}`             | `{dataset_id, spec, features?, matches?, verify?}`  | 202 + LRO |

`recipe ∈ {incremental, global, hierarchical, spherical}` and
`spec.kind` **MUST** match `recipe` or the request **MUST** be rejected
with 422.

### 6.9 Reconstructions, submodels, snapshots

| Method | Path                                                     | Returns                       |
|--------|----------------------------------------------------------|-------------------------------|
| GET    | `/v1/reconstructions/{rid}`                              | `Reconstruction`              |
| GET    | `/v1/reconstructions/{rid}/submodels`                    | `Page<SubModel>`              |
| GET    | `/v1/submodels/{smid}`                                   | `SubModel`                    |
| GET    | `/v1/reconstructions/{rid}/snapshots`                    | `{seqs: int[], _links: {...}}`|
| GET    | `/v1/reconstructions/{rid}/snapshots/{seq}/{name}`       | file bytes (ETag, immutable)  |

Where `{name}` is one of `cameras.json | images.json | rigs.json |
frames.json | points.bin | points_preview.bin | summary.json`.

#### 6.9.1 Octree tiles (optional)

For point clouds too large to ship as a single `points.bin`, the
server **SHOULD** expose an octree-tiled view. Tiles are
addressed `(level, x, y, z)`; each cell is half-open and contains
the points whose centroid falls inside it. A point at level L = 0
sits in tile `(0, 0, 0, 0)` (which covers the whole bbox).

| Method | Path                                                                         | Returns                              |
|--------|------------------------------------------------------------------------------|--------------------------------------|
| GET    | `/v1/reconstructions/{rid}/snapshots/{seq}/tiles/index.json`                 | tile manifest (see below)            |
| GET    | `/v1/reconstructions/{rid}/snapshots/{seq}/tiles/{level}/{x}/{y}/{z}.bin`    | tile bytes (`application/x-sfm-points-v1`) |

`tiles/index.json`:

```json
{
  "bbox_min":   [x, y, z],
  "bbox_max":   [x, y, z],
  "max_level":  4,
  "tile_count": 27,
  "tiles": [
    { "level": 0, "x": 0, "y": 0, "z": 0, "count": 4567, "byte_size": 118784 },
    ...
  ]
}
```

A tile that addresses an empty cell **MUST** return 404. Servers
**MAY** generate tiles lazily on first request and cache them.

Each tile's binary header repeats the **cell's** bbox, not the
parent dataset's, so a client can render a tile without consulting
the index.

#### 6.9.2 Observations (optional)

| Method | Path                                                                              | Returns |
|--------|-----------------------------------------------------------------------------------|---------|
| GET    | `/v1/reconstructions/{rid}/snapshots/{seq}/images/{image_id}/observations`         | `{image_id, count, observations: [...]}` |
| GET    | `/v1/reconstructions/{rid}/snapshots/{seq}/points/{point3d_id}/visibility`         | `{point3d_id, count, observations: [...]}` |

Observation payload (per image):

```json
{
  "point3d_id": <int>,
  "x":          <float>,
  "y":          <float>,
  "kp_idx":     <int>,
  "error":      <float> | null
}
```

Visibility payload (per point):

```json
{
  "image_id": <int | str>,
  "x":        <float>,
  "y":        <float>,
  "kp_idx":   <int>
}
```

If the underlying snapshot has no observations sidecar (the worker
did not emit one), the server **MUST** return 404.

#### 6.9.3 Image similarity (optional)

For "show me images that look like this one" UX (clustering,
deduplication, sequential matching primer):

| Method | Path                                          | Returns                                    |
|--------|-----------------------------------------------|--------------------------------------------|
| GET    | `/v1/datasets/{did}/similarity`               | `{query_image_id, strategy, k, neighbors}` |
| POST   | `/v1/datasets/{did}/similarity:build`         | `dhash` → 200 manifest; `vlad` → 202 + job |

GET query parameters:
- `image_id` (required) — the image to query against.
- `k` (default 5, max 1000) — how many neighbors to return.
- `strategy` (default `dhash`) — one of:
  - **`dhash`** — 64-bit perceptual difference hash. Available
    unconditionally; index built lazily on first query.
  - **`vlad`** — SfM-grade VLAD descriptors (Hamming-style cosine
    distance over L2-normalized 32×128 = 4096-d vectors). The query
    path is **NumPy-only and does not require pycolmap on the API
    process**, but the index must exist — `GET` returns **404** with
    a pointer to `:build` when no `vlad.npz` is present. The build
    requires pycolmap on the worker.
- `include_self` (default `false`) — if true, returns the query image
  with `distance=0` as the first neighbor.

`neighbors` is `[{image_id, distance}, ...]`, sorted ascending by
`distance`. For `dhash` the distance is Hamming over the 64-bit hash
(range `[0, 64]`). For `vlad` the distance is `max(0, 1 - cosine)`
(range `[0, 2]`).

`POST :build`:
- `strategy=dhash` runs synchronously (200 with manifest).
- `strategy=vlad` enqueues a worker job (202 with `Location:
  /v1/jobs/{job_id}`); poll the job for completion.

Implementations **SHOULD** persist the similarity index keyed by the
dataset's `manifest_hash` and rebuild on mismatch.

#### 6.9.4 Pose priors (optional)

For georegistration, GPS-anchored reconstructions, or seeding the
mapper with known camera poses:

| Method | Path                                            | Body            | Returns                     |
|--------|-------------------------------------------------|-----------------|-----------------------------|
| GET    | `/v1/images/{image_id}/pose_prior`              | —               | `PosePrior` or `null`       |
| PUT    | `/v1/images/{image_id}/pose_prior`              | `PosePrior`     | `PosePrior` (echoed)        |
| DELETE | `/v1/images/{image_id}/pose_prior`              | —               | `204`                       |
| GET    | `/v1/datasets/{did}/pose_priors`                | —               | `{"pose_priors": {id: PP}}` |
| PUT    | `/v1/datasets/{did}/pose_priors`                | `{id: PosePrior}` | `{"written": N}`         |

`PosePrior` shape (see §7.2.2): `cam_from_world: Rigid3`, optional
`covariance` (36-float row-major 6×6), optional `gps: GpsCoord`.

When the dataset is mapped via a recipe, every image whose
`pose_prior_json` is non-null is forwarded into the worker's
`MappingInput` as a soft constraint. Servers **MAY** ignore priors if
the underlying mapper does not support them; in that case the prior is
preserved on disk for future runs but not used.

#### 6.9.5 Sim(3) georegistration (optional)

Apply a similarity transform to a reconstruction (e.g., to align it to
a GPS frame or to scale to metric units):

| Method | Path                                                  | Body   | Returns      |
|--------|-------------------------------------------------------|--------|--------------|
| POST   | `/v1/reconstructions/{rid}/georegister`               | `Sim3` | 202 + job    |

`Sim3` shape: `{ rotation: Rotation, translation: [x, y, z], scale: f }`
(see §7.2.2). The worker reads the latest sealed snapshot, applies the
transform to every camera + 3D point, and **seals a fresh snapshot**
that clients can read the same way they read post-mapping snapshots.
Servers **MUST** return 404 when `recon_id` is unknown and 422 on a
malformed `Sim3` body.

#### 6.9.6 Spherical → cubemap conversion (optional)

For VR / Three.js / pinhole-only viewer pipelines there are two
companion endpoints — one operates on the reconstruction, the other
on the source images:

| Method | Path                                                   | Returns      | Operates on    |
|--------|--------------------------------------------------------|--------------|----------------|
| POST   | `/v1/reconstructions/{rid}:to_cubemap`                 | 202 + job    | reconstruction |
| POST   | `/v1/datasets/{did}:render_cubemap?face_size={N}`      | 202 + job    | images only    |

`POST :render_cubemap` accepts an optional `face_size` query
(64–8192) for the per-face pixel edge length. Output is a directory
under the dataset's workspace; the task result carries
``{output_path, num_files, face_size}`` so the client can register
the path as a fresh ``local`` dataset for downstream pinhole-only
pipelines. Servers **MUST** return 422 if the dataset is not marked
``is_spherical=true``.

`POST :to_cubemap` operates on the reconstruction:

Requires the underlying dataset to be marked ``is_spherical=true``;
servers **MUST** return 422 otherwise. The worker re-projects each
panorama into 6 faces and seals a fresh snapshot whose ``rigs.json``
carries the cubemap rig (1 rig × 6 sensors) and ``frames.json``
carries one frame per panorama (each binding 6 sensor-id → image-id
pairs). Clients then read the new snapshot the same way they read
post-mapping snapshots.

The equirectangular camera itself is represented by ``Camera.model ==
"SPHERICAL"`` with empty ``params`` — only ``width`` / ``height``
matter. See §7.2.2.

#### 6.9.7 Pluggable feature extractors (optional)

`FeaturesSpec` is **type-tagged** so a backend can offer multiple
extractors (SIFT, SuperPoint, ALIKED, DISK, R2D2, D2-Net, ...). The
capability flag for each is `features.extract.{type}` — clients gate
on `GET /v1/capabilities` to learn which the backend supports.

```json
{
  "version": 1,
  "type":    "sift" | "superpoint" | "aliked" | "disk" | "r2d2" | "d2net",
  "max_num_features": 8192,
  "use_gpu":          true,
  "extractor_options": { /* extractor-specific overrides */ }
}
```

`POST /v1/datasets/{did}/features` accepts this shape. Servers
**MUST** return 501 with `capability=features.extract.{type}` when
the requested extractor isn't supported. The legacy
`sift_max_num_features` / `sift_first_octave` fields are accepted as
aliases when `type=="sift"`.

#### 6.9.8 Pair selection + per-pair matchers

Pair selection and per-pair matching are independent shapes
(AIP-202). `POST /v1/datasets/{did}/matches` takes both:

```json
// PairsSpec — which image pairs to match.
{
  "version": 1,
  "strategy": "exhaustive" | "sequential" | "spatial" |
              "vocabtree" | "retrieval" | "from_poses",
  "overlap":            10,                 // sequential
  "vocab_tree_path":    "...",              // vocabtree
  "retrieval_strategy": "dhash" | "vlad" | "netvlad",
  "retrieval_k":        20,
  "overlap_distance_m": 5.0,                // spatial / from_poses
  "max_angle_deg":      45.0
}
```

```json
// MatcherSpec — how to match each pair.
{
  "version": 1,
  "type":    "nn-mutual" | "nn-ratio" | "superglue" | "lightglue" |
             "loftr" | "mast3r",
  "use_gpu":         true,
  "cross_check":     true,
  "max_ratio":       0.8,
  "max_distance":    0.7,
  "matcher_options": { /* matcher-specific overrides */ }
}
```

Capability flags: `pairs.{strategy}` and `matchers.{type}`. The
match-stage request body is `{pairs: PairsSpec, matcher: MatcherSpec}`;
the legacy combined `MatchesSpec` shape was retired.

#### 6.9.9 Mesh generation (optional)

`POST /v1/reconstructions/{rid}/mesh` with body
`{"method": "poisson" | "delaunay", "options": {...}}` runs surface
reconstruction. Output is sealed as a fresh snapshot containing
`mesh.ply` (binary little-endian PLY) and `mesh.json` describing
vertex/face counts. Capabilities: `mesh.poisson`, `mesh.delaunay`,
`mesh.texture`.

```json
// mesh.json (the snapshot's MeshFile)
{
  "summary": {
    "method":              "poisson",
    "num_vertices":        184253,
    "num_faces":           368500,
    "has_vertex_colors":   true,
    "has_vertex_normals":  true,
    "bbox_min":            null,
    "bbox_max":            null
  },
  "mesh_url": "/v1/reconstructions/.../snapshots/.../mesh.ply"
}
```

#### 6.9.10 Modern export formats (optional)

In addition to `ply | nvm | colmap_text | colmap_bin`, sfmapi
standardizes four wire formats for downstream neural-rendering
pipelines:

| `format`              | Capability flag             | Output                                     |
|-----------------------|-----------------------------|--------------------------------------------|
| `nerfstudio`          | `export.nerfstudio`         | `transforms.json` (NeRFStudio shape)       |
| `instant_ngp`         | `export.instant_ngp`        | `transforms.json` (instant-ngp + aabb)     |
| `gaussian_splatting`  | `export.gaussian_splatting` | `sparse/0/{cameras,images,points3D}.txt`   |
| `kapture`             | `export.kapture`            | `sensors/` + `reconstruction/` directories |

These emitters are pure-Python and **MUST** be available when the
backend can produce a `Reconstruction` (no engine-specific code).

#### 6.9.11 Map merging (optional)

`POST /v1/reconstructions:merge` takes
`{target_recon_id, source_recon_ids, sim3_aligners?}` and seals the
merged result as a fresh snapshot under the target reconstruction.
All sources **MUST** belong to the same project as the target;
`sim3_aligners` is optional and parallel to `source_recon_ids` (use
the identity Sim3 to leave a model unchanged). Capability:
`recon.merge`.

#### 6.9.12 Batch / sequence localization (optional)

Capabilities `localize.batch` and `localize.sequence` are reserved
for backends that exploit cross-query constraints (relative-pose,
motion smoothing). The reference `colmap_mod` backend currently
implements `localize.batch` as N independent
`localize.from_memory` calls.

#### 6.9.13 Video frame extraction (optional)

`POST /v1/projects/{pid}/datasets:from_video` with body
`{video_path, fps?, max_frames?}` runs ffmpeg on the worker to extract
keyframes. Result carries `{output_dir, num_frames, fps}` so the
client can register the output as a `local`-source dataset.
Capability: `video.frame_extract` (depends on ffmpeg on the worker's
PATH).

#### 6.9.14 Kapture import (optional)

`POST /v1/projects/{pid}/datasets:import_kapture` with body
`{archive_path}` parses an extracted Kapture archive's
`sensors/sensors.txt` and `sensors/records_camera.txt`, returning
`{sensors, records, image_root}` so the client can `POST` a fresh
`local`-source dataset pointing at `image_root`. Capability:
`import.kapture` (pure-Python, always available).

#### 6.9.15 Pose-prior IMU + timestamps (optional)

`PosePrior` carries optional `timestamp_ns` and `imu` fields:

```json
{
  "cam_from_world": { "rotation": {...}, "translation": [...] },
  "covariance":     null,
  "gps":            null,
  "timestamp_ns":   1700000000000000000,
  "imu": {
    "timestamp_ns": 1700000000000000000,
    "gyro":  [0.01, 0.02, 0.03],
    "accel": [0.10, -9.81, 0.00]
  }
}
```

Capabilities `inputs.imu` and `inputs.timestamps` are advertised by
sfmapi itself (pure storage features, backend-independent).

#### 6.9.16 Bundle-adjustment loss kernels (optional)

`BundleAdjustmentSpec` adds:

```json
{
  "loss_kernel":    "squared" | "huber" | "cauchy" | "soft_l1" | "tukey",
  "loss_threshold": 1.0
}
```

`squared` is the unweighted least-squares default. Any other kernel
**MAY** be ignored by backends that don't expose it; clients
**SHOULD** check `features.x` capability flags only when they care
about the algorithm choice.

#### 6.9.17 Featuremetric BA (optional)

`BundleAdjustmentSpec.mode = "featuremetric"` requests Pixel-Perfect
SfM-style refinement (CNN-feature error, not raw reprojection).
Capability `ba.featuremetric`. Servers without the capability
return 501.

#### 6.9.18 Dense MVS (optional)

Run multi-view stereo on top of a sparse reconstruction:

| Method | Path                                               | Returns      |
|--------|----------------------------------------------------|--------------|
| POST   | `/v1/reconstructions/{rid}/dense`                  | 202 + job    |

The worker chains COLMAP's `undistort_images` →
`patch_match_stereo` (CUDA-only) → `stereo_fusion`, converts the
outputs from COLMAP's native binary into sfmapi wire formats, and
seals a fresh snapshot whose ``dense/`` subdirectory holds:

| File                                                                  | Media type                          |
|-----------------------------------------------------------------------|-------------------------------------|
| `dense/index.json`                                                    | `application/json` — `DenseManifestFile` |
| `dense/fused.bin`                                                     | `application/x-sfm-points-v1`       |
| `dense/depth_maps/{image_name}.bin`                                   | `application/x-sfm-depth-v1`        |
| `dense/normal_maps/{image_name}.bin` (optional)                       | `application/x-sfm-normal-v1`       |

`DenseManifestFile` shape:

```json
{
  "summary": {
    "num_images":      42,
    "num_depth_maps":  42,
    "num_normal_maps": 42,
    "fused_points":    1842311,
    "bbox_min": null,
    "bbox_max": null
  },
  "depth_maps": [
    {
      "image_id":       1,
      "image_name":     "DSC_0001.jpg",
      "width":          4032,
      "height":         3024,
      "depth_min":      0.42,
      "depth_max":      18.7,
      "has_normal_map": true
    }
  ]
}
```

#### Depth map binary (`application/x-sfm-depth-v1`)

32-byte header + ``width * height * float32`` body, row-major
top-to-bottom. ``0.0`` is the conventional "no depth" sentinel; clients
**MUST** treat non-finite values as missing.

| Offset | Size | Field      | Type       |
|--------|------|------------|------------|
| 0      | 8    | magic      | `b"SFMDPTH\0"` |
| 8      | 4    | version    | uint32 = 1 |
| 12     | 4    | width      | uint32     |
| 16     | 4    | height     | uint32     |
| 20     | 4    | depth_min  | float32    |
| 24     | 4    | depth_max  | float32    |
| 28     | 4    | _pad       | uint32 = 0 |

#### Normal map binary (`application/x-sfm-normal-v1`)

Same 32-byte header (magic = `b"SFMNRM\0\0"`); body is ``width *
height * 3 * float32``. Vectors are world-space, unit length.

#### 6.9.8 Single-image localization (optional)

Localize a query image against a reconstruction:

| Method | Path                                                | Body                  | Returns      |
|--------|-----------------------------------------------------|-----------------------|--------------|
| POST   | `/v1/reconstructions/{recon_id}/localize`           | `{blob_sha, sift?}`   | 202 + job    |

`blob_sha` is the content-address of the (already-uploaded) query
image. `sift` is an optional dict of SIFT extraction overrides.

The job runs SIFT on the query, then `pycolmap.localize_from_memory`
against the reconstruction's largest sealed snapshot. The task's
`outputs_ref` carries a `LocalizationResult`-shaped payload:

```json
{
  "success": true,
  "cam_from_world": { "rotation": {...}, "translation": [...] },
  "num_inliers": 87,
  "inlier_matches": [[12, 4521], [33, 8002]],
  "diagnostics": { "query_path": "...", "sparse_dir": "..." }
}
```

Servers **MUST** return 404 when `recon_id` is unknown and 422 when
`blob_sha` is missing or the wrong length (must be 64 hex chars).

### 6.10 Admin (optional)

| Method  | Path                          | Body                       | Returns                       |
|---------|-------------------------------|----------------------------|-------------------------------|
| POST    | `/v1/admin/api-keys`          | `{tenant_id, name?}`       | `{raw_key, api_key_id, ...}`  |
| GET     | `/v1/admin/api-keys`          | —                          | `[ApiKeyOut]`                 |
| DELETE  | `/v1/admin/api-keys/{kid}`    | —                          | `ApiKeyOut` (revoked)         |

Servers **MAY** omit this group entirely if keys are provisioned
out-of-band.

---

## 7. Wire formats

### 7.1 Binary points: `application/x-sfm-points-v1`

Header (44 bytes, little-endian):

| Offset | Size | Field    | Type       |
|--------|------|----------|------------|
| 0      | 8    | magic    | `b"SFMP3D\x00\x00"` |
| 8      | 4    | version  | uint32 (1) |
| 12     | 8    | count    | uint64     |
| 20     | 12   | bbox_min | 3 × float32 |
| 32     | 12   | bbox_max | 3 × float32 |

Each record (26 bytes, little-endian):

| Offset | Size | Field      | Type       |
|--------|------|------------|------------|
| 0      | 12   | xyz        | 3 × float32 |
| 12     | 3    | rgb        | 3 × uint8  |
| 15     | 1    | _pad       | uint8      |
| 16     | 2    | track_len  | uint16     |
| 18     | 8    | point3d_id | uint64     |

Records **MUST** be ordered by ascending `point3d_id`. This makes the
file a fixed-stride array, so HTTP `Range: bytes=A-B` requests can
fetch arbitrary point ranges without parsing the body.

`points_preview.bin` is the same format, decimated.

### 7.2 Snapshot JSON files

All snapshot JSONs use a single quaternion convention: **Hamilton
`(w, x, y, z)`, scalar first**. Servers **MUST** convert from any
other internal convention (e.g. Eigen's `(x, y, z, w)`) at the wire
boundary. All transforms are expressed as `Rigid3 = { rotation:
{w,x,y,z}, translation: [tx,ty,tz] }`.

#### `cameras.json`

```json
{
  "cameras": [
    {
      "camera_id": 1,
      "model": "SIMPLE_RADIAL",
      "width": 4032,
      "height": 3024,
      "params": [3200.0, 2016.0, 1512.0, 0.012],
      "has_prior_focal_length": false
    }
  ]
}
```

#### `images.json`

```json
{
  "images": [
    {
      "image_id": 1,
      "name": "DSC_0001.jpg",
      "camera_id": 1,
      "cam_from_world": {
        "rotation":    { "w": 1.0, "x": 0.0, "y": 0.0, "z": 0.0 },
        "translation": [0.0, 0.0, 0.0]
      },
      "points2D": [
        { "xy": [320.5, 240.1], "point3d_id": 42 },
        { "xy": [410.0, 198.7], "point3d_id": null }
      ]
    }
  ]
}
```

The `points2D` array index is the keypoint index (`kp_idx`) referenced
by tracks and TwoViewGeometry inlier sets. `point3d_id: null` means
"keypoint not in any 3D track."

#### `rigs.json` (optional — present when the reconstruction has rigs)

```json
{
  "rigs": [
    {
      "rig_id": 1,
      "ref_sensor_id": 0,
      "sensor_from_rig": {
        "0": { "rotation": {...}, "translation": [...] },
        "1": { "rotation": {...}, "translation": [...] }
      }
    }
  ]
}
```

#### `frames.json` (optional — present for multi-camera frames)

```json
{
  "frames": [
    {
      "frame_id": 10,
      "rig_id": 1,
      "rig_from_world": { "rotation": {...}, "translation": [...] },
      "data_ids": { "0": 100, "1": 101 }
    }
  ]
}
```

#### `pose_graph.json` (optional — present after `pgo`)

```json
{
  "pose_graph": {
    "nodes": [ /* ImagePose, points2D omitted */ ],
    "edges": [
      {
        "image_id1": 1,
        "image_id2": 2,
        "cam2_from_cam1": { "rotation": {...}, "translation": [...] },
        "weight": 1.0
      }
    ]
  }
}
```

#### `summary.json`

```json
{
  "models": [
    { "idx": 0, "num_reg_images": 12, "num_points3D": 4567 }
  ],
  "phase": "incremental_register",
  "mean_reproj_err": 1.07
}
```

Servers **MAY** include additional fields; clients **MUST** ignore
unknown ones.

### 7.2.1 Reconstruction-level files (not per snapshot)

Some artifacts track database state, not a frozen reconstruction —
they live at the reconstruction level and are served from
`/v1/reconstructions/{recon_id}/{name}` instead of inside a snapshot.

#### `two_view_geometries.json`

Emitted by the `verify` worker after `verify_matches` completes. The
file enumerates verified geometries between matched image pairs:

```json
{
  "pairs": [
    {
      "image_id1": 1,
      "image_id2": 2,
      "type": "calibrated",
      "num_inliers": 312,
      "F": null,
      "E": [...9 floats row-major...],
      "H": null,
      "inlier_matches": [[0, 1], [3, 4]]
    }
  ]
}
```

`type` is one of: `undefined | degenerate | calibrated | uncalibrated
| planar | panoramic | planar_or_panoramic | watermark | multiple`.
Only the matrix matching the geometry type is populated.

#### `correspondence_graph.json`

The **raw**, pre-verification matches between image pairs as written
by the matcher. Useful for debugging "why didn't this pair survive
verification?" Emitted by the match worker after every match run.

```json
{
  "pairs": [
    {
      "image_id1": 1,
      "image_id2": 2,
      "num_matches": 312,
      "matches": [[0, 5], [3, 8], [10, 12]]
    }
  ]
}
```

`matches` is a flat list of ``(point2d_idx_in_image1,
point2d_idx_in_image2)`` pairs, indexed against the keypoints in
``images.json`` for each image. Empty pairs are omitted from the file.

### 7.2.2 Native scene types (input shapes)

Servers that accept pose priors / georegistration input **MUST**
accept these shapes (see ``app.schemas.api.scene``):

```json
// PosePrior (covariance is row-major 6x6 over rx, ry, rz, tx, ty, tz)
{
  "cam_from_world": { "rotation": {...}, "translation": [...] },
  "covariance": [...36 floats...] | null,
  "gps": { "lat": 37.0, "lng": -122.0, "alt": 10.0,
           "horiz_accuracy_m": 5.0, "vert_accuracy_m": 8.0 } | null
}

// Sim3 (similarity Sim(3) for georegistration)
{
  "rotation":    { "w": ..., "x": ..., "y": ..., "z": ... },
  "translation": [..., ..., ...],
  "scale":       2.5
}
```

#### Spherical (equirectangular) camera

```json
{
  "camera_id": 1,
  "model":     "SPHERICAL",
  "width":     4096,
  "height":    2048,
  "params":    []
}
```

The ``"SPHERICAL"`` model represents a 360°×180° equirectangular
projection. ``params`` **MUST** be empty — only ``width`` / ``height``
matter. Implementations **SHOULD** test ``Camera.is_spherical()``
rather than string-comparing the model name.

### 7.3 ProgressEvent (SSE / WebSocket)

```json
{
  "schema_version": 1,
  "ts":             "2026-05-02T...",
  "job_id":         "01HZ...",
  "task_id":        "01HZ..." | null,
  "seq":            42,
  "kind":           "phase_started" | "phase_progress" | "phase_completed" |
                    "metric" | "snapshot_available" | "log_line" |
                    "warning" | "error",
  ...kind-specific fields
}
```

Phase enum: `feature_extraction, matching, geometric_verification,
incremental_init, incremental_register, incremental_ba,
global_rotation_avg, global_positioning, global_ba, hierarchical_*,
panorama, spherical, bundle_adjust, triangulate, relocalize,
pose_graph_optimize, segment, export, vlad_index`.

SSE clients **SHOULD** use `Last-Event-ID` to resume.

### 7.4 Specs (input shapes)

```json
// FeaturesSpec
{
  "version": 1,
  "sift_max_num_features": 8192,
  "sift_first_octave":     -1,
  "use_gpu":               true,
  "seed":                  0
}

// PairsSpec — see §6.9.8.
{
  "version":            1,
  "strategy":           "exhaustive" | "sequential" | "spatial" |
                        "vocabtree" | "retrieval" | "from_poses",
  "overlap":            10,
  "vocab_tree_path":    null,
  "retrieval_strategy": "vlad",
  "retrieval_k":        20,
  "overlap_distance_m": null,
  "max_angle_deg":      null
}

// MatcherSpec — see §6.9.8.
{
  "version":         1,
  "type":            "nn-mutual" | "nn-ratio" | "superglue" | "lightglue" |
                     "loftr" | "mast3r",
  "use_gpu":         true,
  "cross_check":     true,
  "max_ratio":       0.8,
  "max_distance":    0.7,
  "matcher_options": {}
}

// VerifySpec
{
  "version":          1,
  "use_gpu":          true,
  "min_inlier_ratio": 0.25
}

// PipelineSpec is a discriminated union on `kind`:
{ "kind": "incremental",  "version": 1, "min_num_matches": 15, ... }
{ "kind": "global",       "version": 1, "backend": "AUTO", ... }
{ "kind": "hierarchical", "version": 1, "cluster_max_size": 100, ... }
{ "kind": "spherical",    "version": 1, "panorama": true, ... }
```

---

## 8. WebSocket protocol

Endpoint: `/ws/v1/jobs/{job_id}` (Upgrade: websocket).
Optional query: `?last_event_id=N`.

Server frames (JSON text):

```json
{ "kind": "hello",            "job_id": "...", "last_event_id": 42 }
{ "kind": "<ProgressEvent>",  ...payload }
{ "kind": "cancel_requested", "force": false }
{ "kind": "terminal",         "status": "succeeded" | ... }
{ "kind": "pong" }
{ "kind": "error",            "message": "..." }
```

Client frames (JSON text):

```json
{ "op": "ping" }
{ "op": "cancel", "force": false }
```

Servers **MUST** close with code `1000` after sending `terminal` and
**MAY** close with `1008` for malformed frames or unknown `op`.

---

## 9. Job semantics

### 9.1 Cache key

Every Task carries
`cache_key = sha256(canonical_json({kind, inputs_hash, params_hash, runtime_version_id}))`.

When the orchestrator sees a Task whose `cache_key` already has a
`succeeded` row, it **MUST** short-circuit: the new Task starts in
`succeeded` with the cached `outputs_ref`, no work is enqueued.

`runtime_version_id` is a server-side identifier of the
`(engine_sha, dependency versions, hardware arch, seed)` tuple. A
server upgrade that changes any of these **MUST** produce a new
`runtime_version_id`.

### 9.2 Cancellation

- `POST /v1/jobs/{jid}:cancel` sets `cancel_requested=true`. Workers
  **MUST** check this flag at every phase boundary and exit cleanly.
  Status transitions from `running` to `cancelled`.
- `POST /v1/jobs/{jid}:cancel?force=true` additionally sets
  `cancel_force=true`. Workers **MAY** then SIGKILL the in-flight
  subprocess and restart. Status transitions to `cancelled_dirty`.
- A `cancelled` Task **MAY** be resumed.

### 9.3 Resume

`POST /v1/jobs/{jid}:resume` resets `(failed | cancelled |
cancelled_dirty)` Tasks to `pending`. `succeeded` Tasks stay (cache
hit). The Job transitions back to `pending`. Mapping tasks
**SHOULD** pick up from the latest checkpoint if the engine
supports it.

### 9.4 Sealed snapshot contract

Workers **MUST** produce snapshots via this protocol:

1. Write to `snapshots/.tmp_{seq}/`.
2. Write a `.complete` marker last.
3. `os.replace` (atomic rename) the temp dir to `snapshots/{seq}/`.
4. Update a `latest` text file via tmp+rename.

Readers (the API serving `GET .../snapshots/{seq}/{name}`)
**MUST**:

- Only enumerate dirs that contain a `.complete` file.
- Treat sealed snapshots as immutable (`Cache-Control: immutable`).
- Never open `database.db` or live `sparse/` files.

---

## 10. Conformance

A *conforming server* **MUST** implement at minimum:

- §6.1 health/meta (except `/metrics` is optional).
- §6.2 projects.
- §6.3 uploads (full chunked flow with idempotency).
- §6.4 datasets (`upload` source kind required; `local` + `s3` optional).
- §6.5 images (single create + list + delete + bytes; `:batchCreate`,
  `thumbnail`, `exif` optional).
- §6.6 stages (features + matches + verify with at least one
  matching `pairs.strategy`).
- §6.7 jobs + SSE events. WebSocket optional.
- §6.9 reconstruction reads + sealed snapshot reads.
- §7.1 binary points format.
- §7.3 `ProgressEvent` v1 schema.
- §9 job semantics: cache short-circuit, cooperative cancel,
  sealed-snapshot contract.

A *conforming server* **MAY** additionally implement:

- §6.8 pipeline recipes.
- §6.10 admin / api-keys.
- `local`/`s3` source kinds.
- WebSocket peek+cancel.
- Mask sets / segmentation (not yet specified).
- Dense reconstruction / mesh extraction (not yet specified).
- Geo-registration / submodel transforms (not yet specified).

Clients **MUST** be prepared for *optional* features to return 404.

---

## 11. Compatibility

### 11.1 Forward-compat for clients

Clients **MUST**:

- Ignore unknown JSON fields.
- Ignore unknown `_links` keys.
- Treat unknown `ProgressEvent.kind` values as "log_line"-equivalent
  (i.e., display message if present, otherwise drop silently).
- Tolerate new HTTP status codes within established classes (e.g.
  treat unrecognised 4xx as a client error).

### 11.2 Vendor extensions

Servers **MAY** add fields prefixed `x-` to any response. Clients
**MUST** ignore them unless they specifically opted in to a vendor
extension.

Vendor-specific endpoints **SHOULD** live under `/v1/x-<vendor>/...`.

### 11.3 Deprecation

A server deprecating an endpoint **SHOULD** emit a
`Deprecation: <date>` and `Sunset: <date>` response header per
[RFC 8594][rfc8594] for at least 90 days before removal in a
*major* version bump.

[rfc8594]: https://www.rfc-editor.org/rfc/rfc8594

---

## 12. Open issues / future revisions

The following surfaces are explicitly **not yet** in the standard,
but are reserved for future minor revisions. Servers **MAY**
implement them ahead of standardization under `x-` prefix paths.

- **Image similarity / VLAD query**: "k nearest images to image_id".
- **Dense reconstruction / mesh**: MVS, mesh + texture extraction.
- **Geo-registration**: rigid + scale transforms applied to a
  submodel (geo, custom world frame).
- **Submodel comparison / alignment**: metrics between two
  submodels.
- **Mask sets**: a stable wire format for segmentation outputs.

(Octree tiles, image observations, and point visibility were
specified inline in §6.9.1 / §6.9.2 in v1.0-draft. Earlier drafts
listed them here as future work.)

---

## Appendix A. Notable invariants

- The same `(dataset_snapshot_hash, params_hash, runtime_version_id)`
  triple **MUST** always resolve to the same Reconstruction.
- Sealed snapshots are immutable; their files **MUST NOT** ever be
  rewritten.
- Tenant boundary is enforced server-side; cross-tenant access
  returns 404 (not 403) to avoid leaking existence.
- Web-process implementations **SHOULD NOT** import heavy SfM
  engines; engines live in workers.

## Appendix B. Reserved status code semantics

| Status | Meaning in this spec                                         |
|--------|--------------------------------------------------------------|
| 202    | Long-running operation accepted; observe via `Location`.     |
| 304    | `If-None-Match` hit; body is empty.                          |
| 416    | Out-of-range chunk in chunked upload.                        |
| 422    | Schema validation failed (request well-formed but invalid).  |
| 503    | Underlying engine (e.g. pycolmap) unavailable.               |
| 507    | Storage error (disk full, blob missing).                     |

## Appendix C. Glossary

- **Blob** — content-addressed bytes in the server's blob store.
- **Materialization** — per-job realization of an `ImageSource` as a
  filesystem directory the engine can read.
- **Reconstruction** — a pipeline run; the result of executing a
  `PipelineSpec` against a dataset.
- **SubModel** — one of N sparse models a reconstruction may produce.
- **Snapshot** — a sealed, immutable directory of reconstruction
  artifacts at a given point in time.
- **Recipe** — a named multi-stage pipeline (`incremental` etc.).
- **Cache key** — server-computed hash that identifies a Task's
  inputs + params + runtime; identical key = identical output.

---

*Comments, issues, and proposed changes:* file under
`https://github.com/opsiclear/sfmapi/issues` with the `spec` label.
