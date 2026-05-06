from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="BackendInfoOut")


@_attrs_define
class BackendInfoOut:
    """
    Attributes:
        name (str):
        version (str):
        vendor (str | Unset):  Default: ''.
    """

    name: str
    version: str
    vendor: str | Unset = ""

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        version = self.version

        vendor = self.vendor

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "name": name,
                "version": version,
            }
        )
        if vendor is not UNSET:
            field_dict["vendor"] = vendor

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        version = d.pop("version")

        vendor = d.pop("vendor", UNSET)

        backend_info_out = cls(
            name=name,
            version=version,
            vendor=vendor,
        )

        return backend_info_out
