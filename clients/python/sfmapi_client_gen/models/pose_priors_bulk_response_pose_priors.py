from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.pose_prior import PosePrior


T = TypeVar("T", bound="PosePriorsBulkResponsePosePriors")


@_attrs_define
class PosePriorsBulkResponsePosePriors:
    """ """

    additional_properties: dict[str, None | PosePrior] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.pose_prior import PosePrior

        field_dict: dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            if isinstance(prop, PosePrior):
                field_dict[prop_name] = prop.to_dict()
            else:
                field_dict[prop_name] = prop

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.pose_prior import PosePrior

        d = dict(src_dict)
        pose_priors_bulk_response_pose_priors = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():

            def _parse_additional_property(data: object) -> None | PosePrior:
                if data is None:
                    return data
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    additional_property_type_0 = PosePrior.from_dict(data)

                    return additional_property_type_0
                except (TypeError, ValueError, AttributeError, KeyError):
                    pass
                return cast(None | PosePrior, data)

            additional_property = _parse_additional_property(prop_dict)

            additional_properties[prop_name] = additional_property

        pose_priors_bulk_response_pose_priors.additional_properties = additional_properties
        return pose_priors_bulk_response_pose_priors

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> None | PosePrior:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: None | PosePrior) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
