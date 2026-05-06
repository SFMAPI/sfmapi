from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="SimilarityNeighborOut")


@_attrs_define
class SimilarityNeighborOut:
    """
    Attributes:
        image_id (str):
        distance (int):
    """

    image_id: str
    distance: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        image_id = self.image_id

        distance = self.distance

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "image_id": image_id,
                "distance": distance,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        image_id = d.pop("image_id")

        distance = d.pop("distance")

        similarity_neighbor_out = cls(
            image_id=image_id,
            distance=distance,
        )

        similarity_neighbor_out.additional_properties = d
        return similarity_neighbor_out

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
