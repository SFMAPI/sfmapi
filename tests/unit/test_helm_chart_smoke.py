"""Helm chart structural sanity (no helm binary required).

We just YAML-parse the templates as raw text and check they reference
the helpers we expect. The full lint + template render runs in
`.github/workflows/helm.yml` against a real `helm` binary.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.unit

CHART = Path(__file__).resolve().parents[2] / "deploy" / "helm" / "sfmapi"


def test_chart_yaml_is_valid() -> None:
    body = yaml.safe_load((CHART / "Chart.yaml").read_text(encoding="utf-8"))
    assert body["apiVersion"] == "v2"
    assert body["name"] == "sfmapi"
    assert body["type"] == "application"
    deps = {d["name"] for d in body.get("dependencies", [])}
    assert {"postgresql", "redis"}.issubset(deps)


def test_values_yaml_has_expected_top_keys() -> None:
    values = yaml.safe_load((CHART / "values.yaml").read_text(encoding="utf-8"))
    for key in ("image", "web", "worker", "workspace", "postgresql", "redis", "env"):
        assert key in values, f"values.yaml missing top-level `{key}`"
    assert values["worker"]["enabled"] is False
    assert values["postgresql"]["enabled"] is True
    assert values["redis"]["enabled"] is True


def test_all_template_files_present() -> None:
    expected = {
        "_helpers.tpl",
        "serviceaccount.yaml",
        "pvc.yaml",
        "web-deployment.yaml",
        "web-service.yaml",
        "web-hpa.yaml",
        "web-ingress.yaml",
        "worker-daemonset.yaml",
        "NOTES.txt",
    }
    have = {p.name for p in (CHART / "templates").iterdir()}
    assert expected.issubset(have), expected - have


def test_helpers_define_expected_macros() -> None:
    text = (CHART / "templates" / "_helpers.tpl").read_text(encoding="utf-8")
    for macro in (
        "sfmapi.fullname",
        "sfmapi.labels",
        "sfmapi.selectorLabels",
        "sfmapi.dbUrl",
        "sfmapi.redisUrl",
        "sfmapi.image",
        "sfmapi.workerImage",
        "sfmapi.commonEnv",
    ):
        assert f'define "{macro}"' in text, f"missing helper macro: {macro}"


def test_worker_template_blocks_when_image_missing() -> None:
    text = (CHART / "templates" / "worker-daemonset.yaml").read_text(encoding="utf-8")
    # The fail() guard is the operator-friendly safety net documented in
    # values.yaml; if the template renders without it, an unset
    # worker.image.repository would silently install a broken pod.
    assert "{{- fail" in text
    assert "worker.image.repository" in text
