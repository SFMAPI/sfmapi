from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UploadInit")


@_attrs_define
class UploadInit:
    """
    Attributes:
        expected_size (int):
        content_type (None | str | Unset):
        expected_sha (None | str | Unset):
    """

    expected_size: int
    content_type: None | str | Unset = UNSET
    expected_sha: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        expected_size = self.expected_size

        content_type: None | str | Unset
        if isinstance(self.content_type, Unset):
            content_type = UNSET
        else:
            content_type = self.content_type

        expected_sha: None | str | Unset
        if isinstance(self.expected_sha, Unset):
            expected_sha = UNSET
        else:
            expected_sha = self.expected_sha

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "expected_size": expected_size,
            }
        )
        if content_type is not UNSET:
            field_dict["content_type"] = content_type
        if expected_sha is not UNSET:
            field_dict["expected_sha"] = expected_sha

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        expected_size = d.pop("expected_size")

        def _parse_content_type(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        content_type = _parse_content_type(d.pop("content_type", UNSET))

        def _parse_expected_sha(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        expected_sha = _parse_expected_sha(d.pop("expected_sha", UNSET))

        upload_init = cls(
            expected_size=expected_size,
            content_type=content_type,
            expected_sha=expected_sha,
        )

        upload_init.additional_properties = d
        return upload_init

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
