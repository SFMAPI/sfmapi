"""Auto-registration for worker task handlers.

Each task module under ``app.workers.tasks`` decorates its ``run``
function with ``@task_handler("kind")``; the dispatcher walks the
package and reads :func:`get_registered` instead of maintaining a
hand-curated dispatch dict. Adding a new task is now: (1) create
``app/workers/tasks/<kind>.py`` with a decorated ``run`` function,
(2) update the (single) capability + spec entry. No dispatcher
edit, no chance of an "imported the module but forgot the dict
entry" drift mode.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])

_HANDLERS: dict[str, Callable[..., Any]] = {}


def task_handler(kind: str) -> Callable[[F], F]:
    """Register the decorated function as the worker handler for
    ``kind``. Re-registration is an error to catch typos."""

    def deco(fn: F) -> F:
        if kind in _HANDLERS:
            raise RuntimeError(
                f"task handler for {kind!r} already registered "
                f"(by {_HANDLERS[kind].__module__}); "
                f"now {fn.__module__}"
            )
        _HANDLERS[kind] = fn
        return fn

    return deco


def get_registered() -> dict[str, Callable[..., Any]]:
    """Return a copy of the registered handler map."""
    return dict(_HANDLERS)


def clear_for_tests() -> None:
    """Reset the registry — used by the test suite when verifying
    auto-discovery semantics."""
    _HANDLERS.clear()


__all__ = ["clear_for_tests", "get_registered", "task_handler"]
