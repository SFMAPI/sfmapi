# Phase 3 — Segmentation + Masks

**Goal:** Image segmentation produces `MaskSet`s. Datasets use
`active_maskset_id` to feed masks into `extract_features`. Model artifacts
(SAM checkpoints) versioned and lazily downloaded.

**Success criteria:**
- `POST /v1/datasets/{did}/masksets {from_segment: SegmentationSpec}` runs
  SAM on each image, writes mask PNGs to `masks/{maskset_id}/`, registers
  `MaskSet` row.
- `PATCH /v1/datasets/{did} {active_maskset_id}` switches; subsequent
  `POST /features` uses masks; cache key includes `active_maskset_id`.
- SAM model file resolved by `model_artifact` row; lazy download +
  sha verify; cache key includes `sam_model_sha`.

## TDD task list

### 3.1 — model_artifact registry

- [ ] `tests/integration/test_model_artifact.py`:
  - First-use download (mocked HTTP); sha verified; row created.
  - Second use: served from local cache; no HTTP.
  - Corrupt local file (mismatch sha) → re-download or fail.
- [ ] Implement: alembic 0004 `model_artifact`,
      `app/services/model_artifact_service.py`,
      `app/storage/models.py` (filesystem layout `models/{family}/{name}/{version}/`).

### 3.2 — SAM adapter (lazy)

- [ ] `tests/unit/test_sam_adapter_lazy.py` — adapter import does not
      import torch; calling raises if torch unavailable.
- [ ] `tests/integration/test_sam_adapter_real.py` (`needs_torch` marker)
      — small image → mask; mask is binary uint8.
- [ ] Implement: `app/adapters/sam_adapter.py`.

### 3.3 — MaskSet model + endpoint

- [ ] `tests/e2e/test_segment_endpoint.py`:
  - `POST /v1/datasets/{did}/masksets {from_segment: {model: sam_vit_b,
    options: {...}}}` → 202 + job; job runs across all images; final
    state has `count` masks.
  - Upload-based maskset: `POST /v1/datasets/{did}/masksets` with
    multipart of mask files keyed by image name.
  - `GET /v1/datasets/{did}/masksets` lists; `GET .../{mid}/masks/{img}`
    returns PNG.
- [ ] Implement: alembic 0005 (`maskset`, `mask`),
      `app/api/v1/masksets.py`, `app/workers/tasks/segment.py`.

### 3.4 — Mask-aware feature extraction

- [ ] `tests/e2e/test_features_with_mask.py`:
  - Without mask vs with mask → keypoint counts differ; cache key
    differs.
- [ ] Implement: extraction task reads `dataset.active_maskset_id`,
      passes mask path to `extract_features`.

## Definition of done

All boxes ticked. A 4-image fixture goes through SAM segmentation, mask
activation, masked feature extraction, and downstream mapping reflects the
masked features.
