from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.one_shot_features_payload import OneShotFeaturesPayload
    from ..models.one_shot_features_response_spec import OneShotFeaturesResponseSpec
    from ..models.one_shot_image_info import OneShotImageInfo
    from ..models.one_shot_runtime_info import OneShotRuntimeInfo


T = TypeVar("T", bound="OneShotFeaturesResponse")


@_attrs_define
class OneShotFeaturesResponse:
    """``POST /v1/oneshot/features`` envelope. No persistence —
    everything the consumer needs is in this body. ``schema_version``
    versions the wire shape; bump on incompatible changes.

        Attributes:
            image (OneShotImageInfo): Decoded image dimensions + size echoed back so consumers can
                sanity-check what the server actually parsed.
            features (OneShotFeaturesPayload): The features themselves. ``keypoints`` is row-major
                ``[[x, y, scale, angle], ...]``; ``descriptors_b64`` is
                base64-encoded float32 descriptors of shape
                ``(count, descriptor_dim)`` in row-major order. ``descriptor_dim``
                is implied by the extractor (128 for SIFT).
            runtime (OneShotRuntimeInfo):
            schema_version (Literal[1] | Unset):  Default: 1.
            kind (Literal['oneshot.features'] | Unset):  Default: 'oneshot.features'.
            spec (OneShotFeaturesResponseSpec | Unset):
    """

    image: OneShotImageInfo
    features: OneShotFeaturesPayload
    runtime: OneShotRuntimeInfo
    schema_version: Literal[1] | Unset = 1
    kind: Literal["oneshot.features"] | Unset = "oneshot.features"
    spec: OneShotFeaturesResponseSpec | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        image = self.image.to_dict()

        features = self.features.to_dict()

        runtime = self.runtime.to_dict()

        schema_version = self.schema_version

        kind = self.kind

        spec: dict[str, Any] | Unset = UNSET
        if not isinstance(self.spec, Unset):
            spec = self.spec.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "image": image,
                "features": features,
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
        from ..models.one_shot_features_payload import OneShotFeaturesPayload
        from ..models.one_shot_features_response_spec import OneShotFeaturesResponseSpec
        from ..models.one_shot_image_info import OneShotImageInfo
        from ..models.one_shot_runtime_info import OneShotRuntimeInfo

        d = dict(src_dict)
        image = OneShotImageInfo.from_dict(d.pop("image"))

        features = OneShotFeaturesPayload.from_dict(d.pop("features"))

        runtime = OneShotRuntimeInfo.from_dict(d.pop("runtime"))

        schema_version = cast(Literal[1] | Unset, d.pop("schema_version", UNSET))
        if schema_version != 1 and not isinstance(schema_version, Unset):
            raise ValueError(f"schema_version must match const 1, got '{schema_version}'")

        kind = cast(Literal["oneshot.features"] | Unset, d.pop("kind", UNSET))
        if kind != "oneshot.features" and not isinstance(kind, Unset):
            raise ValueError(f"kind must match const 'oneshot.features', got '{kind}'")

        _spec = d.pop("spec", UNSET)
        spec: OneShotFeaturesResponseSpec | Unset
        if isinstance(_spec, Unset):
            spec = UNSET
        else:
            spec = OneShotFeaturesResponseSpec.from_dict(_spec)

        one_shot_features_response = cls(
            image=image,
            features=features,
            runtime=runtime,
            schema_version=schema_version,
            kind=kind,
            spec=spec,
        )

        return one_shot_features_response
