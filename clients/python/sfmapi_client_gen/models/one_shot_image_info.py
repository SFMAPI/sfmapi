from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="OneShotImageInfo")


@_attrs_define
class OneShotImageInfo:
    """Decoded image dimensions + size echoed back so consumers can
    sanity-check what the server actually parsed.

        Attributes:
            width (int):
            height (int):
            byte_size (int):
    """

    width: int
    height: int
    byte_size: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        width = self.width

        height = self.height

        byte_size = self.byte_size

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "width": width,
                "height": height,
                "byte_size": byte_size,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        width = d.pop("width")

        height = d.pop("height")

        byte_size = d.pop("byte_size")

        one_shot_image_info = cls(
            width=width,
            height=height,
            byte_size=byte_size,
        )

        one_shot_image_info.additional_properties = d
        return one_shot_image_info

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
