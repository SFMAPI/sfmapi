"""Scheduler — submit job DAG and enqueue tasks for execution.

Persists Job + Task rows and hands each non-cached task off to the
configured queue (see ``app.orchestrator.queue.get_queue``). Whether
the queue is ARQ-backed or in-process is a runtime decision driven by
``settings.queue_backend`` / ``settings.inline_tasks``.
"""

from __future__ import annotations

import contextlib

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.ids import new_id
from app.db.models import Task
from app.orchestrator.dag import TaskNode
from app.orchestrator.queue import InlineQueue, get_queue
from app.services import job_service, runtime_version_service


async def submit_job_dag(
    session: AsyncSession,
    *,
    tenant_id: str,
    project_id: str,
    recipe: str,
    spec: dict | None,
    nodes: list[TaskNode],
    inline: bool = False,
) -> tuple[str, list[Task]]:
    """Persist Job + Task rows and return them. ``inline=True`` forces
    the InlineQueue regardless of settings (used by tests). ARQ enqueue
    failures (e.g. Redis absent in dev) are suppressed — the tasks
    remain ``pending`` and will be picked up on the next worker boot."""
    rv = await runtime_version_service.ensure_runtime_version(session)
    job = await job_service.create_job(
        session,
        tenant_id=tenant_id,
        project_id=project_id,
        recipe=recipe,
        spec=spec,
    )
    for n in nodes:
        if not n.task_id:
            n.task_id = new_id()
    tasks = await job_service.materialize_dag(
        session,
        tenant_id=tenant_id,
        job_id=job.job_id,
        runtime_version_id=rv.rv_id,
        nodes=nodes,
    )
    await session.commit()

    pending = [t for t in tasks if t.status != "succeeded"]
    if not pending:
        return job.job_id, tasks

    queue = InlineQueue(get_settings()) if inline else get_queue()
    try:
        for t in pending:
            # Inline mode surfaces task errors directly; ARQ enqueue
            # failures are tolerated (Redis may be absent in dev).
            if isinstance(queue, InlineQueue):
                await queue.enqueue(t.task_id)
            else:
                with contextlib.suppress(Exception):
                    await queue.enqueue(t.task_id)
    finally:
        await queue.close()
    return job.job_id, tasks
