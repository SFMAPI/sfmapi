from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.spec_response import SpecResponse
from ...types import Response


def _get_kwargs() -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/spec",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> SpecResponse | None:
    if response.status_code == 200:
        response_200 = SpecResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[SpecResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[SpecResponse]:
    """Spec

     Discovery endpoint: identifies which standard this server
    implements. Clients can hit this to learn the spec version + a
    pointer to the human-readable doc.

    ``spec_url`` is configurable via ``SFMAPI_SPEC_URL`` because sfmapi
    has no canonical hosting; deployments point clients at their own
    spec mirror or leave it ``None``.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SpecResponse]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
) -> SpecResponse | None:
    """Spec

     Discovery endpoint: identifies which standard this server
    implements. Clients can hit this to learn the spec version + a
    pointer to the human-readable doc.

    ``spec_url`` is configurable via ``SFMAPI_SPEC_URL`` because sfmapi
    has no canonical hosting; deployments point clients at their own
    spec mirror or leave it ``None``.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        SpecResponse
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[SpecResponse]:
    """Spec

     Discovery endpoint: identifies which standard this server
    implements. Clients can hit this to learn the spec version + a
    pointer to the human-readable doc.

    ``spec_url`` is configurable via ``SFMAPI_SPEC_URL`` because sfmapi
    has no canonical hosting; deployments point clients at their own
    spec mirror or leave it ``None``.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SpecResponse]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
) -> SpecResponse | None:
    """Spec

     Discovery endpoint: identifies which standard this server
    implements. Clients can hit this to learn the spec version + a
    pointer to the human-readable doc.

    ``spec_url`` is configurable via ``SFMAPI_SPEC_URL`` because sfmapi
    has no canonical hosting; deployments point clients at their own
    spec mirror or leave it ``None``.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        SpecResponse
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
