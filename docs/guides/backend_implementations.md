# Implement a backend

sfmapi ships **no concrete SfM engine**. Real reconstructions happen
in a backend package you (or someone else) ships separately. This
page is the contract.

## The Protocol

Backends satisfy [`app.adapters.backend.SfmBackend`][prot] by
structural typing — no inheritance required, no metaclass. A backend
is any class with the right method names, signatures, and an
identity triple (`name`, `version`, `vendor`).

[prot]: ../server/adapters.md

```python
from app.adapters.backend import SfmBackend
from app.core.errors import CapabilityUnavailableError

class MyBackend:
    name = "my_backend"
    version = "0.1.0"
    vendor = "me"

    def capabilities(self) -> set[str]:
        # Advertise only what's wired. The /v1/capabilities endpoint
        # surfaces this set; clients use it to decide which stages
        # they can ask for.
        return {"features.extract", "matches.exhaustive", "ba.standard"}

    def extract_features(self, *, database_path, image_root,
                         image_list, options) -> dict:
        ...

    def match(self, *, database_path, mode, options) -> dict:
        ...

    def bundle_adjustment(self, **kw) -> dict:
        ...

    # Methods you don't support: raise CapabilityUnavailableError.
    def dense_pipeline(self, **_) -> dict:
        raise CapabilityUnavailableError(capability="dense.patch_match_stereo")

    # ...etc; see the SfmBackend Protocol for the full list.

    def runtime_versions(self) -> dict[str, str]:
        # Returned by /v1/version under backend.runtime_versions.
        # Roll any sha / version / arch into here that should
        # invalidate the cache when it changes.
        return {"engine_sha": "abc123", "cuda_arch": "120"}
```

## Registering at startup

```python
from app.adapters.registry import register_backend

register_backend("my_backend", MyBackend)
```

Then either:

- set the env var: `SFMAPI_BACKEND=my_backend`, or
- pass `name=` to `get_backend("my_backend")` for explicit selection.

A common pattern is to register from the package's `__init__.py` so
that `import my_backend` is the only thing the operator needs:

```python
# my_backend/__init__.py
from app.adapters.registry import register_backend
from .backend import MyBackend

register_backend("my_backend", MyBackend)
```

## Capability strings

The capability vocabulary is canonical and stable. Backends advertise
the subset they implement; sfmapi reads `capabilities()` once at
boot and caches the result. The full list lives in
`app.core.capabilities.ALL_KNOWN`.

Common categories:

| Category | Capability strings |
|---|---|
| Feature extraction | `features.extract.{sift, superpoint, aliked, disk, r2d2, d2net}` |
| Pair selection | `pairs.{exhaustive, sequential, spatial, vocabtree, retrieval, from_poses}` |
| Matching | `matchers.{nn-mutual, nn-ratio, superglue, lightglue, loftr, mast3r}` |
| Mapping | `map.{incremental, global, hierarchical, spherical}` |
| Bundle adjustment | `ba.{standard, two_stage, featuremetric}` |
| Dense | `dense.patch_match_stereo`, `dense.fusion`, `mesh.{poisson, delaunay}` |
| Other | `relocalize.images`, `pgo.optimize`, `triangulate.retri`, `export.{ply, nvm, txt, bin}`, `spherical.{to_cubemap, render_cubemap}` |

If you advertise a capability, the corresponding method must succeed
when called. If you don't, the method must `raise
CapabilityUnavailableError(capability=...)` so clients see a clean
501 + the capability name in the problem detail.

## What sfmapi guarantees you

- **No subprocess management for free** — workers run in a process
  the supervisor manages. Lease / heartbeat / cancellation happens
  outside your method.
- **Sealed-snapshot writes** — write your reconstruction artifacts
  under a tempdir; sfmapi atomically renames into `snapshots/{seq}/`
  and signals the API.
- **Cache-key salt** — `runtime_versions()` rolls into the cache key
  for every task. Bump any returned key on engine upgrades.
- **Tenancy isolation** — file paths and DB rows already filtered by
  `tenant_id`. Your methods only see the per-tenant workspace.

## What sfmapi does NOT do

- **Install your engine.** Bring your own pycolmap / OpenSfM /
  hloc / custom binary. Backends typically declare them as
  Python deps and let `pip install` resolve.
- **Configure CUDA.** Backends that need a GPU must check at startup
  and either work in CPU-fallback mode or raise from `__init__`.
- **Validate your dicts.** The `dict` return shape is loose; clients
  validate against `app.schemas.api.scene` if they care.

## Reference: the no-op stub

[`app.adapters.stub_backend.StubBackend`][stub] is the reference
that ships in this repo. It exists for tests, ephemeral mode, and
SDK live-server suites. Every method raises
`CapabilityUnavailableError`; `capabilities()` returns the empty
set; `runtime_versions()` returns a single `stub_version` key.

[stub]: ../server/adapters.md

Use it as a template:

```bash
cp -r vendor/your-backend-template my-backend/
# then implement the methods incrementally, advertising each
# capability only after wiring it.
```

## Testing a backend

Reuse sfmapi's contract tests against your registered backend:

```bash
uv run pytest -m "contract" --backend=my_backend
```

…where the `--backend` arg is whatever your test harness wires
through `register_backend()` in a conftest. The contract tests
assert the protocol shape, not engine semantics — they catch
"forgot to add the new method when sfmapi added one to the
Protocol" regressions.
