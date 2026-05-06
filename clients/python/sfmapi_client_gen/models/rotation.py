from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="Rotation")


@_attrs_define
class Rotation:
    """Hamilton quaternion stored ``(w, x, y, z)``.

    Attributes:
        w (float):
        x (float):
        y (float):
        z (float):
    """

    w: float
    x: float
    y: float
    z: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        w = self.w

        x = self.x

        y = self.y

        z = self.z

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "w": w,
                "x": x,
                "y": y,
                "z": z,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        w = d.pop("w")

        x = d.pop("x")

        y = d.pop("y")

        z = d.pop("z")

        rotation = cls(
            w=w,
            x=x,
            y=y,
            z=z,
        )

        rotation.additional_properties = d
        return rotation

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
