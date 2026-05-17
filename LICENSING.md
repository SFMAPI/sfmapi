# Licensing

> **Not legal advice.** This document explains the project's licensing
> *intent* for integrators. The dual-license offer in §3 is a
> placeholder pending counsel and a contributor agreement — it is not
> yet an active commercial offer. Consult a lawyer for your situation.

sfmapi is licensed under the **GNU Affero General Public License,
version 3 or later (AGPL-3.0-or-later)**. This applies uniformly to:

- the server (`sfmapi`),
- every backend plugin (`sfmapi_colmap_cli`, `sfmapi_pycolmap`,
  `sfmapi_colmap`, `sfmapi_hloc`, `sfmapi_realityscan`,
  `sfmapi_instantsfm` — wrapper is plain AGPL; sfmapi's commercial
  license just doesn't extend to it because its upstream is
  CC-BY-NC, see below — `sfmapi_spheresfm`),
- all three SDKs (Python, TypeScript, C++),
- the benchmark/conformance tools (`sfmapi-bench`).

Bundled third-party engines keep their own upstream licenses, recorded
per plugin under `LICENSES/` (e.g. COLMAP is BSD-3-Clause). Those
licenses govern the upstream code; the AGPL governs *this project's*
code that wraps it.

### `sfmapi_instantsfm` and its CC-BY-NC upstream

**`sfmapi_instantsfm`** wraps upstream InstantSfM
(`cre185/InstantSfM`), which upstream licenses **CC-BY-NC-4.0 —
non-commercial**.

The framing matters, so it is stated precisely:

- **The wrapper + SDK material in `sfmapi_instantsfm` is plain
  AGPL-3.0-or-later, with no additional restrictions.** sfmapi does
  **not** add a non-commercial term to it — doing so would be
  incoherent (AGPLv3 §7 does not permit adding a field-of-use
  restriction, which is why CC-BY-NC and the GPL family are
  incompatible). The AGPL grant on this wrapper is unrestricted, like
  every other plugin.
- **The non-commercial limitation is upstream InstantSfM's, not
  sfmapi's.** It binds whoever *operates* InstantSfM. Wrapping it
  neither adds nor removes that obligation; it is independent of
  sfmapi's license. The published package ships only the wrapper and
  references the upstream as a git submodule — it does not
  redistribute the NC source.
- **sfmapi simply does not extend its §3 commercial / dual license to
  this plugin.** That is a statement about the scope of *sfmapi's
  offer*, not a prohibition imposed on you: a commercial sfmapi
  license cannot usefully cover a plugin whose upstream is
  non-commercial, so it doesn't. Nothing in a commercial deployment
  should depend on `sfmapi_instantsfm`, because the **upstream**
  CC-BY-NC term — not any sfmapi term — would bar that operator's use.

Net: use the wrapper under AGPL freely; whether you may run InstantSfM
through it for commercial advantage is governed entirely by upstream
CC-BY-NC-4.0, on you as the operator. This is the coherent resolution
of the "AGPL + commercial vs. an NC upstream" question — not a defect,
and not an sfmapi-imposed non-commercial clause.

## 1. What the AGPL obligates — by integration shape

How you integrate determines whether your code becomes AGPL-obligated.
Be honest with yourself about which row you are in:

| You... | AGPL reaches your code? |
|---|---|
| Fork or modify sfmapi and run it as a network service | **Yes** — §13 requires you to offer your users the *modified sfmapi's* Corresponding Source. |
| `import` sfmapi in-process / write a backend plugin against `app.adapters.backend` and register via `register_backend(...)` | **Yes** — your plugin is a work based on the Program; it must be AGPL-compatible. The Protocol header carries an explicit SPDX notice for this reason. |
| Import an sfmapi SDK into your client | **Likely** — the SDK source is AGPL; linking it into your client extends the obligation. (The wire protocol itself is not copyrightable; an integrator who reimplements the HTTP calls from scratch escapes this.) |
| Run **stock, unmodified** sfmapi as a separate process and call its REST API over HTTP from a separate program | **No** — an arm's-length program communicating through a published network protocol is not a derivative work. No copyleft license reaches this; this is a property of copyright law, not a gap in this project. |

The blessed extension path is the **in-process plugin** (row 2), not
the arm's-length REST client (row 4) — by design, because that is the
path under which contributions and improvements flow back.

## 2. If you cannot meet the AGPL obligation

If your use puts you in an "AGPL reaches your code" row and you are
unable or unwilling to release your derived/combined work under an
AGPL-compatible license, you must **not** deploy it. Running stock
unmodified sfmapi behind your own arm's-length service (row 4) remains
available to you without source obligations on *your* separate code —
but note you still must not strip or relicense sfmapi itself.

## 3. Commercial / dual licensing — *intent, pending counsel*

The project intends to offer a **dual license**: AGPL-3.0-or-later
**OR** a separate commercial license for organizations that cannot
accept AGPL terms for their derived/combined work. This converts
"cannot open-source" into "open-source **or** purchase a license"
rather than leaving non-compliant use with no lawful path.

This requires (and does not yet have): a contributor license
agreement so the project holds the rights to relicense, and
counsel-drafted commercial terms. Until both exist, **AGPL-3.0-or-later
is the only license on offer.** Do not rely on a commercial option
being available yet.

## 4. Contributing

By contributing you agree your contribution is licensed under
AGPL-3.0-or-later. A formal CLA (prerequisite for §3) will be added;
contributions made before it lands will be solicited for re-sign or
treated as inbound=outbound AGPL.
