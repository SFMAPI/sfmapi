"""Fair-share scheduler.

Picks the next ready Task across all tenants, biased toward tenants
with fewer recent admissions. The interleaving rule:

  Pick the tenant with the *smallest* count of currently-running tasks;
  break ties by the tenant whose last-admitted task is oldest. Within a
  tenant, pick by Task.created_at (FIFO).

A simpler invariant we expose for testing:
  `max_consecutive_jobs_per_tenant`: never admit more than N consecutive
  Tasks from the same tenant when other tenants have ready work.

This is intentionally a *picker* — it does not enqueue. The supervisor
calls `pick_next_task(...)` between subprocess slots; in tests we use
the picker directly to validate fairness.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Task


@dataclass
class FairShareState:
    max_consecutive_per_tenant: int = 2
    recent_tenants: deque[str] = field(default_factory=deque)

    def admit(self, tenant_id: str) -> None:
        self.recent_tenants.append(tenant_id)
        # Keep window bounded — only need the last N for the invariant.
        while len(self.recent_tenants) > 64:
            self.recent_tenants.popleft()

    def consecutive_for(self, tenant_id: str) -> int:
        c = 0
        for t in reversed(self.recent_tenants):
            if t == tenant_id:
                c += 1
            else:
                break
        return c


async def pick_next_task(session: AsyncSession, *, state: FairShareState) -> Task | None:
    """Find the highest-priority ready Task that doesn't violate
    `max_consecutive_per_tenant`. Ready = pending + deps satisfied.

    For Phase 5 v1 we treat 'ready' as `pending` with no remaining deps;
    dep satisfaction is a precondition the orchestrator already enforces
    when emitting tasks. Tenants are weighted by current running count.
    """
    rows = (
        (
            await session.execute(
                select(Task).where(Task.status == "pending").order_by(Task.created_at)
            )
        )
        .scalars()
        .all()
    )
    if not rows:
        return None

    # Group by tenant; compute current running count per tenant.
    running = (
        await session.execute(select(Task.tenant_id, Task.task_id).where(Task.status == "running"))
    ).all()
    running_by_tenant: dict[str, int] = {}
    for tid, _ in running:
        running_by_tenant[tid] = running_by_tenant.get(tid, 0) + 1

    distinct_pending_tenants = {r.tenant_id for r in rows}
    blocked_by_consecutive: set[str] = set()
    if len(distinct_pending_tenants) > 1:
        for tid in distinct_pending_tenants:
            if state.consecutive_for(tid) >= state.max_consecutive_per_tenant:
                blocked_by_consecutive.add(tid)

    # Among non-blocked tenants, pick the one with the smallest running count.
    best: Task | None = None
    best_running = float("inf")
    for r in rows:
        if r.tenant_id in blocked_by_consecutive:
            continue
        rc = running_by_tenant.get(r.tenant_id, 0)
        if rc < best_running:
            best = r
            best_running = rc

    # If everyone was blocked by the consecutive rule, fall back to any.
    if best is None:
        best = rows[0]
    state.admit(best.tenant_id)
    return best
