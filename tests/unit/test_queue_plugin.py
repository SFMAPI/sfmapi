"""Queue Protocol + factory + InlineQueue + ArqQueue surface tests."""

from __future__ import annotations

import asyncio
from typing import Any

import pytest

from app.core.config import Settings
from app.orchestrator.queue import (
    ArqQueue,
    InlineQueue,
    Queue,
    get_queue,
)

pytestmark = pytest.mark.unit


def _settings(**overrides: Any) -> Settings:
    # Explicit defaults — global conftest sets SFMAPI_INLINE_TASKS=true
    # so we have to opt out per test.
    overrides.setdefault("inline_tasks", False)
    overrides.setdefault("queue_backend", "arq")
    return Settings(**overrides)


def test_factory_returns_arq_by_default() -> None:
    q = get_queue(_settings())
    assert isinstance(q, ArqQueue)
    assert q.backend == "arq"
    assert isinstance(q, Queue)


def test_factory_returns_inline_when_inline_tasks_true() -> None:
    q = get_queue(_settings(inline_tasks=True))
    assert isinstance(q, InlineQueue)
    assert q.backend == "inline"


def test_factory_returns_inline_when_queue_backend_inline() -> None:
    q = get_queue(_settings(queue_backend="inline"))
    assert isinstance(q, InlineQueue)


def test_factory_rejects_unknown_backend() -> None:
    s = _settings()
    s.queue_backend = "kafka"  # type: ignore[assignment]
    with pytest.raises(ValueError, match="unknown queue_backend"):
        get_queue(s)


def test_inline_queue_invokes_run_task(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[str] = []

    async def fake_run_task(_ctx: dict, task_id: str) -> dict:
        seen.append(task_id)
        return {"status": "fake"}

    import app.workers.runner as runner_mod

    monkeypatch.setattr(runner_mod, "run_task", fake_run_task)
    q = InlineQueue(_settings())
    asyncio.run(q.enqueue("t_test_1"))
    asyncio.run(q.enqueue("t_test_2"))
    asyncio.run(q.close())
    assert seen == ["t_test_1", "t_test_2"]


def test_inline_queue_health_is_always_true() -> None:
    q = InlineQueue(_settings())
    assert asyncio.run(q.health()) is True


def test_arq_queue_health_returns_false_when_redis_unreachable() -> None:
    # Point at a port nothing is listening on; ping must fail without raising.
    s = _settings(redis_url="redis://127.0.0.1:1/0")
    q = ArqQueue(s)
    assert asyncio.run(q.health()) is False
    asyncio.run(q.close())


def test_close_is_idempotent() -> None:
    q = InlineQueue(_settings())
    asyncio.run(q.close())
    asyncio.run(q.close())  # second close must not raise
