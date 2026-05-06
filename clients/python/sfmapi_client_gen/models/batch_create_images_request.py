from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.image_create import ImageCreate


T = TypeVar("T", bound="BatchCreateImagesRequest")


@_attrs_define
class BatchCreateImagesRequest:
    """AIP-231 batch-create request body. Each entry is a complete
    ``ImageCreate``; the server registers them all in a single
    transaction.

        Attributes:
            requests (list[ImageCreate] | Unset):
    """

    requests: list[ImageCreate] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        requests: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.requests, Unset):
            requests = []
            for requests_item_data in self.requests:
                requests_item = requests_item_data.to_dict()
                requests.append(requests_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if requests is not UNSET:
            field_dict["requests"] = requests

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.image_create import ImageCreate

        d = dict(src_dict)
        _requests = d.pop("requests", UNSET)
        requests: list[ImageCreate] | Unset = UNSET
        if _requests is not UNSET:
            requests = []
            for requests_item_data in _requests:
                requests_item = ImageCreate.from_dict(requests_item_data)

                requests.append(requests_item)

        batch_create_images_request = cls(
            requests=requests,
        )

        batch_create_images_request.additional_properties = d
        return batch_create_images_request

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
