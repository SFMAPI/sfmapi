from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from app.core.errors import ValidationError
from app.services import sfm_stage_service
from sfm_hub.discovery import discover_plugins, load_backend_entry_points
from sfm_hub.doctor import detect_external_tools
from sfm_hub.install import build_docker_install_plan, build_install_plan, parse_github_source
from sfm_hub.models import PluginManifest
from sfm_hub.registry import get_manifest, list_manifests, search_manifests
from sfm_hub.routing import ProviderAmbiguityError, ensure_provider_enabled, resolve_provider
from sfm_hub.state import (
    RoutingProfile,
    load_state,
    record_manual_install,
    save_state,
    set_enabled,
    set_project_profile,
    upsert_profile,
)

pytestmark = pytest.mark.unit


def test_bundled_manifests_validate_and_include_initial_entries() -> None:
    manifests = list_manifests()
    plugin_ids = {manifest.plugin_id for manifest in manifests}

    assert {
        "colmap_cli",
        "pycolmap",
        "colmap_native",
        "realityscan_cli",
        "hloc",
        "instantsfm",
        "spheresfm",
    } <= plugin_ids

    for manifest in manifests:
        assert manifest.github_url.startswith("https://github.com/SFMAPI/")
        assert manifest.entry_points
        assert manifest.providers
        assert manifest.runtime_mode_names()
        assert set(manifest.provider_ids()) == {
            provider.provider_id for provider in manifest.providers
        }


def test_schema_file_lists_required_manifest_fields() -> None:
    schema = json.loads(Path("sfm_hub/schemas/backend-plugin.schema.json").read_text())

    assert "plugin_id" in schema["required"]
    assert "github_url" in schema["required"]
    assert "entry_points" in schema["required"]
    assert "providers" in schema["required"]
    assert "runtime_modes" in schema["required"]


def test_registry_search_and_github_install_plan() -> None:
    assert [manifest.plugin_id for manifest in search_manifests("hloc")] == ["hloc"]

    source = parse_github_source(
        "https://github.com/SFMAPI/sfmapi_colmap_cli/tree/v1.2.3",
        package="sfmapi-colmap-cli",
    )
    plan = build_install_plan(source)

    assert source.normalized_url == "https://github.com/SFMAPI/sfmapi_colmap_cli.git"
    assert source.ref == "v1.2.3"
    assert plan.command == [
        "uv",
        "pip",
        "install",
        "sfmapi-colmap-cli @ git+https://github.com/SFMAPI/sfmapi_colmap_cli.git@v1.2.3",
    ]
    assert not plan.warnings


def test_mutable_github_refs_warn() -> None:
    plan = build_install_plan(parse_github_source("SFMAPI/sfmapi_hloc"))

    assert plan.source.ref == "main"
    assert plan.warnings


def test_docker_install_plan_reports_missing_image() -> None:
    source = parse_github_source("SFMAPI/sfmapi_colmap_cli", package="sfmapi-colmap-cli")
    plan = build_docker_install_plan(
        "colmap_cli", get_manifest("colmap_cli").runtime_modes.docker, source=source
    )

    assert plan.method == "docker"
    assert plan.warnings


def test_provider_resolution_uses_profiles_and_rejects_ambiguity() -> None:
    record_manual_install("colmap_cli", method="external_tool")
    record_manual_install("pycolmap", method="uv")

    with pytest.raises(ProviderAmbiguityError):
        resolve_provider(stage="features", capability="features.extract.sift")

    assert (
        resolve_provider(
            stage="features",
            capability="features.extract.sift",
            requested_provider="colmap_pycolmap",
        )
        == "colmap_pycolmap"
    )

    upsert_profile(
        RoutingProfile(name="prefer-cli", routes={"features": ["colmap_cli"]}),
    )
    state = load_state()
    state.default_profile = "prefer-cli"
    save_state(state)

    assert resolve_provider(stage="features", capability="features.extract.sift") == "colmap_cli"


