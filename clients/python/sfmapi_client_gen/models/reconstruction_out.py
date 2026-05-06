from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.reconstruction_out_status import ReconstructionOutStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.global_spec import GlobalSpec
    from ..models.hierarchical_spec import HierarchicalSpec
    from ..models.incremental_spec import IncrementalSpec
    from ..models.reconstruction_out_links_type_0 import ReconstructionOutLinksType0
    from ..models.spherical_spec import SphericalSpec


T = TypeVar("T", bound="ReconstructionOut")


@_attrs_define
class ReconstructionOut:
    """Wire shape of a Reconstruction row.

    A Reconstruction is a single mapping run against a dataset. It
    produces N :class:`SubModelOut` rows (one per disconnected
    component COLMAP discovers). The reconstruction itself is
    metadata; the actual outputs live as sealed snapshots reachable
    via ``links['snapshots']``. ``rv_id`` is the runtime-version
    fingerprint that gates cache lookup; ``dataset_snapshot_hash``
    pins the input image set for reproducibility.

        Attributes:
            recon_id (str):
            project_id (str):
            dataset_id (str):
            dataset_snapshot_hash (str):
            spec (GlobalSpec | HierarchicalSpec | IncrementalSpec | SphericalSpec):
            rv_id (str):
            status (ReconstructionOutStatus):
            created_at (datetime.datetime):
            field_links (None | ReconstructionOutLinksType0 | Unset):
    """

    recon_id: str
    project_id: str
    dataset_id: str
    dataset_snapshot_hash: str
    spec: GlobalSpec | HierarchicalSpec | IncrementalSpec | SphericalSpec
    rv_id: str
    status: ReconstructionOutStatus
    created_at: datetime.datetime
    field_links: None | ReconstructionOutLinksType0 | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.global_spec import GlobalSpec
        from ..models.hierarchical_spec import HierarchicalSpec
        from ..models.incremental_spec import IncrementalSpec
        from ..models.reconstruction_out_links_type_0 import ReconstructionOutLinksType0

        recon_id = self.recon_id

        project_id = self.project_id

        dataset_id = self.dataset_id

        dataset_snapshot_hash = self.dataset_snapshot_hash

        spec: dict[str, Any]
        if (
            isinstance(self.spec, IncrementalSpec)
            or isinstance(self.spec, GlobalSpec)
            or isinstance(self.spec, HierarchicalSpec)
        ):
            spec = self.spec.to_dict()
        else:
            spec = self.spec.to_dict()

        rv_id = self.rv_id

        status = self.status.value

        created_at = self.created_at.isoformat()

        field_links: dict[str, Any] | None | Unset
        if isinstance(self.field_links, Unset):
            field_links = UNSET
        elif isinstance(self.field_links, ReconstructionOutLinksType0):
            field_links = self.field_links.to_dict()
        else:
            field_links = self.field_links

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "recon_id": recon_id,
                "project_id": project_id,
                "dataset_id": dataset_id,
                "dataset_snapshot_hash": dataset_snapshot_hash,
                "spec": spec,
                "rv_id": rv_id,
                "status": status,
                "created_at": created_at,
            }
        )
        if field_links is not UNSET:
            field_dict["_links"] = field_links

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.global_spec import GlobalSpec
        from ..models.hierarchical_spec import HierarchicalSpec
        from ..models.incremental_spec import IncrementalSpec
        from ..models.reconstruction_out_links_type_0 import ReconstructionOutLinksType0
        from ..models.spherical_spec import SphericalSpec

        d = dict(src_dict)
        recon_id = d.pop("recon_id")

        project_id = d.pop("project_id")

        dataset_id = d.pop("dataset_id")

        dataset_snapshot_hash = d.pop("dataset_snapshot_hash")

        def _parse_spec(
            data: object,
        ) -> GlobalSpec | HierarchicalSpec | IncrementalSpec | SphericalSpec:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                spec_type_0 = IncrementalSpec.from_dict(data)

                return spec_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                spec_type_1 = GlobalSpec.from_dict(data)

                return spec_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                spec_type_2 = HierarchicalSpec.from_dict(data)

                return spec_type_2
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            spec_type_3 = SphericalSpec.from_dict(data)

            return spec_type_3

        spec = _parse_spec(d.pop("spec"))

        rv_id = d.pop("rv_id")

        status = ReconstructionOutStatus(d.pop("status"))

        created_at = isoparse(d.pop("created_at"))

        def _parse_field_links(data: object) -> None | ReconstructionOutLinksType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                field_links_type_0 = ReconstructionOutLinksType0.from_dict(data)

                return field_links_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ReconstructionOutLinksType0 | Unset, data)

        field_links = _parse_field_links(d.pop("_links", UNSET))

        reconstruction_out = cls(
            recon_id=recon_id,
            project_id=project_id,
            dataset_id=dataset_id,
            dataset_snapshot_hash=dataset_snapshot_hash,
            spec=spec,
            rv_id=rv_id,
            status=status,
            created_at=created_at,
            field_links=field_links,
        )

        reconstruction_out.additional_properties = d
        return reconstruction_out

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
