from __future__ import annotations

import pytest

from app.orchestrator.dag import JobDag, TaskNode

pytestmark = pytest.mark.unit


def test_topo_order_resolves_deps() -> None:
    a = TaskNode(task_id="a", kind="extract", inputs_hash="i", params_hash="p")
    b = TaskNode(task_id="b", kind="match", inputs_hash="i", params_hash="p", depends_on=["a"])
    c = TaskNode(task_id="c", kind="verify", inputs_hash="i", params_hash="p", depends_on=["b"])
    dag = JobDag(nodes=[c, a, b])
    order = [n.task_id for n in dag.topo_order()]
    assert order == ["a", "b", "c"]


def test_cycle_detected() -> None:
    a = TaskNode(task_id="a", kind="x", inputs_hash="i", params_hash="p", depends_on=["b"])
    b = TaskNode(task_id="b", kind="x", inputs_hash="i", params_hash="p", depends_on=["a"])
    dag = JobDag(nodes=[a, b])
    with pytest.raises(ValueError, match="Cycle"):
        dag.topo_order()


def test_cache_key_stable() -> None:
    n1 = TaskNode(task_id="x", kind="extract", inputs_hash="abc", params_hash="def")
    n2 = TaskNode(task_id="y", kind="extract", inputs_hash="abc", params_hash="def")
    assert n1.cache_key("rv1") == n2.cache_key("rv1")
    assert n1.cache_key("rv1") != n1.cache_key("rv2")
