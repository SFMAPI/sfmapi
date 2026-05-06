from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.mesh_request_options import MeshRequestOptions


T = TypeVar("T", bound="MeshRequest")


@_attrs_define
class MeshRequest:
    """Request body for ``POST /v1/reconstructions/{rid}/mesh``.

    Attributes:
        method (str | Unset):  Default: 'poisson'.
        options (MeshRequestOptions | Unset):
    """

    method: str | Unset = "poisson"
    options: MeshRequestOptions | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        method = self.method

        options: dict[str, Any] | Unset = UNSET
        if not isinstance(self.options, Unset):
            options = self.options.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if method is not UNSET:
            field_dict["method"] = method
        if options is not UNSET:
            field_dict["options"] = options

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.mesh_request_options import MeshRequestOptions

        d = dict(src_dict)
        method = d.pop("method", UNSET)

        _options = d.pop("options", UNSET)
        options: MeshRequestOptions | Unset
        if isinstance(_options, Unset):
            options = UNSET
        else:
            options = MeshRequestOptions.from_dict(_options)

        mesh_request = cls(
            method=method,
            options=options,
        )

        mesh_request.additional_properties = d
        return mesh_request

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
