from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.dataset_patch_intrinsics_mode_type_0 import DatasetPatchIntrinsicsModeType0
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.dataset_patch_rig_config_type_0 import DatasetPatchRigConfigType0


T = TypeVar("T", bound="DatasetPatch")


@_attrs_define
class DatasetPatch:
    """Partial update. Unset fields are left untouched. The dataset's
    `source_id` is immutable — to change images, create a new dataset.

        Attributes:
            name (None | str | Unset):
            camera_model (None | str | Unset):
            intrinsics_mode (DatasetPatchIntrinsicsModeType0 | None | Unset):
            is_spherical (bool | None | Unset):
            rig_config (DatasetPatchRigConfigType0 | None | Unset):
            respect_exif_orientation (bool | None | Unset):
            active_maskset_id (None | str | Unset):
    """

    name: None | str | Unset = UNSET
    camera_model: None | str | Unset = UNSET
    intrinsics_mode: DatasetPatchIntrinsicsModeType0 | None | Unset = UNSET
    is_spherical: bool | None | Unset = UNSET
    rig_config: DatasetPatchRigConfigType0 | None | Unset = UNSET
    respect_exif_orientation: bool | None | Unset = UNSET
    active_maskset_id: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.dataset_patch_rig_config_type_0 import DatasetPatchRigConfigType0

        name: None | str | Unset
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        camera_model: None | str | Unset
        if isinstance(self.camera_model, Unset):
            camera_model = UNSET
        else:
            camera_model = self.camera_model

        intrinsics_mode: None | str | Unset
        if isinstance(self.intrinsics_mode, Unset):
            intrinsics_mode = UNSET
        elif isinstance(self.intrinsics_mode, DatasetPatchIntrinsicsModeType0):
            intrinsics_mode = self.intrinsics_mode.value
        else:
            intrinsics_mode = self.intrinsics_mode

        is_spherical: bool | None | Unset
        if isinstance(self.is_spherical, Unset):
            is_spherical = UNSET
        else:
            is_spherical = self.is_spherical

        rig_config: dict[str, Any] | None | Unset
        if isinstance(self.rig_config, Unset):
            rig_config = UNSET
        elif isinstance(self.rig_config, DatasetPatchRigConfigType0):
            rig_config = self.rig_config.to_dict()
        else:
            rig_config = self.rig_config

        respect_exif_orientation: bool | None | Unset
        if isinstance(self.respect_exif_orientation, Unset):
            respect_exif_orientation = UNSET
        else:
            respect_exif_orientation = self.respect_exif_orientation

        active_maskset_id: None | str | Unset
        if isinstance(self.active_maskset_id, Unset):
            active_maskset_id = UNSET
        else:
            active_maskset_id = self.active_maskset_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if camera_model is not UNSET:
            field_dict["camera_model"] = camera_model
        if intrinsics_mode is not UNSET:
            field_dict["intrinsics_mode"] = intrinsics_mode
        if is_spherical is not UNSET:
            field_dict["is_spherical"] = is_spherical
        if rig_config is not UNSET:
            field_dict["rig_config"] = rig_config
        if respect_exif_orientation is not UNSET:
            field_dict["respect_exif_orientation"] = respect_exif_orientation
        if active_maskset_id is not UNSET:
            field_dict["active_maskset_id"] = active_maskset_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.dataset_patch_rig_config_type_0 import DatasetPatchRigConfigType0

        d = dict(src_dict)

        def _parse_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_camera_model(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        camera_model = _parse_camera_model(d.pop("camera_model", UNSET))

        def _parse_intrinsics_mode(data: object) -> DatasetPatchIntrinsicsModeType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                intrinsics_mode_type_0 = DatasetPatchIntrinsicsModeType0(data)

                return intrinsics_mode_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(DatasetPatchIntrinsicsModeType0 | None | Unset, data)

        intrinsics_mode = _parse_intrinsics_mode(d.pop("intrinsics_mode", UNSET))

        def _parse_is_spherical(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        is_spherical = _parse_is_spherical(d.pop("is_spherical", UNSET))

        def _parse_rig_config(data: object) -> DatasetPatchRigConfigType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                rig_config_type_0 = DatasetPatchRigConfigType0.from_dict(data)

                return rig_config_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(DatasetPatchRigConfigType0 | None | Unset, data)

        rig_config = _parse_rig_config(d.pop("rig_config", UNSET))

        def _parse_respect_exif_orientation(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        respect_exif_orientation = _parse_respect_exif_orientation(
            d.pop("respect_exif_orientation", UNSET)
        )

        def _parse_active_maskset_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        active_maskset_id = _parse_active_maskset_id(d.pop("active_maskset_id", UNSET))

        dataset_patch = cls(
            name=name,
            camera_model=camera_model,
            intrinsics_mode=intrinsics_mode,
            is_spherical=is_spherical,
            rig_config=rig_config,
            respect_exif_orientation=respect_exif_orientation,
            active_maskset_id=active_maskset_id,
        )

        dataset_patch.additional_properties = d
        return dataset_patch

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
