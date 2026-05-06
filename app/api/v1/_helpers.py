"""Web-layer helpers shared across v1 routes.

These belong in the API layer (not in ``app/schemas/api/``) because
they construct FastAPI ``Response`` objects — schemas modules are
intentionally kept Pydantic-only so workers and the CLI can import
the wire types without pulling FastAPI into their process.
"""

from __future__ import annotations

from fastapi import status
from fastapi.responses import JSONResponse

from app.schemas.api.jobs import JobAcceptedResponse


def accepted_response(body: JobAcceptedResponse) -> JSONResponse:
    """Wrap a :class:`JobAcceptedResponse` as the canonical 202 envelope.

    Every job-submitting route returns 202 + a ``Location`` header
    pointing at ``GET /v1/jobs/{job_id}``. Centralizing the
    construction keeps the wire shape consistent and lets future
    additions (Link header, retry-after, request-id echo) land in
    one place.
    """
    return JSONResponse(
        body.model_dump(),
        status_code=status.HTTP_202_ACCEPTED,
        headers={"Location": f"/v1/jobs/{body.job_id}"},
    )
