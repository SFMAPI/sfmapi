from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="IssueKeyResponse")


@_attrs_define
class IssueKeyResponse:
    """
    Attributes:
        raw_key (str):
        api_key_id (str):
        tenant_id (str):
        name (None | str):
    """

    raw_key: str
    api_key_id: str
    tenant_id: str
    name: None | str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        raw_key = self.raw_key

        api_key_id = self.api_key_id

        tenant_id = self.tenant_id

        name: None | str
        name = self.name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "raw_key": raw_key,
                "api_key_id": api_key_id,
                "tenant_id": tenant_id,
                "name": name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        raw_key = d.pop("raw_key")

        api_key_id = d.pop("api_key_id")

        tenant_id = d.pop("tenant_id")

        def _parse_name(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        name = _parse_name(d.pop("name"))

        issue_key_response = cls(
            raw_key=raw_key,
            api_key_id=api_key_id,
            tenant_id=tenant_id,
            name=name,
        )

        issue_key_response.additional_properties = d
        return issue_key_response

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
