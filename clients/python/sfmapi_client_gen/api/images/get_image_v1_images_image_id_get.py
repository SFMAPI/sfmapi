from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.image_out import ImageOut
from ...types import Response


def _get_kwargs(
    image_id: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/images/{image_id}".format(
            image_id=quote(str(image_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | ImageOut | None:
    if response.status_code == 200:
        response_200 = ImageOut.from_dict(response.json())

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
) -> Response[HTTPValidationError | ImageOut]:
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
) -> Response[HTTPValidationError | ImageOut]:
    """Get Image

     Read one image's metadata by its canonical ``image_id``.

    Returns the same shape as :class:`ImageOut` — width / height /
    EXIF / source pointers — without the bytes themselves. Use
    ``GET /v1/images/{id}/bytes`` for the original payload.

    Args:
        image_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ImageOut]
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
) -> HTTPValidationError | ImageOut | None:
    """Get Image

     Read one image's metadata by its canonical ``image_id``.

    Returns the same shape as :class:`ImageOut` — width / height /
    EXIF / source pointers — without the bytes themselves. Use
    ``GET /v1/images/{id}/bytes`` for the original payload.

    Args:
        image_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ImageOut
    """

    return sync_detailed(
        image_id=image_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    image_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[HTTPValidationError | ImageOut]:
    """Get Image

     Read one image's metadata by its canonical ``image_id``.

    Returns the same shape as :class:`ImageOut` — width / height /
    EXIF / source pointers — without the bytes themselves. Use
    ``GET /v1/images/{id}/bytes`` for the original payload.

    Args:
        image_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ImageOut]
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
) -> HTTPValidationError | ImageOut | None:
    """Get Image

     Read one image's metadata by its canonical ``image_id``.

    Returns the same shape as :class:`ImageOut` — width / height /
    EXIF / source pointers — without the bytes themselves. Use
    ``GET /v1/images/{id}/bytes`` for the original payload.

    Args:
        image_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ImageOut
    """

    return (
        await asyncio_detailed(
            image_id=image_id,
            client=client,
        )
    ).parsed
