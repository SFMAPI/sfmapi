from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="S3SourceSpec")


@_attrs_define
class S3SourceSpec:
    """Image source backed by an S3 prefix. Bytes are lazy-downloaded
    to the worker's LRU cache on first read; remote-only by default.

        Attributes:
            bucket (str):
            prefix (str):
            kind (Literal['s3'] | Unset):  Default: 's3'.
    """

    bucket: str
    prefix: str
    kind: Literal["s3"] | Unset = "s3"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        bucket = self.bucket

        prefix = self.prefix

        kind = self.kind

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "bucket": bucket,
                "prefix": prefix,
            }
        )
        if kind is not UNSET:
            field_dict["kind"] = kind

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        bucket = d.pop("bucket")

        prefix = d.pop("prefix")

        kind = cast(Literal["s3"] | Unset, d.pop("kind", UNSET))
        if kind != "s3" and not isinstance(kind, Unset):
            raise ValueError(f"kind must match const 's3', got '{kind}'")

        s3_source_spec = cls(
            bucket=bucket,
            prefix=prefix,
            kind=kind,
        )

        s3_source_spec.additional_properties = d
        return s3_source_spec

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
