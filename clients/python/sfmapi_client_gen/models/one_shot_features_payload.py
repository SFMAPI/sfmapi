from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="OneShotFeaturesPayload")


@_attrs_define
class OneShotFeaturesPayload:
    """The features themselves. ``keypoints`` is row-major
    ``[[x, y, scale, angle], ...]``; ``descriptors_b64`` is
    base64-encoded float32 descriptors of shape
    ``(count, descriptor_dim)`` in row-major order. ``descriptor_dim``
    is implied by the extractor (128 for SIFT).

        Attributes:
            type_ (str):
            count (int):
            descriptor_dim (int):
            keypoints (list[list[float]] | Unset):
            descriptors_b64 (str | Unset):  Default: ''.
    """

    type_: str
    count: int
    descriptor_dim: int
    keypoints: list[list[float]] | Unset = UNSET
    descriptors_b64: str | Unset = ""
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        count = self.count

        descriptor_dim = self.descriptor_dim

        keypoints: list[list[float]] | Unset = UNSET
        if not isinstance(self.keypoints, Unset):
            keypoints = []
            for keypoints_item_data in self.keypoints:
                keypoints_item = keypoints_item_data

                keypoints.append(keypoints_item)

        descriptors_b64 = self.descriptors_b64

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "count": count,
                "descriptor_dim": descriptor_dim,
            }
        )
        if keypoints is not UNSET:
            field_dict["keypoints"] = keypoints
        if descriptors_b64 is not UNSET:
            field_dict["descriptors_b64"] = descriptors_b64

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = d.pop("type")

        count = d.pop("count")

        descriptor_dim = d.pop("descriptor_dim")

        _keypoints = d.pop("keypoints", UNSET)
        keypoints: list[list[float]] | Unset = UNSET
        if _keypoints is not UNSET:
            keypoints = []
            for keypoints_item_data in _keypoints:
                keypoints_item = cast(list[float], keypoints_item_data)

                keypoints.append(keypoints_item)

        descriptors_b64 = d.pop("descriptors_b64", UNSET)

        one_shot_features_payload = cls(
            type_=type_,
            count=count,
            descriptor_dim=descriptor_dim,
            keypoints=keypoints,
            descriptors_b64=descriptors_b64,
        )

        one_shot_features_payload.additional_properties = d
        return one_shot_features_payload

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
