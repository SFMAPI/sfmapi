"""Shared rendering helper for CLI commands.

Lives in its own module so command modules can import it without
circling back through `cli.main` (which imports the commands).
"""

from __future__ import annotations

from typing import Any

import click


def render(ctx: click.Context, data: Any, *, table: Any = None) -> None:
    """Print `data` as JSON if `--json` was set, else as a Rich `table`
    if provided, else as `repr(data)`.
    """
    if ctx.obj.get("json"):
        import json as _json

        if hasattr(data, "model_dump"):
            click.echo(_json.dumps(data.model_dump(mode="json"), indent=2))
        elif isinstance(data, list) and data and hasattr(data[0], "model_dump"):
            click.echo(
                _json.dumps([d.model_dump(mode="json") for d in data], indent=2),
            )
        else:
            click.echo(_json.dumps(data, indent=2, default=str))
        return
    if table is not None:
        from rich.console import Console

        Console().print(table)
    else:
        click.echo(repr(data))
