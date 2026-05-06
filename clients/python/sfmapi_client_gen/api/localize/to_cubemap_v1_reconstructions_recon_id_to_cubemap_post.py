from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.job_accepted_response import JobAcceptedResponse
from ...types import Response


def _get_kwargs(
    recon_id: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/reconstructions/{recon_id}:to_cubemap".format(
            recon_id=quote(str(recon_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | JobAcceptedResponse | None:
    if response.status_code == 202:
        response_202 = JobAcceptedResponse.from_dict(response.json())

        return response_202

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[HTTPValidationError | JobAcceptedResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    recon_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[HTTPValidationError | JobAcceptedResponse]:
    """To Cubemap

     Convert a spherical reconstruction to a 6-face cubemap rig.

    Requires the dataset to be marked ``is_spherical=true``. The
    worker re-projects each panorama into 6 faces, builds a cubemap
    rig + frames, and seals a fresh snapshot whose ``rigs.json`` and
    ``frames.json`` carry the cubemap layout.

    Args:
        recon_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | JobAcceptedResponse]
    """

    kwargs = _get_kwargs(
        recon_id=recon_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    recon_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> HTTPValidationError | JobAcceptedResponse | None:
    """To Cubemap

     Convert a spherical reconstruction to a 6-face cubemap rig.

    Requires the dataset to be marked ``is_spherical=true``. The
    worker re-projects each panorama into 6 faces, builds a cubemap
    rig + frames, and seals a fresh snapshot whose ``rigs.json`` and
    ``frames.json`` carry the cubemap layout.

    Args:
        recon_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | JobAcceptedResponse
    """

    return sync_detailed(
        recon_id=recon_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    recon_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[HTTPValidationError | JobAcceptedResponse]:
    """To Cubemap

     Convert a spherical reconstruction to a 6-face cubemap rig.

    Requires the dataset to be marked ``is_spherical=true``. The
    worker re-projects each panorama into 6 faces, builds a cubemap
    rig + frames, and seals a fresh snapshot whose ``rigs.json`` and
    ``frames.json`` carry the cubemap layout.

    Args:
        recon_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | JobAcceptedResponse]
    """

    kwargs = _get_kwargs(
        recon_id=recon_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    recon_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> HTTPValidationError | JobAcceptedResponse | None:
    """To Cubemap

     Convert a spherical reconstruction to a 6-face cubemap rig.

    Requires the dataset to be marked ``is_spherical=true``. The
    worker re-projects each panorama into 6 faces, builds a cubemap
    rig + frames, and seals a fresh snapshot whose ``rigs.json`` and
    ``frames.json`` carry the cubemap layout.

    Args:
        recon_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | JobAcceptedResponse
    """

    return (
        await asyncio_detailed(
            recon_id=recon_id,
            client=client,
        )
    ).parsed
