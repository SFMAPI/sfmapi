"""Lazy SAM adapter — Phase 3.

Like the colmap adapter, this never imports `torch` or
`segment_anything` until actually invoked. This keeps the web process
cold of heavy ML deps.

For Phase 3 we expose a single `segment_image(image_path) → mask_bytes`
entry point. The `model_artifact` table tracks which weights file backs
the named SAM model.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.core.errors import SfmApiError


class SamUnavailableError(SfmApiError):
    """SAM (segment-anything) backend can't load. 501 mirrors the
    capability-unavailable pattern used by ``PycolmapUnavailableError``
    (request is well-formed; the deployment doesn't expose this
    capability)."""

    status_code = 501
    error_type = "sam_unavailable"
    title = "segment-anything not available in this deployment"


def _require_sam() -> Any:
    try:
        import segment_anything  # type: ignore[import-not-found]
        import torch  # noqa: F401
    except ImportError as e:
        raise SamUnavailableError(str(e)) from e
    return segment_anything


def segment_image(*, image_path: Path, model_path: Path, model_kind: str = "vit_b") -> bytes:
    """Returns a binary mask as raw bytes (uint8 0/255 PNG)."""
    sam = _require_sam()
    import cv2  # type: ignore[import-not-found]
    import numpy as np  # noqa: F401
    import torch  # type: ignore[import-not-found]

    sam_model = sam.sam_model_registry[model_kind](checkpoint=str(model_path))
    if torch.cuda.is_available():
        sam_model.to("cuda")
    predictor = sam.SamPredictor(sam_model)
    img = cv2.imread(str(image_path))
    if img is None:
        raise SfmApiError(f"Failed to read image: {image_path}")
    predictor.set_image(img)
    masks, _scores, _logits = predictor.predict(multimask_output=False)
    mask = (masks[0] * 255).astype("uint8")
    ok, encoded = cv2.imencode(".png", mask)
    if not ok:
        raise SfmApiError("Failed to encode mask PNG")
    return bytes(encoded)
