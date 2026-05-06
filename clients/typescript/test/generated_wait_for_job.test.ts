// Verifies the generated SDK's `waitForJob()` helper. Uses a
// stubbed fetch that flips the job from `pending` → `running` →
// `succeeded` after a few polls so the test runs without a live
// server.

import { describe, expect, it } from "vitest";

import {
  waitForJob,
  TERMINAL_JOB_STATES,
  NotFoundError,
} from "../src/_generated/client.js";

describe("generated TS waitForJob", () => {
  it("returns the terminal JobDetail body once status is succeeded", async () => {
    const states = ["pending", "running", "succeeded"];
    let i = 0;
    const fn = async (): Promise<Response> => {
      const body = { job_id: "j_test", status: states[Math.min(i++, states.length - 1)] };
      return new Response(JSON.stringify(body), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    };
    const out = await waitForJob("j_test", {
      baseUrl: "http://test.invalid",
      pollInterval: 0.001,
      fetch: fn as unknown as typeof fetch,
    });
    expect(out.status).toBe("succeeded");
    expect(out.job_id).toBe("j_test");
  });

  it("recognizes every TERMINAL_JOB_STATE", async () => {
    for (const terminal of ["failed", "cancelled", "cancelled_dirty"]) {
      const fn = async (): Promise<Response> =>
        new Response(JSON.stringify({ job_id: "j", status: terminal }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        });
      const out = await waitForJob("j", {
        baseUrl: "http://x",
        pollInterval: 0.001,
        fetch: fn as unknown as typeof fetch,
      });
      expect(out.status).toBe(terminal);
      expect(TERMINAL_JOB_STATES.has(String(out.status))).toBe(true);
    }
  });

  it("invokes onEvent callback for each new SSE event observed", async () => {
    const states = ["running", "succeeded"];
    let i = 0;
    const sseBody =
      "id: 1\nevent: progress\ndata: {\"phase\":\"extract\"}\n\n" +
      "id: 2\nevent: progress\ndata: {\"phase\":\"match\"}\n\n";
    const fn = async (
      input: RequestInfo | URL,
    ): Promise<Response> => {
      const url = String(input);
      if (url.endsWith("/events")) {
        return new Response(sseBody, {
          status: 200,
          headers: { "Content-Type": "text/event-stream" },
        });
      }
      const body = { job_id: "j_evt", status: states[Math.min(i++, states.length - 1)] };
      return new Response(JSON.stringify(body), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    };
    const seen: string[] = [];
    const out = await waitForJob("j_evt", {
      baseUrl: "http://x",
      pollInterval: 0.001,
      fetch: fn as unknown as typeof fetch,
      onEvent: (ev) => {
        seen.push(ev.id);
      },
    });
    expect(out.status).toBe("succeeded");
    expect(seen.length).toBeGreaterThanOrEqual(2);
    expect(seen).toContain("1");
    expect(seen).toContain("2");
  });

  it("translates a 404 from the polling GET into NotFoundError", async () => {
    const fn = async (): Promise<Response> =>
      new Response(
        JSON.stringify({
          status: 404,
          title: "Resource not found",
          detail: "Job missing",
        }),
        {
          status: 404,
          headers: { "Content-Type": "application/json" },
        },
      );
    await expect(
      waitForJob("j_missing", {
        baseUrl: "http://x",
        fetch: fn as unknown as typeof fetch,
      }),
    ).rejects.toBeInstanceOf(NotFoundError);
  });

  it("throws on timeout when the job never reaches a terminal state", async () => {
    const fn = async (): Promise<Response> =>
      new Response(JSON.stringify({ job_id: "j_stuck", status: "running" }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    await expect(
      waitForJob("j_stuck", {
        baseUrl: "http://x",
        pollInterval: 0.001,
        timeout: 0.05,
        fetch: fn as unknown as typeof fetch,
      }),
    ).rejects.toThrow(/still in status/);
  });
});