def test_disabled_provider_is_rejected_for_runtime_resolution() -> None:
    record_manual_install("hloc", method="entry_point", enabled=False)

    with pytest.raises(KeyError, match="disabled"):
        ensure_provider_enabled("hloc")

    ensure_provider_enabled("not_registered_in_hub")


def test_provider_resolution_uses_project_profile_before_default() -> None:
    record_manual_install("colmap_cli", method="external_tool")
    record_manual_install("pycolmap", method="uv")
    upsert_profile(RoutingProfile(name="default", routes={"features": ["colmap_cli"]}))
    upsert_profile(RoutingProfile(name="project", routes={"features": ["colmap_pycolmap"]}))
    state = load_state()
    state.default_profile = "default"
    save_state(state)
    set_project_profile("project-1", "project")

    assert (
        resolve_provider(
            stage="features",
            capability="features.extract.sift",
            project_id="project-1",
        )
        == "colmap_pycolmap"
    )


def test_stage_validation_applies_provider_resolution() -> None:
    record_manual_install("colmap_cli", method="external_tool")
    spec = {"type": "sift", "backend_options": {}}

    sfm_stage_service.validate_features_config(spec)

    assert spec["provider"] == "colmap_cli"


def test_stage_validation_reports_ambiguous_provider() -> None:
    record_manual_install("colmap_cli", method="external_tool")
    record_manual_install("pycolmap", method="uv")

    with pytest.raises(ValidationError, match="multiple candidate providers"):
        sfm_stage_service.validate_features_config({"type": "sift", "backend_options": {}})


def test_manifest_lookup_returns_expected_install_metadata() -> None:
    manifest = get_manifest("colmap_cli")

    assert manifest.runtime_modes.uv is not None
    assert manifest.runtime_modes.uv.package == "sfmapi-colmap-cli"
    assert "colmap_cli" in manifest.provider_ids()


def test_external_tool_manifests_use_runtime_env_vars() -> None:
    colmap_cli = get_manifest("colmap_cli")
    colmap_native = get_manifest("colmap_native")
    realityscan = get_manifest("realityscan_cli")
    spheresfm = get_manifest("spheresfm")

    assert colmap_cli.runtime_modes.external_tool is not None
    assert colmap_native.runtime_modes.external_tool is not None
    assert realityscan.runtime_modes.external_tool is not None
    assert spheresfm.runtime_modes.external_tool is not None
    assert "SFMAPI_COLMAP_EXECUTABLE" in colmap_cli.runtime_modes.external_tool.env_vars
    assert "SFMAPI_COLMAP_EXECUTABLE" in colmap_native.runtime_modes.external_tool.env_vars
    assert "SFMAPI_RC_EXECUTABLE" in realityscan.runtime_modes.external_tool.env_vars
    assert "SFMAPI_SPHERESFM_EXECUTABLE" in spheresfm.runtime_modes.external_tool.env_vars


def test_upstream_license_metadata_is_specific() -> None:
    upstream = {
        item.name: item.license
        for manifest in list_manifests(include_entry_points=False)
        for item in manifest.upstream_projects
    }

    assert upstream["COLMAP"] == "BSD-3-Clause"
    assert upstream["Hierarchical Localization"] == "Apache-2.0"
    assert upstream["InstantSfM"] == "CC-BY-NC-4.0"
    assert upstream["SphereSfM"] == "BSD-3-Clause"
    assert all(value != "Upstream license" for value in upstream.values())


def test_external_tool_detection_checks_env_and_version(monkeypatch: pytest.MonkeyPatch) -> None:
    manifest = get_manifest("colmap_cli").model_copy(deep=True)
    assert manifest.runtime_modes.external_tool is not None
    manifest.runtime_modes.external_tool.executable_names = []
    manifest.runtime_modes.external_tool.env_vars = ["TEST_TOOL_EXE"]
    manifest.runtime_modes.external_tool.version_args = ["--version"]
    monkeypatch.setenv("TEST_TOOL_EXE", sys.executable)

    tools = detect_external_tools([manifest])["colmap_cli"]

    assert tools[0].source == "env"
    assert tools[0].path == sys.executable
    assert tools[0].version


