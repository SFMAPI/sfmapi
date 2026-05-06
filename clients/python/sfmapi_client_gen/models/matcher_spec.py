from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.matcher_spec_type import MatcherSpecType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.matcher_spec_matcher_options import MatcherSpecMatcherOptions


T = TypeVar("T", bound="MatcherSpec")


@_attrs_define
class MatcherSpec:
    """Per-pair feature matcher.

    ``nn-mutual`` is the COLMAP default (mutual nearest-neighbor).
    ``nn-ratio`` adds Lowe's ratio test. ``superglue`` / ``lightglue``
    are learned matchers. ``loftr`` is semi-dense (no separate
    extractor — set ``FeaturesSpec.type`` to a placeholder).

        Attributes:
            version (Literal[1] | Unset):  Default: 1.
            type_ (MatcherSpecType | Unset):  Default: MatcherSpecType.NN_MUTUAL.
            use_gpu (bool | Unset):  Default: True.
            cross_check (bool | Unset):  Default: True.
            max_ratio (float | Unset):  Default: 0.8.
            max_distance (float | Unset):  Default: 0.7.
            matcher_options (MatcherSpecMatcherOptions | Unset):
    """

    version: Literal[1] | Unset = 1
    type_: MatcherSpecType | Unset = MatcherSpecType.NN_MUTUAL
    use_gpu: bool | Unset = True
    cross_check: bool | Unset = True
    max_ratio: float | Unset = 0.8
    max_distance: float | Unset = 0.7
    matcher_options: MatcherSpecMatcherOptions | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        version = self.version

        type_: str | Unset = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        use_gpu = self.use_gpu

        cross_check = self.cross_check

        max_ratio = self.max_ratio

        max_distance = self.max_distance

        matcher_options: dict[str, Any] | Unset = UNSET
        if not isinstance(self.matcher_options, Unset):
            matcher_options = self.matcher_options.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if version is not UNSET:
            field_dict["version"] = version
        if type_ is not UNSET:
            field_dict["type"] = type_
        if use_gpu is not UNSET:
            field_dict["use_gpu"] = use_gpu
        if cross_check is not UNSET:
            field_dict["cross_check"] = cross_check
        if max_ratio is not UNSET:
            field_dict["max_ratio"] = max_ratio
        if max_distance is not UNSET:
            field_dict["max_distance"] = max_distance
        if matcher_options is not UNSET:
            field_dict["matcher_options"] = matcher_options

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.matcher_spec_matcher_options import MatcherSpecMatcherOptions

        d = dict(src_dict)
        version = cast(Literal[1] | Unset, d.pop("version", UNSET))
        if version != 1 and not isinstance(version, Unset):
            raise ValueError(f"version must match const 1, got '{version}'")

        _type_ = d.pop("type", UNSET)
        type_: MatcherSpecType | Unset
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = MatcherSpecType(_type_)

        use_gpu = d.pop("use_gpu", UNSET)

        cross_check = d.pop("cross_check", UNSET)

        max_ratio = d.pop("max_ratio", UNSET)

        max_distance = d.pop("max_distance", UNSET)

        _matcher_options = d.pop("matcher_options", UNSET)
        matcher_options: MatcherSpecMatcherOptions | Unset
        if isinstance(_matcher_options, Unset):
            matcher_options = UNSET
        else:
            matcher_options = MatcherSpecMatcherOptions.from_dict(_matcher_options)

        matcher_spec = cls(
            version=version,
            type_=type_,
            use_gpu=use_gpu,
            cross_check=cross_check,
            max_ratio=max_ratio,
            max_distance=max_distance,
            matcher_options=matcher_options,
        )

        matcher_spec.additional_properties = d
        return matcher_spec

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
