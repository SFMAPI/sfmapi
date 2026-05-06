from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="VideoFramesRequest")


@_attrs_define
class VideoFramesRequest:
    """``POST /v1/projects/{pid}/datasets:from_video`` — extract
    keyframes from a worker-local video file.

        Attributes:
            video_path (str):
            fps (float | Unset):  Default: 2.0.
            max_frames (int | Unset):  Default: 1000.
    """

    video_path: str
    fps: float | Unset = 2.0
    max_frames: int | Unset = 1000
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        video_path = self.video_path

        fps = self.fps

        max_frames = self.max_frames

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "video_path": video_path,
            }
        )
        if fps is not UNSET:
            field_dict["fps"] = fps
        if max_frames is not UNSET:
            field_dict["max_frames"] = max_frames

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        video_path = d.pop("video_path")

        fps = d.pop("fps", UNSET)

        max_frames = d.pop("max_frames", UNSET)

        video_frames_request = cls(
            video_path=video_path,
            fps=fps,
            max_frames=max_frames,
        )

        video_frames_request.additional_properties = d
        return video_frames_request

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
