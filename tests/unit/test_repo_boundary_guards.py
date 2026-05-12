from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_workflows_do_not_reference_removed_in_repo_clients() -> None:
    stale = (
        "clients" + "/python",
        "clients" + "/typescript",
        "clients" + "/cpp",
        "clients" + "/",
    )
    failures: list[str] = []
    for path in (ROOT / ".github" / "workflows").glob("*.yml"):
        text = _read_text(path)
        for marker in stale:
            if marker in text:
                failures.append(f"{path.relative_to(ROOT)} contains {marker!r}")

    assert not failures, "\n".join(failures)


def test_public_docs_use_public_runtime_entrypoint() -> None:
    stale = "app.main" + ":app"
    checked = [ROOT / "README.md", *Path(ROOT / "docs").rglob("*.md")]
    failures = [
        str(path.relative_to(ROOT))
        for path in checked
        if path.is_file() and stale in _read_text(path)
    ]

    assert not failures, "\n".join(failures)
