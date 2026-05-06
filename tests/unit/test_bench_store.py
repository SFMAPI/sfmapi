"""Bench harness store + lint logic — unit-tested without a server."""

from __future__ import annotations

from pathlib import Path

import pytest

from bench import store

pytestmark = pytest.mark.unit


def _result(
    dataset: str,
    recipe: str,
    *,
    sha: str = "abc",
    finished_at: str = "2026-05-02T00:00:00Z",
    metrics: dict[str, float] | None = None,
) -> store.BenchResult:
    return store.BenchResult(
        dataset=dataset,
        recipe=recipe,
        git_sha=sha,
        runtime_version_id="x:y:z:120",
        started_at=finished_at,
        finished_at=finished_at,
        wall_seconds=metrics.get("wall_seconds", 1.0) if metrics else 1.0,
        status="succeeded",
        metrics=metrics or {},
    )


def test_append_and_iter_roundtrip(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(store, "RESULTS_DIR", tmp_path)
    a = _result("fountain", "incremental", metrics={"num_reg_images": 11.0, "wall_seconds": 12.3})
    b = _result("fountain", "incremental", metrics={"num_reg_images": 11.0, "wall_seconds": 13.0})
    store.append(a)
    store.append(b)
    rows = list(store.iter_history())
    assert len(rows) == 2
    assert rows[0].dataset == "fountain"
    assert rows[1].metrics["wall_seconds"] == 13.0


def test_lint_flags_drop_in_num_reg_images(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(store, "RESULTS_DIR", tmp_path)
    # 5 historical "good" runs at 100 registered images each
    for i in range(5):
        store.append(
            _result(
                "fountain",
                "incremental",
                sha=f"sha{i:02d}",
                finished_at=f"2026-05-0{i + 1}T00:00:00Z",
                metrics={
                    "num_reg_images": 100.0,
                    "num_points3D": 50000.0,
                    "mean_reproj_err": 1.0,
                    "wall_seconds": 60.0,
                },
            )
        )
    # New run drops to 80 -> -20% > 5% tolerance for max-direction metric.
    bad = _result(
        "fountain",
        "incremental",
        sha="newsha",
        finished_at="2026-05-10T00:00:00Z",
        metrics={
            "num_reg_images": 80.0,
            "num_points3D": 50000.0,
            "mean_reproj_err": 1.0,
            "wall_seconds": 60.0,
        },
    )
    store.append(bad)
    regs = store.lint([bad])
    assert any(r.metric == "num_reg_images" for r in regs), [r.as_text() for r in regs]


def test_lint_flags_increase_in_reproj_err(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(store, "RESULTS_DIR", tmp_path)
    for i in range(5):
        store.append(
            _result(
                "fountain",
                "incremental",
                sha=f"sha{i:02d}",
                metrics={"num_reg_images": 100.0, "mean_reproj_err": 1.0, "wall_seconds": 60.0},
            )
        )
    bad = _result(
        "fountain",
        "incremental",
        sha="newsha",
        metrics={"num_reg_images": 100.0, "mean_reproj_err": 1.5, "wall_seconds": 60.0},
    )
    store.append(bad)
    regs = store.lint([bad])
    assert any(r.metric == "mean_reproj_err" for r in regs)


def test_lint_silent_with_no_regression(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(store, "RESULTS_DIR", tmp_path)
    for i in range(5):
        store.append(
            _result(
                "fountain",
                "incremental",
                sha=f"sha{i:02d}",
                metrics={"num_reg_images": 100.0, "mean_reproj_err": 1.0, "wall_seconds": 60.0},
            )
        )
    same = _result(
        "fountain",
        "incremental",
        sha="newsha",
        metrics={"num_reg_images": 101.0, "mean_reproj_err": 1.0, "wall_seconds": 61.0},
    )
    store.append(same)
    regs = store.lint([same])
    assert regs == []


def test_lint_skips_when_history_too_short(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(store, "RESULTS_DIR", tmp_path)
    for i in range(2):
        store.append(
            _result("fountain", "incremental", sha=f"sha{i:02d}", metrics={"num_reg_images": 100.0})
        )
    bad = _result("fountain", "incremental", sha="newsha", metrics={"num_reg_images": 1.0})
    regs = store.lint([bad])
    assert regs == []  # < 3 prior samples -> no opinion
