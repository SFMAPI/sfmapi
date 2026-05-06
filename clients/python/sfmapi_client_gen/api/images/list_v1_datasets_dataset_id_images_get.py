from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.page_image_out import PageImageOut
from ...types import UNSET, Response, Unset


def _get_kwargs(
    dataset_id: str,
    *,
    page_token: None | str | Unset = UNSET,
    page_size: int | Unset = 100,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_page_token: None | str | Unset
    if isinstance(page_token, Unset):
        json_page_token = UNSET
    else:
        json_page_token = page_token
    params["page_token"] = json_page_token

    params["page_size"] = page_size

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/datasets/{dataset_id}/images".format(
            dataset_id=quote(str(dataset_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | PageImageOut | None:
    if response.status_code == 200:
        response_200 = PageImageOut.from_dict(response.json())

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
) -> Response[HTTPValidationError | PageImageOut]:
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
    page_token: None | str | Unset = UNSET,
    page_size: int | Unset = 100,
) -> Response[HTTPValidationError | PageImageOut]:
    """List

     List images in a dataset (AIP-158 paginated).

    Ordered by ``created_at`` ascending — registration order. Iterate
    by threading ``next_page_token`` back; ``null`` ends the cursor.

    Args:
        dataset_id (str):
        page_token (None | str | Unset):
        page_size (int | Unset):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | PageImageOut]
    """

    kwargs = _get_kwargs(
        dataset_id=dataset_id,
        page_token=page_token,
        page_size=page_size,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    dataset_id: str,
    *,
    client: AuthenticatedClient | Client,
    page_token: None | str | Unset = UNSET,
    page_size: int | Unset = 100,
) -> HTTPValidationError | PageImageOut | None:
    """List

     List images in a dataset (AIP-158 paginated).

    Ordered by ``created_at`` ascending — registration order. Iterate
    by threading ``next_page_token`` back; ``null`` ends the cursor.

    Args:
        dataset_id (str):
        page_token (None | str | Unset):
        page_size (int | Unset):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | PageImageOut
    """

    return sync_detailed(
        dataset_id=dataset_id,
        client=client,
        page_token=page_token,
        page_size=page_size,
    ).parsed


async def asyncio_detailed(
    dataset_id: str,
    *,
    client: AuthenticatedClient | Client,
    page_token: None | str | Unset = UNSET,
    page_size: int | Unset = 100,
) -> Response[HTTPValidationError | PageImageOut]:
    """List

     List images in a dataset (AIP-158 paginated).

    Ordered by ``created_at`` ascending — registration order. Iterate
    by threading ``next_page_token`` back; ``null`` ends the cursor.

    Args:
        dataset_id (str):
        page_token (None | str | Unset):
        page_size (int | Unset):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | PageImageOut]
    """

    kwargs = _get_kwargs(
        dataset_id=dataset_id,
        page_token=page_token,
        page_size=page_size,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    dataset_id: str,
    *,
    client: AuthenticatedClient | Client,
    page_token: None | str | Unset = UNSET,
    page_size: int | Unset = 100,
) -> HTTPValidationError | PageImageOut | None:
    """List

     List images in a dataset (AIP-158 paginated).

    Ordered by ``created_at`` ascending — registration order. Iterate
    by threading ``next_page_token`` back; ``null`` ends the cursor.

    Args:
        dataset_id (str):
        page_token (None | str | Unset):
        page_size (int | Unset):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | PageImageOut
    """

    return (
        await asyncio_detailed(
            dataset_id=dataset_id,
            client=client,
            page_token=page_token,
            page_size=page_size,
        )
    ).parsed
