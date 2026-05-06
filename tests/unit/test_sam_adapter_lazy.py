from __future__ import annotations

import sys

import pytest

pytestmark = pytest.mark.unit


def test_sam_adapter_import_does_not_load_torch() -> None:
    sys.modules.pop("torch", None)
    sys.modules.pop("segment_anything", None)
    sys.modules.pop("app.adapters.sam_adapter", None)
    import app.adapters.sam_adapter  # noqa: F401

    assert "torch" not in sys.modules
    assert "segment_anything" not in sys.modules
