from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.one_shot_localize_response import OneShotLocalizeResponse
from ...models.oneshot_localize_v1_oneshot_localize_post_type import (
    OneshotLocalizeV1OneshotLocalizePostType,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    recon_id: str,
    type_: OneshotLocalizeV1OneshotLocalizePostType
    | Unset = OneshotLocalizeV1OneshotLocalizePostType.SIFT,
    max_num_features: int | Unset = 8192,
    use_gpu: bool | Unset = True,
    seed: int | Unset = 0,
    content_type: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(content_type, Unset):
        headers["Content-Type"] = content_type

    params: dict[str, Any] = {}

    params["recon_id"] = recon_id

    json_type_: str | Unset = UNSET
    if not isinstance(type_, Unset):
        json_type_ = type_.value

    params["type"] = json_type_

    params["max_num_features"] = max_num_features

    params["use_gpu"] = use_gpu

    params["seed"] = seed

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/oneshot/localize",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | OneShotLocalizeResponse | None:
    if response.status_code == 200:
        response_200 = OneShotLocalizeResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | OneShotLocalizeResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    recon_id: str,
    type_: OneshotLocalizeV1OneshotLocalizePostType
    | Unset = OneshotLocalizeV1OneshotLocalizePostType.SIFT,
    max_num_features: int | Unset = 8192,
    use_gpu: bool | Unset = True,
    seed: int | Unset = 0,
    content_type: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | OneShotLocalizeResponse]:
    r"""Oneshot Localize

     Localize a single image against an existing reconstruction.
    Bytes-in / typed-result-out. No persistence.

    Collapses the eight-step \"upload + register + submit-localize +
    poll-job + decode\" flow to one HTTP request. The query image is
    held in memory and (briefly) on disk in a tempdir for pycolmap;
    no Image / Blob / Upload / Job row is created.

    Args:
        recon_id (str): Existing reconstruction to localize against.
        type_ (OneshotLocalizeV1OneshotLocalizePostType | Unset): Local feature extractor.
            Default: OneshotLocalizeV1OneshotLocalizePostType.SIFT.
        max_num_features (int | Unset):  Default: 8192.
        use_gpu (bool | Unset):  Default: True.
        seed (int | Unset):  Default: 0.
        content_type (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | OneShotLocalizeResponse]
    """

    kwargs = _get_kwargs(
        recon_id=recon_id,
        type_=type_,
        max_num_features=max_num_features,
        use_gpu=use_gpu,
        seed=seed,
        content_type=content_type,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    recon_id: str,
    type_: OneshotLocalizeV1OneshotLocalizePostType
    | Unset = OneshotLocalizeV1OneshotLocalizePostType.SIFT,
    max_num_features: int | Unset = 8192,
    use_gpu: bool | Unset = True,
    seed: int | Unset = 0,
    content_type: None | str | Unset = UNSET,
) -> HTTPValidationError | OneShotLocalizeResponse | None:
    r"""Oneshot Localize

     Localize a single image against an existing reconstruction.
    Bytes-in / typed-result-out. No persistence.

    Collapses the eight-step \"upload + register + submit-localize +
    poll-job + decode\" flow to one HTTP request. The query image is
    held in memory and (briefly) on disk in a tempdir for pycolmap;
    no Image / Blob / Upload / Job row is created.

    Args:
        recon_id (str): Existing reconstruction to localize against.
        type_ (OneshotLocalizeV1OneshotLocalizePostType | Unset): Local feature extractor.
            Default: OneshotLocalizeV1OneshotLocalizePostType.SIFT.
        max_num_features (int | Unset):  Default: 8192.
        use_gpu (bool | Unset):  Default: True.
        seed (int | Unset):  Default: 0.
        content_type (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | OneShotLocalizeResponse
    """

    return sync_detailed(
        client=client,
        recon_id=recon_id,
        type_=type_,
        max_num_features=max_num_features,
        use_gpu=use_gpu,
        seed=seed,
        content_type=content_type,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    recon_id: str,
    type_: OneshotLocalizeV1OneshotLocalizePostType
    | Unset = OneshotLocalizeV1OneshotLocalizePostType.SIFT,
    max_num_features: int | Unset = 8192,
    use_gpu: bool | Unset = True,
    seed: int | Unset = 0,
    content_type: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | OneShotLocalizeResponse]:
    r"""Oneshot Localize

     Localize a single image against an existing reconstruction.
    Bytes-in / typed-result-out. No persistence.

    Collapses the eight-step \"upload + register + submit-localize +
    poll-job + decode\" flow to one HTTP request. The query image is
    held in memory and (briefly) on disk in a tempdir for pycolmap;
    no Image / Blob / Upload / Job row is created.

    Args:
        recon_id (str): Existing reconstruction to localize against.
        type_ (OneshotLocalizeV1OneshotLocalizePostType | Unset): Local feature extractor.
            Default: OneshotLocalizeV1OneshotLocalizePostType.SIFT.
        max_num_features (int | Unset):  Default: 8192.
        use_gpu (bool | Unset):  Default: True.
        seed (int | Unset):  Default: 0.
        content_type (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | OneShotLocalizeResponse]
    """

    kwargs = _get_kwargs(
        recon_id=recon_id,
        type_=type_,
        max_num_features=max_num_features,
        use_gpu=use_gpu,
        seed=seed,
        content_type=content_type,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    recon_id: str,
    type_: OneshotLocalizeV1OneshotLocalizePostType
    | Unset = OneshotLocalizeV1OneshotLocalizePostType.SIFT,
    max_num_features: int | Unset = 8192,
    use_gpu: bool | Unset = True,
    seed: int | Unset = 0,
    content_type: None | str | Unset = UNSET,
) -> HTTPValidationError | OneShotLocalizeResponse | None:
    r"""Oneshot Localize

     Localize a single image against an existing reconstruction.
    Bytes-in / typed-result-out. No persistence.

    Collapses the eight-step \"upload + register + submit-localize +
    poll-job + decode\" flow to one HTTP request. The query image is
    held in memory and (briefly) on disk in a tempdir for pycolmap;
    no Image / Blob / Upload / Job row is created.

    Args:
        recon_id (str): Existing reconstruction to localize against.
        type_ (OneshotLocalizeV1OneshotLocalizePostType | Unset): Local feature extractor.
            Default: OneshotLocalizeV1OneshotLocalizePostType.SIFT.
        max_num_features (int | Unset):  Default: 8192.
        use_gpu (bool | Unset):  Default: True.
        seed (int | Unset):  Default: 0.
        content_type (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | OneShotLocalizeResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            recon_id=recon_id,
            type_=type_,
            max_num_features=max_num_features,
            use_gpu=use_gpu,
            seed=seed,
            content_type=content_type,
        )
    ).parsed
