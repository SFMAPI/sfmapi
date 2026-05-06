from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="LocalSourceSpec")


@_attrs_define
class LocalSourceSpec:
    """Image source pointing at a worker-local directory tree. Bytes
    are NEVER copied — workers stream from ``root`` in place. Locked
    by ``L3`` in ``docs/guides/decisions.md`` (50GB local dirs).

        Attributes:
            root (str):
            kind (Literal['local'] | Unset):  Default: 'local'.
            recursive (bool | Unset):  Default: True.
    """

    root: str
    kind: Literal["local"] | Unset = "local"
    recursive: bool | Unset = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        root = self.root

        kind = self.kind

        recursive = self.recursive

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "root": root,
            }
        )
        if kind is not UNSET:
            field_dict["kind"] = kind
        if recursive is not UNSET:
            field_dict["recursive"] = recursive

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        root = d.pop("root")

        kind = cast(Literal["local"] | Unset, d.pop("kind", UNSET))
        if kind != "local" and not isinstance(kind, Unset):
            raise ValueError(f"kind must match const 'local', got '{kind}'")

        recursive = d.pop("recursive", UNSET)

        local_source_spec = cls(
            root=root,
            kind=kind,
            recursive=recursive,
        )

        local_source_spec.additional_properties = d
        return local_source_spec

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
