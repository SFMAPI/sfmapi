"""`sfmapi health` and `sfmapi version`."""

from __future__ import annotations

import click

from sfmapi_client.cli._render import render


@click.group()
def health() -> None:
    """Server health + version."""


@health.command("check")
@click.pass_context
def check(ctx: click.Context) -> None:
    """GET /healthz."""
    body = ctx.obj["client"].healthz()
    render(ctx, body)


@health.command("version")
@click.pass_context
def version(ctx: click.Context) -> None:
    """GET /version."""
    body = ctx.obj["client"].version()
    if ctx.obj.get("json"):
        render(ctx, body)
        return
    from rich.table import Table

    t = Table(title="sfmapi version", show_header=False)
    for k, v in body.model_dump().items():
        t.add_row(k, str(v))
    render(ctx, body, table=t)
