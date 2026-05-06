from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    dataset_id: str,
    name: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/v1/datasets/{dataset_id}/images/{name}".format(
            dataset_id=quote(str(dataset_id), safe=""),
            name=quote(str(name), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | HTTPValidationError | None:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    dataset_id: str,
    name: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Any | HTTPValidationError]:
    """Delete

     Unregister an image from a dataset by ``name``.

    NOTE: addressed by the human-readable ``name`` here, not the
    canonical ``image_id`` (the audit doc captures the ergonomic
    inconsistency — kept stable in place; reads + bytes routes
    use ``image_id``). 204 on success, 404 if no image with that
    name exists in the dataset.

    Args:
        dataset_id (str):
        name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        dataset_id=dataset_id,
        name=name,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    dataset_id: str,
    name: str,
    *,
    client: AuthenticatedClient | Client,
) -> Any | HTTPValidationError | None:
    """Delete

     Unregister an image from a dataset by ``name``.

    NOTE: addressed by the human-readable ``name`` here, not the
    canonical ``image_id`` (the audit doc captures the ergonomic
    inconsistency — kept stable in place; reads + bytes routes
    use ``image_id``). 204 on success, 404 if no image with that
    name exists in the dataset.

    Args:
        dataset_id (str):
        name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return sync_detailed(
        dataset_id=dataset_id,
        name=name,
        client=client,
    ).parsed


async def asyncio_detailed(
    dataset_id: str,
    name: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Any | HTTPValidationError]:
    """Delete

     Unregister an image from a dataset by ``name``.

    NOTE: addressed by the human-readable ``name`` here, not the
    canonical ``image_id`` (the audit doc captures the ergonomic
    inconsistency — kept stable in place; reads + bytes routes
    use ``image_id``). 204 on success, 404 if no image with that
    name exists in the dataset.

    Args:
        dataset_id (str):
        name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        dataset_id=dataset_id,
        name=name,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    dataset_id: str,
    name: str,
    *,
    client: AuthenticatedClient | Client,
) -> Any | HTTPValidationError | None:
    """Delete

     Unregister an image from a dataset by ``name``.

    NOTE: addressed by the human-readable ``name`` here, not the
    canonical ``image_id`` (the audit doc captures the ergonomic
    inconsistency — kept stable in place; reads + bytes routes
    use ``image_id``). 204 on success, 404 if no image with that
    name exists in the dataset.

    Args:
        dataset_id (str):
        name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            dataset_id=dataset_id,
            name=name,
            client=client,
        )
    ).parsed
