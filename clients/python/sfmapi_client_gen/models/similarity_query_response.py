from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.similarity_neighbor_out import SimilarityNeighborOut


T = TypeVar("T", bound="SimilarityQueryResponse")


@_attrs_define
class SimilarityQueryResponse:
    """``GET /v1/datasets/{id}/similarity?image_id=...`` envelope.

    Attributes:
        query_image_id (str):
        strategy (str):
        k (int):
        neighbors (list[SimilarityNeighborOut] | Unset):
    """

    query_image_id: str
    strategy: str
    k: int
    neighbors: list[SimilarityNeighborOut] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        query_image_id = self.query_image_id

        strategy = self.strategy

        k = self.k

        neighbors: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.neighbors, Unset):
            neighbors = []
            for neighbors_item_data in self.neighbors:
                neighbors_item = neighbors_item_data.to_dict()
                neighbors.append(neighbors_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "query_image_id": query_image_id,
                "strategy": strategy,
                "k": k,
            }
        )
        if neighbors is not UNSET:
            field_dict["neighbors"] = neighbors

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.similarity_neighbor_out import SimilarityNeighborOut

        d = dict(src_dict)
        query_image_id = d.pop("query_image_id")

        strategy = d.pop("strategy")

        k = d.pop("k")

        _neighbors = d.pop("neighbors", UNSET)
        neighbors: list[SimilarityNeighborOut] | Unset = UNSET
        if _neighbors is not UNSET:
            neighbors = []
            for neighbors_item_data in _neighbors:
                neighbors_item = SimilarityNeighborOut.from_dict(neighbors_item_data)

                neighbors.append(neighbors_item)

        similarity_query_response = cls(
            query_image_id=query_image_id,
            strategy=strategy,
            k=k,
            neighbors=neighbors,
        )

        similarity_query_response.additional_properties = d
        return similarity_query_response

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
