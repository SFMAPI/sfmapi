from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.pose_priors_bulk_response_pose_priors import PosePriorsBulkResponsePosePriors


T = TypeVar("T", bound="PosePriorsBulkResponse")


@_attrs_define
class PosePriorsBulkResponse:
    """Per-image PosePrior map for ``GET /v1/datasets/{id}/pose_priors``.

    Attributes:
        pose_priors (PosePriorsBulkResponsePosePriors | Unset):
    """

    pose_priors: PosePriorsBulkResponsePosePriors | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        pose_priors: dict[str, Any] | Unset = UNSET
        if not isinstance(self.pose_priors, Unset):
            pose_priors = self.pose_priors.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if pose_priors is not UNSET:
            field_dict["pose_priors"] = pose_priors

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.pose_priors_bulk_response_pose_priors import PosePriorsBulkResponsePosePriors

        d = dict(src_dict)
        _pose_priors = d.pop("pose_priors", UNSET)
        pose_priors: PosePriorsBulkResponsePosePriors | Unset
        if isinstance(_pose_priors, Unset):
            pose_priors = UNSET
        else:
            pose_priors = PosePriorsBulkResponsePosePriors.from_dict(_pose_priors)

        pose_priors_bulk_response = cls(
            pose_priors=pose_priors,
        )

        pose_priors_bulk_response.additional_properties = d
        return pose_priors_bulk_response

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
