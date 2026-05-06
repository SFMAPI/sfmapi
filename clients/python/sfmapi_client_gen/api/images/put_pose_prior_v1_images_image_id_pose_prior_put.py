from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.pose_prior import PosePrior
from ...types import Response


def _get_kwargs(
    image_id: str,
    *,
    body: PosePrior,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/v1/images/{image_id}/pose_prior".format(
            image_id=quote(str(image_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | PosePrior | None:
    if response.status_code == 200:
        response_200 = PosePrior.from_dict(response.json())

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
) -> Response[HTTPValidationError | PosePrior]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    image_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: PosePrior,
) -> Response[HTTPValidationError | PosePrior]:
    """Put Pose Prior

     Set (or replace) the PosePrior on an image.

    Args:
        image_id (str):
        body (PosePrior): Prior on a camera's ``cam_from_world`` pose.

            ``covariance`` is a 36-float row-major 6x6 matrix (rx, ry, rz, tx,
            ty, tz). Diagonal-only priors send only the six diagonal entries
            inside the 36-vector with off-diagonals zero. ``timestamp_ns`` is
            the optional nanosecond timestamp the prior corresponds to —
            needed when the same image appears at multiple times in a
            sequence (rolling shutter, video). ``imu`` is an optional IMU
            sample colocated with the pose prior.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | PosePrior]
    """

    kwargs = _get_kwargs(
        image_id=image_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    image_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: PosePrior,
) -> HTTPValidationError | PosePrior | None:
    """Put Pose Prior

     Set (or replace) the PosePrior on an image.

    Args:
        image_id (str):
        body (PosePrior): Prior on a camera's ``cam_from_world`` pose.

            ``covariance`` is a 36-float row-major 6x6 matrix (rx, ry, rz, tx,
            ty, tz). Diagonal-only priors send only the six diagonal entries
            inside the 36-vector with off-diagonals zero. ``timestamp_ns`` is
            the optional nanosecond timestamp the prior corresponds to —
            needed when the same image appears at multiple times in a
            sequence (rolling shutter, video). ``imu`` is an optional IMU
            sample colocated with the pose prior.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | PosePrior
    """

    return sync_detailed(
        image_id=image_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    image_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: PosePrior,
) -> Response[HTTPValidationError | PosePrior]:
    """Put Pose Prior

     Set (or replace) the PosePrior on an image.

    Args:
        image_id (str):
        body (PosePrior): Prior on a camera's ``cam_from_world`` pose.

            ``covariance`` is a 36-float row-major 6x6 matrix (rx, ry, rz, tx,
            ty, tz). Diagonal-only priors send only the six diagonal entries
            inside the 36-vector with off-diagonals zero. ``timestamp_ns`` is
            the optional nanosecond timestamp the prior corresponds to —
            needed when the same image appears at multiple times in a
            sequence (rolling shutter, video). ``imu`` is an optional IMU
            sample colocated with the pose prior.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | PosePrior]
    """

    kwargs = _get_kwargs(
        image_id=image_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    image_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: PosePrior,
) -> HTTPValidationError | PosePrior | None:
    """Put Pose Prior

     Set (or replace) the PosePrior on an image.

    Args:
        image_id (str):
        body (PosePrior): Prior on a camera's ``cam_from_world`` pose.

            ``covariance`` is a 36-float row-major 6x6 matrix (rx, ry, rz, tx,
            ty, tz). Diagonal-only priors send only the six diagonal entries
            inside the 36-vector with off-diagonals zero. ``timestamp_ns`` is
            the optional nanosecond timestamp the prior corresponds to —
            needed when the same image appears at multiple times in a
            sequence (rolling shutter, video). ``imu`` is an optional IMU
            sample colocated with the pose prior.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | PosePrior
    """

    return (
        await asyncio_detailed(
            image_id=image_id,
            client=client,
            body=body,
        )
    ).parsed
