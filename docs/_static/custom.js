// sfmapi docs — small client-side enhancements.
//
// 1. Tag the API reference page with a body class so its scoped styles
//    in custom.css apply (extra typography flourishes, numbered section
//    markers, denser tables).
// 2. Decorate inline code that starts with an HTTP verb so it renders
//    as a tiny tracked tag inside the API reference tables.
//
// Everything is progressive enhancement; the page reads fine without
// JS.
(function () {
    const path = location.pathname;
    const isApiRef = /\/reference\/api(\.html)?$/.test(path) ||
                     path.endsWith("/reference/api");

    if (!isApiRef) return;
    document.body.classList.add("api-reference");

    const VERBS = new Set([
        "GET", "POST", "PATCH", "PUT", "DELETE", "HEAD", "OPTIONS",
    ]);

    function tag(tok) {
        const cls = `http-verb http-${tok.toLowerCase()}`;
        return `<code class="${cls}">${tok}</code>`;
    }

    document.querySelectorAll(
        "article table.docutils tbody tr td:first-child"
    ).forEach((td) => {
        // Markdown tables in MyST render the cell as <td><p>GET</p></td>.
        // We only touch cells whose visible text is exactly a verb (or
        // a slash-separated list of verbs).
        const txt = td.textContent.trim();
        if (!txt) return;
        const tokens = txt.split("/").map((t) => t.trim());
        if (!tokens.length || !tokens.every((t) => VERBS.has(t))) return;

        const inner =
            tokens.length === 1
                ? tag(tokens[0])
                : tokens
                      .map(tag)
                      .join(' <span class="http-verb-sep">/</span> ');
        // Replace the cell's HTML — keeps any wrapping <p> Sphinx
        // emits but swaps its contents.
        const p = td.querySelector("p");
        if (p) p.innerHTML = inner;
        else td.innerHTML = inner;
    });
})();
