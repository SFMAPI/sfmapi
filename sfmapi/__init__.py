"""Public Python API for sfmapi extensions.

Backend packages should import from this package instead of the server's
internal ``app`` package. The ``app`` package remains the implementation
detail that powers the FastAPI service.
"""

from app import __version__

__all__ = ["__version__"]
