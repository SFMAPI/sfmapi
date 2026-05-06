from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.bulk_set_pose_priors_v1_datasets_dataset_id_pose_priors_put_body import (
    BulkSetPosePriorsV1DatasetsDatasetIdPosePriorsPutBody,
)
from ...models.http_validation_error import HTTPValidationError
from ...models.pose_priors_bulk_write_response import PosePriorsBulkWriteResponse
from ...types import Response


def _get_kwargs(
    dataset_id: str,
    *,
    body: BulkSetPosePriorsV1DatasetsDatasetIdPosePriorsPutBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/v1/datasets/{dataset_id}/pose_priors".format(
            dataset_id=quote(str(dataset_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | PosePriorsBulkWriteResponse | None:
    if response.status_code == 200:
        response_200 = PosePriorsBulkWriteResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | PosePriorsBulkWriteResponse]:
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
    body: BulkSetPosePriorsV1DatasetsDatasetIdPosePriorsPutBody,
) -> Response[HTTPValidationError | PosePriorsBulkWriteResponse]:
    """Bulk Set Pose Priors

     Bulk-set PosePriors for the dataset. Body is `{image_id: PosePrior}`.
    Existing priors for image_ids not in the body are left untouched —
    use `DELETE /v1/images/{image_id}/pose_prior` to clear individuals.

    Args:
        dataset_id (str):
        body (BulkSetPosePriorsV1DatasetsDatasetIdPosePriorsPutBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | PosePriorsBulkWriteResponse]
    """

    kwargs = _get_kwargs(
        dataset_id=dataset_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    dataset_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: BulkSetPosePriorsV1DatasetsDatasetIdPosePriorsPutBody,
) -> HTTPValidationError | PosePriorsBulkWriteResponse | None:
    """Bulk Set Pose Priors

     Bulk-set PosePriors for the dataset. Body is `{image_id: PosePrior}`.
    Existing priors for image_ids not in the body are left untouched —
    use `DELETE /v1/images/{image_id}/pose_prior` to clear individuals.

    Args:
        dataset_id (str):
        body (BulkSetPosePriorsV1DatasetsDatasetIdPosePriorsPutBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | PosePriorsBulkWriteResponse
    """

    return sync_detailed(
        dataset_id=dataset_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    dataset_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: BulkSetPosePriorsV1DatasetsDatasetIdPosePriorsPutBody,
) -> Response[HTTPValidationError | PosePriorsBulkWriteResponse]:
    """Bulk Set Pose Priors

     Bulk-set PosePriors for the dataset. Body is `{image_id: PosePrior}`.
    Existing priors for image_ids not in the body are left untouched —
    use `DELETE /v1/images/{image_id}/pose_prior` to clear individuals.

    Args:
        dataset_id (str):
        body (BulkSetPosePriorsV1DatasetsDatasetIdPosePriorsPutBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | PosePriorsBulkWriteResponse]
    """

    kwargs = _get_kwargs(
        dataset_id=dataset_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    dataset_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: BulkSetPosePriorsV1DatasetsDatasetIdPosePriorsPutBody,
) -> HTTPValidationError | PosePriorsBulkWriteResponse | None:
    """Bulk Set Pose Priors

     Bulk-set PosePriors for the dataset. Body is `{image_id: PosePrior}`.
    Existing priors for image_ids not in the body are left untouched —
    use `DELETE /v1/images/{image_id}/pose_prior` to clear individuals.

    Args:
        dataset_id (str):
        body (BulkSetPosePriorsV1DatasetsDatasetIdPosePriorsPutBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | PosePriorsBulkWriteResponse
    """

    return (
        await asyncio_detailed(
            dataset_id=dataset_id,
            client=client,
            body=body,
        )
    ).parsed
