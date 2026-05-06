from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.localization_request_sift_type_0 import LocalizationRequestSiftType0


T = TypeVar("T", bound="LocalizationRequest")


@_attrs_define
class LocalizationRequest:
    """Request body for ``POST /v1/reconstructions/{rid}/localize``.

    Attributes:
        blob_sha (str):
        sift (LocalizationRequestSiftType0 | None | Unset):
    """

    blob_sha: str
    sift: LocalizationRequestSiftType0 | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.localization_request_sift_type_0 import LocalizationRequestSiftType0

        blob_sha = self.blob_sha

        sift: dict[str, Any] | None | Unset
        if isinstance(self.sift, Unset):
            sift = UNSET
        elif isinstance(self.sift, LocalizationRequestSiftType0):
            sift = self.sift.to_dict()
        else:
            sift = self.sift

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "blob_sha": blob_sha,
            }
        )
        if sift is not UNSET:
            field_dict["sift"] = sift

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.localization_request_sift_type_0 import LocalizationRequestSiftType0

        d = dict(src_dict)
        blob_sha = d.pop("blob_sha")

        def _parse_sift(data: object) -> LocalizationRequestSiftType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                sift_type_0 = LocalizationRequestSiftType0.from_dict(data)

                return sift_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(LocalizationRequestSiftType0 | None | Unset, data)

        sift = _parse_sift(d.pop("sift", UNSET))

        localization_request = cls(
            blob_sha=blob_sha,
            sift=sift,
        )

        localization_request.additional_properties = d
        return localization_request

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
