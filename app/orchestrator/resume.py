"""Resume a previously failed/cancelled Job.

The resume contract:
  - Tasks in `(failed, cancelled, cancelled_dirty)` are reset to
    `pending`. Their `cache_key` is preserved so the same upstream
    cache hits replay.
  - Tasks in `succeeded` are kept as-is (free cache).
  - The Job itself transitions back to `pending`, cancel flags
    cleared.
  - If `inline=True` (or `SFMAPI_INLINE_TASKS=true`), reset tasks are
    re-run synchronously here. Otherwise they're re-enqueued via ARQ.
  - For mapping tasks specifically, the worker reads
    `jobs/{job_id}/checkpoints/` (see `app.storage.mapping_input`) to
    resume from the latest `MappingInput.save` write, avoiding a
    full restart.
"""

from __future__ import annotations

import contextlib

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.errors import NotFoundError
from app.db.models import Job, Task


async def resume_job(
    session: AsyncSession, *, tenant_id: str, job_id: str, inline: bool | None = None
) -> Job:
    j = (
        await session.execute(select(Job).where(Job.tenant_id == tenant_id, Job.job_id == job_id))
    ).scalar_one_or_none()
    if j is None:
        raise NotFoundError(f"Job {job_id} not found")
    # Reset only failed/cancelled tasks; keep succeeded ones to leverage cache.
    tasks = (await session.execute(select(Task).where(Task.job_id == job_id))).scalars().all()
    for t in tasks:
        if t.status in ("failed", "cancelled", "cancelled_dirty"):
            t.status = "pending"
            t.error_class = None
            t.error_message = None
            t.lease_expires_at = None
            t.worker_id = None
    j.cancel_requested = False
    j.cancel_force = False
    j.status = "pending"
    j.error_class = None
    j.error_message = None
    await session.flush()

    settings = get_settings()
    use_inline = settings.inline_tasks if inline is None else inline
    reset_ids = [t.task_id for t in tasks if t.status == "pending"]
    if reset_ids:
        from app.orchestrator.queue import InlineQueue, get_queue

        queue = InlineQueue(settings) if use_inline else get_queue(settings)
        if use_inline:
            # Commit + close so SQLite writer lock is free for the
            # worker's session inside `run_task`.
            await session.commit()
            await session.close()
        try:
            for tid in reset_ids:
                if use_inline:
                    await queue.enqueue(tid)
                else:
                    with contextlib.suppress(Exception):
                        await queue.enqueue(tid)
        finally:
            await queue.close()
    return j
