# OpenAPI

The full OpenAPI 3.1 document for the `/v1` surface is published as a
release asset (`openapi.json`) and rendered interactively here.

```{raw} html
<div id="swagger-ui" style="margin-top:1.2rem"></div>

<link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5.18.2/swagger-ui.css" />
<script src="https://unpkg.com/swagger-ui-dist@5.18.2/swagger-ui-bundle.js" crossorigin></script>
<script src="https://unpkg.com/swagger-ui-dist@5.18.2/swagger-ui-standalone-preset.js" crossorigin></script>
<script>
  window.addEventListener("load", function () {
    const ui = SwaggerUIBundle({
      url: "/_static/openapi.json",
      dom_id: "#swagger-ui",
      presets: [SwaggerUIBundle.presets.apis, SwaggerUIStandalonePreset],
      layout: "BaseLayout",
      docExpansion: "list",
      tryItOutEnabled: false,
      defaultModelsExpandDepth: 0,
    });
    window.ui = ui;
  });
</script>
```

## Static download

- [`openapi.json`](../_static/openapi.json)

This file is regenerated on every docs build (and pinned into each
GitHub release as `openapi.json`).

## Code generation

Use it with any OpenAPI-aware generator:

```bash
# TypeScript types
npx openapi-typescript https://sfmapi.github.io/_static/openapi.json -o sfmapi.d.ts

# Full client
npx @openapitools/openapi-generator-cli generate \
    -i https://sfmapi.github.io/_static/openapi.json \
    -g python -o ./gen-python
```

Our own SDKs (`sfmapi-client` for Python and `@sfmapi/client` for
TypeScript) are hand-rolled rather than generated, but the OpenAPI
document is the source of truth either way.
