from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.features_spec import FeaturesSpec


T = TypeVar("T", bound="FeaturesRequest")


@_attrs_define
class FeaturesRequest:
    """
    Attributes:
        spec (FeaturesSpec | Unset): Type-tagged feature extractor request.

            Backends report which ``type`` values they support via the
            ``features.extract.{type}`` capability flags. Unsupported types
            return 501 with the canonical capability name.

            Backwards compat: the legacy ``sift_max_num_features`` /
            ``sift_first_octave`` fields are accepted as aliases when
            ``type=="sift"``.
    """

    spec: FeaturesSpec | Unset = UNSET

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
        from ..models.features_spec import FeaturesSpec

        d = dict(src_dict)
        _spec = d.pop("spec", UNSET)
        spec: FeaturesSpec | Unset
        if isinstance(_spec, Unset):
            spec = UNSET
        else:
            spec = FeaturesSpec.from_dict(_spec)

        features_request = cls(
            spec=spec,
        )

        return features_request
