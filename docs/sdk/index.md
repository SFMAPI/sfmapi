# SDKs

Three officially-supported clients, all generated from the same
OpenAPI spec, with hand-written ergonomics shims for chunked
upload, SSE event streaming, binary points/depth/normal parsing,
typed exceptions, and `wait_for_job` / `submit_and_wait` /
`submit_and_stream` helpers.

| Language | Install | Source |
|---|---|---|
| Python | `pip install ./clients/python/sfmapi_client_gen` | [`clients/python/`](https://github.com/SFMAPI/sfmapi/tree/main/clients/python) |
| TypeScript | `npm install @sfmapi/client` | [`clients/typescript/`](https://github.com/SFMAPI/sfmapi/tree/main/clients/typescript) |
| C++17 | header-only, [`clients/cpp/`](https://github.com/SFMAPI/sfmapi/tree/main/clients/cpp) | [`clients/cpp/`](https://github.com/SFMAPI/sfmapi/tree/main/clients/cpp) |

All three speak the same `/v1` REST API and share the same model
shapes. Wire fixtures in `tests/contract/fixtures/` are replayed
through every SDK, so a server change ripples to all three or fails
CI immediately.

A **deprecated hand-rolled Python SDK** at
`clients/python/sfmapi_client/` ships in parallel for now; new
consumers should pick the generated SDK above.

## Python

```{include} ../../clients/python/README.md
```

## TypeScript

```{include} ../../clients/typescript/README.md
```

## C++

```{include} ../../clients/cpp/README.md
```

