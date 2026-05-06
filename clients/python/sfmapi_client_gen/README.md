# sfmapi-client-gen

Auto-generated typed Python SDK for [sfmapi](https://github.com/sfmapi/sfmapi).

> **Generated** — do not hand-edit. Regenerate from the repo root via:
> ```
> uv run python scripts/regen_sdk.py
> ```

## Install

```bash
pip install sfmapi-client-gen
```

## Usage

```python
from sfmapi_client_gen.client import Client
from sfmapi_client_gen.api.capabilities import capabilities_v1_capabilities_get

client = Client(base_url="http://localhost:8080")
caps_resp = capabilities_v1_capabilities_get.sync_detailed(client=client)
print(caps_resp.parsed)  # CapabilitiesOut with schema_version, backend, features
```

## Versus the hand-rolled `sfmapi-client`

This package is regenerated from the OpenAPI spec on every release. The
hand-rolled `sfmapi-client` package adds ergonomic helpers (typed
`SfmApiError` hierarchy, `Capabilities.supports()`, binary wire-format
parsers for `points.bin` / `depth_maps`, SSE event iterators, sync +
async parity). Use the generated client for raw typed access; use the
hand-rolled client when you want the ergonomic surface.

Both decode identical wire formats — the contract test suite at
`tests/contract/` in the repo replays recorded server responses
through both.

## License

Apache-2.0.
