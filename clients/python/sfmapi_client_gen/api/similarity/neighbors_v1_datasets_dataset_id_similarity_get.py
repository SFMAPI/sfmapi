from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.similarity_query_response import SimilarityQueryResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    dataset_id: str,
    *,
    image_id: str,
    k: int | Unset = 5,
    strategy: str | Unset = "dhash",
    include_self: bool | Unset = False,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["image_id"] = image_id

    params["k"] = k

    params["strategy"] = strategy

    params["include_self"] = include_self

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/datasets/{dataset_id}/similarity".format(
            dataset_id=quote(str(dataset_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | SimilarityQueryResponse | None:
    if response.status_code == 200:
        response_200 = SimilarityQueryResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | SimilarityQueryResponse]:
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
    image_id: str,
    k: int | Unset = 5,
    strategy: str | Unset = "dhash",
    include_self: bool | Unset = False,
) -> Response[HTTPValidationError | SimilarityQueryResponse]:
    """Neighbors

     Return the k images most similar to `image_id`.

    For `strategy=dhash` the index is built lazily on first call and
    cached on disk; subsequent calls reuse the cache until the
    dataset's `manifest_hash` changes.

    Args:
        dataset_id (str):
        image_id (str): The image to query against.
        k (int | Unset):  Default: 5.
        strategy (str | Unset):  Default: 'dhash'.
        include_self (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | SimilarityQueryResponse]
    """

    kwargs = _get_kwargs(
        dataset_id=dataset_id,
        image_id=image_id,
        k=k,
        strategy=strategy,
        include_self=include_self,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    dataset_id: str,
    *,
    client: AuthenticatedClient | Client,
    image_id: str,
    k: int | Unset = 5,
    strategy: str | Unset = "dhash",
    include_self: bool | Unset = False,
) -> HTTPValidationError | SimilarityQueryResponse | None:
    """Neighbors

     Return the k images most similar to `image_id`.

    For `strategy=dhash` the index is built lazily on first call and
    cached on disk; subsequent calls reuse the cache until the
    dataset's `manifest_hash` changes.

    Args:
        dataset_id (str):
        image_id (str): The image to query against.
        k (int | Unset):  Default: 5.
        strategy (str | Unset):  Default: 'dhash'.
        include_self (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | SimilarityQueryResponse
    """

    return sync_detailed(
        dataset_id=dataset_id,
        client=client,
        image_id=image_id,
        k=k,
        strategy=strategy,
        include_self=include_self,
    ).parsed


async def asyncio_detailed(
    dataset_id: str,
    *,
    client: AuthenticatedClient | Client,
    image_id: str,
    k: int | Unset = 5,
    strategy: str | Unset = "dhash",
    include_self: bool | Unset = False,
) -> Response[HTTPValidationError | SimilarityQueryResponse]:
    """Neighbors

     Return the k images most similar to `image_id`.

    For `strategy=dhash` the index is built lazily on first call and
    cached on disk; subsequent calls reuse the cache until the
    dataset's `manifest_hash` changes.

    Args:
        dataset_id (str):
        image_id (str): The image to query against.
        k (int | Unset):  Default: 5.
        strategy (str | Unset):  Default: 'dhash'.
        include_self (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | SimilarityQueryResponse]
    """

    kwargs = _get_kwargs(
        dataset_id=dataset_id,
        image_id=image_id,
        k=k,
        strategy=strategy,
        include_self=include_self,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    dataset_id: str,
    *,
    client: AuthenticatedClient | Client,
    image_id: str,
    k: int | Unset = 5,
    strategy: str | Unset = "dhash",
    include_self: bool | Unset = False,
) -> HTTPValidationError | SimilarityQueryResponse | None:
    """Neighbors

     Return the k images most similar to `image_id`.

    For `strategy=dhash` the index is built lazily on first call and
    cached on disk; subsequent calls reuse the cache until the
    dataset's `manifest_hash` changes.

    Args:
        dataset_id (str):
        image_id (str): The image to query against.
        k (int | Unset):  Default: 5.
        strategy (str | Unset):  Default: 'dhash'.
        include_self (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | SimilarityQueryResponse
    """

    return (
        await asyncio_detailed(
            dataset_id=dataset_id,
            client=client,
            image_id=image_id,
            k=k,
            strategy=strategy,
            include_self=include_self,
        )
    ).parsed
