from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.one_shot_image_info import OneShotImageInfo
    from ..models.one_shot_localize_response_result import OneShotLocalizeResponseResult
    from ..models.one_shot_localize_response_spec import OneShotLocalizeResponseSpec
    from ..models.one_shot_runtime_info import OneShotRuntimeInfo


T = TypeVar("T", bound="OneShotLocalizeResponse")


@_attrs_define
class OneShotLocalizeResponse:
    """``POST /v1/oneshot/localize`` envelope. Single-frame pose
    against an existing reconstruction with no DB row, no Job row,
    no upload step. The ``result`` field re-uses the existing
    :class:`~app.schemas.api.scene.LocalizationResult` shape verbatim
    so SDK consumers can re-decode through the typed model.

        Attributes:
            recon_id (str):
            image (OneShotImageInfo): Decoded image dimensions + size echoed back so consumers can
                sanity-check what the server actually parsed.
            result (OneShotLocalizeResponseResult):
            runtime (OneShotRuntimeInfo):
            schema_version (Literal[1] | Unset):  Default: 1.
            kind (Literal['oneshot.localize'] | Unset):  Default: 'oneshot.localize'.
            spec (OneShotLocalizeResponseSpec | Unset):
    """

    recon_id: str
    image: OneShotImageInfo
    result: OneShotLocalizeResponseResult
    runtime: OneShotRuntimeInfo
    schema_version: Literal[1] | Unset = 1
    kind: Literal["oneshot.localize"] | Unset = "oneshot.localize"
    spec: OneShotLocalizeResponseSpec | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        recon_id = self.recon_id

        image = self.image.to_dict()

        result = self.result.to_dict()

        runtime = self.runtime.to_dict()

        schema_version = self.schema_version

        kind = self.kind

        spec: dict[str, Any] | Unset = UNSET
        if not isinstance(self.spec, Unset):
            spec = self.spec.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "recon_id": recon_id,
                "image": image,
                "result": result,
                "runtime": runtime,
            }
        )
        if schema_version is not UNSET:
            field_dict["schema_version"] = schema_version
        if kind is not UNSET:
            field_dict["kind"] = kind
        if spec is not UNSET:
            field_dict["spec"] = spec

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.one_shot_image_info import OneShotImageInfo
        from ..models.one_shot_localize_response_result import OneShotLocalizeResponseResult
        from ..models.one_shot_localize_response_spec import OneShotLocalizeResponseSpec
        from ..models.one_shot_runtime_info import OneShotRuntimeInfo

        d = dict(src_dict)
        recon_id = d.pop("recon_id")

        image = OneShotImageInfo.from_dict(d.pop("image"))

        result = OneShotLocalizeResponseResult.from_dict(d.pop("result"))

        runtime = OneShotRuntimeInfo.from_dict(d.pop("runtime"))

        schema_version = cast(Literal[1] | Unset, d.pop("schema_version", UNSET))
        if schema_version != 1 and not isinstance(schema_version, Unset):
            raise ValueError(f"schema_version must match const 1, got '{schema_version}'")

        kind = cast(Literal["oneshot.localize"] | Unset, d.pop("kind", UNSET))
        if kind != "oneshot.localize" and not isinstance(kind, Unset):
            raise ValueError(f"kind must match const 'oneshot.localize', got '{kind}'")

        _spec = d.pop("spec", UNSET)
        spec: OneShotLocalizeResponseSpec | Unset
        if isinstance(_spec, Unset):
            spec = UNSET
        else:
            spec = OneShotLocalizeResponseSpec.from_dict(_spec)

        one_shot_localize_response = cls(
            recon_id=recon_id,
            image=image,
            result=result,
            runtime=runtime,
            schema_version=schema_version,
            kind=kind,
            spec=spec,
        )

        return one_shot_localize_response
