"""Cooperative job cancellation at task pickup.

``POST /v1/jobs/{id}:cancel`` flips ``Job.cancel_requested`` /
``cancel_force``; the dispatcher honors them when it picks up a task.
Before this wiring those flags were set but never read — a cancelled
job ran to completion. These tests pin the short-circuit path.
"""

from __future__ import annotations

import pytest

from app.core.ids import new_id
from app.db.models import Job, Project, RuntimeVersion, Task

pytestmark = pytest.mark.integration


async def _seed_cancelled_job(session, *, force: bool) -> tuple[str, str]:
    """Persist a Project + a cancel-requested Job + one pending Task.

    Returns ``(job_id, task_id)``.
    """
    rv = RuntimeVersion(rv_id=new_id(), runtime_version_id="test-rv", seed="0")
    session.add(rv)
    project = Project(tenant_id="default", name="cancelp")
    session.add(project)
    await session.flush()
    job = Job(
        tenant_id="default",
        project_id=project.project_id,
        recipe="x",
        cancel_requested=True,
        cancel_force=force,
    )
    session.add(job)
    await session.flush()
    task = Task(
        task_id=new_id(),
        tenant_id="default",
        job_id=job.job_id,
        kind="noop",
        inputs_hash="x",
        params_hash="x",
        runtime_version_id=rv.rv_id,
        cache_key=new_id(),
        gpu_required=False,
    )
    session.add(task)
    await session.commit()
    return job.job_id, task.task_id


async def test_cancel_requested_short_circuits_task_to_cancelled(session) -> None:
    from app.workers.dispatcher import execute_task

    job_id, task_id = await _seed_cancelled_job(session, force=False)

    result = await execute_task(task_id)
    assert result == {"status": "cancelled"}

    refreshed_task = await session.get(Task, task_id)
    await session.refresh(refreshed_task)
    assert refreshed_task.status == "cancelled"
    assert refreshed_task.finished_at is not None

    refreshed_job = await session.get(Job, job_id)
    await session.refresh(refreshed_job)
    assert refreshed_job.status == "cancelled"
    assert refreshed_job.finished_at is not None


async def test_cancel_force_marks_task_cancelled_dirty(session) -> None:
    from app.workers.dispatcher import execute_task

    job_id, task_id = await _seed_cancelled_job(session, force=True)

    result = await execute_task(task_id)
    assert result == {"status": "cancelled"}

    refreshed_task = await session.get(Task, task_id)
    await session.refresh(refreshed_task)
    assert refreshed_task.status == "cancelled_dirty"

    refreshed_job = await session.get(Job, job_id)
    await session.refresh(refreshed_job)
    # _maybe_finalize_job rolls cancelled_dirty up to the cancelled job state.
    assert refreshed_job.status == "cancelled"


async def test_uncancelled_job_runs_the_task_normally(session) -> None:
    """Guard the negative: a job with no cancel flag is not short-circuited
    — the noop handler runs and the task reaches ``succeeded``."""
    from app.workers.dispatcher import execute_task

    rv = RuntimeVersion(rv_id=new_id(), runtime_version_id="test-rv", seed="0")
    session.add(rv)
    project = Project(tenant_id="default", name="okp")
    session.add(project)
    await session.flush()
    job = Job(tenant_id="default", project_id=project.project_id, recipe="x")
    session.add(job)
    await session.flush()
    task = Task(
        task_id=new_id(),
        tenant_id="default",
        job_id=job.job_id,
        kind="noop",
        inputs_hash="x",
        params_hash="x",
        runtime_version_id=rv.rv_id,
        cache_key=new_id(),
        gpu_required=False,
    )
    session.add(task)
    await session.commit()

    result = await execute_task(task.task_id)
    assert result["status"] == "succeeded"

    refreshed_task = await session.get(Task, task.task_id)
    await session.refresh(refreshed_task)
    assert refreshed_task.status == "succeeded"
