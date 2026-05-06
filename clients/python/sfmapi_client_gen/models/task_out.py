from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.task_out_status import TaskOutStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.task_out_outputs_ref_type_0 import TaskOutOutputsRefType0


T = TypeVar("T", bound="TaskOut")


@_attrs_define
class TaskOut:
    """Wire shape of a Task row inside a Job.

    Each Task = one ARQ job (see ``L5`` in ``decisions.md``). ``kind``
    is the worker handler name (``extract`` | ``match`` | ``map`` |
    ...). ``cache_key`` is the content-addressed lookup key; tasks
    that hit cache transition straight to ``skipped``. ``outputs_ref``
    carries the typed result payload — clients read this once
    ``status`` is terminal (the localize / oneshot result lives here,
    for instance).

        Attributes:
            task_id (str):
            job_id (str):
            kind (str):
            status (TaskOutStatus):
            cache_key (str):
            inputs_hash (str):
            params_hash (str):
            outputs_ref (None | TaskOutOutputsRefType0 | Unset):
    """

    task_id: str
    job_id: str
    kind: str
    status: TaskOutStatus
    cache_key: str
    inputs_hash: str
    params_hash: str
    outputs_ref: None | TaskOutOutputsRefType0 | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.task_out_outputs_ref_type_0 import TaskOutOutputsRefType0

        task_id = self.task_id

        job_id = self.job_id

        kind = self.kind

        status = self.status.value

        cache_key = self.cache_key

        inputs_hash = self.inputs_hash

        params_hash = self.params_hash

        outputs_ref: dict[str, Any] | None | Unset
        if isinstance(self.outputs_ref, Unset):
            outputs_ref = UNSET
        elif isinstance(self.outputs_ref, TaskOutOutputsRefType0):
            outputs_ref = self.outputs_ref.to_dict()
        else:
            outputs_ref = self.outputs_ref

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "task_id": task_id,
                "job_id": job_id,
                "kind": kind,
                "status": status,
                "cache_key": cache_key,
                "inputs_hash": inputs_hash,
                "params_hash": params_hash,
            }
        )
        if outputs_ref is not UNSET:
            field_dict["outputs_ref"] = outputs_ref

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.task_out_outputs_ref_type_0 import TaskOutOutputsRefType0

        d = dict(src_dict)
        task_id = d.pop("task_id")

        job_id = d.pop("job_id")

        kind = d.pop("kind")

        status = TaskOutStatus(d.pop("status"))

        cache_key = d.pop("cache_key")

        inputs_hash = d.pop("inputs_hash")

        params_hash = d.pop("params_hash")

        def _parse_outputs_ref(data: object) -> None | TaskOutOutputsRefType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                outputs_ref_type_0 = TaskOutOutputsRefType0.from_dict(data)

                return outputs_ref_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | TaskOutOutputsRefType0 | Unset, data)

        outputs_ref = _parse_outputs_ref(d.pop("outputs_ref", UNSET))

        task_out = cls(
            task_id=task_id,
            job_id=job_id,
            kind=kind,
            status=status,
            cache_key=cache_key,
            inputs_hash=inputs_hash,
            params_hash=params_hash,
            outputs_ref=outputs_ref,
        )

        task_out.additional_properties = d
        return task_out

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
