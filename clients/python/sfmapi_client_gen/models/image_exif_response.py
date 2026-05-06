from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.image_exif_response_exif import ImageExifResponseExif


T = TypeVar("T", bound="ImageExifResponse")


@_attrs_define
class ImageExifResponse:
    """EXIF metadata as a free-form dict. Empty when the source has
    no EXIF or when the bytes can't be located on the worker.

        Attributes:
            exif (ImageExifResponseExif | Unset):
    """

    exif: ImageExifResponseExif | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        exif: dict[str, Any] | Unset = UNSET
        if not isinstance(self.exif, Unset):
            exif = self.exif.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if exif is not UNSET:
            field_dict["exif"] = exif

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.image_exif_response_exif import ImageExifResponseExif

        d = dict(src_dict)
        _exif = d.pop("exif", UNSET)
        exif: ImageExifResponseExif | Unset
        if isinstance(_exif, Unset):
            exif = UNSET
        else:
            exif = ImageExifResponseExif.from_dict(_exif)

        image_exif_response = cls(
            exif=exif,
        )

        image_exif_response.additional_properties = d
        return image_exif_response

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
