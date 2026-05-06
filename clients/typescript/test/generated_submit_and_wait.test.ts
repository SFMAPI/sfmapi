// Verifies the generated SDK's `submitAndWait()` combinator.
// Stubbed fetch so the test runs without a live server.

import { describe, expect, it } from "vitest";

import { submitAndWait } from "../src/_generated/client.js";

describe("generated TS submitAndWait", () => {
  it("calls submitFn then waits until terminal status", async () => {
    const states = ["pending", "running", "succeeded"];
    let i = 0;
    const fn = async (): Promise<Response> => {
      const status = states[Math.min(i++, states.length - 1)];
      return new Response(JSON.stringify({ job_id: "j_chain", status }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    };
    let submitted = false;
    const out = await submitAndWait(
      () => {
        submitted = true;
        return Promise.resolve({ job_id: "j_chain", task_ids: ["t1"] });
      },
      {
        baseUrl: "http://test.invalid",
        pollInterval: 0.001,
        fetch: fn as unknown as typeof fetch,
      },
    );
    expect(submitted).toBe(true);
    expect(out.job_id).toBe("j_chain");
    expect(out.status).toBe("succeeded");
  });

  it("accepts a synchronous submitFn return value", async () => {
    const fn = async (): Promise<Response> =>
      new Response(JSON.stringify({ job_id: "j_sync", status: "succeeded" }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    const out = await submitAndWait(
      () => ({ job_id: "j_sync", task_ids: [] }),
      {
        baseUrl: "http://x",
        pollInterval: 0.001,
        fetch: fn as unknown as typeof fetch,
      },
    );
    expect(out.job_id).toBe("j_sync");
  });

  it("throws when submitFn returns no job_id", async () => {
    await expect(
      submitAndWait(() => ({ task_ids: [] }), { baseUrl: "http://x" }),
    ).rejects.toThrow(/no job_id/);
  });
});
