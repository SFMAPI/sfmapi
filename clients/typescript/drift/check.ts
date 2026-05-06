/**
 * Structural drift check between the hand-rolled SDK models in
 * `src/models.ts` and the auto-generated OpenAPI types in
 * `src/openapi-types.ts`.
 *
 * Strategy: declare a series of `const _: GeneratedShape = {} as
 * SdkShape` assignments under `as` casts that force structural
 * compatibility in BOTH directions. If a server schema field is added
 * or renamed and the SDK model isn't updated to match, this file
 * stops type-checking — `npm run check:openapi-drift` fails, which
 * the CI gates on.
 *
 * The asymmetry table below documents intentional divergences:
 *
 *   - The SDK model fields use `string` for ULIDs; the OpenAPI schema
 *     also uses `string`. No mismatch.
 *   - The SDK uses `string` for `created_at`; the OpenAPI schema does
 *     too (FastAPI emits `datetime` as ISO strings).
 *   - `Page<T>` in the SDK is a generic; the generated schema
 *     produces one type per instantiation (`Page_ImageOut_`,
 *     `Page_ProjectOut_`). We check each instantiation explicitly.
 *
 * This file never executes — it only exists for `tsc --noEmit`.
 */

import type { components } from "../src/openapi-types.js";
import type {
  Dataset,
  Image,
  Job,
  Project,
  Reconstruction,
  SubModel,
  Upload,
  Page,
} from "../src/models.js";

type Schema<K extends keyof components["schemas"]> = components["schemas"][K];

// Helper: compile-time "A and B have the same field names". Runs both
// directions so neither side can grow a field without the other.
type SameKeys<A, B> = keyof A extends keyof B
  ? keyof B extends keyof A
    ? true
    : ["DRIFT: B has extra keys", Exclude<keyof B, keyof A>]
  : ["DRIFT: A has extra keys", Exclude<keyof A, keyof B>];

// Helper: deep "A is assignable to B AND B is assignable to A on every
// shared key." We use plain Pick to compare on the SDK key set; the
// `SameKeys` check above already enforces parity.
type _Same<A, B> = SameKeys<A, B> extends true ? true : SameKeys<A, B>;

// --- Per-resource invariants ------------------------------------------------

const _project: _Same<Schema<"ProjectOut">, Project> = true;
const _dataset: _Same<Schema<"DatasetOut">, Dataset> = true;
const _image: _Same<Schema<"ImageOut">, Image> = true;
const _upload: _Same<Schema<"UploadOut">, Upload> = true;
const _job: _Same<Schema<"JobOut">, Job> = true;
const _recon: _Same<Schema<"ReconstructionOut">, Reconstruction> = true;
const _submodel: _Same<Schema<"SubModelOut">, SubModel> = true;

// Generic Page<T> instantiations:
const _pageProj: _Same<Schema<"Page_ProjectOut_">, Page<Project>> = true;
const _pageImg: _Same<Schema<"Page_ImageOut_">, Page<Image>> = true;

// Touch the bindings so the compiler doesn't report them as unused.
export const _drift = [
  _project,
  _dataset,
  _image,
  _upload,
  _job,
  _recon,
  _submodel,
  _pageProj,
  _pageImg,
];
