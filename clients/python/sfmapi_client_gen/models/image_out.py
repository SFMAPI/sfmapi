from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.image_out_links_type_0 import ImageOutLinksType0


T = TypeVar("T", bound="ImageOut")


@_attrs_define
class ImageOut:
    """
    Attributes:
        created_at (datetime.datetime):
        image_id (str):
        dataset_id (str):
        name (str):
        content_sha (str):
        source_kind (str):
        rel_path (None | str | Unset):
        byte_size (int | None | Unset):
        width (int | None | Unset):
        height (int | None | Unset):
        field_links (ImageOutLinksType0 | None | Unset):
    """

    created_at: datetime.datetime
    image_id: str
    dataset_id: str
    name: str
    content_sha: str
    source_kind: str
    rel_path: None | str | Unset = UNSET
    byte_size: int | None | Unset = UNSET
    width: int | None | Unset = UNSET
    height: int | None | Unset = UNSET
    field_links: ImageOutLinksType0 | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.image_out_links_type_0 import ImageOutLinksType0

        created_at = self.created_at.isoformat()

        image_id = self.image_id

        dataset_id = self.dataset_id

        name = self.name

        content_sha = self.content_sha

        source_kind = self.source_kind

        rel_path: None | str | Unset
        if isinstance(self.rel_path, Unset):
            rel_path = UNSET
        else:
            rel_path = self.rel_path

        byte_size: int | None | Unset
        if isinstance(self.byte_size, Unset):
            byte_size = UNSET
        else:
            byte_size = self.byte_size

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

        field_links: dict[str, Any] | None | Unset
        if isinstance(self.field_links, Unset):
            field_links = UNSET
        elif isinstance(self.field_links, ImageOutLinksType0):
            field_links = self.field_links.to_dict()
        else:
            field_links = self.field_links

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "created_at": created_at,
                "image_id": image_id,
                "dataset_id": dataset_id,
                "name": name,
                "content_sha": content_sha,
                "source_kind": source_kind,
            }
        )
        if rel_path is not UNSET:
            field_dict["rel_path"] = rel_path
        if byte_size is not UNSET:
            field_dict["byte_size"] = byte_size
        if width is not UNSET:
            field_dict["width"] = width
        if height is not UNSET:
            field_dict["height"] = height
        if field_links is not UNSET:
            field_dict["_links"] = field_links

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.image_out_links_type_0 import ImageOutLinksType0

        d = dict(src_dict)
        created_at = isoparse(d.pop("created_at"))

        image_id = d.pop("image_id")

        dataset_id = d.pop("dataset_id")

        name = d.pop("name")

        content_sha = d.pop("content_sha")

        source_kind = d.pop("source_kind")

        def _parse_rel_path(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        rel_path = _parse_rel_path(d.pop("rel_path", UNSET))

        def _parse_byte_size(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        byte_size = _parse_byte_size(d.pop("byte_size", UNSET))

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

        def _parse_field_links(data: object) -> ImageOutLinksType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                field_links_type_0 = ImageOutLinksType0.from_dict(data)

                return field_links_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ImageOutLinksType0 | None | Unset, data)

        field_links = _parse_field_links(d.pop("_links", UNSET))

        image_out = cls(
            created_at=created_at,
            image_id=image_id,
            dataset_id=dataset_id,
            name=name,
            content_sha=content_sha,
            source_kind=source_kind,
            rel_path=rel_path,
            byte_size=byte_size,
            width=width,
            height=height,
            field_links=field_links,
        )

        image_out.additional_properties = d
        return image_out

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
