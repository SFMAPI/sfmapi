"""Shared transport utilities: URL building, auth headers, ETag-style hashes."""

from __future__ import annotations

import hashlib
from collections.abc import Iterable
from typing import BinaryIO

CHUNK_SIZE = 1 * 1024 * 1024  # 1 MiB


def auth_headers(api_key: str | None) -> dict[str, str]:
    if not api_key:
        return {}
    return {"Authorization": f"Bearer {api_key}"}


def stream_sha256(reader: BinaryIO) -> tuple[str, int]:
    """Return (sha256, byte_count) of the stream from current position to EOF.
    The caller is responsible for resetting the stream if needed."""
    h = hashlib.sha256()
    n = 0
    while True:
        chunk = reader.read(CHUNK_SIZE)
        if not chunk:
            break
        h.update(chunk)
        n += len(chunk)
    return h.hexdigest(), n


def chunk_bytes(data: bytes, *, size: int = CHUNK_SIZE) -> Iterable[bytes]:
    for offset in range(0, len(data), size):
        yield data[offset : offset + size]
