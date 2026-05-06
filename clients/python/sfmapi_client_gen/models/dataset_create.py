from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.dataset_create_intrinsics_mode import DatasetCreateIntrinsicsMode
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.dataset_create_rig_config_type_0 import DatasetCreateRigConfigType0
    from ..models.local_source_spec import LocalSourceSpec
    from ..models.s3_source_spec import S3SourceSpec
    from ..models.upload_source_spec import UploadSourceSpec


T = TypeVar("T", bound="DatasetCreate")


@_attrs_define
class DatasetCreate:
    """
    Attributes:
        name (str):
        source (LocalSourceSpec | S3SourceSpec | UploadSourceSpec):
        camera_model (str | Unset):  Default: 'SIMPLE_RADIAL'.
        intrinsics_mode (DatasetCreateIntrinsicsMode | Unset):  Default: DatasetCreateIntrinsicsMode.SINGLE_CAMERA.
        is_spherical (bool | Unset):  Default: False.
        rig_config (DatasetCreateRigConfigType0 | None | Unset):
        respect_exif_orientation (bool | Unset):  Default: False.
    """

    name: str
    source: LocalSourceSpec | S3SourceSpec | UploadSourceSpec
    camera_model: str | Unset = "SIMPLE_RADIAL"
    intrinsics_mode: DatasetCreateIntrinsicsMode | Unset = DatasetCreateIntrinsicsMode.SINGLE_CAMERA
    is_spherical: bool | Unset = False
    rig_config: DatasetCreateRigConfigType0 | None | Unset = UNSET
    respect_exif_orientation: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.dataset_create_rig_config_type_0 import DatasetCreateRigConfigType0
        from ..models.local_source_spec import LocalSourceSpec
        from ..models.upload_source_spec import UploadSourceSpec

        name = self.name

        source: dict[str, Any]
        if isinstance(self.source, UploadSourceSpec) or isinstance(self.source, LocalSourceSpec):
            source = self.source.to_dict()
        else:
            source = self.source.to_dict()

        camera_model = self.camera_model

        intrinsics_mode: str | Unset = UNSET
        if not isinstance(self.intrinsics_mode, Unset):
            intrinsics_mode = self.intrinsics_mode.value

        is_spherical = self.is_spherical

        rig_config: dict[str, Any] | None | Unset
        if isinstance(self.rig_config, Unset):
            rig_config = UNSET
        elif isinstance(self.rig_config, DatasetCreateRigConfigType0):
            rig_config = self.rig_config.to_dict()
        else:
            rig_config = self.rig_config

        respect_exif_orientation = self.respect_exif_orientation

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "source": source,
            }
        )
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

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.dataset_create_rig_config_type_0 import DatasetCreateRigConfigType0
        from ..models.local_source_spec import LocalSourceSpec
        from ..models.s3_source_spec import S3SourceSpec
        from ..models.upload_source_spec import UploadSourceSpec

        d = dict(src_dict)
        name = d.pop("name")

        def _parse_source(data: object) -> LocalSourceSpec | S3SourceSpec | UploadSourceSpec:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                source_type_0 = UploadSourceSpec.from_dict(data)

                return source_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                source_type_1 = LocalSourceSpec.from_dict(data)

                return source_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            source_type_2 = S3SourceSpec.from_dict(data)

            return source_type_2

        source = _parse_source(d.pop("source"))

        camera_model = d.pop("camera_model", UNSET)

        _intrinsics_mode = d.pop("intrinsics_mode", UNSET)
        intrinsics_mode: DatasetCreateIntrinsicsMode | Unset
        if isinstance(_intrinsics_mode, Unset):
            intrinsics_mode = UNSET
        else:
            intrinsics_mode = DatasetCreateIntrinsicsMode(_intrinsics_mode)

        is_spherical = d.pop("is_spherical", UNSET)

        def _parse_rig_config(data: object) -> DatasetCreateRigConfigType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                rig_config_type_0 = DatasetCreateRigConfigType0.from_dict(data)

                return rig_config_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(DatasetCreateRigConfigType0 | None | Unset, data)

        rig_config = _parse_rig_config(d.pop("rig_config", UNSET))

        respect_exif_orientation = d.pop("respect_exif_orientation", UNSET)

        dataset_create = cls(
            name=name,
            source=source,
            camera_model=camera_model,
            intrinsics_mode=intrinsics_mode,
            is_spherical=is_spherical,
            rig_config=rig_config,
            respect_exif_orientation=respect_exif_orientation,
        )

        dataset_create.additional_properties = d
        return dataset_create

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
