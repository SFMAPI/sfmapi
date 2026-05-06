from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.job_accepted_response import JobAcceptedResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    dataset_id: str,
    *,
    face_size: int | None | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_face_size: int | None | Unset
    if isinstance(face_size, Unset):
        json_face_size = UNSET
    else:
        json_face_size = face_size
    params["face_size"] = json_face_size

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/datasets/{dataset_id}:render_cubemap".format(
            dataset_id=quote(str(dataset_id), safe=""),
        ),
        "params": params,
    }

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
    face_size: int | None | Unset = UNSET,
) -> Response[HTTPValidationError | JobAcceptedResponse]:
    """Render Cubemap

     Render every spherical panorama in this dataset into 6 cubemap faces.

    Requires the dataset to be marked ``is_spherical=true``. The
    output directory is returned in the task result; clients can then
    register it as a new ``local`` source for downstream pinhole-only
    pipelines.

    Args:
        dataset_id (str):
        face_size (int | None | Unset): Pixel edge length per cubemap face

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | JobAcceptedResponse]
    """

    kwargs = _get_kwargs(
        dataset_id=dataset_id,
        face_size=face_size,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    dataset_id: str,
    *,
    client: AuthenticatedClient | Client,
    face_size: int | None | Unset = UNSET,
) -> HTTPValidationError | JobAcceptedResponse | None:
    """Render Cubemap

     Render every spherical panorama in this dataset into 6 cubemap faces.

    Requires the dataset to be marked ``is_spherical=true``. The
    output directory is returned in the task result; clients can then
    register it as a new ``local`` source for downstream pinhole-only
    pipelines.

    Args:
        dataset_id (str):
        face_size (int | None | Unset): Pixel edge length per cubemap face

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | JobAcceptedResponse
    """

    return sync_detailed(
        dataset_id=dataset_id,
        client=client,
        face_size=face_size,
    ).parsed


async def asyncio_detailed(
    dataset_id: str,
    *,
    client: AuthenticatedClient | Client,
    face_size: int | None | Unset = UNSET,
) -> Response[HTTPValidationError | JobAcceptedResponse]:
    """Render Cubemap

     Render every spherical panorama in this dataset into 6 cubemap faces.

    Requires the dataset to be marked ``is_spherical=true``. The
    output directory is returned in the task result; clients can then
    register it as a new ``local`` source for downstream pinhole-only
    pipelines.

    Args:
        dataset_id (str):
        face_size (int | None | Unset): Pixel edge length per cubemap face

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | JobAcceptedResponse]
    """

    kwargs = _get_kwargs(
        dataset_id=dataset_id,
        face_size=face_size,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    dataset_id: str,
    *,
    client: AuthenticatedClient | Client,
    face_size: int | None | Unset = UNSET,
) -> HTTPValidationError | JobAcceptedResponse | None:
    """Render Cubemap

     Render every spherical panorama in this dataset into 6 cubemap faces.

    Requires the dataset to be marked ``is_spherical=true``. The
    output directory is returned in the task result; clients can then
    register it as a new ``local`` source for downstream pinhole-only
    pipelines.

    Args:
        dataset_id (str):
        face_size (int | None | Unset): Pixel edge length per cubemap face

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
            face_size=face_size,
        )
    ).parsed
