"""SfmBackend protocol contract tests.

Verifies the registry resolves the default backend, that a user-defined
stub satisfies the structural protocol, and that swapping is the
single-import-change the design promises.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

from app.adapters.backend import SfmBackend
from app.adapters.colmap_backend import ColmapModBackend
from app.adapters.registry import (
    get_backend,
    list_backends,
    register_backend,
)
from app.core.errors import CapabilityUnavailableError

pytestmark = pytest.mark.unit


def test_default_backend_is_colmap_mod() -> None:
    backend = get_backend()
    assert backend.name == "colmap_mod"
    assert isinstance(backend, ColmapModBackend)


def test_get_backend_with_explicit_name() -> None:
    backend = get_backend("colmap_mod")
    assert backend.name == "colmap_mod"


def test_unknown_backend_name_raises() -> None:
    with pytest.raises(KeyError, match="unknown SfmBackend"):
        get_backend("not.a.real.backend")


class _StubBackend:
    """Minimal stub satisfying SfmBackend by structural typing —
    every method exists and most just raise CapabilityUnavailableError.
    Demonstrates that adding a new backend is purely additive."""

    name = "stub"
    version = "0.0.1"
    vendor = "test"

    def capabilities(self) -> set[str]:
        return {"features.extract"}

    def extract_features(
        self,
        *,
        database_path: Path,
        image_root: Path,
        image_list: list[str],
        options: dict,
    ) -> dict:
        return {"num_images": len(image_list), "num_keypoints": 0, "stub": True}

    def match(self, *, database_path: Path, mode: str, options: dict) -> dict:
        raise CapabilityUnavailableError(capability=f"matches.{mode}")

    def verify_matches(self, *, database_path: Path, options: dict) -> dict:
        raise CapabilityUnavailableError(capability="matches.verify")

    def iter_two_view_geometries(self, *, database_path: Path) -> Iterator:
        return iter([])

    def iter_correspondences(self, *, database_path: Path) -> Iterator:
        return iter([])

    def run_mapping(self, **_: Any) -> tuple[list[dict], list[Any]]:
        raise CapabilityUnavailableError(capability="map.incremental")

    def bundle_adjustment(self, **_: Any) -> dict:
        raise CapabilityUnavailableError(capability="ba.standard")

    def triangulate(self, **_: Any) -> dict:
        raise CapabilityUnavailableError(capability="triangulate.retri")

    def relocalize(self, **_: Any) -> dict:
        raise CapabilityUnavailableError(capability="relocalize.images")

    def pose_graph_optimize(self, **_: Any) -> dict:
        raise CapabilityUnavailableError(capability="pgo.optimize")

    def export(self, **_: Any) -> dict:
        raise CapabilityUnavailableError(capability="export.ply")

    def convert_spherical_to_cubemap(self, **_: Any) -> dict:
        raise CapabilityUnavailableError(capability="spherical.to_cubemap")

    def render_spherical_cubemap_images(self, **_: Any) -> dict:
        raise CapabilityUnavailableError(capability="spherical.render_cubemap")

    def dense_pipeline(self, **_: Any) -> dict:
        raise CapabilityUnavailableError(capability="dense.patch_match_stereo")

    def build_vlad_index(self, **_: Any) -> dict:
        raise CapabilityUnavailableError(capability="similarity.vlad")

    def localize_from_memory(self, **_: Any) -> dict:
        raise CapabilityUnavailableError(capability="localize.from_memory")

    def apply_sim3(self, **_: Any) -> dict:
        raise CapabilityUnavailableError(capability="georegister.sim3")

    def generate_mesh(self, **_: Any) -> dict:
        raise CapabilityUnavailableError(capability="mesh.poisson")

    def merge_reconstructions(self, **_: Any) -> dict:
        raise CapabilityUnavailableError(capability="recon.merge")

    def localize_batch(self, **_: Any) -> list:
        raise CapabilityUnavailableError(capability="localize.batch")

    def read_reconstruction(self, path: Path) -> Any:
        raise CapabilityUnavailableError(capability="features.extract")

    def runtime_versions(self) -> dict[str, str]:
        return {"stub_version": "0.0.1"}


def test_stub_satisfies_sfmbackend_structurally() -> None:
    """Structural typing: any class with the right method names + sigs
    is a SfmBackend, no inheritance required."""
    stub = _StubBackend()
    assert isinstance(stub, SfmBackend)


def test_register_and_resolve_custom_backend() -> None:
    register_backend("stub-test", _StubBackend)
    try:
        assert "stub-test" in list_backends()
        backend = get_backend("stub-test")
        assert backend.name == "stub"
        result = backend.extract_features(
            database_path=Path("/tmp/db"),
            image_root=Path("/tmp/imgs"),
            image_list=["a.jpg", "b.jpg"],
            options={},
        )
        assert result == {"num_images": 2, "num_keypoints": 0, "stub": True}
    finally:
        # Don't pollute the registry for sibling tests.
        from app.adapters.registry import _REGISTRY

        _REGISTRY.pop("stub-test", None)


def test_unsupported_capability_raises_501_shaped_error() -> None:
    backend = _StubBackend()
    with pytest.raises(CapabilityUnavailableError) as exc:
        backend.match(database_path=Path("/tmp/db"), mode="exhaustive", options={})
    assert exc.value.status_code == 501
    assert exc.value.extras["capability"] == "matches.exhaustive"


def test_capabilities_endpoint_picks_up_swapped_backend() -> None:
    """Replacing the default backend in the registry changes the
    capability snapshot. Proves swap-is-one-import-change."""
    from app.core.capabilities import detect_capabilities

    register_backend("colmap_mod", _StubBackend)
    try:
        caps = detect_capabilities()
        assert caps.backend.name == "stub"
        # Stub only advertises features.extract — the rest stay False.
        assert caps.supports("features.extract")
        assert not caps.supports("ba.standard")
        assert not caps.supports("dense.patch_match_stereo")
        # sfmapi-internal capabilities still on regardless of backend:
        assert caps.supports("similarity.dhash")
        assert caps.supports("pose_priors.read_write")
    finally:
        # Restore the colmap_mod default.
        register_backend("colmap_mod", ColmapModBackend)
