"""runtime_version row management."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings, runtime_version_tuple
from app.db.models import RuntimeVersion


async def ensure_runtime_version(
    session: AsyncSession, settings: Settings | None = None
) -> RuntimeVersion:
    s = settings or get_settings()
    tup = runtime_version_tuple(s)
    stmt = select(RuntimeVersion).where(
        RuntimeVersion.colmap_sha == tup[0],
        RuntimeVersion.baxx_sha == tup[1],
        RuntimeVersion.cudss_ver == tup[2],
        RuntimeVersion.cuda_arch == tup[3],
        RuntimeVersion.sam_model_sha == tup[4],
        RuntimeVersion.seed == tup[5],
    )
    result = await session.execute(stmt)
    row = result.scalar_one_or_none()
    if row is not None:
        return row
    row = RuntimeVersion(
        colmap_sha=tup[0],
        baxx_sha=tup[1],
        cudss_ver=tup[2],
        cuda_arch=tup[3],
        sam_model_sha=tup[4],
        seed=tup[5],
    )
    session.add(row)
    await session.flush()
    return row
