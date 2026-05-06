from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.job_out_status import JobOutStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.job_out_links_type_0 import JobOutLinksType0


T = TypeVar("T", bound="JobOut")


@_attrs_define
class JobOut:
    """Wire shape of a Job row.

    A Job is a long-running operation rolled up from N constituent
    Task rows (see :class:`TaskOut`). ``status`` reaches a terminal
    state (see :data:`JobStatus`) once every Task is terminal; the
    rollup is driven by ``app/workers/dispatcher.py::_maybe_finalize_job``.
    ``cancel_requested`` flips when ``POST /v1/jobs/{id}:cancel``
    arrives; ``cancel_force`` flips when ``?force=true`` was passed.
    ``error_class`` / ``error_message`` are populated only when the
    job ends in ``failed``.

        Attributes:
            job_id (str):
            tenant_id (str):
            project_id (str):
            recipe (str):
            status (JobOutStatus):
            cancel_requested (bool):
            cancel_force (bool):
            created_at (datetime.datetime):
            started_at (datetime.datetime | None | Unset):
            finished_at (datetime.datetime | None | Unset):
            error_class (None | str | Unset):
            error_message (None | str | Unset):
            field_links (JobOutLinksType0 | None | Unset):
    """

    job_id: str
    tenant_id: str
    project_id: str
    recipe: str
    status: JobOutStatus
    cancel_requested: bool
    cancel_force: bool
    created_at: datetime.datetime
    started_at: datetime.datetime | None | Unset = UNSET
    finished_at: datetime.datetime | None | Unset = UNSET
    error_class: None | str | Unset = UNSET
    error_message: None | str | Unset = UNSET
    field_links: JobOutLinksType0 | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.job_out_links_type_0 import JobOutLinksType0

        job_id = self.job_id

        tenant_id = self.tenant_id

        project_id = self.project_id

        recipe = self.recipe

        status = self.status.value

        cancel_requested = self.cancel_requested

        cancel_force = self.cancel_force

        created_at = self.created_at.isoformat()

        started_at: None | str | Unset
        if isinstance(self.started_at, Unset):
            started_at = UNSET
        elif isinstance(self.started_at, datetime.datetime):
            started_at = self.started_at.isoformat()
        else:
            started_at = self.started_at

        finished_at: None | str | Unset
        if isinstance(self.finished_at, Unset):
            finished_at = UNSET
        elif isinstance(self.finished_at, datetime.datetime):
            finished_at = self.finished_at.isoformat()
        else:
            finished_at = self.finished_at

        error_class: None | str | Unset
        if isinstance(self.error_class, Unset):
            error_class = UNSET
        else:
            error_class = self.error_class

        error_message: None | str | Unset
        if isinstance(self.error_message, Unset):
            error_message = UNSET
        else:
            error_message = self.error_message

        field_links: dict[str, Any] | None | Unset
        if isinstance(self.field_links, Unset):
            field_links = UNSET
        elif isinstance(self.field_links, JobOutLinksType0):
            field_links = self.field_links.to_dict()
        else:
            field_links = self.field_links

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "job_id": job_id,
                "tenant_id": tenant_id,
                "project_id": project_id,
                "recipe": recipe,
                "status": status,
                "cancel_requested": cancel_requested,
                "cancel_force": cancel_force,
                "created_at": created_at,
            }
        )
        if started_at is not UNSET:
            field_dict["started_at"] = started_at
        if finished_at is not UNSET:
            field_dict["finished_at"] = finished_at
        if error_class is not UNSET:
            field_dict["error_class"] = error_class
        if error_message is not UNSET:
            field_dict["error_message"] = error_message
        if field_links is not UNSET:
            field_dict["_links"] = field_links

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.job_out_links_type_0 import JobOutLinksType0

        d = dict(src_dict)
        job_id = d.pop("job_id")

        tenant_id = d.pop("tenant_id")

        project_id = d.pop("project_id")

        recipe = d.pop("recipe")

        status = JobOutStatus(d.pop("status"))

        cancel_requested = d.pop("cancel_requested")

        cancel_force = d.pop("cancel_force")

        created_at = isoparse(d.pop("created_at"))

        def _parse_started_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                started_at_type_0 = isoparse(data)

                return started_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        started_at = _parse_started_at(d.pop("started_at", UNSET))

        def _parse_finished_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                finished_at_type_0 = isoparse(data)

                return finished_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        finished_at = _parse_finished_at(d.pop("finished_at", UNSET))

        def _parse_error_class(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        error_class = _parse_error_class(d.pop("error_class", UNSET))

        def _parse_error_message(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        error_message = _parse_error_message(d.pop("error_message", UNSET))

        def _parse_field_links(data: object) -> JobOutLinksType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                field_links_type_0 = JobOutLinksType0.from_dict(data)

                return field_links_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(JobOutLinksType0 | None | Unset, data)

        field_links = _parse_field_links(d.pop("_links", UNSET))

        job_out = cls(
            job_id=job_id,
            tenant_id=tenant_id,
            project_id=project_id,
            recipe=recipe,
            status=status,
            cancel_requested=cancel_requested,
            cancel_force=cancel_force,
            created_at=created_at,
            started_at=started_at,
            finished_at=finished_at,
            error_class=error_class,
            error_message=error_message,
            field_links=field_links,
        )

        job_out.additional_properties = d
        return job_out

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
