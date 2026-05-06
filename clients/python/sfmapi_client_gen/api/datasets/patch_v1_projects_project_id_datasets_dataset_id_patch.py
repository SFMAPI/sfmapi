from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.dataset_out import DatasetOut
from ...models.dataset_patch import DatasetPatch
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project_id: str,
    dataset_id: str,
    *,
    body: DatasetPatch,
    update_mask: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    json_update_mask: None | str | Unset
    if isinstance(update_mask, Unset):
        json_update_mask = UNSET
    else:
        json_update_mask = update_mask
    params["update_mask"] = json_update_mask

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/v1/projects/{project_id}/datasets/{dataset_id}".format(
            project_id=quote(str(project_id), safe=""),
            dataset_id=quote(str(dataset_id), safe=""),
        ),
        "params": params,
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
    update_mask: None | str | Unset = UNSET,
) -> Response[DatasetOut | HTTPValidationError]:
    """Patch

     Partially update a dataset.

    Without ``update_mask``, only fields present in the request body
    are written. With ``update_mask``, only the named field paths are
    applied and they must also be present in the body.

    The dataset's ``source_id`` is immutable; to change image inputs,
    create a new dataset. 422 if the row exists but belongs to another project.

    Args:
        project_id (str):
        dataset_id (str):
        update_mask (None | str | Unset): Optional AIP-161 comma-separated field mask. Allowed
            paths: name, camera_model, intrinsics_mode, is_spherical, rig_config,
            respect_exif_orientation, active_maskset_id.
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
        update_mask=update_mask,
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
    update_mask: None | str | Unset = UNSET,
) -> DatasetOut | HTTPValidationError | None:
    """Patch

     Partially update a dataset.

    Without ``update_mask``, only fields present in the request body
    are written. With ``update_mask``, only the named field paths are
    applied and they must also be present in the body.

    The dataset's ``source_id`` is immutable; to change image inputs,
    create a new dataset. 422 if the row exists but belongs to another project.

    Args:
        project_id (str):
        dataset_id (str):
        update_mask (None | str | Unset): Optional AIP-161 comma-separated field mask. Allowed
            paths: name, camera_model, intrinsics_mode, is_spherical, rig_config,
            respect_exif_orientation, active_maskset_id.
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
        update_mask=update_mask,
    ).parsed


async def asyncio_detailed(
    project_id: str,
    dataset_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: DatasetPatch,
    update_mask: None | str | Unset = UNSET,
) -> Response[DatasetOut | HTTPValidationError]:
    """Patch

     Partially update a dataset.

    Without ``update_mask``, only fields present in the request body
    are written. With ``update_mask``, only the named field paths are
    applied and they must also be present in the body.

    The dataset's ``source_id`` is immutable; to change image inputs,
    create a new dataset. 422 if the row exists but belongs to another project.

    Args:
        project_id (str):
        dataset_id (str):
        update_mask (None | str | Unset): Optional AIP-161 comma-separated field mask. Allowed
            paths: name, camera_model, intrinsics_mode, is_spherical, rig_config,
            respect_exif_orientation, active_maskset_id.
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
        update_mask=update_mask,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project_id: str,
    dataset_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: DatasetPatch,
    update_mask: None | str | Unset = UNSET,
) -> DatasetOut | HTTPValidationError | None:
    """Patch

     Partially update a dataset.

    Without ``update_mask``, only fields present in the request body
    are written. With ``update_mask``, only the named field paths are
    applied and they must also be present in the body.

    The dataset's ``source_id`` is immutable; to change image inputs,
    create a new dataset. 422 if the row exists but belongs to another project.

    Args:
        project_id (str):
        dataset_id (str):
        update_mask (None | str | Unset): Optional AIP-161 comma-separated field mask. Allowed
            paths: name, camera_model, intrinsics_mode, is_spherical, rig_config,
            respect_exif_orientation, active_maskset_id.
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
            update_mask=update_mask,
        )
    ).parsed