def test_entry_point_discovery_loads_plugin_manifest(monkeypatch: pytest.MonkeyPatch) -> None:
    manifest = get_manifest("hloc")

    class FakeEntryPoint:
        name = "hloc"
        value = "fake.module:plugin"
        dist = None

        def load(self) -> PluginManifest:
            return manifest

    class FakeEntryPoints(list[FakeEntryPoint]):
        def select(self, *, group: str) -> list[FakeEntryPoint]:
            assert group == "sfmapi.backends"
            return list(self)

    import sfm_hub.discovery as discovery

    monkeypatch.setattr(
        discovery.metadata, "entry_points", lambda: FakeEntryPoints([FakeEntryPoint()])
    )

    found = discover_plugins(load=True)

    assert found[0].plugin_id == "hloc"
    assert found[0].manifest == manifest


def test_entry_point_loader_registers_backend_factory(monkeypatch: pytest.MonkeyPatch) -> None:
    manifest_obj = get_manifest("hloc")

    class PluginObject:
        backend_name = "entry_backend"
        manifest = manifest_obj

        @staticmethod
        def backend_factory() -> object:
            return object()

    class FakeEntryPoint:
        name = "entry_backend"
        value = "fake.module:plugin"
        dist = None

        def load(self) -> PluginObject:
            return PluginObject()

    class FakeEntryPoints(list[FakeEntryPoint]):
        def select(self, *, group: str) -> list[FakeEntryPoint]:
            assert group == "sfmapi.backends"
            return list(self)

    import sfm_hub.discovery as discovery

    monkeypatch.setattr(
        discovery.metadata, "entry_points", lambda: FakeEntryPoints([FakeEntryPoint()])
    )
    registered: dict[str, object] = {}
    providers: dict[str, object] = {}

    def register_backend(name: str, factory: object) -> None:
        registered[name] = factory

    def register_provider(provider_id: str, factory: object) -> None:
        providers[provider_id] = factory

    loaded = load_backend_entry_points(  # type: ignore[arg-type]
        register_backend,
        register_provider=register_provider,
    )

    assert loaded[0].plugin_id == "hloc"
    assert "entry_backend" in registered
    assert providers["hloc"] is registered["entry_backend"]


def test_entry_point_loader_skips_disabled_plugin(monkeypatch: pytest.MonkeyPatch) -> None:
    manifest_obj = get_manifest("hloc")
    record_manual_install("hloc", method="uv")
    set_enabled("hloc", False)

    class PluginObject:
        backend_name = "hloc"
        manifest = manifest_obj

        @staticmethod
        def backend_factory() -> object:
            return object()

    class FakeEntryPoint:
        name = "hloc"
        value = "fake.module:plugin"
        dist = None

        def load(self) -> PluginObject:
            return PluginObject()

    class FakeEntryPoints(list[FakeEntryPoint]):
        def select(self, *, group: str) -> list[FakeEntryPoint]:
            assert group == "sfmapi.backends"
            return list(self)

    import sfm_hub.discovery as discovery

    monkeypatch.setattr(
        discovery.metadata, "entry_points", lambda: FakeEntryPoints([FakeEntryPoint()])
    )
    registered: dict[str, object] = {}
    providers: dict[str, object] = {}

    loaded = load_backend_entry_points(  # type: ignore[arg-type]
        registered.setdefault,
        register_provider=providers.setdefault,
    )

    assert loaded[0].plugin_id == "hloc"
    assert loaded[0].skipped is True
    assert loaded[0].load_error is None
    assert not registered
    assert not providers


