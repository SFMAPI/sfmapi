from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="SimilarityBuildResponse")


@_attrs_define
class SimilarityBuildResponse:
    """``POST /v1/datasets/{id}/similarity:build`` synchronous build
    response (dhash). Async vlad path returns :class:`JobAcceptedResponse`.

        Attributes:
            strategy (str):
            manifest_hash (str):
            count (int):
    """

    strategy: str
    manifest_hash: str
    count: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        strategy = self.strategy

        manifest_hash = self.manifest_hash

        count = self.count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "strategy": strategy,
                "manifest_hash": manifest_hash,
                "count": count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        strategy = d.pop("strategy")

        manifest_hash = d.pop("manifest_hash")

        count = d.pop("count")

        similarity_build_response = cls(
            strategy=strategy,
            manifest_hash=manifest_hash,
            count=count,
        )

        similarity_build_response.additional_properties = d
        return similarity_build_response

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
