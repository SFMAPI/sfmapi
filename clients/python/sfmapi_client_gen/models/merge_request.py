from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.merge_request_sim_3_aligners_type_0_item import MergeRequestSim3AlignersType0Item


T = TypeVar("T", bound="MergeRequest")


@_attrs_define
class MergeRequest:
    """Request body for ``POST /v1/reconstructions:merge``.

    Attributes:
        target_recon_id (str):
        source_recon_ids (list[str]):
        sim3_aligners (list[MergeRequestSim3AlignersType0Item] | None | Unset):
    """

    target_recon_id: str
    source_recon_ids: list[str]
    sim3_aligners: list[MergeRequestSim3AlignersType0Item] | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        target_recon_id = self.target_recon_id

        source_recon_ids = self.source_recon_ids

        sim3_aligners: list[dict[str, Any]] | None | Unset
        if isinstance(self.sim3_aligners, Unset):
            sim3_aligners = UNSET
        elif isinstance(self.sim3_aligners, list):
            sim3_aligners = []
            for sim3_aligners_type_0_item_data in self.sim3_aligners:
                sim3_aligners_type_0_item = sim3_aligners_type_0_item_data.to_dict()
                sim3_aligners.append(sim3_aligners_type_0_item)

        else:
            sim3_aligners = self.sim3_aligners

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "target_recon_id": target_recon_id,
                "source_recon_ids": source_recon_ids,
            }
        )
        if sim3_aligners is not UNSET:
            field_dict["sim3_aligners"] = sim3_aligners

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.merge_request_sim_3_aligners_type_0_item import (
            MergeRequestSim3AlignersType0Item,
        )

        d = dict(src_dict)
        target_recon_id = d.pop("target_recon_id")

        source_recon_ids = cast(list[str], d.pop("source_recon_ids"))

        def _parse_sim3_aligners(
            data: object,
        ) -> list[MergeRequestSim3AlignersType0Item] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                sim3_aligners_type_0 = []
                _sim3_aligners_type_0 = data
                for sim3_aligners_type_0_item_data in _sim3_aligners_type_0:
                    sim3_aligners_type_0_item = MergeRequestSim3AlignersType0Item.from_dict(
                        sim3_aligners_type_0_item_data
                    )

                    sim3_aligners_type_0.append(sim3_aligners_type_0_item)

                return sim3_aligners_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[MergeRequestSim3AlignersType0Item] | None | Unset, data)

        sim3_aligners = _parse_sim3_aligners(d.pop("sim3_aligners", UNSET))

        merge_request = cls(
            target_recon_id=target_recon_id,
            source_recon_ids=source_recon_ids,
            sim3_aligners=sim3_aligners,
        )

        merge_request.additional_properties = d
        return merge_request

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
