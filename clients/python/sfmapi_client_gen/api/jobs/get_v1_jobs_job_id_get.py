from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.job_detail import JobDetail
from ...types import Response


def _get_kwargs(
    job_id: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/jobs/{job_id}".format(
            job_id=quote(str(job_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | JobDetail | None:
    if response.status_code == 200:
        response_200 = JobDetail.from_dict(response.json())

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
) -> Response[HTTPValidationError | JobDetail]:
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
) -> Response[HTTPValidationError | JobDetail]:
    """Get

     Read a job + its constituent tasks.

    The canonical AIP-151 LRO poll endpoint. Clients submitting work
    via any ``POST`` that returns ``202`` follow the ``Location``
    header here and poll until ``status`` reaches a terminal value
    (``succeeded`` | ``failed`` | ``cancelled`` | ``cancelled_dirty``).
    Task ``outputs_ref`` carries the typed result payload for stages
    that return data (e.g. ``localize``).

    Args:
        job_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | JobDetail]
    """

    kwargs = _get_kwargs(
        job_id=job_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    job_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> HTTPValidationError | JobDetail | None:
    """Get

     Read a job + its constituent tasks.

    The canonical AIP-151 LRO poll endpoint. Clients submitting work
    via any ``POST`` that returns ``202`` follow the ``Location``
    header here and poll until ``status`` reaches a terminal value
    (``succeeded`` | ``failed`` | ``cancelled`` | ``cancelled_dirty``).
    Task ``outputs_ref`` carries the typed result payload for stages
    that return data (e.g. ``localize``).

    Args:
        job_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | JobDetail
    """

    return sync_detailed(
        job_id=job_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    job_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[HTTPValidationError | JobDetail]:
    """Get

     Read a job + its constituent tasks.

    The canonical AIP-151 LRO poll endpoint. Clients submitting work
    via any ``POST`` that returns ``202`` follow the ``Location``
    header here and poll until ``status`` reaches a terminal value
    (``succeeded`` | ``failed`` | ``cancelled`` | ``cancelled_dirty``).
    Task ``outputs_ref`` carries the typed result payload for stages
    that return data (e.g. ``localize``).

    Args:
        job_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | JobDetail]
    """

    kwargs = _get_kwargs(
        job_id=job_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    job_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> HTTPValidationError | JobDetail | None:
    """Get

     Read a job + its constituent tasks.

    The canonical AIP-151 LRO poll endpoint. Clients submitting work
    via any ``POST`` that returns ``202`` follow the ``Location``
    header here and poll until ``status`` reaches a terminal value
    (``succeeded`` | ``failed`` | ``cancelled`` | ``cancelled_dirty``).
    Task ``outputs_ref`` carries the typed result payload for stages
    that return data (e.g. ``localize``).

    Args:
        job_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | JobDetail
    """

    return (
        await asyncio_detailed(
            job_id=job_id,
            client=client,
        )
    ).parsed
