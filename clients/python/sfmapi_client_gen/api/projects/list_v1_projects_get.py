from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.page_project_out import PageProjectOut
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    page_token: None | str | Unset = UNSET,
    page_size: int | Unset = 50,
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
        "url": "/v1/projects",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | PageProjectOut | None:
    if response.status_code == 200:
        response_200 = PageProjectOut.from_dict(response.json())

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
) -> Response[HTTPValidationError | PageProjectOut]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    page_token: None | str | Unset = UNSET,
    page_size: int | Unset = 50,
) -> Response[HTTPValidationError | PageProjectOut]:
    """List

     List the caller's projects, AIP-158 paginated.

    Pass an empty ``page_token`` for the first page; iterate by
    threading the previous response's ``next_page_token`` back. A
    ``null`` ``next_page_token`` means the iteration is exhausted.

    Args:
        page_token (None | str | Unset):
        page_size (int | Unset):  Default: 50.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | PageProjectOut]
    """

    kwargs = _get_kwargs(
        page_token=page_token,
        page_size=page_size,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    page_token: None | str | Unset = UNSET,
    page_size: int | Unset = 50,
) -> HTTPValidationError | PageProjectOut | None:
    """List

     List the caller's projects, AIP-158 paginated.

    Pass an empty ``page_token`` for the first page; iterate by
    threading the previous response's ``next_page_token`` back. A
    ``null`` ``next_page_token`` means the iteration is exhausted.

    Args:
        page_token (None | str | Unset):
        page_size (int | Unset):  Default: 50.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | PageProjectOut
    """

    return sync_detailed(
        client=client,
        page_token=page_token,
        page_size=page_size,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    page_token: None | str | Unset = UNSET,
    page_size: int | Unset = 50,
) -> Response[HTTPValidationError | PageProjectOut]:
    """List

     List the caller's projects, AIP-158 paginated.

    Pass an empty ``page_token`` for the first page; iterate by
    threading the previous response's ``next_page_token`` back. A
    ``null`` ``next_page_token`` means the iteration is exhausted.

    Args:
        page_token (None | str | Unset):
        page_size (int | Unset):  Default: 50.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | PageProjectOut]
    """

    kwargs = _get_kwargs(
        page_token=page_token,
        page_size=page_size,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    page_token: None | str | Unset = UNSET,
    page_size: int | Unset = 50,
) -> HTTPValidationError | PageProjectOut | None:
    """List

     List the caller's projects, AIP-158 paginated.

    Pass an empty ``page_token`` for the first page; iterate by
    threading the previous response's ``next_page_token`` back. A
    ``null`` ``next_page_token`` means the iteration is exhausted.

    Args:
        page_token (None | str | Unset):
        page_size (int | Unset):  Default: 50.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | PageProjectOut
    """

    return (
        await asyncio_detailed(
            client=client,
            page_token=page_token,
            page_size=page_size,
        )
    ).parsed
