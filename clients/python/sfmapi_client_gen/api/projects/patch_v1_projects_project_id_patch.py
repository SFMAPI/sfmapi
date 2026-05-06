from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.project_out import ProjectOut
from ...models.project_patch import ProjectPatch
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project_id: str,
    *,
    body: ProjectPatch,
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
        "url": "/v1/projects/{project_id}".format(
            project_id=quote(str(project_id), safe=""),
        ),
        "params": params,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | ProjectOut | None:
    if response.status_code == 200:
        response_200 = ProjectOut.from_dict(response.json())

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
) -> Response[HTTPValidationError | ProjectOut]:
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
    body: ProjectPatch,
    update_mask: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ProjectOut]:
    """Patch

     Partially update a project.

    Without ``update_mask``, only fields present in the request body
    are written. With ``update_mask``, only the named field paths are
    applied and they must also be present in the body.

    Args:
        project_id (str):
        update_mask (None | str | Unset): Optional AIP-161 comma-separated field mask. Allowed
            paths: name, description.
        body (ProjectPatch): Partial update. Unset fields are left untouched.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ProjectOut]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        body=body,
        update_mask=update_mask,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    project_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ProjectPatch,
    update_mask: None | str | Unset = UNSET,
) -> HTTPValidationError | ProjectOut | None:
    """Patch

     Partially update a project.

    Without ``update_mask``, only fields present in the request body
    are written. With ``update_mask``, only the named field paths are
    applied and they must also be present in the body.

    Args:
        project_id (str):
        update_mask (None | str | Unset): Optional AIP-161 comma-separated field mask. Allowed
            paths: name, description.
        body (ProjectPatch): Partial update. Unset fields are left untouched.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ProjectOut
    """

    return sync_detailed(
        project_id=project_id,
        client=client,
        body=body,
        update_mask=update_mask,
    ).parsed


async def asyncio_detailed(
    project_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ProjectPatch,
    update_mask: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ProjectOut]:
    """Patch

     Partially update a project.

    Without ``update_mask``, only fields present in the request body
    are written. With ``update_mask``, only the named field paths are
    applied and they must also be present in the body.

    Args:
        project_id (str):
        update_mask (None | str | Unset): Optional AIP-161 comma-separated field mask. Allowed
            paths: name, description.
        body (ProjectPatch): Partial update. Unset fields are left untouched.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ProjectOut]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        body=body,
        update_mask=update_mask,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ProjectPatch,
    update_mask: None | str | Unset = UNSET,
) -> HTTPValidationError | ProjectOut | None:
    """Patch

     Partially update a project.

    Without ``update_mask``, only fields present in the request body
    are written. With ``update_mask``, only the named field paths are
    applied and they must also be present in the body.

    Args:
        project_id (str):
        update_mask (None | str | Unset): Optional AIP-161 comma-separated field mask. Allowed
            paths: name, description.
        body (ProjectPatch): Partial update. Unset fields are left untouched.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ProjectOut
    """

    return (
        await asyncio_detailed(
            project_id=project_id,
            client=client,
            body=body,
            update_mask=update_mask,
        )
    ).parsed
