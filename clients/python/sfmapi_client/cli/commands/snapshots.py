"""`sfmapi snapshots ...` — read sealed snapshots."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from sfmapi_client.cli._render import render


@click.group()
def snapshots() -> None:
    """Sealed-snapshot reads."""


@snapshots.command("list")
@click.argument("recon_id")
@click.pass_context
def list_(ctx: click.Context, recon_id: str) -> None:
    seqs = ctx.obj["client"].list_snapshots(recon_id)
    if ctx.obj.get("json"):
        render(ctx, {"seqs": seqs})
        return
    if not seqs:
        click.secho(f"no sealed snapshots for {recon_id}", fg="yellow")
        return
    click.echo("\n".join(f"#{s}" for s in seqs))


@snapshots.command("get")
@click.argument("recon_id")
@click.argument("seq", type=int)
@click.argument("name")
@click.option(
    "--out",
    type=click.Path(dir_okay=False, path_type=Path),
    default=None,
    help="Write to file instead of stdout. Required for binary outputs.",
)
@click.pass_context
def get(ctx: click.Context, recon_id: str, seq: int, name: str, out: Path | None) -> None:
    """Download a sealed-snapshot file (cameras.json, points.bin, ...)."""
    payload = ctx.obj["client"].read_snapshot_file(recon_id, seq, name)
    if out is not None:
        out.write_bytes(payload)
        click.secho(f"wrote {out} ({len(payload):,} bytes)", fg="green")
        return
    if name.endswith(".bin"):
        raise click.UsageError("binary output: pass --out PATH")
    sys.stdout.buffer.write(payload)
