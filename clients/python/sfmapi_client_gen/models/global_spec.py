from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.global_spec_backend import GlobalSpecBackend
from ..models.global_spec_formulation import GlobalSpecFormulation
from ..types import UNSET, Unset

T = TypeVar("T", bound="GlobalSpec")


@_attrs_define
class GlobalSpec:
    """
    Attributes:
        version (Literal[1] | Unset):  Default: 1.
        seed (int | Unset):  Default: 0.
        max_runtime_seconds (int | None | Unset):
        snapshot_frames_freq (int | None | Unset):  Default: 50.
        kind (Literal['global'] | Unset):  Default: 'global'.
        backend (GlobalSpecBackend | Unset):  Default: GlobalSpecBackend.AUTO.
        formulation (GlobalSpecFormulation | Unset):  Default: GlobalSpecFormulation.AUTO.
        use_incremental_quality_fallback (bool | Unset):  Default: True.
    """

    version: Literal[1] | Unset = 1
    seed: int | Unset = 0
    max_runtime_seconds: int | None | Unset = UNSET
    snapshot_frames_freq: int | None | Unset = 50
    kind: Literal["global"] | Unset = "global"
    backend: GlobalSpecBackend | Unset = GlobalSpecBackend.AUTO
    formulation: GlobalSpecFormulation | Unset = GlobalSpecFormulation.AUTO
    use_incremental_quality_fallback: bool | Unset = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        version = self.version

        seed = self.seed

        max_runtime_seconds: int | None | Unset
        if isinstance(self.max_runtime_seconds, Unset):
            max_runtime_seconds = UNSET
        else:
            max_runtime_seconds = self.max_runtime_seconds

        snapshot_frames_freq: int | None | Unset
        if isinstance(self.snapshot_frames_freq, Unset):
            snapshot_frames_freq = UNSET
        else:
            snapshot_frames_freq = self.snapshot_frames_freq

        kind = self.kind

        backend: str | Unset = UNSET
        if not isinstance(self.backend, Unset):
            backend = self.backend.value

        formulation: str | Unset = UNSET
        if not isinstance(self.formulation, Unset):
            formulation = self.formulation.value

        use_incremental_quality_fallback = self.use_incremental_quality_fallback

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if version is not UNSET:
            field_dict["version"] = version
        if seed is not UNSET:
            field_dict["seed"] = seed
        if max_runtime_seconds is not UNSET:
            field_dict["max_runtime_seconds"] = max_runtime_seconds
        if snapshot_frames_freq is not UNSET:
            field_dict["snapshot_frames_freq"] = snapshot_frames_freq
        if kind is not UNSET:
            field_dict["kind"] = kind
        if backend is not UNSET:
            field_dict["backend"] = backend
        if formulation is not UNSET:
            field_dict["formulation"] = formulation
        if use_incremental_quality_fallback is not UNSET:
            field_dict["use_incremental_quality_fallback"] = use_incremental_quality_fallback

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        version = cast(Literal[1] | Unset, d.pop("version", UNSET))
        if version != 1 and not isinstance(version, Unset):
            raise ValueError(f"version must match const 1, got '{version}'")

        seed = d.pop("seed", UNSET)

        def _parse_max_runtime_seconds(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        max_runtime_seconds = _parse_max_runtime_seconds(d.pop("max_runtime_seconds", UNSET))

        def _parse_snapshot_frames_freq(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        snapshot_frames_freq = _parse_snapshot_frames_freq(d.pop("snapshot_frames_freq", UNSET))

        kind = cast(Literal["global"] | Unset, d.pop("kind", UNSET))
        if kind != "global" and not isinstance(kind, Unset):
            raise ValueError(f"kind must match const 'global', got '{kind}'")

        _backend = d.pop("backend", UNSET)
        backend: GlobalSpecBackend | Unset
        if isinstance(_backend, Unset):
            backend = UNSET
        else:
            backend = GlobalSpecBackend(_backend)

        _formulation = d.pop("formulation", UNSET)
        formulation: GlobalSpecFormulation | Unset
        if isinstance(_formulation, Unset):
            formulation = UNSET
        else:
            formulation = GlobalSpecFormulation(_formulation)

        use_incremental_quality_fallback = d.pop("use_incremental_quality_fallback", UNSET)

        global_spec = cls(
            version=version,
            seed=seed,
            max_runtime_seconds=max_runtime_seconds,
            snapshot_frames_freq=snapshot_frames_freq,
            kind=kind,
            backend=backend,
            formulation=formulation,
            use_incremental_quality_fallback=use_incremental_quality_fallback,
        )

        global_spec.additional_properties = d
        return global_spec

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
