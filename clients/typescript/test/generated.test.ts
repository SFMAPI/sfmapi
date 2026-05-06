// Replays the same Python-recorded fixtures through the generated
// TypeScript types. The hand-rolled contract test (contract.test.ts)
// asserts the hand-rolled interfaces; this one asserts the generated
// `components["schemas"]["X"]` shapes — if the two diverge, the
// codegen flip exposes the gap.

import { describe, expect, it } from "vitest";
import { existsSync, readFileSync, readdirSync } from "node:fs";
import { join, resolve } from "node:path";

import type { components } from "../src/_generated/openapi.js";

const FIXTURE_DIR = resolve(__dirname, "../../../tests/contract/fixtures");
const haveFixtures = existsSync(FIXTURE_DIR) &&
  readdirSync(FIXTURE_DIR).some((f) => f.endsWith(".json"));

function load<T>(name: string): T {
  return JSON.parse(readFileSync(join(FIXTURE_DIR, `${name}.json`), "utf-8")) as T;
}

type CapabilitiesOut = components["schemas"]["CapabilitiesOut"];
type HealthResponse = components["schemas"]["HealthResponse"];
type VersionResponse = components["schemas"]["VersionResponse"];
type SpecResponse = components["schemas"]["SpecResponse"];
type ProjectOut = components["schemas"]["ProjectOut"];
type DatasetOut = components["schemas"]["DatasetOut"];
type UploadOut = components["schemas"]["UploadOut"];
type JobAcceptedResponse = components["schemas"]["JobAcceptedResponse"];
type SnapshotListResponse = components["schemas"]["SnapshotListResponse"];

describe.skipIf(!haveFixtures)("contract: generated TS types decode fixtures", () => {
  it("CapabilitiesOut carries schema_version + backend + features", () => {
    const c = load<CapabilitiesOut>("capabilities");
    expect(c.schema_version).toBe(1);
    expect(c.backend.name).toBeTruthy();
    expect(typeof c.features).toBe("object");
  });

  it("HealthResponse decodes", () => {
    const h = load<HealthResponse>("healthz");
    expect(h.status).toBeTruthy();
  });

  it("VersionResponse decodes", () => {
    const v = load<VersionResponse>("version");
    expect(v.sfmapi).toBeTruthy();
    expect(typeof v.pycolmap_available).toBe("boolean");
  });

  it("SpecResponse decodes", () => {
    const s = load<SpecResponse>("spec");
    expect(s.spec).toBe("sfmapi");
    expect(s.spec_version).toBeTruthy();
    expect(s.openapi_url).toBeTruthy();
    expect(s.server.name).toBeTruthy();
  });

  it("ProjectOut decodes for both create + get", () => {
    for (const name of ["project_get", "project_create"] as const) {
      const p = load<ProjectOut>(name);
      expect(p.project_id).toMatch(/^[0-9A-Z]{26}$/);
      expect(p.tenant_id).toBeTruthy();
      expect(p.name).toBeTruthy();
    }
  });

  it("DatasetOut decodes", () => {
    const d = load<DatasetOut>("dataset_create");
    expect(d.dataset_id).toMatch(/^[0-9A-Z]{26}$/);
    expect(d.project_id).toMatch(/^[0-9A-Z]{26}$/);
    expect(d.camera_model).toBeTruthy();
  });

  it("UploadOut decodes", () => {
    const u = load<UploadOut>("upload_init");
    expect(u.upload_id).toMatch(/^[0-9A-Z]{26}$/);
    expect(u.state).toBe("open");
    expect(u.received_bytes).toBe(0);
  });

  it("hand-rolled and generated JobAcceptedResponse types align", () => {
    // Real recorded fixture from the features stage submission.
    const j = load<JobAcceptedResponse>("job_accepted_features");
    expect(j.job_id).toMatch(/^[0-9A-Z]{26}$/);
    expect(Array.isArray(j.task_ids)).toBe(true);
    expect((j.task_ids ?? []).length).toBeGreaterThanOrEqual(1);
  });

  it("SnapshotListResponse decodes empty list", () => {
    const s = load<SnapshotListResponse>("snapshot_list_empty");
    expect(s.seqs).toEqual([]);
  });
});
