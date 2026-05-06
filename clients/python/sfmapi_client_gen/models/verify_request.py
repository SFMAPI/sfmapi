from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.verify_spec import VerifySpec


T = TypeVar("T", bound="VerifyRequest")


@_attrs_define
class VerifyRequest:
    """
    Attributes:
        spec (VerifySpec | Unset):
    """

    spec: VerifySpec | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        spec: dict[str, Any] | Unset = UNSET
        if not isinstance(self.spec, Unset):
            spec = self.spec.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if spec is not UNSET:
            field_dict["spec"] = spec

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.verify_spec import VerifySpec

        d = dict(src_dict)
        _spec = d.pop("spec", UNSET)
        spec: VerifySpec | Unset
        if isinstance(_spec, Unset):
            spec = UNSET
        else:
            spec = VerifySpec.from_dict(_spec)

        verify_request = cls(
            spec=spec,
        )

        return verify_request
