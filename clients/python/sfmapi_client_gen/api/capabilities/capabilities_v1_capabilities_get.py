from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.capabilities_out import CapabilitiesOut
from ...types import Response


def _get_kwargs() -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/capabilities",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> CapabilitiesOut | None:
    if response.status_code == 200:
        response_200 = CapabilitiesOut.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[CapabilitiesOut]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[CapabilitiesOut]:
    """Capabilities

     Discovery: backend identity + feature flags this deployment exposes.

    Clients MUST hit this once at startup and cache the result for
    the duration of the connection. Use it to gate UI affordances and
    short-circuit against a 501 round-trip on unsupported operations.

    Feature names
    -------------
    The ``features`` map keys are dot-notated, mirroring AIP-style
    capability namespaces:

    - ``features.extract.{type}`` — feature extractor types
      (``sift`` | ``superpoint`` | ``aliked`` | ...).
    - ``matchers.{type}`` — per-pair matcher implementations.
    - ``pairs.{strategy}`` — pair-selection strategies
      (``exhaustive`` | ``vocabtree`` | ``retrieval`` | ...).
    - ``pipelines.{kind}`` — mapping recipes (``incremental`` |
      ``global`` | ``hierarchical`` | ``spherical``).
    - ``ba.{mode}`` — bundle-adjustment modes.
    - ``mesh.{method}`` / ``sources.{kind}`` — etc.

    Absence rule
    ------------
    A feature key absent from the map means **unsupported** by this
    deployment. Endpoints that require an unsupported feature return
    ``501 capability_unavailable`` with the canonical name in
    ``capability``. Never assume unlisted keys are ``true``; SDK shims
    use :func:`supports(name)` (Python / TS / C++) which checks for
    the exact key + truthy value.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CapabilitiesOut]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
) -> CapabilitiesOut | None:
    """Capabilities

     Discovery: backend identity + feature flags this deployment exposes.

    Clients MUST hit this once at startup and cache the result for
    the duration of the connection. Use it to gate UI affordances and
    short-circuit against a 501 round-trip on unsupported operations.

    Feature names
    -------------
    The ``features`` map keys are dot-notated, mirroring AIP-style
    capability namespaces:

    - ``features.extract.{type}`` — feature extractor types
      (``sift`` | ``superpoint`` | ``aliked`` | ...).
    - ``matchers.{type}`` — per-pair matcher implementations.
    - ``pairs.{strategy}`` — pair-selection strategies
      (``exhaustive`` | ``vocabtree`` | ``retrieval`` | ...).
    - ``pipelines.{kind}`` — mapping recipes (``incremental`` |
      ``global`` | ``hierarchical`` | ``spherical``).
    - ``ba.{mode}`` — bundle-adjustment modes.
    - ``mesh.{method}`` / ``sources.{kind}`` — etc.

    Absence rule
    ------------
    A feature key absent from the map means **unsupported** by this
    deployment. Endpoints that require an unsupported feature return
    ``501 capability_unavailable`` with the canonical name in
    ``capability``. Never assume unlisted keys are ``true``; SDK shims
    use :func:`supports(name)` (Python / TS / C++) which checks for
    the exact key + truthy value.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CapabilitiesOut
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[CapabilitiesOut]:
    """Capabilities

     Discovery: backend identity + feature flags this deployment exposes.

    Clients MUST hit this once at startup and cache the result for
    the duration of the connection. Use it to gate UI affordances and
    short-circuit against a 501 round-trip on unsupported operations.

    Feature names
    -------------
    The ``features`` map keys are dot-notated, mirroring AIP-style
    capability namespaces:

    - ``features.extract.{type}`` — feature extractor types
      (``sift`` | ``superpoint`` | ``aliked`` | ...).
    - ``matchers.{type}`` — per-pair matcher implementations.
    - ``pairs.{strategy}`` — pair-selection strategies
      (``exhaustive`` | ``vocabtree`` | ``retrieval`` | ...).
    - ``pipelines.{kind}`` — mapping recipes (``incremental`` |
      ``global`` | ``hierarchical`` | ``spherical``).
    - ``ba.{mode}`` — bundle-adjustment modes.
    - ``mesh.{method}`` / ``sources.{kind}`` — etc.

    Absence rule
    ------------
    A feature key absent from the map means **unsupported** by this
    deployment. Endpoints that require an unsupported feature return
    ``501 capability_unavailable`` with the canonical name in
    ``capability``. Never assume unlisted keys are ``true``; SDK shims
    use :func:`supports(name)` (Python / TS / C++) which checks for
    the exact key + truthy value.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CapabilitiesOut]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
) -> CapabilitiesOut | None:
    """Capabilities

     Discovery: backend identity + feature flags this deployment exposes.

    Clients MUST hit this once at startup and cache the result for
    the duration of the connection. Use it to gate UI affordances and
    short-circuit against a 501 round-trip on unsupported operations.

    Feature names
    -------------
    The ``features`` map keys are dot-notated, mirroring AIP-style
    capability namespaces:

    - ``features.extract.{type}`` — feature extractor types
      (``sift`` | ``superpoint`` | ``aliked`` | ...).
    - ``matchers.{type}`` — per-pair matcher implementations.
    - ``pairs.{strategy}`` — pair-selection strategies
      (``exhaustive`` | ``vocabtree`` | ``retrieval`` | ...).
    - ``pipelines.{kind}`` — mapping recipes (``incremental`` |
      ``global`` | ``hierarchical`` | ``spherical``).
    - ``ba.{mode}`` — bundle-adjustment modes.
    - ``mesh.{method}`` / ``sources.{kind}`` — etc.

    Absence rule
    ------------
    A feature key absent from the map means **unsupported** by this
    deployment. Endpoints that require an unsupported feature return
    ``501 capability_unavailable`` with the canonical name in
    ``capability``. Never assume unlisted keys are ``true``; SDK shims
    use :func:`supports(name)` (Python / TS / C++) which checks for
    the exact key + truthy value.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CapabilitiesOut
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
