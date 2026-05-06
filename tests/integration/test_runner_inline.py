"""Inline runner test — submits a no-op task DAG and runs it synchronously."""

from __future__ import annotations

import pytest

from app.core.ids import new_id
from app.db.models import Project, Task
from app.orchestrator.dag import TaskNode
from app.orchestrator.scheduler import submit_job_dag

pytestmark = pytest.mark.integration


async def test_noop_task_runs_and_succeeds(session) -> None:
    p = Project(tenant_id="default", name="t-runner")
    session.add(p)
    await session.flush()

    node = TaskNode(
        task_id=new_id(),
        kind="noop",
        inputs_hash="i",
        params_hash="p",
        depends_on=[],
        gpu_required=False,
    )
    _job_id, tasks = await submit_job_dag(
        session,
        tenant_id="default",
        project_id=p.project_id,
        recipe="noop",
        spec={},
        nodes=[node],
        inline=True,
    )
    await session.commit()
    t = await session.get(Task, tasks[0].task_id)
    await session.refresh(t)
    assert t.status == "succeeded"
    assert t.outputs_ref_json["ok"] is True


async def test_cache_short_circuit(session) -> None:
    p = Project(tenant_id="default", name="t-cache")
    session.add(p)
    await session.flush()

    def make_node() -> TaskNode:
        return TaskNode(
            task_id=new_id(),
            kind="noop",
            inputs_hash="ih",
            params_hash="ph",
            depends_on=[],
            gpu_required=False,
        )

    _, tasks_a = await submit_job_dag(
        session,
        tenant_id="default",
        project_id=p.project_id,
        recipe="noop",
        spec={},
        nodes=[make_node()],
        inline=True,
    )
    a_id = tasks_a[0].task_id
    a = await session.get(Task, a_id)
    await session.refresh(a)
    assert a.status == "succeeded"

    _, tasks_b = await submit_job_dag(
        session,
        tenant_id="default",
        project_id=p.project_id,
        recipe="noop",
        spec={},
        nodes=[make_node()],
        inline=True,
    )
    b_id = tasks_b[0].task_id
    b = await session.get(Task, b_id)
    await session.refresh(b)
    # Same cache_key -> second task starts as 'succeeded' (cached).
    assert b.status == "succeeded"
    assert b.outputs_ref_json == a.outputs_ref_json
    assert b.cache_key == a.cache_key
