from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.dataset_out_links_type_0 import DatasetOutLinksType0
    from ..models.dataset_out_rig_config_json_type_0 import DatasetOutRigConfigJsonType0


T = TypeVar("T", bound="DatasetOut")


@_attrs_define
class DatasetOut:
    """Wire shape of a Dataset row.

    A Dataset binds an image source (``source_id`` -> one of the
    :data:`SourceSpec` variants) to per-dataset SfM settings:
    ``camera_model`` (COLMAP camera-model string), ``intrinsics_mode``
    (single shared / per-image / per-folder), and the spherical /
    rig metadata. ``manifest_hash`` is the content-addressed
    fingerprint of the materialized image set; downstream stages
    (features, similarity) cache against it.

        Attributes:
            created_at (datetime.datetime):
            dataset_id (str):
            tenant_id (str):
            project_id (str):
            source_id (str):
            name (str):
            camera_model (str):
            intrinsics_mode (str):
            is_spherical (bool):
            respect_exif_orientation (bool):
            manifest_hash (str):
            rig_config_json (DatasetOutRigConfigJsonType0 | None | Unset):
            active_maskset_id (None | str | Unset):
            updated_at (datetime.datetime | None | Unset):
            field_links (DatasetOutLinksType0 | None | Unset):
    """

    created_at: datetime.datetime
    dataset_id: str
    tenant_id: str
    project_id: str
    source_id: str
    name: str
    camera_model: str
    intrinsics_mode: str
    is_spherical: bool
    respect_exif_orientation: bool
    manifest_hash: str
    rig_config_json: DatasetOutRigConfigJsonType0 | None | Unset = UNSET
    active_maskset_id: None | str | Unset = UNSET
    updated_at: datetime.datetime | None | Unset = UNSET
    field_links: DatasetOutLinksType0 | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.dataset_out_links_type_0 import DatasetOutLinksType0
        from ..models.dataset_out_rig_config_json_type_0 import DatasetOutRigConfigJsonType0

        created_at = self.created_at.isoformat()

        dataset_id = self.dataset_id

        tenant_id = self.tenant_id

        project_id = self.project_id

        source_id = self.source_id

        name = self.name

        camera_model = self.camera_model

        intrinsics_mode = self.intrinsics_mode

        is_spherical = self.is_spherical

        respect_exif_orientation = self.respect_exif_orientation

        manifest_hash = self.manifest_hash

        rig_config_json: dict[str, Any] | None | Unset
        if isinstance(self.rig_config_json, Unset):
            rig_config_json = UNSET
        elif isinstance(self.rig_config_json, DatasetOutRigConfigJsonType0):
            rig_config_json = self.rig_config_json.to_dict()
        else:
            rig_config_json = self.rig_config_json

        active_maskset_id: None | str | Unset
        if isinstance(self.active_maskset_id, Unset):
            active_maskset_id = UNSET
        else:
            active_maskset_id = self.active_maskset_id

        updated_at: None | str | Unset
        if isinstance(self.updated_at, Unset):
            updated_at = UNSET
        elif isinstance(self.updated_at, datetime.datetime):
            updated_at = self.updated_at.isoformat()
        else:
            updated_at = self.updated_at

        field_links: dict[str, Any] | None | Unset
        if isinstance(self.field_links, Unset):
            field_links = UNSET
        elif isinstance(self.field_links, DatasetOutLinksType0):
            field_links = self.field_links.to_dict()
        else:
            field_links = self.field_links

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "created_at": created_at,
                "dataset_id": dataset_id,
                "tenant_id": tenant_id,
                "project_id": project_id,
                "source_id": source_id,
                "name": name,
                "camera_model": camera_model,
                "intrinsics_mode": intrinsics_mode,
                "is_spherical": is_spherical,
                "respect_exif_orientation": respect_exif_orientation,
                "manifest_hash": manifest_hash,
            }
        )
        if rig_config_json is not UNSET:
            field_dict["rig_config_json"] = rig_config_json
        if active_maskset_id is not UNSET:
            field_dict["active_maskset_id"] = active_maskset_id
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at
        if field_links is not UNSET:
            field_dict["_links"] = field_links

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.dataset_out_links_type_0 import DatasetOutLinksType0
        from ..models.dataset_out_rig_config_json_type_0 import DatasetOutRigConfigJsonType0

        d = dict(src_dict)
        created_at = isoparse(d.pop("created_at"))

        dataset_id = d.pop("dataset_id")

        tenant_id = d.pop("tenant_id")

        project_id = d.pop("project_id")

        source_id = d.pop("source_id")

        name = d.pop("name")

        camera_model = d.pop("camera_model")

        intrinsics_mode = d.pop("intrinsics_mode")

        is_spherical = d.pop("is_spherical")

        respect_exif_orientation = d.pop("respect_exif_orientation")

        manifest_hash = d.pop("manifest_hash")

        def _parse_rig_config_json(data: object) -> DatasetOutRigConfigJsonType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                rig_config_json_type_0 = DatasetOutRigConfigJsonType0.from_dict(data)

                return rig_config_json_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(DatasetOutRigConfigJsonType0 | None | Unset, data)

        rig_config_json = _parse_rig_config_json(d.pop("rig_config_json", UNSET))

        def _parse_active_maskset_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        active_maskset_id = _parse_active_maskset_id(d.pop("active_maskset_id", UNSET))

        def _parse_updated_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                updated_at_type_0 = isoparse(data)

                return updated_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        updated_at = _parse_updated_at(d.pop("updated_at", UNSET))

        def _parse_field_links(data: object) -> DatasetOutLinksType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                field_links_type_0 = DatasetOutLinksType0.from_dict(data)

                return field_links_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(DatasetOutLinksType0 | None | Unset, data)

        field_links = _parse_field_links(d.pop("_links", UNSET))

        dataset_out = cls(
            created_at=created_at,
            dataset_id=dataset_id,
            tenant_id=tenant_id,
            project_id=project_id,
            source_id=source_id,
            name=name,
            camera_model=camera_model,
            intrinsics_mode=intrinsics_mode,
            is_spherical=is_spherical,
            respect_exif_orientation=respect_exif_orientation,
            manifest_hash=manifest_hash,
            rig_config_json=rig_config_json,
            active_maskset_id=active_maskset_id,
            updated_at=updated_at,
            field_links=field_links,
        )

        dataset_out.additional_properties = d
        return dataset_out

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
