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
    name: str,
    *,
    download: bool | Unset = False,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["download"] = download

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/reconstructions/{recon_id}/snapshots/{seq}/{name}".format(
            recon_id=quote(str(recon_id), safe=""),
            seq=quote(str(seq), safe=""),
            name=quote(str(name), safe=""),
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
    name: str,
    *,
    client: AuthenticatedClient | Client,
    download: bool | Unset = False,
) -> Response[Any | HTTPValidationError]:
    """Read Snapshot File

     Serve a single sealed-snapshot file. `name` is one of:
    `cameras.json | images.json | rigs.json | frames.json |
    pose_graph.json | points.bin | points_preview.bin | summary.json`.
    Anything else returns 404. Sealed snapshots are immutable, so the
    response carries an `ETag` and honors `If-None-Match`.

    Args:
        recon_id (str):
        seq (int):
        name (str):
        download (bool | Unset): Force Content-Disposition: attachment Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        recon_id=recon_id,
        seq=seq,
        name=name,
        download=download,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    recon_id: str,
    seq: int,
    name: str,
    *,
    client: AuthenticatedClient | Client,
    download: bool | Unset = False,
) -> Any | HTTPValidationError | None:
    """Read Snapshot File

     Serve a single sealed-snapshot file. `name` is one of:
    `cameras.json | images.json | rigs.json | frames.json |
    pose_graph.json | points.bin | points_preview.bin | summary.json`.
    Anything else returns 404. Sealed snapshots are immutable, so the
    response carries an `ETag` and honors `If-None-Match`.

    Args:
        recon_id (str):
        seq (int):
        name (str):
        download (bool | Unset): Force Content-Disposition: attachment Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return sync_detailed(
        recon_id=recon_id,
        seq=seq,
        name=name,
        client=client,
        download=download,
    ).parsed


async def asyncio_detailed(
    recon_id: str,
    seq: int,
    name: str,
    *,
    client: AuthenticatedClient | Client,
    download: bool | Unset = False,
) -> Response[Any | HTTPValidationError]:
    """Read Snapshot File

     Serve a single sealed-snapshot file. `name` is one of:
    `cameras.json | images.json | rigs.json | frames.json |
    pose_graph.json | points.bin | points_preview.bin | summary.json`.
    Anything else returns 404. Sealed snapshots are immutable, so the
    response carries an `ETag` and honors `If-None-Match`.

    Args:
        recon_id (str):
        seq (int):
        name (str):
        download (bool | Unset): Force Content-Disposition: attachment Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        recon_id=recon_id,
        seq=seq,
        name=name,
        download=download,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    recon_id: str,
    seq: int,
    name: str,
    *,
    client: AuthenticatedClient | Client,
    download: bool | Unset = False,
) -> Any | HTTPValidationError | None:
    """Read Snapshot File

     Serve a single sealed-snapshot file. `name` is one of:
    `cameras.json | images.json | rigs.json | frames.json |
    pose_graph.json | points.bin | points_preview.bin | summary.json`.
    Anything else returns 404. Sealed snapshots are immutable, so the
    response carries an `ETag` and honors `If-None-Match`.

    Args:
        recon_id (str):
        seq (int):
        name (str):
        download (bool | Unset): Force Content-Disposition: attachment Default: False.

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
            name=name,
            client=client,
            download=download,
        )
    ).parsed
