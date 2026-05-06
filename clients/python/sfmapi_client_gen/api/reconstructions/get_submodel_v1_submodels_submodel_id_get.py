from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.sub_model_out import SubModelOut
from ...types import Response


def _get_kwargs(
    submodel_id: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/submodels/{submodel_id}".format(
            submodel_id=quote(str(submodel_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | SubModelOut | None:
    if response.status_code == 200:
        response_200 = SubModelOut.from_dict(response.json())

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
) -> Response[HTTPValidationError | SubModelOut]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    submodel_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[HTTPValidationError | SubModelOut]:
    """Get Submodel

     Read one SubModel by its canonical ``submodel_id``.

    Direct read of a single connected component without going through
    ``GET /v1/reconstructions/{recon_id}/submodels``. 404 if absent.

    Args:
        submodel_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | SubModelOut]
    """

    kwargs = _get_kwargs(
        submodel_id=submodel_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    submodel_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> HTTPValidationError | SubModelOut | None:
    """Get Submodel

     Read one SubModel by its canonical ``submodel_id``.

    Direct read of a single connected component without going through
    ``GET /v1/reconstructions/{recon_id}/submodels``. 404 if absent.

    Args:
        submodel_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | SubModelOut
    """

    return sync_detailed(
        submodel_id=submodel_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    submodel_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[HTTPValidationError | SubModelOut]:
    """Get Submodel

     Read one SubModel by its canonical ``submodel_id``.

    Direct read of a single connected component without going through
    ``GET /v1/reconstructions/{recon_id}/submodels``. 404 if absent.

    Args:
        submodel_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | SubModelOut]
    """

    kwargs = _get_kwargs(
        submodel_id=submodel_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    submodel_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> HTTPValidationError | SubModelOut | None:
    """Get Submodel

     Read one SubModel by its canonical ``submodel_id``.

    Direct read of a single connected component without going through
    ``GET /v1/reconstructions/{recon_id}/submodels``. 404 if absent.

    Args:
        submodel_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | SubModelOut
    """

    return (
        await asyncio_detailed(
            submodel_id=submodel_id,
            client=client,
        )
    ).parsed
