from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.backend_info_out import BackendInfoOut
    from ..models.capabilities_out_features import CapabilitiesOutFeatures


T = TypeVar("T", bound="CapabilitiesOut")


@_attrs_define
class CapabilitiesOut:
    """Snapshot of what the current deployment supports.

    ``schema_version`` tracks the wire envelope shape — independent
    of the feature flags themselves, which are negotiated via the
    ``features`` dict.

        Attributes:
            backend (BackendInfoOut):
            schema_version (int | Unset):  Default: 1.
            features (CapabilitiesOutFeatures | Unset):
    """

    backend: BackendInfoOut
    schema_version: int | Unset = 1
    features: CapabilitiesOutFeatures | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        backend = self.backend.to_dict()

        schema_version = self.schema_version

        features: dict[str, Any] | Unset = UNSET
        if not isinstance(self.features, Unset):
            features = self.features.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "backend": backend,
            }
        )
        if schema_version is not UNSET:
            field_dict["schema_version"] = schema_version
        if features is not UNSET:
            field_dict["features"] = features

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.backend_info_out import BackendInfoOut
        from ..models.capabilities_out_features import CapabilitiesOutFeatures

        d = dict(src_dict)
        backend = BackendInfoOut.from_dict(d.pop("backend"))

        schema_version = d.pop("schema_version", UNSET)

        _features = d.pop("features", UNSET)
        features: CapabilitiesOutFeatures | Unset
        if isinstance(_features, Unset):
            features = UNSET
        else:
            features = CapabilitiesOutFeatures.from_dict(_features)

        capabilities_out = cls(
            backend=backend,
            schema_version=schema_version,
            features=features,
        )

        return capabilities_out
