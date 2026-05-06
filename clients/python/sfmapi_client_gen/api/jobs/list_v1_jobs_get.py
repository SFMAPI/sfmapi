from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.list_v1_jobs_get_status_type_0 import ListV1JobsGetStatusType0
from ...models.page_job_out import PageJobOut
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    page_token: None | str | Unset = UNSET,
    page_size: int | Unset = 50,
    status: ListV1JobsGetStatusType0 | None | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_page_token: None | str | Unset
    if isinstance(page_token, Unset):
        json_page_token = UNSET
    else:
        json_page_token = page_token
    params["page_token"] = json_page_token

    params["page_size"] = page_size

    json_status: None | str | Unset
    if isinstance(status, Unset):
        json_status = UNSET
    elif isinstance(status, ListV1JobsGetStatusType0):
        json_status = status.value
    else:
        json_status = status
    params["status"] = json_status

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/jobs",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | PageJobOut | None:
    if response.status_code == 200:
        response_200 = PageJobOut.from_dict(response.json())

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
) -> Response[HTTPValidationError | PageJobOut]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    page_token: None | str | Unset = UNSET,
    page_size: int | Unset = 50,
    status: ListV1JobsGetStatusType0 | None | Unset = UNSET,
) -> Response[HTTPValidationError | PageJobOut]:
    """List

     List jobs for the caller's tenant (AIP-158 paginated).

    Most-recent first (sorted by ``job_id`` descending — ULIDs are
    timestamp-prefixed). Pass ``status=running`` to find active work
    or ``status=failed`` to triage. Without ``status``, all jobs in
    every state are returned. ``next_page_token=null`` ends the
    cursor.

    Args:
        page_token (None | str | Unset):
        page_size (int | Unset):  Default: 50.
        status (ListV1JobsGetStatusType0 | None | Unset): Filter to one lifecycle state. Closed
            set: pending | running | succeeded | failed | cancelled | cancelled_dirty.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | PageJobOut]
    """

    kwargs = _get_kwargs(
        page_token=page_token,
        page_size=page_size,
        status=status,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    page_token: None | str | Unset = UNSET,
    page_size: int | Unset = 50,
    status: ListV1JobsGetStatusType0 | None | Unset = UNSET,
) -> HTTPValidationError | PageJobOut | None:
    """List

     List jobs for the caller's tenant (AIP-158 paginated).

    Most-recent first (sorted by ``job_id`` descending — ULIDs are
    timestamp-prefixed). Pass ``status=running`` to find active work
    or ``status=failed`` to triage. Without ``status``, all jobs in
    every state are returned. ``next_page_token=null`` ends the
    cursor.

    Args:
        page_token (None | str | Unset):
        page_size (int | Unset):  Default: 50.
        status (ListV1JobsGetStatusType0 | None | Unset): Filter to one lifecycle state. Closed
            set: pending | running | succeeded | failed | cancelled | cancelled_dirty.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | PageJobOut
    """

    return sync_detailed(
        client=client,
        page_token=page_token,
        page_size=page_size,
        status=status,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    page_token: None | str | Unset = UNSET,
    page_size: int | Unset = 50,
    status: ListV1JobsGetStatusType0 | None | Unset = UNSET,
) -> Response[HTTPValidationError | PageJobOut]:
    """List

     List jobs for the caller's tenant (AIP-158 paginated).

    Most-recent first (sorted by ``job_id`` descending — ULIDs are
    timestamp-prefixed). Pass ``status=running`` to find active work
    or ``status=failed`` to triage. Without ``status``, all jobs in
    every state are returned. ``next_page_token=null`` ends the
    cursor.

    Args:
        page_token (None | str | Unset):
        page_size (int | Unset):  Default: 50.
        status (ListV1JobsGetStatusType0 | None | Unset): Filter to one lifecycle state. Closed
            set: pending | running | succeeded | failed | cancelled | cancelled_dirty.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | PageJobOut]
    """

    kwargs = _get_kwargs(
        page_token=page_token,
        page_size=page_size,
        status=status,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    page_token: None | str | Unset = UNSET,
    page_size: int | Unset = 50,
    status: ListV1JobsGetStatusType0 | None | Unset = UNSET,
) -> HTTPValidationError | PageJobOut | None:
    """List

     List jobs for the caller's tenant (AIP-158 paginated).

    Most-recent first (sorted by ``job_id`` descending — ULIDs are
    timestamp-prefixed). Pass ``status=running`` to find active work
    or ``status=failed`` to triage. Without ``status``, all jobs in
    every state are returned. ``next_page_token=null`` ends the
    cursor.

    Args:
        page_token (None | str | Unset):
        page_size (int | Unset):  Default: 50.
        status (ListV1JobsGetStatusType0 | None | Unset): Filter to one lifecycle state. Closed
            set: pending | running | succeeded | failed | cancelled | cancelled_dirty.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | PageJobOut
    """

    return (
        await asyncio_detailed(
            client=client,
            page_token=page_token,
            page_size=page_size,
            status=status,
        )
    ).parsed
