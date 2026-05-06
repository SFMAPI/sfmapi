from __future__ import annotations

import sys

import pytest

pytestmark = pytest.mark.integration


def test_adapter_import_does_not_load_pycolmap() -> None:
    sys.modules.pop("pycolmap", None)
    sys.modules.pop("app.adapters.colmap_adapter", None)
    import app.adapters.colmap_adapter  # noqa: F401

    assert "pycolmap" not in sys.modules


def test_adapter_raises_when_unavailable(monkeypatch) -> None:
    from app.adapters import colmap_adapter
    from app.core.config import get_settings
    from app.core.errors import PycolmapUnavailableError

    s = get_settings()
    monkeypatch.setattr(s, "pycolmap_available", False)
    with pytest.raises(PycolmapUnavailableError):
        colmap_adapter.extract_features_into_db(
            database_path="x", image_root="y", image_list=[], options={}
        )
