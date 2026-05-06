from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.sub_model_out_links_type_0 import SubModelOutLinksType0
    from ..models.sub_model_out_rigidity_type_0 import SubModelOutRigidityType0
    from ..models.sub_model_out_summary_type_0 import SubModelOutSummaryType0


T = TypeVar("T", bound="SubModelOut")


@_attrs_define
class SubModelOut:
    """Wire shape of a SubModel row.

    A SubModel is one disconnected component within a Reconstruction
    (``sparse/0``, ``sparse/1``, ...). ``idx`` is the COLMAP-assigned
    component index; ``parent_submodel_id`` points at the source when
    the model came out of a hierarchical merge / split. ``summary``
    carries per-component stats (image count, point count, mean
    reprojection error) so collection endpoints don't need to crack
    the snapshot. ``snapshot_seq`` / ``sealed_path`` point at the
    on-disk sealed snapshot; clients read points / cameras / images
    from there.

        Attributes:
            submodel_id (str):
            recon_id (str):
            idx (int):
            created_at (datetime.datetime):
            field_links (None | SubModelOutLinksType0 | Unset):
            parent_submodel_id (None | str | Unset):
            summary (None | SubModelOutSummaryType0 | Unset):
            rigidity (None | SubModelOutRigidityType0 | Unset):
            snapshot_seq (int | None | Unset):
            sealed_path (None | str | Unset):
    """

    submodel_id: str
    recon_id: str
    idx: int
    created_at: datetime.datetime
    field_links: None | SubModelOutLinksType0 | Unset = UNSET
    parent_submodel_id: None | str | Unset = UNSET
    summary: None | SubModelOutSummaryType0 | Unset = UNSET
    rigidity: None | SubModelOutRigidityType0 | Unset = UNSET
    snapshot_seq: int | None | Unset = UNSET
    sealed_path: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.sub_model_out_links_type_0 import SubModelOutLinksType0
        from ..models.sub_model_out_rigidity_type_0 import SubModelOutRigidityType0
        from ..models.sub_model_out_summary_type_0 import SubModelOutSummaryType0

        submodel_id = self.submodel_id

        recon_id = self.recon_id

        idx = self.idx

        created_at = self.created_at.isoformat()

        field_links: dict[str, Any] | None | Unset
        if isinstance(self.field_links, Unset):
            field_links = UNSET
        elif isinstance(self.field_links, SubModelOutLinksType0):
            field_links = self.field_links.to_dict()
        else:
            field_links = self.field_links

        parent_submodel_id: None | str | Unset
        if isinstance(self.parent_submodel_id, Unset):
            parent_submodel_id = UNSET
        else:
            parent_submodel_id = self.parent_submodel_id

        summary: dict[str, Any] | None | Unset
        if isinstance(self.summary, Unset):
            summary = UNSET
        elif isinstance(self.summary, SubModelOutSummaryType0):
            summary = self.summary.to_dict()
        else:
            summary = self.summary

        rigidity: dict[str, Any] | None | Unset
        if isinstance(self.rigidity, Unset):
            rigidity = UNSET
        elif isinstance(self.rigidity, SubModelOutRigidityType0):
            rigidity = self.rigidity.to_dict()
        else:
            rigidity = self.rigidity

        snapshot_seq: int | None | Unset
        if isinstance(self.snapshot_seq, Unset):
            snapshot_seq = UNSET
        else:
            snapshot_seq = self.snapshot_seq

        sealed_path: None | str | Unset
        if isinstance(self.sealed_path, Unset):
            sealed_path = UNSET
        else:
            sealed_path = self.sealed_path

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "submodel_id": submodel_id,
                "recon_id": recon_id,
                "idx": idx,
                "created_at": created_at,
            }
        )
        if field_links is not UNSET:
            field_dict["_links"] = field_links
        if parent_submodel_id is not UNSET:
            field_dict["parent_submodel_id"] = parent_submodel_id
        if summary is not UNSET:
            field_dict["summary"] = summary
        if rigidity is not UNSET:
            field_dict["rigidity"] = rigidity
        if snapshot_seq is not UNSET:
            field_dict["snapshot_seq"] = snapshot_seq
        if sealed_path is not UNSET:
            field_dict["sealed_path"] = sealed_path

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.sub_model_out_links_type_0 import SubModelOutLinksType0
        from ..models.sub_model_out_rigidity_type_0 import SubModelOutRigidityType0
        from ..models.sub_model_out_summary_type_0 import SubModelOutSummaryType0

        d = dict(src_dict)
        submodel_id = d.pop("submodel_id")

        recon_id = d.pop("recon_id")

        idx = d.pop("idx")

        created_at = isoparse(d.pop("created_at"))

        def _parse_field_links(data: object) -> None | SubModelOutLinksType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                field_links_type_0 = SubModelOutLinksType0.from_dict(data)

                return field_links_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SubModelOutLinksType0 | Unset, data)

        field_links = _parse_field_links(d.pop("_links", UNSET))

        def _parse_parent_submodel_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        parent_submodel_id = _parse_parent_submodel_id(d.pop("parent_submodel_id", UNSET))

        def _parse_summary(data: object) -> None | SubModelOutSummaryType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                summary_type_0 = SubModelOutSummaryType0.from_dict(data)

                return summary_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SubModelOutSummaryType0 | Unset, data)

        summary = _parse_summary(d.pop("summary", UNSET))

        def _parse_rigidity(data: object) -> None | SubModelOutRigidityType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                rigidity_type_0 = SubModelOutRigidityType0.from_dict(data)

                return rigidity_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SubModelOutRigidityType0 | Unset, data)

        rigidity = _parse_rigidity(d.pop("rigidity", UNSET))

        def _parse_snapshot_seq(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        snapshot_seq = _parse_snapshot_seq(d.pop("snapshot_seq", UNSET))

        def _parse_sealed_path(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        sealed_path = _parse_sealed_path(d.pop("sealed_path", UNSET))

        sub_model_out = cls(
            submodel_id=submodel_id,
            recon_id=recon_id,
            idx=idx,
            created_at=created_at,
            field_links=field_links,
            parent_submodel_id=parent_submodel_id,
            summary=summary,
            rigidity=rigidity,
            snapshot_seq=snapshot_seq,
            sealed_path=sealed_path,
        )

        sub_model_out.additional_properties = d
        return sub_model_out

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
