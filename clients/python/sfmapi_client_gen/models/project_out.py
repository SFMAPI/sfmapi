from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.project_out_links_type_0 import ProjectOutLinksType0


T = TypeVar("T", bound="ProjectOut")


@_attrs_define
class ProjectOut:
    """
    Attributes:
        created_at (datetime.datetime):
        project_id (str):
        tenant_id (str):
        name (str):
        description (None | str | Unset):
        updated_at (datetime.datetime | None | Unset):
        field_links (None | ProjectOutLinksType0 | Unset):
    """

    created_at: datetime.datetime
    project_id: str
    tenant_id: str
    name: str
    description: None | str | Unset = UNSET
    updated_at: datetime.datetime | None | Unset = UNSET
    field_links: None | ProjectOutLinksType0 | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.project_out_links_type_0 import ProjectOutLinksType0

        created_at = self.created_at.isoformat()

        project_id = self.project_id

        tenant_id = self.tenant_id

        name = self.name

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        updated_at: None | str | Unset
        if isinstance(self.updated_at, Unset):
            updated_at = UNSET
        elif isinstance(self.updated_at, datetime.datetime):
            updated_at = self.updated_at.isoformat()
        else:
            updated_at = self.updated_at

        field_links: dict[str, Any] | None | Unset
        if isinstance(self.field_links, Unset):
            field_links = UNSET
        elif isinstance(self.field_links, ProjectOutLinksType0):
            field_links = self.field_links.to_dict()
        else:
            field_links = self.field_links

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "created_at": created_at,
                "project_id": project_id,
                "tenant_id": tenant_id,
                "name": name,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at
        if field_links is not UNSET:
            field_dict["_links"] = field_links

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.project_out_links_type_0 import ProjectOutLinksType0

        d = dict(src_dict)
        created_at = isoparse(d.pop("created_at"))

        project_id = d.pop("project_id")

        tenant_id = d.pop("tenant_id")

        name = d.pop("name")

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_updated_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                updated_at_type_0 = isoparse(data)

                return updated_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        updated_at = _parse_updated_at(d.pop("updated_at", UNSET))

        def _parse_field_links(data: object) -> None | ProjectOutLinksType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                field_links_type_0 = ProjectOutLinksType0.from_dict(data)

                return field_links_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ProjectOutLinksType0 | Unset, data)

        field_links = _parse_field_links(d.pop("_links", UNSET))

        project_out = cls(
            created_at=created_at,
            project_id=project_id,
            tenant_id=tenant_id,
            name=name,
            description=description,
            updated_at=updated_at,
            field_links=field_links,
        )

        project_out.additional_properties = d
        return project_out

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
