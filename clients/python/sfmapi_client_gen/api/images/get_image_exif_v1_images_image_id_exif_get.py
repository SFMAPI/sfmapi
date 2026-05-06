from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.image_exif_response import ImageExifResponse
from ...types import Response


def _get_kwargs(
    image_id: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/images/{image_id}/exif".format(
            image_id=quote(str(image_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | ImageExifResponse | None:
    if response.status_code == 200:
        response_200 = ImageExifResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | ImageExifResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    image_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[HTTPValidationError | ImageExifResponse]:
    """Get Image Exif

     Return the image's EXIF metadata as a free-form dict.

    Uses the cached ``exif_json`` row when present; otherwise falls
    back to extracting from the on-disk bytes. Returns an empty
    ``exif`` map (not 404) when the source has no EXIF or the bytes
    can't be located.

    Args:
        image_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ImageExifResponse]
    """

    kwargs = _get_kwargs(
        image_id=image_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    image_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> HTTPValidationError | ImageExifResponse | None:
    """Get Image Exif

     Return the image's EXIF metadata as a free-form dict.

    Uses the cached ``exif_json`` row when present; otherwise falls
    back to extracting from the on-disk bytes. Returns an empty
    ``exif`` map (not 404) when the source has no EXIF or the bytes
    can't be located.

    Args:
        image_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ImageExifResponse
    """

    return sync_detailed(
        image_id=image_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    image_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[HTTPValidationError | ImageExifResponse]:
    """Get Image Exif

     Return the image's EXIF metadata as a free-form dict.

    Uses the cached ``exif_json`` row when present; otherwise falls
    back to extracting from the on-disk bytes. Returns an empty
    ``exif`` map (not 404) when the source has no EXIF or the bytes
    can't be located.

    Args:
        image_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ImageExifResponse]
    """

    kwargs = _get_kwargs(
        image_id=image_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    image_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> HTTPValidationError | ImageExifResponse | None:
    """Get Image Exif

     Return the image's EXIF metadata as a free-form dict.

    Uses the cached ``exif_json`` row when present; otherwise falls
    back to extracting from the on-disk bytes. Returns an empty
    ``exif`` map (not 404) when the source has no EXIF or the bytes
    can't be located.

    Args:
        image_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ImageExifResponse
    """

    return (
        await asyncio_detailed(
            image_id=image_id,
            client=client,
        )
    ).parsed
