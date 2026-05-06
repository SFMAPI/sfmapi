from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.job_accepted_response import JobAcceptedResponse
from ...models.verify_request import VerifyRequest
from ...types import UNSET, Response, Unset


def _get_kwargs(
    dataset_id: str,
    *,
    body: VerifyRequest | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/datasets/{dataset_id}/verify".format(
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
    body: VerifyRequest | Unset = UNSET,
) -> Response[HTTPValidationError | JobAcceptedResponse]:
    """Verify

     Enqueue two-view geometric verification on the matched pairs.

    Filters raw matches with RANSAC / fundamental matrix / homography
    estimation and writes the verified inlier subset to
    ``two_view_geometries.json``. Required before any mapping recipe.
    Returns 202 + ``Location`` pointing at the job.

    Args:
        dataset_id (str):
        body (VerifyRequest | Unset):

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
    body: VerifyRequest | Unset = UNSET,
) -> HTTPValidationError | JobAcceptedResponse | None:
    """Verify

     Enqueue two-view geometric verification on the matched pairs.

    Filters raw matches with RANSAC / fundamental matrix / homography
    estimation and writes the verified inlier subset to
    ``two_view_geometries.json``. Required before any mapping recipe.
    Returns 202 + ``Location`` pointing at the job.

    Args:
        dataset_id (str):
        body (VerifyRequest | Unset):

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
    body: VerifyRequest | Unset = UNSET,
) -> Response[HTTPValidationError | JobAcceptedResponse]:
    """Verify

     Enqueue two-view geometric verification on the matched pairs.

    Filters raw matches with RANSAC / fundamental matrix / homography
    estimation and writes the verified inlier subset to
    ``two_view_geometries.json``. Required before any mapping recipe.
    Returns 202 + ``Location`` pointing at the job.

    Args:
        dataset_id (str):
        body (VerifyRequest | Unset):

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
    body: VerifyRequest | Unset = UNSET,
) -> HTTPValidationError | JobAcceptedResponse | None:
    """Verify

     Enqueue two-view geometric verification on the matched pairs.

    Filters raw matches with RANSAC / fundamental matrix / homography
    estimation and writes the verified inlier subset to
    ``two_view_geometries.json``. Required before any mapping recipe.
    Returns 202 + ``Location`` pointing at the job.

    Args:
        dataset_id (str):
        body (VerifyRequest | Unset):

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
