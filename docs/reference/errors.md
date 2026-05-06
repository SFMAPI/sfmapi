# Error model

All errors follow [RFC 7807](https://www.rfc-editor.org/rfc/rfc7807)
`application/problem+json`:

```json
{
  "type": "https://sfmapi/errors/conflict",
  "title": "Conflict",
  "status": 409,
  "detail": "Project 'foo' already exists",
  "instance": "/v1/projects"
}
```

## Status code → exception class

| HTTP | server error class | SDK exception |
|---|---|---|
| 403 | `TenantViolationError` | `AuthError` |
| 404 | `NotFoundError` | `NotFoundError` |
| 409 | `ConflictError` | `ConflictError` |
| 413 | `QuotaExceededError` (storage) | `QuotaExceededError` |
| 422 | `ValidationError` | `ValidationError` |
| 429 | `QuotaExceededError` (rate / gpu_seconds) | `QuotaExceededError` |
| 503 | `PycolmapUnavailableError` | `PycolmapUnavailableError` |
| 507 | `StorageError` | `StorageError` |

## Server-side hierarchy

```{eval-rst}
.. automodule:: app.core.errors
   :members:
   :no-index:
```

## SDK side

```{eval-rst}
.. automodule:: sfmapi_client.errors
   :members:
   :no-index:
```
