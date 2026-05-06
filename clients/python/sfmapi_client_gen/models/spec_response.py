from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.spec_server_info import SpecServerInfo


T = TypeVar("T", bound="SpecResponse")


@_attrs_define
class SpecResponse:
    """Discovery envelope for ``GET /spec``. Identifies which standard
    this server implements so clients can pick a compatible SDK.

    ``spec_url`` defaults to the canonical GitHub Pages doc site;
    deployments may override via ``SFMAPI_SPEC_URL`` to point at a
    private mirror, or set it ``None`` to omit the field entirely.

        Attributes:
            spec (str):
            spec_version (str):
            openapi_url (str):
            server (SpecServerInfo):
            spec_url (None | str | Unset):  Default: 'https://sfmapi.github.io/spec'.
    """

    spec: str
    spec_version: str
    openapi_url: str
    server: SpecServerInfo
    spec_url: None | str | Unset = "https://sfmapi.github.io/spec"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        spec = self.spec

        spec_version = self.spec_version

        openapi_url = self.openapi_url

        server = self.server.to_dict()

        spec_url: None | str | Unset
        if isinstance(self.spec_url, Unset):
            spec_url = UNSET
        else:
            spec_url = self.spec_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "spec": spec,
                "spec_version": spec_version,
                "openapi_url": openapi_url,
                "server": server,
            }
        )
        if spec_url is not UNSET:
            field_dict["spec_url"] = spec_url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.spec_server_info import SpecServerInfo

        d = dict(src_dict)
        spec = d.pop("spec")

        spec_version = d.pop("spec_version")

        openapi_url = d.pop("openapi_url")

        server = SpecServerInfo.from_dict(d.pop("server"))

        def _parse_spec_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        spec_url = _parse_spec_url(d.pop("spec_url", UNSET))

        spec_response = cls(
            spec=spec,
            spec_version=spec_version,
            openapi_url=openapi_url,
            server=server,
            spec_url=spec_url,
        )

        spec_response.additional_properties = d
        return spec_response

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
