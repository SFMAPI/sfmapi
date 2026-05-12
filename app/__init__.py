"""sfmapi - generic HTTP/REST API for Structure-from-Motion tasks.

Backend-agnostic: any SfM engine or native tool wrapper implementing
the appropriate protocol in :mod:`sfmapi.backends` can power the
wire surface. This package ships **no concrete backend**;
implementations (pycolmap, OpenSfM, hloc, vendor CLIs, custom forks)
live in separate repositories and register themselves at app startup
via :func:`sfmapi.runtime.register_backend`. A no-op
:class:`app.adapters.stub_backend.StubBackend` is bundled for tests
and the ``SFMAPI_EPHEMERAL=true`` demo runtime.
"""

__version__ = "0.0.1"
