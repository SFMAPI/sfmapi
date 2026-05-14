"""Portable dataset-scoped stage route contracts.

The stub backend advertises no capabilities, so each stage service
builder's ``require_capability`` gate fires before any DB lookup and
the route returns 501 with the canonical capability name.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.e2e

_FAKE_DATASET = "01HGHOST00000000000000000A"


async def test_build_vocab_tree_returns_501_without_capability(client) -> None:
    resp = await client.post(f"/v1/datasets/{_FAKE_DATASET}:buildVocabTree", json={})
    assert resp.status_code == 501
    assert resp.json()["capability"] == "index.vocab_tree"


async def test_configure_rig_returns_501_without_capability(client) -> None:
    resp = await client.post(f"/v1/datasets/{_FAKE_DATASET}:configureRig", json={})
    assert resp.status_code == 501
    assert resp.json()["capability"] == "rigs.configure"


async def test_estimate_two_view_returns_501_without_capability(client) -> None:
    resp = await client.post(f"/v1/datasets/{_FAKE_DATASET}:estimateTwoView", json={})
    assert resp.status_code == 501
    assert resp.json()["capability"] == "geometry.two_view"


async def test_dataset_stage_rejects_unknown_field(client) -> None:
    resp = await client.post(f"/v1/datasets/{_FAKE_DATASET}:buildVocabTree", json={"bogus": 1})
    assert resp.status_code == 422


async def test_dataset_stage_rejects_bad_provider(client) -> None:
    resp = await client.post(
        f"/v1/datasets/{_FAKE_DATASET}:estimateTwoView", json={"provider": "bad provider!"}
    )
    assert resp.status_code == 422
