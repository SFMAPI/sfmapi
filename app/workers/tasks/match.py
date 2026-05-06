"""Matching task — pair selection (PairsSpec) + per-pair matcher
(MatcherSpec).

The ``spec`` half of the task state carries ``{pairs: {...},
matcher: {...}}`` (the AIP-202 split shape). ``pairs.strategy``
selects which image pairs to consider; ``matcher.type`` selects the
per-pair algorithm."""

from __future__ import annotations

import contextlib
from pathlib import Path

from app.adapters.registry import get_backend
from app.db.models import Task
from app.storage.correspondence_emit import export_correspondence_graph
from app.workers._task_io import read_state


def run(task: Task) -> dict:
    inputs, spec = read_state(task)
    db_path = Path(inputs["database_path"])
    pairs = spec.get("pairs") or {}
    matcher = spec.get("matcher") or {}
    strategy = pairs.get("strategy", "exhaustive")
    backend = get_backend()
    summary = backend.match(
        database_path=db_path,
        mode=strategy,
        options={**pairs, **matcher},
    )

    out: dict = {"database_path": str(db_path), "strategy": strategy, **summary}
    # Best-effort: dump the raw correspondence graph so the
    # reconstruction-level read endpoint has fresh data. Failure here
    # doesn't fail match — geometric verification is what matters.
    with contextlib.suppress(Exception):
        written = export_correspondence_graph(
            backend.iter_correspondences(database_path=db_path), db_path.parent
        )
        out["correspondence_graph_path"] = str(written)
    return out
