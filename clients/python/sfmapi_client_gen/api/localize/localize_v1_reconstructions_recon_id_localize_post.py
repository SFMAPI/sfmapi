from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.job_accepted_response import JobAcceptedResponse
from ...models.localization_request import LocalizationRequest
from ...types import Response


def _get_kwargs(
    recon_id: str,
    *,
    body: LocalizationRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/reconstructions/{recon_id}/localize".format(
            recon_id=quote(str(recon_id), safe=""),
        ),
    }

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
    recon_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: LocalizationRequest,
) -> Response[HTTPValidationError | JobAcceptedResponse]:
    """Localize

     Localize a single query image against the reconstruction.

    The job's task carries a :class:`~app.schemas.api.scene.LocalizationResult`-
    shaped payload in its ``outputs_ref`` once finished.

    Args:
        recon_id (str):
        body (LocalizationRequest): Request body for ``POST /v1/reconstructions/{rid}/localize``.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | JobAcceptedResponse]
    """

    kwargs = _get_kwargs(
        recon_id=recon_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    recon_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: LocalizationRequest,
) -> HTTPValidationError | JobAcceptedResponse | None:
    """Localize

     Localize a single query image against the reconstruction.

    The job's task carries a :class:`~app.schemas.api.scene.LocalizationResult`-
    shaped payload in its ``outputs_ref`` once finished.

    Args:
        recon_id (str):
        body (LocalizationRequest): Request body for ``POST /v1/reconstructions/{rid}/localize``.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | JobAcceptedResponse
    """

    return sync_detailed(
        recon_id=recon_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    recon_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: LocalizationRequest,
) -> Response[HTTPValidationError | JobAcceptedResponse]:
    """Localize

     Localize a single query image against the reconstruction.

    The job's task carries a :class:`~app.schemas.api.scene.LocalizationResult`-
    shaped payload in its ``outputs_ref`` once finished.

    Args:
        recon_id (str):
        body (LocalizationRequest): Request body for ``POST /v1/reconstructions/{rid}/localize``.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | JobAcceptedResponse]
    """

    kwargs = _get_kwargs(
        recon_id=recon_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    recon_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: LocalizationRequest,
) -> HTTPValidationError | JobAcceptedResponse | None:
    """Localize

     Localize a single query image against the reconstruction.

    The job's task carries a :class:`~app.schemas.api.scene.LocalizationResult`-
    shaped payload in its ``outputs_ref`` once finished.

    Args:
        recon_id (str):
        body (LocalizationRequest): Request body for ``POST /v1/reconstructions/{rid}/localize``.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | JobAcceptedResponse
    """

    return (
        await asyncio_detailed(
            recon_id=recon_id,
            client=client,
            body=body,
        )
    ).parsed
