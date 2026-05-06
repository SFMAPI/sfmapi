from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.page_sub_model_out import PageSubModelOut
from ...types import UNSET, Response, Unset


def _get_kwargs(
    recon_id: str,
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
        "url": "/v1/reconstructions/{recon_id}/submodels".format(
            recon_id=quote(str(recon_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | PageSubModelOut | None:
    if response.status_code == 200:
        response_200 = PageSubModelOut.from_dict(response.json())

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
) -> Response[HTTPValidationError | PageSubModelOut]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    recon_id: str,
    *,
    client: AuthenticatedClient | Client,
    page_token: None | str | Unset = UNSET,
    page_size: int | Unset = 100,
) -> Response[HTTPValidationError | PageSubModelOut]:
    """List Submodels

     List the SubModels (disconnected components) of a reconstruction.

    AIP-158 paginated; results within a page are presented in ``idx``
    order (COLMAP component index). Most reconstructions have a
    handful of submodels — pagination matters only for hierarchical
    runs that produce hundreds.

    Args:
        recon_id (str):
        page_token (None | str | Unset):
        page_size (int | Unset):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | PageSubModelOut]
    """

    kwargs = _get_kwargs(
        recon_id=recon_id,
        page_token=page_token,
        page_size=page_size,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    recon_id: str,
    *,
    client: AuthenticatedClient | Client,
    page_token: None | str | Unset = UNSET,
    page_size: int | Unset = 100,
) -> HTTPValidationError | PageSubModelOut | None:
    """List Submodels

     List the SubModels (disconnected components) of a reconstruction.

    AIP-158 paginated; results within a page are presented in ``idx``
    order (COLMAP component index). Most reconstructions have a
    handful of submodels — pagination matters only for hierarchical
    runs that produce hundreds.

    Args:
        recon_id (str):
        page_token (None | str | Unset):
        page_size (int | Unset):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | PageSubModelOut
    """

    return sync_detailed(
        recon_id=recon_id,
        client=client,
        page_token=page_token,
        page_size=page_size,
    ).parsed


async def asyncio_detailed(
    recon_id: str,
    *,
    client: AuthenticatedClient | Client,
    page_token: None | str | Unset = UNSET,
    page_size: int | Unset = 100,
) -> Response[HTTPValidationError | PageSubModelOut]:
    """List Submodels

     List the SubModels (disconnected components) of a reconstruction.

    AIP-158 paginated; results within a page are presented in ``idx``
    order (COLMAP component index). Most reconstructions have a
    handful of submodels — pagination matters only for hierarchical
    runs that produce hundreds.

    Args:
        recon_id (str):
        page_token (None | str | Unset):
        page_size (int | Unset):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | PageSubModelOut]
    """

    kwargs = _get_kwargs(
        recon_id=recon_id,
        page_token=page_token,
        page_size=page_size,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    recon_id: str,
    *,
    client: AuthenticatedClient | Client,
    page_token: None | str | Unset = UNSET,
    page_size: int | Unset = 100,
) -> HTTPValidationError | PageSubModelOut | None:
    """List Submodels

     List the SubModels (disconnected components) of a reconstruction.

    AIP-158 paginated; results within a page are presented in ``idx``
    order (COLMAP component index). Most reconstructions have a
    handful of submodels — pagination matters only for hierarchical
    runs that produce hundreds.

    Args:
        recon_id (str):
        page_token (None | str | Unset):
        page_size (int | Unset):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | PageSubModelOut
    """

    return (
        await asyncio_detailed(
            recon_id=recon_id,
            client=client,
            page_token=page_token,
            page_size=page_size,
        )
    ).parsed
