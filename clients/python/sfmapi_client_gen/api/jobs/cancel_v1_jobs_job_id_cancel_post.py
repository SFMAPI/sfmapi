from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.job_out import JobOut
from ...types import UNSET, Response, Unset


def _get_kwargs(
    job_id: str,
    *,
    force: bool | Unset = False,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["force"] = force

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/jobs/{job_id}:cancel".format(
            job_id=quote(str(job_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | JobOut | None:
    if response.status_code == 200:
        response_200 = JobOut.from_dict(response.json())

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
) -> Response[HTTPValidationError | JobOut]:
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
    force: bool | Unset = False,
) -> Response[HTTPValidationError | JobOut]:
    """Cancel

     Cooperatively cancel a long-running job (AIP-151, AIP-136
    ``:cancel``). ``force=true`` SIGKILLs subprocesses immediately;
    default is the cooperative phase-boundary stop.

    Returns the up-to-date ``JobOut`` row. The terminal state lands
    asynchronously — clients should follow up with ``GET
    /v1/jobs/{job_id}`` (or watch the SSE stream) to observe the
    transition to ``cancelled`` or ``cancelled_dirty``.

    Args:
        job_id (str):
        force (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | JobOut]
    """

    kwargs = _get_kwargs(
        job_id=job_id,
        force=force,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    job_id: str,
    *,
    client: AuthenticatedClient | Client,
    force: bool | Unset = False,
) -> HTTPValidationError | JobOut | None:
    """Cancel

     Cooperatively cancel a long-running job (AIP-151, AIP-136
    ``:cancel``). ``force=true`` SIGKILLs subprocesses immediately;
    default is the cooperative phase-boundary stop.

    Returns the up-to-date ``JobOut`` row. The terminal state lands
    asynchronously — clients should follow up with ``GET
    /v1/jobs/{job_id}`` (or watch the SSE stream) to observe the
    transition to ``cancelled`` or ``cancelled_dirty``.

    Args:
        job_id (str):
        force (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | JobOut
    """

    return sync_detailed(
        job_id=job_id,
        client=client,
        force=force,
    ).parsed


async def asyncio_detailed(
    job_id: str,
    *,
    client: AuthenticatedClient | Client,
    force: bool | Unset = False,
) -> Response[HTTPValidationError | JobOut]:
    """Cancel

     Cooperatively cancel a long-running job (AIP-151, AIP-136
    ``:cancel``). ``force=true`` SIGKILLs subprocesses immediately;
    default is the cooperative phase-boundary stop.

    Returns the up-to-date ``JobOut`` row. The terminal state lands
    asynchronously — clients should follow up with ``GET
    /v1/jobs/{job_id}`` (or watch the SSE stream) to observe the
    transition to ``cancelled`` or ``cancelled_dirty``.

    Args:
        job_id (str):
        force (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | JobOut]
    """

    kwargs = _get_kwargs(
        job_id=job_id,
        force=force,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    job_id: str,
    *,
    client: AuthenticatedClient | Client,
    force: bool | Unset = False,
) -> HTTPValidationError | JobOut | None:
    """Cancel

     Cooperatively cancel a long-running job (AIP-151, AIP-136
    ``:cancel``). ``force=true`` SIGKILLs subprocesses immediately;
    default is the cooperative phase-boundary stop.

    Returns the up-to-date ``JobOut`` row. The terminal state lands
    asynchronously — clients should follow up with ``GET
    /v1/jobs/{job_id}`` (or watch the SSE stream) to observe the
    transition to ``cancelled`` or ``cancelled_dirty``.

    Args:
        job_id (str):
        force (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | JobOut
    """

    return (
        await asyncio_detailed(
            job_id=job_id,
            client=client,
            force=force,
        )
    ).parsed
