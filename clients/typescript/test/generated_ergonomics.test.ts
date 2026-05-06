// Confirms the TS generated SDK's ergonomics shim closes the parity
// gap with the hand-rolled `SfmApiClient`. Mirrors
// tests/contract/test_e_generated_ergonomics.py on the Python side.

import { describe, expect, it } from "vitest";
import { existsSync, readFileSync, readdirSync } from "node:fs";
import { join, resolve } from "node:path";

import {
  SfmApiError,
  NotFoundError,
  ConflictError,
  ValidationError,
  AuthError,
  QuotaExceededError,
  StorageError,
  PycolmapUnavailableError,
  TransportError,
  buildSfmApiError,
  raiseForStatus,
  supports,
  type components,
} from "../src/_generated/client.js";

const FIXTURE_DIR = resolve(__dirname, "../../../tests/contract/fixtures");
const haveFixtures = existsSync(FIXTURE_DIR) &&
  readdirSync(FIXTURE_DIR).some((f) => f.endsWith(".json"));

function load<T>(name: string): T {
  return JSON.parse(readFileSync(join(FIXTURE_DIR, `${name}.json`), "utf-8")) as T;
}

describe("generated TS ergonomics: error hierarchy", () => {
  it("every typed error inherits from SfmApiError", () => {
    for (const Cls of [
      NotFoundError,
      ConflictError,
      ValidationError,
      AuthError,
      QuotaExceededError,
      StorageError,
      PycolmapUnavailableError,
      TransportError,
    ]) {
      const inst = new Cls(500, "x");
      expect(inst).toBeInstanceOf(SfmApiError);
      expect(inst).toBeInstanceOf(Cls);
      expect(inst.statusCode).toBe(500);
      expect(inst.name).toBe(Cls.name);
    }
  });
});

describe.skipIf(!haveFixtures)("generated TS ergonomics: against real fixtures", () => {
  it("buildSfmApiError translates 404 problem+json to NotFoundError", () => {
    const body = load<Record<string, unknown>>("error_404_project_missing");
    const err = buildSfmApiError(404, body);
    expect(err).toBeInstanceOf(NotFoundError);
    expect(err.statusCode).toBe(404);
    expect(err.detail.toLowerCase()).toContain("not found");
  });

  it("buildSfmApiError translates 422 validation envelope", () => {
    const body = load<Record<string, unknown>>("error_422_validation");
    const err = buildSfmApiError(422, body);
    expect(err).toBeInstanceOf(ValidationError);
    expect(err.statusCode).toBe(422);
  });

  it("unknown status falls through to bare SfmApiError", () => {
    const err = buildSfmApiError(418, {});
    expect(err.constructor).toBe(SfmApiError);
    expect(err.statusCode).toBe(418);
  });

  it("raiseForStatus throws the typed subclass", () => {
    expect(() => raiseForStatus(409, { detail: "name in use" })).toThrow(ConflictError);
    try {
      raiseForStatus(409, { detail: "name in use" });
    } catch (e) {
      expect(e).toBeInstanceOf(SfmApiError);
      if (e instanceof SfmApiError) {
        expect(e.detail).toBe("name in use");
      }
    }
  });

  it("supports(caps, name) reads features off real CapabilitiesOut", () => {
    const caps = load<components["schemas"]["CapabilitiesOut"]>("capabilities");
    // `spec.read` is a CORE capability — every conforming server has it.
    expect(supports(caps, "spec.read")).toBe(true);
    expect(supports(caps, "no.such.capability.exists")).toBe(false);
  });
});

describe("generated TS ergonomics: input shapes", () => {
  it("buildSfmApiError handles a non-object body without crashing", () => {
    const err = buildSfmApiError(500, "raw text body");
    expect(err.statusCode).toBe(500);
    expect(err.detail).toBe("raw text body");
    expect(err.body).toEqual({});
  });

  it("buildSfmApiError handles undefined body", () => {
    const err = buildSfmApiError(500, undefined);
    expect(err.statusCode).toBe(500);
    expect(err.detail).toBe("");
    expect(err.body).toEqual({});
  });
});
