from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    job_id: str,
    *,
    last_event_id: int | None | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(last_event_id, Unset):
        headers["Last-Event-ID"] = last_event_id

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/jobs/{job_id}/events".format(
            job_id=quote(str(job_id), safe=""),
        ),
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = response.json()
        return response_200

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    job_id: str,
    *,
    client: AuthenticatedClient | Client,
    last_event_id: int | None | Unset = UNSET,
) -> Response[Any | HTTPValidationError]:
    """Events

     SSE stream of progress events for the given job.

    Body
    ----
    ``Content-Type: text/event-stream``. Each event is one
    :class:`~app.schemas.progress_event.ProgressEvent` JSON-encoded
    in the SSE ``data:`` field, prefixed by an ``id:`` line carrying
    the monotonic per-job event sequence.

    Resume (``Last-Event-ID``)
    --------------------------
    Clients reconnecting after a transient disconnect SHOULD pass the
    last event id they observed via the standard ``Last-Event-ID``
    request header (browsers do this automatically). The server replays
    every persisted event with ``event_id > last_event_id`` from the
    ring buffer before resuming the live tail. Sending a value larger
    than any persisted id yields an empty replay and the live tail.

    Termination
    -----------
    The stream closes (server-side EOF) once the job's status reaches
    a terminal value (``succeeded`` | ``failed`` | ``cancelled`` |
    ``cancelled_dirty``) AND one final drain cycle has shipped any
    pending events. Without this exit condition, ``submit_and_stream``
    consumers would block forever waiting for EOF on a job that
    already finished. The terminal vocabulary is shared with
    ``app/workers/dispatcher.py::_maybe_finalize_job`` (see ``L13``,
    ``L14`` in ``decisions.md``).

    Mid-stream deletion
    -------------------
    If the underlying job row vanishes while the stream is open
    (e.g., tenant teardown, DB GC), the next poll cycle observes a
    ``None`` job and exits as if a terminal state were reached — the
    stream closes cleanly rather than 500-ing mid-flight. Clients see
    EOF; a follow-up ``GET /v1/jobs/{job_id}`` then returns 404.

    Phase 1 implementation tails by polling the DB on a 1s cadence;
    Phase 5 swaps to Redis pub/sub without changing the wire shape.

    Args:
        job_id (str):
        last_event_id (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        job_id=job_id,
        last_event_id=last_event_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    job_id: str,
    *,
    client: AuthenticatedClient | Client,
    last_event_id: int | None | Unset = UNSET,
) -> Any | HTTPValidationError | None:
    """Events

     SSE stream of progress events for the given job.

    Body
    ----
    ``Content-Type: text/event-stream``. Each event is one
    :class:`~app.schemas.progress_event.ProgressEvent` JSON-encoded
    in the SSE ``data:`` field, prefixed by an ``id:`` line carrying
    the monotonic per-job event sequence.

    Resume (``Last-Event-ID``)
    --------------------------
    Clients reconnecting after a transient disconnect SHOULD pass the
    last event id they observed via the standard ``Last-Event-ID``
    request header (browsers do this automatically). The server replays
    every persisted event with ``event_id > last_event_id`` from the
    ring buffer before resuming the live tail. Sending a value larger
    than any persisted id yields an empty replay and the live tail.

    Termination
    -----------
    The stream closes (server-side EOF) once the job's status reaches
    a terminal value (``succeeded`` | ``failed`` | ``cancelled`` |
    ``cancelled_dirty``) AND one final drain cycle has shipped any
    pending events. Without this exit condition, ``submit_and_stream``
    consumers would block forever waiting for EOF on a job that
    already finished. The terminal vocabulary is shared with
    ``app/workers/dispatcher.py::_maybe_finalize_job`` (see ``L13``,
    ``L14`` in ``decisions.md``).

    Mid-stream deletion
    -------------------
    If the underlying job row vanishes while the stream is open
    (e.g., tenant teardown, DB GC), the next poll cycle observes a
    ``None`` job and exits as if a terminal state were reached — the
    stream closes cleanly rather than 500-ing mid-flight. Clients see
    EOF; a follow-up ``GET /v1/jobs/{job_id}`` then returns 404.

    Phase 1 implementation tails by polling the DB on a 1s cadence;
    Phase 5 swaps to Redis pub/sub without changing the wire shape.

    Args:
        job_id (str):
        last_event_id (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return sync_detailed(
        job_id=job_id,
        client=client,
        last_event_id=last_event_id,
    ).parsed


async def asyncio_detailed(
    job_id: str,
    *,
    client: AuthenticatedClient | Client,
    last_event_id: int | None | Unset = UNSET,
) -> Response[Any | HTTPValidationError]:
    """Events

     SSE stream of progress events for the given job.

    Body
    ----
    ``Content-Type: text/event-stream``. Each event is one
    :class:`~app.schemas.progress_event.ProgressEvent` JSON-encoded
    in the SSE ``data:`` field, prefixed by an ``id:`` line carrying
    the monotonic per-job event sequence.

    Resume (``Last-Event-ID``)
    --------------------------
    Clients reconnecting after a transient disconnect SHOULD pass the
    last event id they observed via the standard ``Last-Event-ID``
    request header (browsers do this automatically). The server replays
    every persisted event with ``event_id > last_event_id`` from the
    ring buffer before resuming the live tail. Sending a value larger
    than any persisted id yields an empty replay and the live tail.

    Termination
    -----------
    The stream closes (server-side EOF) once the job's status reaches
    a terminal value (``succeeded`` | ``failed`` | ``cancelled`` |
    ``cancelled_dirty``) AND one final drain cycle has shipped any
    pending events. Without this exit condition, ``submit_and_stream``
    consumers would block forever waiting for EOF on a job that
    already finished. The terminal vocabulary is shared with
    ``app/workers/dispatcher.py::_maybe_finalize_job`` (see ``L13``,
    ``L14`` in ``decisions.md``).

    Mid-stream deletion
    -------------------
    If the underlying job row vanishes while the stream is open
    (e.g., tenant teardown, DB GC), the next poll cycle observes a
    ``None`` job and exits as if a terminal state were reached — the
    stream closes cleanly rather than 500-ing mid-flight. Clients see
    EOF; a follow-up ``GET /v1/jobs/{job_id}`` then returns 404.

    Phase 1 implementation tails by polling the DB on a 1s cadence;
    Phase 5 swaps to Redis pub/sub without changing the wire shape.

    Args:
        job_id (str):
        last_event_id (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        job_id=job_id,
        last_event_id=last_event_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    job_id: str,
    *,
    client: AuthenticatedClient | Client,
    last_event_id: int | None | Unset = UNSET,
) -> Any | HTTPValidationError | None:
    """Events

     SSE stream of progress events for the given job.

    Body
    ----
    ``Content-Type: text/event-stream``. Each event is one
    :class:`~app.schemas.progress_event.ProgressEvent` JSON-encoded
    in the SSE ``data:`` field, prefixed by an ``id:`` line carrying
    the monotonic per-job event sequence.

    Resume (``Last-Event-ID``)
    --------------------------
    Clients reconnecting after a transient disconnect SHOULD pass the
    last event id they observed via the standard ``Last-Event-ID``
    request header (browsers do this automatically). The server replays
    every persisted event with ``event_id > last_event_id`` from the
    ring buffer before resuming the live tail. Sending a value larger
    than any persisted id yields an empty replay and the live tail.

    Termination
    -----------
    The stream closes (server-side EOF) once the job's status reaches
    a terminal value (``succeeded`` | ``failed`` | ``cancelled`` |
    ``cancelled_dirty``) AND one final drain cycle has shipped any
    pending events. Without this exit condition, ``submit_and_stream``
    consumers would block forever waiting for EOF on a job that
    already finished. The terminal vocabulary is shared with
    ``app/workers/dispatcher.py::_maybe_finalize_job`` (see ``L13``,
    ``L14`` in ``decisions.md``).

    Mid-stream deletion
    -------------------
    If the underlying job row vanishes while the stream is open
    (e.g., tenant teardown, DB GC), the next poll cycle observes a
    ``None`` job and exits as if a terminal state were reached — the
    stream closes cleanly rather than 500-ing mid-flight. Clients see
    EOF; a follow-up ``GET /v1/jobs/{job_id}`` then returns 404.

    Phase 1 implementation tails by polling the DB on a 1s cadence;
    Phase 5 swaps to Redis pub/sub without changing the wire shape.

    Args:
        job_id (str):
        last_event_id (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            job_id=job_id,
            client=client,
            last_event_id=last_event_id,
        )
    ).parsed
