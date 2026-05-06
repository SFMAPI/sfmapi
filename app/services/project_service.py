"""Project CRUD."""

from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ConflictError, NotFoundError
from app.db.models import Project


async def create_project(
    session: AsyncSession, *, tenant_id: str, name: str, description: str | None = None
) -> Project:
    p = Project(tenant_id=tenant_id, name=name, description=description)
    session.add(p)
    try:
        await session.flush()
    except IntegrityError as e:
        await session.rollback()
        raise ConflictError(f"Project {name!r} already exists") from e
    return p


async def get_project(session: AsyncSession, *, tenant_id: str, project_id: str) -> Project:
    stmt = select(Project).where(Project.tenant_id == tenant_id, Project.project_id == project_id)
    result = await session.execute(stmt)
    p = result.scalar_one_or_none()
    if p is None:
        raise NotFoundError(f"Project {project_id} not found")
    return p


async def list_projects(
    session: AsyncSession,
    *,
    tenant_id: str,
    page_size: int = 50,
    page_token: str | None = None,
) -> tuple[list[Project], str | None]:
    stmt = select(Project).where(Project.tenant_id == tenant_id).order_by(Project.project_id)
    if page_token:
        stmt = stmt.where(Project.project_id > page_token)
    stmt = stmt.limit(page_size + 1)
    result = await session.execute(stmt)
    rows = list(result.scalars().all())
    next_page_token = None
    if len(rows) > page_size:
        next_page_token = rows[page_size - 1].project_id
        rows = rows[:page_size]
    return rows, next_page_token


async def patch_project(
    session: AsyncSession,
    *,
    tenant_id: str,
    project_id: str,
    updates: dict,
) -> Project:
    if not updates:
        return await get_project(session, tenant_id=tenant_id, project_id=project_id)
    p = await get_project(session, tenant_id=tenant_id, project_id=project_id)
    allowed = {"name", "description"}
    for k, v in updates.items():
        if k in allowed:
            setattr(p, k, v)
    try:
        await session.flush()
    except IntegrityError as e:
        await session.rollback()
        raise ConflictError("Project name conflict on update") from e
    return p


async def delete_project(session: AsyncSession, *, tenant_id: str, project_id: str) -> None:
    p = await get_project(session, tenant_id=tenant_id, project_id=project_id)
    await session.execute(delete(Project).where(Project.project_id == p.project_id))
