from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.finalize_v1_uploads_upload_id_finalize_post_payload import (
    FinalizeV1UploadsUploadIdFinalizePostPayload,
)
from ...models.http_validation_error import HTTPValidationError
from ...models.upload_out import UploadOut
from ...types import UNSET, Response, Unset


def _get_kwargs(
    upload_id: str,
    *,
    body: FinalizeV1UploadsUploadIdFinalizePostPayload | Unset = UNSET,
    x_content_sha256: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(x_content_sha256, Unset):
        headers["X-Content-SHA256"] = x_content_sha256

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/uploads/{upload_id}:finalize".format(
            upload_id=quote(str(upload_id), safe=""),
        ),
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

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
    body: FinalizeV1UploadsUploadIdFinalizePostPayload | Unset = UNSET,
    x_content_sha256: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | UploadOut]:
    """Finalize

     Seal an upload — verify the assembled bytes match the
    expected size and (when supplied) ``X-Content-SHA256``, then
    transition the row to ``finalized`` with the canonical
    ``blob_sha``. AIP-136 ``:finalize`` colon verb (the operation
    has side effects beyond a Standard Update).

    Args:
        upload_id (str):
        x_content_sha256 (None | str | Unset):
        body (FinalizeV1UploadsUploadIdFinalizePostPayload | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | UploadOut]
    """

    kwargs = _get_kwargs(
        upload_id=upload_id,
        body=body,
        x_content_sha256=x_content_sha256,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    upload_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: FinalizeV1UploadsUploadIdFinalizePostPayload | Unset = UNSET,
    x_content_sha256: None | str | Unset = UNSET,
) -> HTTPValidationError | UploadOut | None:
    """Finalize

     Seal an upload — verify the assembled bytes match the
    expected size and (when supplied) ``X-Content-SHA256``, then
    transition the row to ``finalized`` with the canonical
    ``blob_sha``. AIP-136 ``:finalize`` colon verb (the operation
    has side effects beyond a Standard Update).

    Args:
        upload_id (str):
        x_content_sha256 (None | str | Unset):
        body (FinalizeV1UploadsUploadIdFinalizePostPayload | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | UploadOut
    """

    return sync_detailed(
        upload_id=upload_id,
        client=client,
        body=body,
        x_content_sha256=x_content_sha256,
    ).parsed


async def asyncio_detailed(
    upload_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: FinalizeV1UploadsUploadIdFinalizePostPayload | Unset = UNSET,
    x_content_sha256: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | UploadOut]:
    """Finalize

     Seal an upload — verify the assembled bytes match the
    expected size and (when supplied) ``X-Content-SHA256``, then
    transition the row to ``finalized`` with the canonical
    ``blob_sha``. AIP-136 ``:finalize`` colon verb (the operation
    has side effects beyond a Standard Update).

    Args:
        upload_id (str):
        x_content_sha256 (None | str | Unset):
        body (FinalizeV1UploadsUploadIdFinalizePostPayload | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | UploadOut]
    """

    kwargs = _get_kwargs(
        upload_id=upload_id,
        body=body,
        x_content_sha256=x_content_sha256,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    upload_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: FinalizeV1UploadsUploadIdFinalizePostPayload | Unset = UNSET,
    x_content_sha256: None | str | Unset = UNSET,
) -> HTTPValidationError | UploadOut | None:
    """Finalize

     Seal an upload — verify the assembled bytes match the
    expected size and (when supplied) ``X-Content-SHA256``, then
    transition the row to ``finalized`` with the canonical
    ``blob_sha``. AIP-136 ``:finalize`` colon verb (the operation
    has side effects beyond a Standard Update).

    Args:
        upload_id (str):
        x_content_sha256 (None | str | Unset):
        body (FinalizeV1UploadsUploadIdFinalizePostPayload | Unset):

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
            body=body,
            x_content_sha256=x_content_sha256,
        )
    ).parsed
