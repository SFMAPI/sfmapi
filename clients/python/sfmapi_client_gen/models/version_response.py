from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="VersionResponse")


@_attrs_define
class VersionResponse:
    """
    Attributes:
        sfmapi (str):
        pycolmap_available (bool):
        colmap_sha (str):
        baxx_sha (str):
        cudss_ver (str):
        cuda_arch (str):
        sam_model_sha (str):
    """

    sfmapi: str
    pycolmap_available: bool
    colmap_sha: str
    baxx_sha: str
    cudss_ver: str
    cuda_arch: str
    sam_model_sha: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        sfmapi = self.sfmapi

        pycolmap_available = self.pycolmap_available

        colmap_sha = self.colmap_sha

        baxx_sha = self.baxx_sha

        cudss_ver = self.cudss_ver

        cuda_arch = self.cuda_arch

        sam_model_sha = self.sam_model_sha

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "sfmapi": sfmapi,
                "pycolmap_available": pycolmap_available,
                "colmap_sha": colmap_sha,
                "baxx_sha": baxx_sha,
                "cudss_ver": cudss_ver,
                "cuda_arch": cuda_arch,
                "sam_model_sha": sam_model_sha,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        sfmapi = d.pop("sfmapi")

        pycolmap_available = d.pop("pycolmap_available")

        colmap_sha = d.pop("colmap_sha")

        baxx_sha = d.pop("baxx_sha")

        cudss_ver = d.pop("cudss_ver")

        cuda_arch = d.pop("cuda_arch")

        sam_model_sha = d.pop("sam_model_sha")

        version_response = cls(
            sfmapi=sfmapi,
            pycolmap_available=pycolmap_available,
            colmap_sha=colmap_sha,
            baxx_sha=baxx_sha,
            cudss_ver=cudss_ver,
            cuda_arch=cuda_arch,
            sam_model_sha=sam_model_sha,
        )

        version_response.additional_properties = d
        return version_response

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
