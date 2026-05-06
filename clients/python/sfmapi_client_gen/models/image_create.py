from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.image_create_exif_type_0 import ImageCreateExifType0


T = TypeVar("T", bound="ImageCreate")


@_attrs_define
class ImageCreate:
    """
    Attributes:
        name (str):
        blob_sha (None | str | Unset):
        rel_path (None | str | Unset):
        width (int | None | Unset):
        height (int | None | Unset):
        exif (ImageCreateExifType0 | None | Unset):
    """

    name: str
    blob_sha: None | str | Unset = UNSET
    rel_path: None | str | Unset = UNSET
    width: int | None | Unset = UNSET
    height: int | None | Unset = UNSET
    exif: ImageCreateExifType0 | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.image_create_exif_type_0 import ImageCreateExifType0

        name = self.name

        blob_sha: None | str | Unset
        if isinstance(self.blob_sha, Unset):
            blob_sha = UNSET
        else:
            blob_sha = self.blob_sha

        rel_path: None | str | Unset
        if isinstance(self.rel_path, Unset):
            rel_path = UNSET
        else:
            rel_path = self.rel_path

        width: int | None | Unset
        if isinstance(self.width, Unset):
            width = UNSET
        else:
            width = self.width

        height: int | None | Unset
        if isinstance(self.height, Unset):
            height = UNSET
        else:
            height = self.height

        exif: dict[str, Any] | None | Unset
        if isinstance(self.exif, Unset):
            exif = UNSET
        elif isinstance(self.exif, ImageCreateExifType0):
            exif = self.exif.to_dict()
        else:
            exif = self.exif

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if blob_sha is not UNSET:
            field_dict["blob_sha"] = blob_sha
        if rel_path is not UNSET:
            field_dict["rel_path"] = rel_path
        if width is not UNSET:
            field_dict["width"] = width
        if height is not UNSET:
            field_dict["height"] = height
        if exif is not UNSET:
            field_dict["exif"] = exif

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.image_create_exif_type_0 import ImageCreateExifType0

        d = dict(src_dict)
        name = d.pop("name")

        def _parse_blob_sha(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        blob_sha = _parse_blob_sha(d.pop("blob_sha", UNSET))

        def _parse_rel_path(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        rel_path = _parse_rel_path(d.pop("rel_path", UNSET))

        def _parse_width(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        width = _parse_width(d.pop("width", UNSET))

        def _parse_height(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        height = _parse_height(d.pop("height", UNSET))

        def _parse_exif(data: object) -> ImageCreateExifType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                exif_type_0 = ImageCreateExifType0.from_dict(data)

                return exif_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ImageCreateExifType0 | None | Unset, data)

        exif = _parse_exif(d.pop("exif", UNSET))

        image_create = cls(
            name=name,
            blob_sha=blob_sha,
            rel_path=rel_path,
            width=width,
            height=height,
            exif=exif,
        )

        image_create.additional_properties = d
        return image_create

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
