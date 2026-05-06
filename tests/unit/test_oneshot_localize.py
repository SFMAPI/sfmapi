"""Unit tests for the one-shot localize service. Covers the layers
that DON'T require pycolmap (input validation, missing sparse dir,
spec translation). The pycolmap-bound localize call itself is covered
by the existing localize integration test path."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.core.errors import NotFoundError, ValidationError
from app.schemas.pipeline_spec import FeaturesSpec
from app.services import oneshot_service

pytestmark = pytest.mark.unit


def test_localize_oneshot_rejects_empty_body(tmp_path: Path) -> None:
    sparse_dir = tmp_path / "sparse"
    sparse_dir.mkdir()
    with pytest.raises(ValidationError, match="empty request body"):
        oneshot_service.localize_oneshot(
            b"", recon_id="r1", spec=FeaturesSpec(), sparse_dir=sparse_dir
        )


def test_localize_oneshot_rejects_bad_content_type(tmp_path: Path) -> None:
    sparse_dir = tmp_path / "sparse"
    sparse_dir.mkdir()
    with pytest.raises(ValidationError, match="unsupported content type"):
        oneshot_service.localize_oneshot(
            b"\xff\xd8\xff\xe0fake-jpeg",
            recon_id="r1",
            spec=FeaturesSpec(),
            sparse_dir=sparse_dir,
            content_type="text/csv",
        )


def test_localize_oneshot_rejects_missing_sparse_dir(tmp_path: Path) -> None:
    """No mapping has run yet — the sparse_dir doesn't exist on disk."""
    missing = tmp_path / "no-such-dir"
    with pytest.raises(NotFoundError, match="sparse dir for recon"):
        oneshot_service.localize_oneshot(
            b"\xff\xd8\xff\xe0image-bytes",
            recon_id="r1",
            spec=FeaturesSpec(),
            sparse_dir=missing,
            content_type="image/jpeg",
        )
