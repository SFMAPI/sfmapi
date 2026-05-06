from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.features_request import FeaturesRequest
from ...models.http_validation_error import HTTPValidationError
from ...models.job_accepted_response import JobAcceptedResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    dataset_id: str,
    *,
    body: FeaturesRequest | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/datasets/{dataset_id}/features".format(
            dataset_id=quote(str(dataset_id), safe=""),
        ),
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
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
    dataset_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: FeaturesRequest | Unset = UNSET,
) -> Response[HTTPValidationError | JobAcceptedResponse]:
    """Features

     Enqueue local-feature extraction on every image in the dataset.

    Returns 202 with a ``Location`` header pointing at the job. The
    extractor type (``sift``, ``superpoint``, ``aliked``, ...) is
    chosen via :class:`FeaturesSpec.type`; backends advertise
    supported types via the ``features.extract.{type}`` capability
    flags. Re-running with an identical spec hits the cache.

    Args:
        dataset_id (str):
        body (FeaturesRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | JobAcceptedResponse]
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
    body: FeaturesRequest | Unset = UNSET,
) -> HTTPValidationError | JobAcceptedResponse | None:
    """Features

     Enqueue local-feature extraction on every image in the dataset.

    Returns 202 with a ``Location`` header pointing at the job. The
    extractor type (``sift``, ``superpoint``, ``aliked``, ...) is
    chosen via :class:`FeaturesSpec.type`; backends advertise
    supported types via the ``features.extract.{type}`` capability
    flags. Re-running with an identical spec hits the cache.

    Args:
        dataset_id (str):
        body (FeaturesRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | JobAcceptedResponse
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
    body: FeaturesRequest | Unset = UNSET,
) -> Response[HTTPValidationError | JobAcceptedResponse]:
    """Features

     Enqueue local-feature extraction on every image in the dataset.

    Returns 202 with a ``Location`` header pointing at the job. The
    extractor type (``sift``, ``superpoint``, ``aliked``, ...) is
    chosen via :class:`FeaturesSpec.type`; backends advertise
    supported types via the ``features.extract.{type}`` capability
    flags. Re-running with an identical spec hits the cache.

    Args:
        dataset_id (str):
        body (FeaturesRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | JobAcceptedResponse]
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
    body: FeaturesRequest | Unset = UNSET,
) -> HTTPValidationError | JobAcceptedResponse | None:
    """Features

     Enqueue local-feature extraction on every image in the dataset.

    Returns 202 with a ``Location`` header pointing at the job. The
    extractor type (``sift``, ``superpoint``, ``aliked``, ...) is
    chosen via :class:`FeaturesSpec.type`; backends advertise
    supported types via the ``features.extract.{type}`` capability
    flags. Re-running with an identical spec hits the cache.

    Args:
        dataset_id (str):
        body (FeaturesRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | JobAcceptedResponse
    """

    return (
        await asyncio_detailed(
            dataset_id=dataset_id,
            client=client,
            body=body,
        )
    ).parsed
