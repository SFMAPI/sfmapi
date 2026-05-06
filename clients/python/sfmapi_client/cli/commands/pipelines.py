"""`sfmapi pipelines ...` — recipe-style SfM jobs."""

from __future__ import annotations

import json
from pathlib import Path

import click

from sfmapi_client.cli._render import render
from sfmapi_client.models import (
    GlobalSpec,
    HierarchicalSpec,
    IncrementalSpec,
    SphericalSpec,
)

_SPEC_BY_KIND = {
    "incremental": IncrementalSpec,
    "global": GlobalSpec,
    "hierarchical": HierarchicalSpec,
    "spherical": SphericalSpec,
}


@click.group()
def pipelines() -> None:
    """Recipe-style SfM jobs."""


@pipelines.command("run")
@click.argument("project_id")
@click.option("--dataset-id", required=True)
@click.option(
    "--kind",
    type=click.Choice(tuple(_SPEC_BY_KIND), case_sensitive=False),
    default="incremental",
    show_default=True,
)
@click.option(
    "--spec-file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=None,
    help="JSON file overriding the PipelineSpec defaults.",
)
@click.pass_context
def run(
    ctx: click.Context,
    project_id: str,
    dataset_id: str,
    kind: str,
    spec_file: Path | None,
) -> None:
    """Submit a `/v1/projects/{pid}/pipelines/{kind}` job.

    The image source + database path are derived server-side from the
    dataset, so the CLI no longer needs `--image-root` / `--image`.
    """
    cls = _SPEC_BY_KIND[kind]
    if spec_file is not None:
        body = json.loads(spec_file.read_text(encoding="utf-8"))
        body.setdefault("kind", kind)
        spec = cls.model_validate(body)
    else:
        spec = cls()
    job = ctx.obj["client"].run_pipeline(
        project_id,
        dataset_id=dataset_id,
        spec=spec,
    )
    render(ctx, job)
