from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.point_visibility_response import PointVisibilityResponse
from ...types import Response


def _get_kwargs(
    recon_id: str,
    seq: int,
    point3d_id: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/reconstructions/{recon_id}/snapshots/{seq}/points/{point3d_id}/visibility".format(
            recon_id=quote(str(recon_id), safe=""),
            seq=quote(str(seq), safe=""),
            point3d_id=quote(str(point3d_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | PointVisibilityResponse | None:
    if response.status_code == 200:
        response_200 = PointVisibilityResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | PointVisibilityResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    recon_id: str,
    seq: int,
    point3d_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[HTTPValidationError | PointVisibilityResponse]:
    """Point Visibility

     Per-point visibility: which images observe a given 3D point.

    Args:
        recon_id (str):
        seq (int):
        point3d_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | PointVisibilityResponse]
    """

    kwargs = _get_kwargs(
        recon_id=recon_id,
        seq=seq,
        point3d_id=point3d_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    recon_id: str,
    seq: int,
    point3d_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> HTTPValidationError | PointVisibilityResponse | None:
    """Point Visibility

     Per-point visibility: which images observe a given 3D point.

    Args:
        recon_id (str):
        seq (int):
        point3d_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | PointVisibilityResponse
    """

    return sync_detailed(
        recon_id=recon_id,
        seq=seq,
        point3d_id=point3d_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    recon_id: str,
    seq: int,
    point3d_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[HTTPValidationError | PointVisibilityResponse]:
    """Point Visibility

     Per-point visibility: which images observe a given 3D point.

    Args:
        recon_id (str):
        seq (int):
        point3d_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | PointVisibilityResponse]
    """

    kwargs = _get_kwargs(
        recon_id=recon_id,
        seq=seq,
        point3d_id=point3d_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    recon_id: str,
    seq: int,
    point3d_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> HTTPValidationError | PointVisibilityResponse | None:
    """Point Visibility

     Per-point visibility: which images observe a given 3D point.

    Args:
        recon_id (str):
        seq (int):
        point3d_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | PointVisibilityResponse
    """

    return (
        await asyncio_detailed(
            recon_id=recon_id,
            seq=seq,
            point3d_id=point3d_id,
            client=client,
        )
    ).parsed
