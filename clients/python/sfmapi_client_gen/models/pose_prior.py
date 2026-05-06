from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.gps_coord import GpsCoord
    from ..models.imu_measurement import ImuMeasurement
    from ..models.rigid_3 import Rigid3


T = TypeVar("T", bound="PosePrior")


@_attrs_define
class PosePrior:
    """Prior on a camera's ``cam_from_world`` pose.

    ``covariance`` is a 36-float row-major 6x6 matrix (rx, ry, rz, tx,
    ty, tz). Diagonal-only priors send only the six diagonal entries
    inside the 36-vector with off-diagonals zero. ``timestamp_ns`` is
    the optional nanosecond timestamp the prior corresponds to —
    needed when the same image appears at multiple times in a
    sequence (rolling shutter, video). ``imu`` is an optional IMU
    sample colocated with the pose prior.

        Attributes:
            cam_from_world (Rigid3): Rigid SE(3) transform: ``y = R @ x + t``.
            covariance (list[float] | None | Unset):
            gps (GpsCoord | None | Unset):
            timestamp_ns (int | None | Unset):
            imu (ImuMeasurement | None | Unset):
    """

    cam_from_world: Rigid3
    covariance: list[float] | None | Unset = UNSET
    gps: GpsCoord | None | Unset = UNSET
    timestamp_ns: int | None | Unset = UNSET
    imu: ImuMeasurement | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.gps_coord import GpsCoord
        from ..models.imu_measurement import ImuMeasurement

        cam_from_world = self.cam_from_world.to_dict()

        covariance: list[float] | None | Unset
        if isinstance(self.covariance, Unset):
            covariance = UNSET
        elif isinstance(self.covariance, list):
            covariance = self.covariance

        else:
            covariance = self.covariance

        gps: dict[str, Any] | None | Unset
        if isinstance(self.gps, Unset):
            gps = UNSET
        elif isinstance(self.gps, GpsCoord):
            gps = self.gps.to_dict()
        else:
            gps = self.gps

        timestamp_ns: int | None | Unset
        if isinstance(self.timestamp_ns, Unset):
            timestamp_ns = UNSET
        else:
            timestamp_ns = self.timestamp_ns

        imu: dict[str, Any] | None | Unset
        if isinstance(self.imu, Unset):
            imu = UNSET
        elif isinstance(self.imu, ImuMeasurement):
            imu = self.imu.to_dict()
        else:
            imu = self.imu

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "cam_from_world": cam_from_world,
            }
        )
        if covariance is not UNSET:
            field_dict["covariance"] = covariance
        if gps is not UNSET:
            field_dict["gps"] = gps
        if timestamp_ns is not UNSET:
            field_dict["timestamp_ns"] = timestamp_ns
        if imu is not UNSET:
            field_dict["imu"] = imu

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.gps_coord import GpsCoord
        from ..models.imu_measurement import ImuMeasurement
        from ..models.rigid_3 import Rigid3

        d = dict(src_dict)
        cam_from_world = Rigid3.from_dict(d.pop("cam_from_world"))

        def _parse_covariance(data: object) -> list[float] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                covariance_type_0 = cast(list[float], data)

                return covariance_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[float] | None | Unset, data)

        covariance = _parse_covariance(d.pop("covariance", UNSET))

        def _parse_gps(data: object) -> GpsCoord | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                gps_type_0 = GpsCoord.from_dict(data)

                return gps_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(GpsCoord | None | Unset, data)

        gps = _parse_gps(d.pop("gps", UNSET))

        def _parse_timestamp_ns(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        timestamp_ns = _parse_timestamp_ns(d.pop("timestamp_ns", UNSET))

        def _parse_imu(data: object) -> ImuMeasurement | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                imu_type_0 = ImuMeasurement.from_dict(data)

                return imu_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ImuMeasurement | None | Unset, data)

        imu = _parse_imu(d.pop("imu", UNSET))

        pose_prior = cls(
            cam_from_world=cam_from_world,
            covariance=covariance,
            gps=gps,
            timestamp_ns=timestamp_ns,
            imu=imu,
        )

        pose_prior.additional_properties = d
        return pose_prior

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
