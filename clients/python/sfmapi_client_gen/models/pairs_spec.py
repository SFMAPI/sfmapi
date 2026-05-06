from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.pairs_spec_retrieval_strategy import PairsSpecRetrievalStrategy
from ..models.pairs_spec_strategy import PairsSpecStrategy
from ..types import UNSET, Unset

T = TypeVar("T", bound="PairsSpec")


@_attrs_define
class PairsSpec:
    """Pair-selection strategy. Decoupled from the matcher so the
    standard supports "select pairs with hloc-style retrieval, then
    match with any local-feature matcher" workflows.

    Capability flag is ``pairs.{strategy}``.

        Attributes:
            version (Literal[1] | Unset):  Default: 1.
            strategy (PairsSpecStrategy | Unset):  Default: PairsSpecStrategy.EXHAUSTIVE.
            overlap (int | Unset):  Default: 10.
            vocab_tree_path (None | str | Unset):
            retrieval_strategy (PairsSpecRetrievalStrategy | Unset):  Default: PairsSpecRetrievalStrategy.VLAD.
            retrieval_k (int | Unset):  Default: 20.
            overlap_distance_m (float | None | Unset):
            max_angle_deg (float | None | Unset):
    """

    version: Literal[1] | Unset = 1
    strategy: PairsSpecStrategy | Unset = PairsSpecStrategy.EXHAUSTIVE
    overlap: int | Unset = 10
    vocab_tree_path: None | str | Unset = UNSET
    retrieval_strategy: PairsSpecRetrievalStrategy | Unset = PairsSpecRetrievalStrategy.VLAD
    retrieval_k: int | Unset = 20
    overlap_distance_m: float | None | Unset = UNSET
    max_angle_deg: float | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        version = self.version

        strategy: str | Unset = UNSET
        if not isinstance(self.strategy, Unset):
            strategy = self.strategy.value

        overlap = self.overlap

        vocab_tree_path: None | str | Unset
        if isinstance(self.vocab_tree_path, Unset):
            vocab_tree_path = UNSET
        else:
            vocab_tree_path = self.vocab_tree_path

        retrieval_strategy: str | Unset = UNSET
        if not isinstance(self.retrieval_strategy, Unset):
            retrieval_strategy = self.retrieval_strategy.value

        retrieval_k = self.retrieval_k

        overlap_distance_m: float | None | Unset
        if isinstance(self.overlap_distance_m, Unset):
            overlap_distance_m = UNSET
        else:
            overlap_distance_m = self.overlap_distance_m

        max_angle_deg: float | None | Unset
        if isinstance(self.max_angle_deg, Unset):
            max_angle_deg = UNSET
        else:
            max_angle_deg = self.max_angle_deg

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if version is not UNSET:
            field_dict["version"] = version
        if strategy is not UNSET:
            field_dict["strategy"] = strategy
        if overlap is not UNSET:
            field_dict["overlap"] = overlap
        if vocab_tree_path is not UNSET:
            field_dict["vocab_tree_path"] = vocab_tree_path
        if retrieval_strategy is not UNSET:
            field_dict["retrieval_strategy"] = retrieval_strategy
        if retrieval_k is not UNSET:
            field_dict["retrieval_k"] = retrieval_k
        if overlap_distance_m is not UNSET:
            field_dict["overlap_distance_m"] = overlap_distance_m
        if max_angle_deg is not UNSET:
            field_dict["max_angle_deg"] = max_angle_deg

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        version = cast(Literal[1] | Unset, d.pop("version", UNSET))
        if version != 1 and not isinstance(version, Unset):
            raise ValueError(f"version must match const 1, got '{version}'")

        _strategy = d.pop("strategy", UNSET)
        strategy: PairsSpecStrategy | Unset
        if isinstance(_strategy, Unset):
            strategy = UNSET
        else:
            strategy = PairsSpecStrategy(_strategy)

        overlap = d.pop("overlap", UNSET)

        def _parse_vocab_tree_path(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        vocab_tree_path = _parse_vocab_tree_path(d.pop("vocab_tree_path", UNSET))

        _retrieval_strategy = d.pop("retrieval_strategy", UNSET)
        retrieval_strategy: PairsSpecRetrievalStrategy | Unset
        if isinstance(_retrieval_strategy, Unset):
            retrieval_strategy = UNSET
        else:
            retrieval_strategy = PairsSpecRetrievalStrategy(_retrieval_strategy)

        retrieval_k = d.pop("retrieval_k", UNSET)

        def _parse_overlap_distance_m(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        overlap_distance_m = _parse_overlap_distance_m(d.pop("overlap_distance_m", UNSET))

        def _parse_max_angle_deg(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        max_angle_deg = _parse_max_angle_deg(d.pop("max_angle_deg", UNSET))

        pairs_spec = cls(
            version=version,
            strategy=strategy,
            overlap=overlap,
            vocab_tree_path=vocab_tree_path,
            retrieval_strategy=retrieval_strategy,
            retrieval_k=retrieval_k,
            overlap_distance_m=overlap_distance_m,
            max_angle_deg=max_angle_deg,
        )

        pairs_spec.additional_properties = d
        return pairs_spec

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
