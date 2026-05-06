// Replays the contract fixtures recorded by the Python suite
// (`tests/contract/fixtures/*.json`) through the TypeScript SDK's
// types and assertions. Catches semantic drift the static
// type-shape diff in `drift/check.ts` misses — for instance, the
// server adding/removing a discriminator value on a tagged union.

import { describe, expect, it } from "vitest";
import { readFileSync, readdirSync, existsSync } from "node:fs";
import { join, resolve } from "node:path";

import {
  supports,
  type Capabilities,
  type Project,
  type Dataset,
  type Page,
  type HealthResponse,
  type VersionResponse,
} from "../src/index.js";

const FIXTURE_DIR = resolve(__dirname, "../../../tests/contract/fixtures");

function load<T>(name: string): T {
  const p = join(FIXTURE_DIR, `${name}.json`);
  return JSON.parse(readFileSync(p, "utf-8")) as T;
}

const haveFixtures = existsSync(FIXTURE_DIR) &&
  readdirSync(FIXTURE_DIR).some((f) => f.endsWith(".json"));

describe.skipIf(!haveFixtures)("contract: TS SDK decodes Python fixtures", () => {
  it("capabilities carries schema_version + features", () => {
    const caps = load<Capabilities>("capabilities");
    expect(caps.schema_version).toBe(1);
    expect(caps.backend.name).toBeTruthy();
    expect(typeof caps.features).toBe("object");
    // supports() helper still works on the round-tripped payload.
    expect(typeof supports(caps, "spec.read")).toBe("boolean");
  });

  it("healthz body has status field", () => {
    const h = load<HealthResponse>("healthz");
    expect(h.status).toBeTruthy();
  });

  it("version body has expected runtime fields", () => {
    const v = load<VersionResponse>("version");
    expect(v.sfmapi).toBeTruthy();
    // `backend` is optional — present when a backend is registered.
    if (v.backend) {
      expect(typeof v.backend.name).toBe("string");
      expect(typeof v.backend.version).toBe("string");
    }
  });

  it("project_get and project_create are Project-shaped", () => {
    const p1 = load<Project>("project_get");
    const p2 = load<Project>("project_create");
    for (const p of [p1, p2]) {
      expect(p.project_id).toMatch(/^[0-9A-Z]{26}$/);
      expect(p.tenant_id).toBeTruthy();
      expect(p.name).toBeTruthy();
      expect(p.created_at).toBeTruthy();
    }
  });

  it("project_list is a Page<Project>", () => {
    const list = load<Page<Project>>("project_list");
    expect(Array.isArray(list.items)).toBe(true);
    for (const item of list.items) {
      expect(item.project_id).toMatch(/^[0-9A-Z]{26}$/);
    }
  });

  it("dataset_create is Dataset-shaped", () => {
    const d = load<Dataset>("dataset_create");
    expect(d.dataset_id).toMatch(/^[0-9A-Z]{26}$/);
    expect(d.project_id).toMatch(/^[0-9A-Z]{26}$/);
    expect(d.name).toBeTruthy();
    expect(d.camera_model).toBeTruthy();
  });

  it("spec endpoint advertises sfmapi", () => {
    const s = load<{ spec: string; spec_version: string; openapi_url: string }>("spec");
    expect(s.spec).toBe("sfmapi");
    expect(s.spec_version).toBeTruthy();
    expect(s.openapi_url).toBeTruthy();
  });

  it("upload_init has open state and zero received bytes", () => {
    const u = load<{
      upload_id: string;
      state: string;
      expected_size: number;
      received_bytes: number;
    }>("upload_init");
    expect(u.upload_id).toMatch(/^[0-9A-Z]{26}$/);
    expect(u.state).toBe("open");
    expect(u.received_bytes).toBe(0);
    expect(u.expected_size).toBeGreaterThan(0);
  });

  it("404 envelopes are RFC7807-shaped for both project + dataset", () => {
    const proj = load<{ status: number; title: string; detail: string }>(
      "error_404_project_missing",
    );
    const ds = load<{ status: number; title: string; detail: string }>(
      "error_404_dataset_missing",
    );
    for (const body of [proj, ds]) {
      expect(body.status).toBe(404);
      expect(body.title).toBeTruthy();
      expect(body.detail).toBeTruthy();
    }
  });

  it("422 validation envelope is RFC 7807 with errors list", () => {
    // sfmapi wraps Pydantic field errors in problem+json so the wire
    // shape stays consistent. `detail` is a human summary; the
    // structured per-field errors are preserved under `errors`.
    const v = load<{
      type: string;
      title: string;
      status: number;
      detail: string;
      errors: { loc: unknown[]; msg: string }[];
    }>("error_422_validation");
    expect(v.status).toBe(422);
    expect(typeof v.detail).toBe("string");
    expect(Array.isArray(v.errors)).toBe(true);
    expect(v.errors.length).toBeGreaterThan(0);
    for (const e of v.errors) {
      expect(Array.isArray(e.loc)).toBe(true);
      expect(typeof e.msg).toBe("string");
    }
  });

  it("job_accepted_features envelope has job_id + task_ids", () => {
    const j = load<{ job_id: string; task_ids: string[] }>("job_accepted_features");
    expect(j.job_id).toMatch(/^[0-9A-Z]{26}$/);
    expect(Array.isArray(j.task_ids)).toBe(true);
    expect(j.task_ids.length).toBeGreaterThanOrEqual(1);
    for (const t of j.task_ids) {
      expect(t).toMatch(/^[0-9A-Z]{26}$/);
    }
  });

  it("snapshot_list_empty envelope has empty seqs + null latest link", () => {
    const s = load<{ seqs: number[]; _links?: { latest: unknown } }>("snapshot_list_empty");
    expect(s.seqs).toEqual([]);
    expect(s._links?.latest).toBeNull();
  });
});
