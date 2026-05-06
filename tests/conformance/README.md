# sfmapi conformance suite

Verifies that an HTTP server implements the contract described in
[`SFMAPI-SPEC.md`](../../SFMAPI-SPEC.md). Designed to be run against
**any** sfmapi implementation, not just the reference one.

## Run against the reference impl (in-process)

```bash
uv run pytest tests/conformance -v
```

## Run against a remote server

```bash
SFMAPI_TEST_BASE_URL=https://api.example.com \
SFMAPI_TEST_KEY=sfm_xxx \
uv run pytest tests/conformance -v
```

Or use the standalone runner:

```bash
python -m tests.conformance \
    --base-url https://api.example.com \
    --api-key sfm_xxx \
    --junit conformance.xml
```

## What it checks

| File                           | Spec sections              |
|--------------------------------|----------------------------|
| `test_meta.py`                 | §6.1, §11                  |
| `test_projects.py`             | §3.4, §3.6, §6.2           |
| `test_uploads.py`              | §3.7, §6.3                 |
| `test_datasets_images.py`      | §3.5, §6.4, §6.5           |
| `test_jobs_and_lro.py`         | §3.9, §6.6, §6.7, §9.1     |
| `test_pipelines.py`            | §6.8 (optional)            |
| `test_errors_and_caching.py`   | §3.4, §3.6, §3.10          |
| `test_links.py`                | §3.5                       |

Optional features (admin, pipelines, thumbnails, batch, etc.) `skip`
cleanly rather than fail when the target server doesn't implement
them.

## Capability detection

The `caps` fixture probes `/spec` + a few well-known paths on first
use and surfaces:

- `spec_version`, `server_name`
- `has_admin_api_keys`
- `has_pipelines`
- `has_image_thumbnail`
- `has_image_batch`
- `has_resume`
- `has_ws_jobs`
- `has_metrics`

## Conformance levels

A server that passes every non-`skipped` test in this suite is a
**conforming v1 server** under §10.

To claim **conforming + recipes** the server must additionally pass
`test_pipelines.py`. To claim **conforming + image-bytes** it must
pass `test_image_bytes_returns_payload`. (These are the named
optional capability tiers.)

## Reporting

`--junit conformance.xml` produces a JUnit-XML report you can drop
into CI dashboards. Each `<testcase classname="...">` corresponds to
a spec-section grouping; `<skipped>` entries reference the optional
feature that wasn't implemented.
