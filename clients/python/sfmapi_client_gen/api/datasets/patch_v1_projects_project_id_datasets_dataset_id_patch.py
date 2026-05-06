from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.dataset_out import DatasetOut
from ...models.dataset_patch import DatasetPatch
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    project_id: str,
    dataset_id: str,
    *,
    body: DatasetPatch,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/v1/projects/{project_id}/datasets/{dataset_id}".format(
            project_id=quote(str(project_id), safe=""),
            dataset_id=quote(str(dataset_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> DatasetOut | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = DatasetOut.from_dict(response.json())

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
) -> Response[DatasetOut | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project_id: str,
    dataset_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: DatasetPatch,
) -> Response[DatasetOut | HTTPValidationError]:
    """Patch

     Partially update a dataset.

    Only the fields present in the request body are written. The
    dataset's ``source_id`` is immutable — to change image inputs,
    create a new dataset. 422 if the row exists but belongs to a
    different project than the one in the path.

    Args:
        project_id (str):
        dataset_id (str):
        body (DatasetPatch): Partial update. Unset fields are left untouched. The dataset's
            `source_id` is immutable — to change images, create a new dataset.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DatasetOut | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        dataset_id=dataset_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    project_id: str,
    dataset_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: DatasetPatch,
) -> DatasetOut | HTTPValidationError | None:
    """Patch

     Partially update a dataset.

    Only the fields present in the request body are written. The
    dataset's ``source_id`` is immutable — to change image inputs,
    create a new dataset. 422 if the row exists but belongs to a
    different project than the one in the path.

    Args:
        project_id (str):
        dataset_id (str):
        body (DatasetPatch): Partial update. Unset fields are left untouched. The dataset's
            `source_id` is immutable — to change images, create a new dataset.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DatasetOut | HTTPValidationError
    """

    return sync_detailed(
        project_id=project_id,
        dataset_id=dataset_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    project_id: str,
    dataset_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: DatasetPatch,
) -> Response[DatasetOut | HTTPValidationError]:
    """Patch

     Partially update a dataset.

    Only the fields present in the request body are written. The
    dataset's ``source_id`` is immutable — to change image inputs,
    create a new dataset. 422 if the row exists but belongs to a
    different project than the one in the path.

    Args:
        project_id (str):
        dataset_id (str):
        body (DatasetPatch): Partial update. Unset fields are left untouched. The dataset's
            `source_id` is immutable — to change images, create a new dataset.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DatasetOut | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        dataset_id=dataset_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project_id: str,
    dataset_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: DatasetPatch,
) -> DatasetOut | HTTPValidationError | None:
    """Patch

     Partially update a dataset.

    Only the fields present in the request body are written. The
    dataset's ``source_id`` is immutable — to change image inputs,
    create a new dataset. 422 if the row exists but belongs to a
    different project than the one in the path.

    Args:
        project_id (str):
        dataset_id (str):
        body (DatasetPatch): Partial update. Unset fields are left untouched. The dataset's
            `source_id` is immutable — to change images, create a new dataset.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DatasetOut | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            project_id=project_id,
            dataset_id=dataset_id,
            client=client,
            body=body,
        )
    ).parsed
