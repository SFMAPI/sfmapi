# Authentication

sfmapi has two authentication modes selected by the
`SFMAPI_AUTH_MODE` environment variable.

## `auth_mode=none` (default — dev / single-tenant)

Every request resolves to the `default` tenant. No `Authorization`
header is required; admin routes are open. Use this for local
development, single-user deployments, and the ephemeral mode demo
(`SFMAPI_EPHEMERAL=true`).

Operationally this is the equivalent of "trust whatever's on the
other side of the socket" — terminate at a reverse proxy or
front-end auth layer if you need a perimeter.

## `auth_mode=api_key` (multi-tenant)

Every non-public request must carry a bearer API key.

```http
Authorization: Bearer sfm_<26-char-ULID>_<random>
```

Public routes (no key required): `GET /healthz`, `GET /readyz`,
`GET /version`, `GET /spec`, `GET /metrics`.

Keys are scoped to a single `tenant_id` and resolved on every
request through `app.core.tenancy.current_tenant`. Cross-tenant
reads / writes return `403 tenant_violation` per
[RFC 7807][rfc7807].

[rfc7807]: https://www.rfc-editor.org/rfc/rfc7807

### Issuing keys

Under `auth_mode=none` the admin endpoints are open; under
`auth_mode=api_key` an existing operator key is required to mint
new ones.

```bash
# Mint a new key (returns the raw key ONCE — store it).
curl -X POST http://localhost:8000/v1/admin/api-keys \
     -H "Authorization: Bearer $OPERATOR_KEY" \
     -d '{"tenant_id": "acme", "name": "ci-bot"}'

# List keys (raw_key field is null for non-just-issued rows).
curl http://localhost:8000/v1/admin/api-keys \
     -H "Authorization: Bearer $OPERATOR_KEY"

# Revoke (returns the row with revoked_at set; key stops working).
curl -X DELETE http://localhost:8000/v1/admin/api-keys/$KEY_ID \
     -H "Authorization: Bearer $OPERATOR_KEY"
```

`raw_key` is the only time you see the secret. The DB stores a
content-addressed digest; lose the raw key, mint a new one.

## Tenant boundaries

The web layer never trusts a caller-provided `tenant_id` — it pulls
the tenant from `current_tenant()` and adds it to every query in
the service layer. A row that exists under a different tenant looks
identical to "not present" (404), per
[L2](../guides/decisions.md#locked-decisions).

For implementation details (Postgres RLS proposal etc.) see
[multitenancy](../guides/multitenancy.md) and the
[Postgres RLS proposal](../guides/rls_postgres_tenancy_proposal.md).

## SDK usage

All three SDKs accept an `api_key` parameter (or env var):

```python
# Python
from sfmapi_client_gen import Client
client = Client(base_url="https://api.example.com", token="sfm_...")
```

```ts
// TypeScript
import { createSfmApiClient } from "@sfmapi/client/generated";
const client = createSfmApiClient({
  baseUrl: "https://api.example.com",
  apiKey: process.env.SFMAPI_KEY,
});
```

```cpp
// C++
sfmapi::Client client({"https://api.example.com", api_key, transport});
```
