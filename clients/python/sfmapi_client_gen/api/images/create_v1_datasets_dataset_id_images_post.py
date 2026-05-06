from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.image_create import ImageCreate
from ...models.image_out import ImageOut
from ...types import Response


def _get_kwargs(
    dataset_id: str,
    *,
    body: ImageCreate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/datasets/{dataset_id}/images".format(
            dataset_id=quote(str(dataset_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | ImageOut | None:
    if response.status_code == 201:
        response_201 = ImageOut.from_dict(response.json())

        return response_201

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
    dataset_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ImageCreate,
) -> Response[HTTPValidationError | ImageOut]:
    """Create

     Register a single image in a dataset.

    Provide ``blob_sha`` for upload-source datasets (the value is the
    canonical sha returned by ``POST /v1/uploads/{id}:finalize``) or
    ``rel_path`` for local-source datasets (the path relative to the
    source root). Exactly one MUST be set; 422 ``ValidationError``
    otherwise. For batch ingestion use ``POST :batchCreate``.

    Args:
        dataset_id (str):
        body (ImageCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ImageOut]
    """

    kwargs = _get_kwargs(
        dataset_id=dataset_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    dataset_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ImageCreate,
) -> HTTPValidationError | ImageOut | None:
    """Create

     Register a single image in a dataset.

    Provide ``blob_sha`` for upload-source datasets (the value is the
    canonical sha returned by ``POST /v1/uploads/{id}:finalize``) or
    ``rel_path`` for local-source datasets (the path relative to the
    source root). Exactly one MUST be set; 422 ``ValidationError``
    otherwise. For batch ingestion use ``POST :batchCreate``.

    Args:
        dataset_id (str):
        body (ImageCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ImageOut
    """

    return sync_detailed(
        dataset_id=dataset_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    dataset_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ImageCreate,
) -> Response[HTTPValidationError | ImageOut]:
    """Create

     Register a single image in a dataset.

    Provide ``blob_sha`` for upload-source datasets (the value is the
    canonical sha returned by ``POST /v1/uploads/{id}:finalize``) or
    ``rel_path`` for local-source datasets (the path relative to the
    source root). Exactly one MUST be set; 422 ``ValidationError``
    otherwise. For batch ingestion use ``POST :batchCreate``.

    Args:
        dataset_id (str):
        body (ImageCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ImageOut]
    """

    kwargs = _get_kwargs(
        dataset_id=dataset_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    dataset_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ImageCreate,
) -> HTTPValidationError | ImageOut | None:
    """Create

     Register a single image in a dataset.

    Provide ``blob_sha`` for upload-source datasets (the value is the
    canonical sha returned by ``POST /v1/uploads/{id}:finalize``) or
    ``rel_path`` for local-source datasets (the path relative to the
    source root). Exactly one MUST be set; 422 ``ValidationError``
    otherwise. For batch ingestion use ``POST :batchCreate``.

    Args:
        dataset_id (str):
        body (ImageCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ImageOut
    """

    return (
        await asyncio_detailed(
            dataset_id=dataset_id,
            client=client,
            body=body,
        )
    ).parsed
