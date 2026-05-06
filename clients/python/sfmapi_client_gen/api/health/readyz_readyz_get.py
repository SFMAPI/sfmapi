from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.readyz_response import ReadyzResponse
from ...types import Response


def _get_kwargs() -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/readyz",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ReadyzResponse | None:
    if response.status_code == 200:
        response_200 = ReadyzResponse.from_dict(response.json())

        return response_200

    if response.status_code == 503:
        response_503 = ReadyzResponse.from_dict(response.json())

        return response_503

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ReadyzResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[ReadyzResponse]:
    """Readyz

     Readiness — verifies backing stores (DB; Redis when configured)
    are reachable. Returns ``503`` with a per-check breakdown when
    anything is unreachable so Kubernetes / load balancers can drain
    traffic during a degraded state.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ReadyzResponse]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
) -> ReadyzResponse | None:
    """Readyz

     Readiness — verifies backing stores (DB; Redis when configured)
    are reachable. Returns ``503`` with a per-check breakdown when
    anything is unreachable so Kubernetes / load balancers can drain
    traffic during a degraded state.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ReadyzResponse
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[ReadyzResponse]:
    """Readyz

     Readiness — verifies backing stores (DB; Redis when configured)
    are reachable. Returns ``503`` with a per-check breakdown when
    anything is unreachable so Kubernetes / load balancers can drain
    traffic during a degraded state.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ReadyzResponse]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
) -> ReadyzResponse | None:
    """Readyz

     Readiness — verifies backing stores (DB; Redis when configured)
    are reachable. Returns ``503`` with a per-check breakdown when
    anything is unreachable so Kubernetes / load balancers can drain
    traffic during a degraded state.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ReadyzResponse
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
