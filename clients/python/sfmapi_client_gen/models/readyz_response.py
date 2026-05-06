from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.readyz_response_checks import ReadyzResponseChecks


T = TypeVar("T", bound="ReadyzResponse")


@_attrs_define
class ReadyzResponse:
    """Readiness check envelope. ``status`` is ``"ok"`` when every
    backing store reports healthy; ``"degraded"`` when one or more
    are unreachable. ``checks`` carries a per-component status string.

        Attributes:
            status (str):
            checks (ReadyzResponseChecks | Unset):
    """

    status: str
    checks: ReadyzResponseChecks | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status = self.status

        checks: dict[str, Any] | Unset = UNSET
        if not isinstance(self.checks, Unset):
            checks = self.checks.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "status": status,
            }
        )
        if checks is not UNSET:
            field_dict["checks"] = checks

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.readyz_response_checks import ReadyzResponseChecks

        d = dict(src_dict)
        status = d.pop("status")

        _checks = d.pop("checks", UNSET)
        checks: ReadyzResponseChecks | Unset
        if isinstance(_checks, Unset):
            checks = UNSET
        else:
            checks = ReadyzResponseChecks.from_dict(_checks)

        readyz_response = cls(
            status=status,
            checks=checks,
        )

        readyz_response.additional_properties = d
        return readyz_response

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
