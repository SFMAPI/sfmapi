"""Admin endpoints — issue/revoke API keys.

Mounted at `/v1/admin/...`. In v0 these are unauthenticated when
`auth_mode=none` (single-user dev). Production deployments must front
this with an admin-only auth layer (e.g., a deploy-time master key).
"""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.db.models import ApiKey
from app.db.session import get_db
from app.services import api_key_service

router = APIRouter(prefix="/admin", tags=["admin"])


class IssueKeyBody(BaseModel):
    tenant_id: str
    name: str | None = None


class IssueKeyResponse(BaseModel):
    raw_key: str
    api_key_id: str
    tenant_id: str
    name: str | None


class ApiKeyOut(BaseModel):
    api_key_id: str
    tenant_id: str
    name: str | None
    revoked: bool


@router.post(
    "/api-keys",
    response_model=IssueKeyResponse,
    status_code=status.HTTP_201_CREATED,
)
async def issue(
    body: IssueKeyBody,
    session: AsyncSession = Depends(get_db),
) -> IssueKeyResponse:
    """Mint a fresh API key bound to a tenant.

    Returns the raw key in ``raw_key`` exactly once — only a salted
    hash is persisted, so callers MUST capture the value here. Use
    the key as the ``Bearer`` token in ``Authorization`` against any
    tenant-scoped route once ``auth_mode != "none"``.

    WARNING — auth_mode=none default
    --------------------------------
    Until ``SFMAPI_AUTH_MODE`` is flipped to ``api_key``, this route
    is itself unauthenticated. Production deployments MUST front
    ``/v1/admin/...`` with an admin-only auth layer (deploy-time
    master key, mesh-level mTLS, infra-network-only). See ``L2`` in
    ``decisions.md``.
    """
    raw, row = await api_key_service.issue_key(session, tenant_id=body.tenant_id, name=body.name)
    return IssueKeyResponse(
        raw_key=raw,
        api_key_id=row.api_key_id,
        tenant_id=row.tenant_id,
        name=row.name,
    )


@router.delete("/api-keys/{api_key_id}", response_model=ApiKeyOut)
async def revoke(
    api_key_id: str,
    session: AsyncSession = Depends(get_db),
) -> ApiKeyOut:
    """Revoke a previously-issued API key.

    Soft-delete: the row stays for audit, ``revoked_at`` is stamped
    and ``revoked=true`` shipped on the next read. Subsequent auth
    attempts with that key will fail. Idempotent — revoking an
    already-revoked key is a 200 no-op.

    See WARNING on ``POST /v1/admin/api-keys`` — this route is
    unauthenticated when ``auth_mode=none`` (the dev default).
    """
    row = await session.get(ApiKey, api_key_id)
    if row is None:
        raise NotFoundError(f"ApiKey {api_key_id} not found")
    if row.revoked_at is None:
        row.revoked_at = datetime.now(UTC)
        await session.flush()
    return ApiKeyOut(
        api_key_id=row.api_key_id,
        tenant_id=row.tenant_id,
        name=row.name,
        revoked=True,
    )


@router.get("/api-keys", response_model=list[ApiKeyOut])
async def list_keys(session: AsyncSession = Depends(get_db)) -> list[ApiKeyOut]:
    """List every API key on file (active + revoked).

    Raw-key material is NEVER returned — use :func:`issue` and capture
    the value at creation time. Ordered by ``created_at`` ascending.

    See WARNING on ``POST /v1/admin/api-keys`` — this route is
    unauthenticated when ``auth_mode=none`` (the dev default).
    """
    rows = (await session.execute(select(ApiKey).order_by(ApiKey.created_at))).scalars().all()
    return [
        ApiKeyOut(
            api_key_id=r.api_key_id,
            tenant_id=r.tenant_id,
            name=r.name,
            revoked=r.revoked_at is not None,
        )
        for r in rows
    ]
