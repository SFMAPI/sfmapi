from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.image_observation_row import ImageObservationRow


T = TypeVar("T", bound="ImageObservationsResponse")


@_attrs_define
class ImageObservationsResponse:
    """``GET .../images/{image_id}/observations`` envelope.

    Attributes:
        image_id (str):
        observations (list[ImageObservationRow] | Unset):
        count (int | Unset):  Default: 0.
    """

    image_id: str
    observations: list[ImageObservationRow] | Unset = UNSET
    count: int | Unset = 0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        image_id = self.image_id

        observations: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.observations, Unset):
            observations = []
            for observations_item_data in self.observations:
                observations_item = observations_item_data.to_dict()
                observations.append(observations_item)

        count = self.count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "image_id": image_id,
            }
        )
        if observations is not UNSET:
            field_dict["observations"] = observations
        if count is not UNSET:
            field_dict["count"] = count

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.image_observation_row import ImageObservationRow

        d = dict(src_dict)
        image_id = d.pop("image_id")

        _observations = d.pop("observations", UNSET)
        observations: list[ImageObservationRow] | Unset = UNSET
        if _observations is not UNSET:
            observations = []
            for observations_item_data in _observations:
                observations_item = ImageObservationRow.from_dict(observations_item_data)

                observations.append(observations_item)

        count = d.pop("count", UNSET)

        image_observations_response = cls(
            image_id=image_id,
            observations=observations,
            count=count,
        )

        image_observations_response.additional_properties = d
        return image_observations_response

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
