from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.dataset_create import DatasetCreate
from ...models.dataset_out import DatasetOut
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    project_id: str,
    *,
    body: DatasetCreate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/projects/{project_id}/datasets".format(
            project_id=quote(str(project_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> DatasetOut | HTTPValidationError | None:
    if response.status_code == 201:
        response_201 = DatasetOut.from_dict(response.json())

        return response_201

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[DatasetOut | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: DatasetCreate,
) -> Response[DatasetOut | HTTPValidationError]:
    """Create

     Create a Dataset under a project.

    ``body.source`` is a discriminated :data:`SourceSpec` (``upload``
    | ``local`` | ``s3``); the source is materialized server-side and
    bound to the new Dataset. ``camera_model`` / ``intrinsics_mode`` /
    ``is_spherical`` / ``rig_config`` configure the SfM pipeline
    defaults. 404 if the project doesn't exist for this tenant.

    Args:
        project_id (str):
        body (DatasetCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DatasetOut | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    project_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: DatasetCreate,
) -> DatasetOut | HTTPValidationError | None:
    """Create

     Create a Dataset under a project.

    ``body.source`` is a discriminated :data:`SourceSpec` (``upload``
    | ``local`` | ``s3``); the source is materialized server-side and
    bound to the new Dataset. ``camera_model`` / ``intrinsics_mode`` /
    ``is_spherical`` / ``rig_config`` configure the SfM pipeline
    defaults. 404 if the project doesn't exist for this tenant.

    Args:
        project_id (str):
        body (DatasetCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DatasetOut | HTTPValidationError
    """

    return sync_detailed(
        project_id=project_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    project_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: DatasetCreate,
) -> Response[DatasetOut | HTTPValidationError]:
    """Create

     Create a Dataset under a project.

    ``body.source`` is a discriminated :data:`SourceSpec` (``upload``
    | ``local`` | ``s3``); the source is materialized server-side and
    bound to the new Dataset. ``camera_model`` / ``intrinsics_mode`` /
    ``is_spherical`` / ``rig_config`` configure the SfM pipeline
    defaults. 404 if the project doesn't exist for this tenant.

    Args:
        project_id (str):
        body (DatasetCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DatasetOut | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: DatasetCreate,
) -> DatasetOut | HTTPValidationError | None:
    """Create

     Create a Dataset under a project.

    ``body.source`` is a discriminated :data:`SourceSpec` (``upload``
    | ``local`` | ``s3``); the source is materialized server-side and
    bound to the new Dataset. ``camera_model`` / ``intrinsics_mode`` /
    ``is_spherical`` / ``rig_config`` configure the SfM pipeline
    defaults. 404 if the project doesn't exist for this tenant.

    Args:
        project_id (str):
        body (DatasetCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DatasetOut | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            project_id=project_id,
            client=client,
            body=body,
        )
    ).parsed
