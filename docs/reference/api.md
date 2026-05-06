# REST API reference

All paths are prefixed with `/v1` unless noted.

## Conventions

- **Auth**: `Authorization: Bearer <api_key>` when `auth_mode=api_key`.
- **Errors**: `application/problem+json` per RFC 7807. See
  [errors](errors.md).
- **IDs**: 26-char ULIDs.
- **Pagination**: cursor-based via `?cursor=` and `?limit=`. Responses
  include `next_cursor` (or `null`).
- **Long-running ops**: `POST` returns `202 Accepted` with
  `{job_id, task_ids[]}` and a `Location: /v1/jobs/{id}` header.

## Health & meta

| Method | Path | Purpose |
|---|---|---|
| GET | `/healthz` | Liveness — always 200 if process alive |
| GET | `/readyz` | Readiness — checks DB + dependencies |
| GET | `/version` | Versions of sfmapi + pycolmap stack |
| GET | `/metrics` | Prometheus exposition |

## Projects

| Method | Path | Body | Returns |
|---|---|---|---|
| POST | `/v1/projects` | `{name, description?}` | `Project` |
| GET | `/v1/projects` | — | `Page<Project>` |
| GET | `/v1/projects/{pid}` | — | `Project` |
| DELETE | `/v1/projects/{pid}` | — | 204 |

## Uploads (chunked)

| Method | Path | Body / Headers | Returns |
|---|---|---|---|
| POST | `/v1/uploads` | `{expected_size, content_type?, expected_sha?}` + `Idempotency-Key` | `Upload` |
| GET | `/v1/uploads/{uid}` | — | `Upload` |
| PATCH | `/v1/uploads/{uid}` | raw chunk body + `Content-Range: bytes A-B/T` | `Upload` |
| POST | `/v1/uploads/{uid}:finalize` | `{}` (or `X-Content-SHA256` header) | `Upload` |

## Image sources / datasets / images

| Method | Path | Body | Returns |
|---|---|---|---|
| POST | `/v1/projects/{pid}/datasets` | `{name, source: {kind: upload\|local\|s3, ...}, camera_model, intrinsics_mode, is_spherical, rig_config?, respect_exif_orientation}` | `Dataset` |
| GET | `/v1/projects/{pid}/datasets` | — | `[Dataset]` |
| GET | `/v1/projects/{pid}/datasets/{did}` | — | `Dataset` |
| POST | `/v1/datasets/{did}/images` | `{name, blob_sha?, rel_path?, width?, height?, exif?}` | `Image` |
| GET | `/v1/datasets/{did}/images` | — | `Page<Image>` |
| DELETE | `/v1/datasets/{did}/images/{name}` | — | 204 |

## SfM stages (single-task jobs)

| Method | Path | Body | Returns |
|---|---|---|---|
| POST | `/v1/datasets/{did}/features` | `{spec: FeaturesSpec, image_root, image_list[]}` | 202 + `JobSubmitResponse` |
| POST | `/v1/datasets/{did}/matches` | `{pairs: PairsSpec, matcher: MatcherSpec, database_path}` | 202 + `JobSubmitResponse` |
| POST | `/v1/datasets/{did}/verify` | `{spec: VerifySpec, database_path}` | 202 + `JobSubmitResponse` |

## Pipelines (recipe sugar)

| Method | Path | Body | Returns |
|---|---|---|---|
| POST | `/v1/projects/{pid}/pipelines/{recipe}` | `{dataset_id, image_root, image_list[], features?, pairs?, matcher?, verify?, spec: PipelineSpec}` | 202 + `JobSubmitResponse` |

`recipe ∈ {incremental, global, hierarchical, spherical}` — and
`spec.kind` must match.

## Jobs

| Method | Path | Body | Returns |
|---|---|---|---|
| GET | `/v1/jobs/{jid}` | — | `JobDetail` |
| POST | `/v1/jobs/{jid}:cancel` | `?force=true` (optional) | `Job` (cancelled) |
| POST | `/v1/jobs/{jid}:resume` | — | 202 + `Job` |
| GET | `/v1/jobs/{jid}/events` | `Last-Event-ID` (optional) | SSE stream of `ProgressEvent` |

## Reconstructions / submodels / snapshots

| Method | Path | Returns |
|---|---|---|
| GET | `/v1/reconstructions/{rid}` | `Reconstruction` |
| GET | `/v1/reconstructions/{rid}/submodels` | `[SubModel]` |
| GET | `/v1/submodels/{smid}` | `SubModel` |
| GET | `/v1/reconstructions/{rid}/snapshots` | `{seqs: [int]}` |
| GET | `/v1/reconstructions/{rid}/snapshots/{seq}/{name}` | file bytes |

`{name}` is one of `cameras.json | images.json | rigs.json |
frames.json | points.bin | points_preview.bin | summary.json`.

## Admin

| Method | Path | Body | Returns |
|---|---|---|---|
| POST | `/v1/admin/api-keys` | `{tenant_id, name?}` | `IssueKeyResponse` (raw_key only returned once) |
| GET | `/v1/admin/api-keys` | — | `[ApiKeyOut]` |
| DELETE | `/v1/admin/api-keys/{kid}` | — | `ApiKeyOut` (revoked) |

## ProgressEvent

```{eval-rst}
.. automodule:: app.schemas.progress_event
   :members:
   :no-index:
```

## Pipeline specs

```{eval-rst}
.. automodule:: app.schemas.pipeline_spec
   :members:
   :no-index:
```

## Binary points format

`Content-Type: application/x-sfm-points-v1`. Fixed 44-byte header,
26 bytes per point.

```{eval-rst}
.. automodule:: app.schemas.points_binary
   :members:
   :no-index:
```

Records are written in ascending `point3d_id` order so HTTP `Range`
requests treat the file as a fixed-stride array. `points_preview.bin`
is the same format, decimated.
