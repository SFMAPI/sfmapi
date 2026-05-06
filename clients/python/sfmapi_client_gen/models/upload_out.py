from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.upload_out_state import UploadOutState
from ..types import UNSET, Unset

T = TypeVar("T", bound="UploadOut")


@_attrs_define
class UploadOut:
    """
    Attributes:
        upload_id (str):
        state (UploadOutState):
        expected_size (int):
        received_bytes (int):
        expires_at (datetime.datetime):
        blob_sha (None | str | Unset):
    """

    upload_id: str
    state: UploadOutState
    expected_size: int
    received_bytes: int
    expires_at: datetime.datetime
    blob_sha: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        upload_id = self.upload_id

        state = self.state.value

        expected_size = self.expected_size

        received_bytes = self.received_bytes

        expires_at = self.expires_at.isoformat()

        blob_sha: None | str | Unset
        if isinstance(self.blob_sha, Unset):
            blob_sha = UNSET
        else:
            blob_sha = self.blob_sha

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "upload_id": upload_id,
                "state": state,
                "expected_size": expected_size,
                "received_bytes": received_bytes,
                "expires_at": expires_at,
            }
        )
        if blob_sha is not UNSET:
            field_dict["blob_sha"] = blob_sha

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        upload_id = d.pop("upload_id")

        state = UploadOutState(d.pop("state"))

        expected_size = d.pop("expected_size")

        received_bytes = d.pop("received_bytes")

        expires_at = isoparse(d.pop("expires_at"))

        def _parse_blob_sha(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        blob_sha = _parse_blob_sha(d.pop("blob_sha", UNSET))

        upload_out = cls(
            upload_id=upload_id,
            state=state,
            expected_size=expected_size,
            received_bytes=received_bytes,
            expires_at=expires_at,
            blob_sha=blob_sha,
        )

        upload_out.additional_properties = d
        return upload_out

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
