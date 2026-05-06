# 5-minute curl tour

A complete `curl`-driven walk through the canonical SfM flow:
project → upload bytes → register dataset → register images →
extract features → match → verify → run incremental mapping →
read sealed snapshot.

Runs against an ephemeral local dev server; no GPU required to
walk the calls themselves (the worker tasks just stub when
`pycolmap` isn't installed).

## Prerequisites

```bash
# Start the server in ephemeral mode (in-memory DB, inline queue).
SFMAPI_EPHEMERAL=true uv run uvicorn app.main:app --port 8000 &
BASE=http://localhost:8000
```

## 1. Create a project

```bash
PROJECT_ID=$(curl -sX POST $BASE/v1/projects \
  -H 'Content-Type: application/json' \
  -d '{"name": "tour"}' | jq -r .project_id)
echo "PROJECT_ID=$PROJECT_ID"
```

## 2. Upload an image (chunked)

```bash
# Open an upload session.
PAYLOAD_SIZE=$(stat -c '%s' my_image.jpg)
UPLOAD_ID=$(curl -sX POST $BASE/v1/uploads \
  -H 'Content-Type: application/json' \
  -d "{\"expected_size\": $PAYLOAD_SIZE}" | jq -r .upload_id)

# Push bytes in one chunk (Content-Range: bytes 0-(N-1)/N).
END=$((PAYLOAD_SIZE - 1))
curl -sX PATCH $BASE/v1/uploads/$UPLOAD_ID \
  -H "Content-Range: bytes 0-$END/$PAYLOAD_SIZE" \
  --data-binary @my_image.jpg

# Seal it; returns blob_sha.
BLOB_SHA=$(curl -sX POST $BASE/v1/uploads/$UPLOAD_ID:finalize \
  | jq -r .blob_sha)
```

## 3. Create a dataset (upload-source)

```bash
DATASET_ID=$(curl -sX POST $BASE/v1/projects/$PROJECT_ID/datasets \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "tour-ds",
    "source": {"kind": "upload", "entries": []},
    "camera_model": "SIMPLE_RADIAL",
    "intrinsics_mode": "single_camera",
    "is_spherical": false,
    "respect_exif_orientation": true
  }' | jq -r .dataset_id)
```

## 4. Register the image

```bash
curl -sX POST $BASE/v1/datasets/$DATASET_ID/images \
  -H 'Content-Type: application/json' \
  -d "{\"name\": \"my_image.jpg\", \"blob_sha\": \"$BLOB_SHA\"}"
```

For multiple images use `:batchCreate` (up to 1000 per call):

```bash
curl -sX POST $BASE/v1/datasets/$DATASET_ID/images:batchCreate \
  -H 'Content-Type: application/json' \
  -d '{"requests": [
    {"name": "a.jpg", "blob_sha": "..."},
    {"name": "b.jpg", "blob_sha": "..."}
  ]}'
```

## 5. Run a recipe pipeline

The fastest path: one POST kicks off features → matches → verify → map.

```bash
JOB_ID=$(curl -sX POST $BASE/v1/projects/$PROJECT_ID/pipelines/incremental \
  -H 'Content-Type: application/json' \
  -d "{
    \"dataset_id\": \"$DATASET_ID\",
    \"features\": {\"version\": 1, \"type\": \"sift\"},
    \"pairs\":    {\"version\": 1, \"strategy\": \"exhaustive\"},
    \"matcher\":  {\"version\": 1, \"type\": \"nn-mutual\"},
    \"verify\":   {\"version\": 1},
    \"spec\":     {\"kind\": \"incremental\", \"version\": 1}
  }" | jq -r .job_id)
echo "JOB_ID=$JOB_ID"
```

## 6. Poll the job

```bash
# Quick poll loop.
while true; do
  STATUS=$(curl -s $BASE/v1/jobs/$JOB_ID | jq -r .status)
  echo "  status=$STATUS"
  case "$STATUS" in
    succeeded|failed|cancelled|cancelled_dirty) break ;;
  esac
  sleep 1
done
```

Or stream the live progress events:

```bash
curl -N $BASE/v1/jobs/$JOB_ID/events
```

## 7. Read the sealed snapshot

```bash
# Find the reconstruction this job produced.
RECON_ID=$(curl -s $BASE/v1/jobs/$JOB_ID | jq -r .recon_id // empty)

# List snapshots; pick the latest seq.
SEQ=$(curl -s $BASE/v1/reconstructions/$RECON_ID/snapshots \
  | jq -r '.seqs[-1]')

# Pull each artifact (cameras / images / points / summary).
curl -o cameras.json   $BASE/v1/reconstructions/$RECON_ID/snapshots/$SEQ/cameras.json
curl -o images.json    $BASE/v1/reconstructions/$RECON_ID/snapshots/$SEQ/images.json
curl -o points.bin     $BASE/v1/reconstructions/$RECON_ID/snapshots/$SEQ/points.bin
curl -o summary.json   $BASE/v1/reconstructions/$RECON_ID/snapshots/$SEQ/summary.json

# Decode points.bin in Python:
#   from sfmapi_client_gen._ergonomics import parse_points_binary
#   pts = parse_points_binary(open("points.bin","rb").read())
```

## 8. Cancel mid-flight

```bash
curl -sX POST $BASE/v1/jobs/$JOB_ID:cancel
# or with hard-kill:
curl -sX POST "$BASE/v1/jobs/$JOB_ID:cancel?force=true"
```

## See also

- [authentication](auth.md) for the production `auth_mode=api_key`
  flow.
- [openapi](openapi.md) for the live, machine-readable contract.
- [errors](errors.md) for the RFC 7807 error envelope shape.
- [api](api.md) for the full route catalog.
