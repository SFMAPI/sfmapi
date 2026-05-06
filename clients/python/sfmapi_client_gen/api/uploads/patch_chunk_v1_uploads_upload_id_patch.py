from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.upload_out import UploadOut
from ...types import UNSET, Response, Unset


def _get_kwargs(
    upload_id: str,
    *,
    content_range: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(content_range, Unset):
        headers["Content-Range"] = content_range

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/v1/uploads/{upload_id}".format(
            upload_id=quote(str(upload_id), safe=""),
        ),
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | UploadOut | None:
    if response.status_code == 200:
        response_200 = UploadOut.from_dict(response.json())

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
) -> Response[HTTPValidationError | UploadOut]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    upload_id: str,
    *,
    client: AuthenticatedClient | Client,
    content_range: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | UploadOut]:
    """Patch Chunk

     Append one chunk of bytes to the upload.

    Requires ``Content-Range: bytes <start>-<end>/<total>`` (RFC 7233);
    the body length MUST equal the byte range. 422
    ``ValidationError`` on malformed Content-Range or length mismatch.
    Chunks are idempotent at the same offset — retries are safe.

    Args:
        upload_id (str):
        content_range (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | UploadOut]
    """

    kwargs = _get_kwargs(
        upload_id=upload_id,
        content_range=content_range,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    upload_id: str,
    *,
    client: AuthenticatedClient | Client,
    content_range: None | str | Unset = UNSET,
) -> HTTPValidationError | UploadOut | None:
    """Patch Chunk

     Append one chunk of bytes to the upload.

    Requires ``Content-Range: bytes <start>-<end>/<total>`` (RFC 7233);
    the body length MUST equal the byte range. 422
    ``ValidationError`` on malformed Content-Range or length mismatch.
    Chunks are idempotent at the same offset — retries are safe.

    Args:
        upload_id (str):
        content_range (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | UploadOut
    """

    return sync_detailed(
        upload_id=upload_id,
        client=client,
        content_range=content_range,
    ).parsed


async def asyncio_detailed(
    upload_id: str,
    *,
    client: AuthenticatedClient | Client,
    content_range: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | UploadOut]:
    """Patch Chunk

     Append one chunk of bytes to the upload.

    Requires ``Content-Range: bytes <start>-<end>/<total>`` (RFC 7233);
    the body length MUST equal the byte range. 422
    ``ValidationError`` on malformed Content-Range or length mismatch.
    Chunks are idempotent at the same offset — retries are safe.

    Args:
        upload_id (str):
        content_range (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | UploadOut]
    """

    kwargs = _get_kwargs(
        upload_id=upload_id,
        content_range=content_range,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    upload_id: str,
    *,
    client: AuthenticatedClient | Client,
    content_range: None | str | Unset = UNSET,
) -> HTTPValidationError | UploadOut | None:
    """Patch Chunk

     Append one chunk of bytes to the upload.

    Requires ``Content-Range: bytes <start>-<end>/<total>`` (RFC 7233);
    the body length MUST equal the byte range. 422
    ``ValidationError`` on malformed Content-Range or length mismatch.
    Chunks are idempotent at the same offset — retries are safe.

    Args:
        upload_id (str):
        content_range (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | UploadOut
    """

    return (
        await asyncio_detailed(
            upload_id=upload_id,
            client=client,
            content_range=content_range,
        )
    ).parsed
