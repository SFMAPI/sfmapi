from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    recon_id: str,
    seq: int,
    *,
    max_level: int | Unset = 4,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["max_level"] = max_level

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/reconstructions/{recon_id}/snapshots/{seq}/tiles/index.json".format(
            recon_id=quote(str(recon_id), safe=""),
            seq=quote(str(seq), safe=""),
        ),
        "params": params,
    }

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
    recon_id: str,
    seq: int,
    *,
    client: AuthenticatedClient | Client,
    max_level: int | Unset = 4,
) -> Response[Any | HTTPValidationError]:
    """Tiles Index

     Octree tile index for the snapshot's `points.bin`. Tiles are
    generated lazily on first request, then cached on disk under
    `<snapshot>/tiles/`. Subsequent requests for tile bytes hit the
    cache directly.

    Args:
        recon_id (str):
        seq (int):
        max_level (int | Unset):  Default: 4.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        recon_id=recon_id,
        seq=seq,
        max_level=max_level,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    recon_id: str,
    seq: int,
    *,
    client: AuthenticatedClient | Client,
    max_level: int | Unset = 4,
) -> Any | HTTPValidationError | None:
    """Tiles Index

     Octree tile index for the snapshot's `points.bin`. Tiles are
    generated lazily on first request, then cached on disk under
    `<snapshot>/tiles/`. Subsequent requests for tile bytes hit the
    cache directly.

    Args:
        recon_id (str):
        seq (int):
        max_level (int | Unset):  Default: 4.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return sync_detailed(
        recon_id=recon_id,
        seq=seq,
        client=client,
        max_level=max_level,
    ).parsed


async def asyncio_detailed(
    recon_id: str,
    seq: int,
    *,
    client: AuthenticatedClient | Client,
    max_level: int | Unset = 4,
) -> Response[Any | HTTPValidationError]:
    """Tiles Index

     Octree tile index for the snapshot's `points.bin`. Tiles are
    generated lazily on first request, then cached on disk under
    `<snapshot>/tiles/`. Subsequent requests for tile bytes hit the
    cache directly.

    Args:
        recon_id (str):
        seq (int):
        max_level (int | Unset):  Default: 4.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        recon_id=recon_id,
        seq=seq,
        max_level=max_level,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    recon_id: str,
    seq: int,
    *,
    client: AuthenticatedClient | Client,
    max_level: int | Unset = 4,
) -> Any | HTTPValidationError | None:
    """Tiles Index

     Octree tile index for the snapshot's `points.bin`. Tiles are
    generated lazily on first request, then cached on disk under
    `<snapshot>/tiles/`. Subsequent requests for tile bytes hit the
    cache directly.

    Args:
        recon_id (str):
        seq (int):
        max_level (int | Unset):  Default: 4.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            recon_id=recon_id,
            seq=seq,
            client=client,
            max_level=max_level,
        )
    ).parsed
