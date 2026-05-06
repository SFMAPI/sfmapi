"""Lazy pycolmap adapter.

The web layer must never import this module's `pycolmap` symbol — only
worker processes call into the adapter's functions. To enforce this we
import `pycolmap` lazily at first use and raise a clean error if it's
unavailable in the current deployment.

Phase 1: feature extraction, matching, verification entry points.
Phase 2+: mapping, BA, triangulation, relocalization, PGO, diagnostics.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.core.config import get_settings
from app.core.errors import PycolmapUnavailableError


def _require_pycolmap() -> Any:
    s = get_settings()
    if not s.pycolmap_available:
        raise PycolmapUnavailableError(
            "pycolmap is not enabled (set SFMAPI_PYCOLMAP_AVAILABLE=true)"
        )
    try:
        import pycolmap  # type: ignore[import-not-found]
    except ImportError as e:
        raise PycolmapUnavailableError(f"pycolmap import failed: {e}") from e
    return pycolmap


def get_runtime_versions() -> dict[str, str]:
    """Probe the loaded pycolmap (or settings) for runtime version vector."""
    s = get_settings()
    out = {
        "colmap_sha": s.colmap_sha,
        "baxx_sha": s.baxx_sha,
        "cudss_ver": s.cudss_ver,
        "cuda_arch": s.cuda_arch,
    }
    if s.pycolmap_available:
        try:
            pc = _require_pycolmap()
            ver = getattr(pc, "__version__", None)
            if ver:
                out["pycolmap_version"] = ver
        except PycolmapUnavailableError:
            pass
    return out


def extract_features_into_db(
    *,
    database_path: Path,
    image_root: Path,
    image_list: list[str],
    options: dict,
) -> dict:
    pc = _require_pycolmap()
    db_path_str = str(database_path)
    img_path_str = str(image_root)
    reader_options = pc.ImageReaderOptions()
    sift_options = pc.SiftExtractionOptions()
    for k, v in (options.get("sift") or {}).items():
        if hasattr(sift_options, k):
            setattr(sift_options, k, v)
    pc.extract_features(
        database_path=db_path_str,
        image_path=img_path_str,
        image_names=image_list,
        reader_options=reader_options,
        sift_options=sift_options,
    )
    with pc.Database(db_path_str) as db:
        return {
            "num_images": db.num_images,
            "num_keypoints": db.num_keypoints,
        }


def match_in_db(*, database_path: Path, mode: str, options: dict) -> dict:
    pc = _require_pycolmap()
    p = str(database_path)
    if mode == "exhaustive":
        opts = pc.ExhaustiveMatchingOptions()
        pc.match_exhaustive(database_path=p, matching_options=opts)
    elif mode == "sequential":
        opts = pc.SequentialMatchingOptions()
        for k, v in (options.get("sequential") or {}).items():
            if hasattr(opts, k):
                setattr(opts, k, v)
        pc.match_sequential(database_path=p, matching_options=opts)
    elif mode == "spatial":
        opts = pc.SpatialMatchingOptions()
        pc.match_spatial(database_path=p, matching_options=opts)
    elif mode == "vocabtree":
        opts = pc.VocabTreeMatchingOptions()
        for k, v in (options.get("vocabtree") or {}).items():
            if hasattr(opts, k):
                setattr(opts, k, v)
        pc.match_vocabtree(database_path=p, matching_options=opts)
    else:
        raise ValueError(f"Unknown match mode: {mode}")
    with pc.Database(p) as db:
        return {"num_matches": db.num_matches}


def verify_matches(*, database_path: Path, options: dict) -> dict:
    pc = _require_pycolmap()
    p = str(database_path)
    opts = pc.TwoViewGeometryOptions()
    for k, v in (options or {}).items():
        if hasattr(opts, k):
            setattr(opts, k, v)
    pc.verify_matches(database_path=p, options=opts)
    with pc.Database(p) as db:
        return {"num_verified_matches": db.num_verified_matches}