def test_entry_point_loader_registrar_accepts_providers_kwarg(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Entry-point plugins can declare provider aliases through the
    ``registrar`` callback rather than only through the manifest."""
    manifest_obj = get_manifest("hloc")

    class PluginObject:
        manifest = manifest_obj

        @staticmethod
        def register(registrar) -> None:  # type: ignore[no-untyped-def]
            registrar(
                "explicit_backend",
                lambda: object(),
                providers=["explicit.provider"],
            )

    class FakeEntryPoint:
        name = "explicit_entry"
        value = "fake.module:plugin"
        dist = None

        def load(self) -> PluginObject:
            return PluginObject()

    class FakeEntryPoints(list[FakeEntryPoint]):
        def select(self, *, group: str) -> list[FakeEntryPoint]:
            return list(self)

    import sfm_hub.discovery as discovery

    monkeypatch.setattr(
        discovery.metadata, "entry_points", lambda: FakeEntryPoints([FakeEntryPoint()])
    )
    registered: dict[str, object] = {}
    providers: dict[str, object] = {}

    load_backend_entry_points(  # type: ignore[arg-type]
        registered.setdefault,
        register_provider=providers.setdefault,
    )

    # Callback-declared provider wins; manifest providers (hloc) for the same
    # single backend still register via the manifest fallback path.
    assert "explicit.provider" in providers
    assert providers["explicit.provider"] is registered["explicit_backend"]
    assert "hloc" in providers


def test_entry_point_loader_logs_unmatched_manifest_provider(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """When a plugin registers >1 backend and the manifest lists provider
    ids that don't match any registered backend name, sfm_hub warns
    instead of silently dropping the alias."""
    manifest_obj = get_manifest("hloc")

    class PluginObject:
        manifest = manifest_obj

        @staticmethod
        def register(registrar) -> None:  # type: ignore[no-untyped-def]
            registrar("alpha", lambda: object())
            registrar("beta", lambda: object())

    class FakeEntryPoint:
        name = "multi_entry"
        value = "fake.module:plugin"
        dist = None

        def load(self) -> PluginObject:
            return PluginObject()

    class FakeEntryPoints(list[FakeEntryPoint]):
        def select(self, *, group: str) -> list[FakeEntryPoint]:
            return list(self)

    import sfm_hub.discovery as discovery

    monkeypatch.setattr(
        discovery.metadata, "entry_points", lambda: FakeEntryPoints([FakeEntryPoint()])
    )
    registered: dict[str, object] = {}
    providers: dict[str, object] = {}

    with caplog.at_level("WARNING", logger="sfm_hub.discovery"):
        load_backend_entry_points(  # type: ignore[arg-type]
            registered.setdefault,
            register_provider=providers.setdefault,
        )

    assert {"alpha", "beta"} <= registered.keys()
    # Manifest provider id "hloc" matches neither "alpha" nor "beta" so it
    # must NOT be silently aliased to one of them, and a warning must fire.
    assert "hloc" not in providers
    assert any("unmatched_manifest_provider" in str(record.msg) for record in caplog.records)


def test_plugin_service_enable_records_entry_point_install(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """enable_plugin on a discovered-but-not-yet-installed entry-point
    plugin records a manual install instead of raising."""
    from app.services import plugin_service

    monkeypatch.setattr(
        "app.services.plugin_service.discovered_plugin_ids",
        lambda: {"hloc"},
    )

    detail = plugin_service.enable_plugin("hloc")

    state = load_state()
    assert "hloc" in state.installed
    assert state.installed["hloc"].method == "entry_point"
    assert state.installed["hloc"].enabled is True
    assert detail["enabled"] is True


def test_plugin_service_disable_records_entry_point_install(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Symmetric to enable: disable on a discovered-but-not-yet-installed
    entry-point plugin records the manual install (disabled)."""
    from app.services import plugin_service

    monkeypatch.setattr(
        "app.services.plugin_service.discovered_plugin_ids",
        lambda: {"hloc"},
    )

    plugin_service.disable_plugin("hloc")

    state = load_state()
    assert "hloc" in state.installed
    assert state.installed["hloc"].enabled is False
