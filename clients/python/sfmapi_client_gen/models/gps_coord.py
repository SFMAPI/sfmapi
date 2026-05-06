from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GpsCoord")


@_attrs_define
class GpsCoord:
    """WGS84 geographic coordinate (lat/lng in degrees, alt in meters).

    Attributes:
        lat (float):
        lng (float):
        alt (float | None | Unset):
        horiz_accuracy_m (float | None | Unset):
        vert_accuracy_m (float | None | Unset):
    """

    lat: float
    lng: float
    alt: float | None | Unset = UNSET
    horiz_accuracy_m: float | None | Unset = UNSET
    vert_accuracy_m: float | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        lat = self.lat

        lng = self.lng

        alt: float | None | Unset
        if isinstance(self.alt, Unset):
            alt = UNSET
        else:
            alt = self.alt

        horiz_accuracy_m: float | None | Unset
        if isinstance(self.horiz_accuracy_m, Unset):
            horiz_accuracy_m = UNSET
        else:
            horiz_accuracy_m = self.horiz_accuracy_m

        vert_accuracy_m: float | None | Unset
        if isinstance(self.vert_accuracy_m, Unset):
            vert_accuracy_m = UNSET
        else:
            vert_accuracy_m = self.vert_accuracy_m

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "lat": lat,
                "lng": lng,
            }
        )
        if alt is not UNSET:
            field_dict["alt"] = alt
        if horiz_accuracy_m is not UNSET:
            field_dict["horiz_accuracy_m"] = horiz_accuracy_m
        if vert_accuracy_m is not UNSET:
            field_dict["vert_accuracy_m"] = vert_accuracy_m

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        lat = d.pop("lat")

        lng = d.pop("lng")

        def _parse_alt(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        alt = _parse_alt(d.pop("alt", UNSET))

        def _parse_horiz_accuracy_m(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        horiz_accuracy_m = _parse_horiz_accuracy_m(d.pop("horiz_accuracy_m", UNSET))

        def _parse_vert_accuracy_m(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        vert_accuracy_m = _parse_vert_accuracy_m(d.pop("vert_accuracy_m", UNSET))

        gps_coord = cls(
            lat=lat,
            lng=lng,
            alt=alt,
            horiz_accuracy_m=horiz_accuracy_m,
            vert_accuracy_m=vert_accuracy_m,
        )

        gps_coord.additional_properties = d
        return gps_coord

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
