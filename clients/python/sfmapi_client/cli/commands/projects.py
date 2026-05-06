"""`sfmapi projects ...`."""

from __future__ import annotations

import click

from sfmapi_client.cli._render import render


@click.group()
def projects() -> None:
    """Projects CRUD."""


@projects.command("create")
@click.argument("name")
@click.option("--description", default=None)
@click.pass_context
def create(ctx: click.Context, name: str, description: str | None) -> None:
    p = ctx.obj["client"].create_project(name, description=description)
    render(ctx, p)


@projects.command("list")
@click.option("--page-size", type=int, default=50)
@click.option("--page-token", default=None)
@click.pass_context
def list_(ctx: click.Context, page_size: int, page_token: str | None) -> None:
    page = ctx.obj["client"].list_projects(page_size=page_size, page_token=page_token)
    if ctx.obj.get("json"):
        render(ctx, page)
        return
    from rich.table import Table

    t = Table(title=f"projects (page_size={page_size})")
    t.add_column("project_id", style="cyan")
    t.add_column("name")
    t.add_column("tenant_id", style="dim")
    t.add_column("created_at", style="dim")
    for row in page.items:
        t.add_row(row.project_id, row.name, row.tenant_id, str(row.created_at))
    render(ctx, page.items, table=t)


@projects.command("get")
@click.argument("project_id")
@click.pass_context
def get(ctx: click.Context, project_id: str) -> None:
    render(ctx, ctx.obj["client"].get_project(project_id))


@projects.command("delete")
@click.argument("project_id")
@click.confirmation_option(prompt="Delete project (and its datasets)?")
@click.pass_context
def delete(ctx: click.Context, project_id: str) -> None:
    ctx.obj["client"].delete_project(project_id)
    click.echo(f"deleted {project_id}")
