// Verifies the generated SDK's `submitAndStream()` recipe.
// Stubbed fetch — submit returns 202; SSE returns 2 events; final
// /v1/jobs/{id} poll returns succeeded.

import { describe, expect, it } from "vitest";

import {
  submitAndStream,
  NotFoundError,
} from "../src/_generated/client.js";

function makeFetch(): typeof fetch {
  let pollIdx = 0;
  return async (input: RequestInfo | URL): Promise<Response> => {
    const url = String(input);
    if (url.includes("/events")) {
      const body =
        "id: 1\nevent: progress\ndata: {\"phase\":\"extract\"}\n\n" +
        "id: 2\nevent: progress\ndata: {\"phase\":\"match\"}\n\n";
      return new Response(body, {
        status: 200,
        headers: { "Content-Type": "text/event-stream" },
      });
    }
    if (url.includes("/v1/jobs/")) {
      const states = ["pending", "succeeded"];
      const status = states[Math.min(pollIdx++, states.length - 1)];
      return new Response(JSON.stringify({ job_id: "j_stream", status }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    }
    return new Response("not routed", { status: 404 });
  };
}

describe("generated TS submitAndStream", () => {
  it("yields events live and resolves result with terminal JobDetail", async () => {
    const handle = await submitAndStream(
      () => Promise.resolve({ job_id: "j_stream", task_ids: ["t1"] }),
      { baseUrl: "http://x", fetch: makeFetch() },
    );
    const seen: string[] = [];
    for await (const ev of handle.events) seen.push(ev.id);
    const final = await handle.result;
    expect(seen).toEqual(["1", "2"]);
    expect(final.status).toBe("succeeded");
    expect(final.job_id).toBe("j_stream");
  });

  it("throws when submitFn returns no job_id", async () => {
    await expect(
      submitAndStream(() => ({ task_ids: [] }), { baseUrl: "http://x" }),
    ).rejects.toThrow(/no job_id/);
  });

  it("propagates a NotFoundError when the wait poll 404s", async () => {
    let phase: "events" | "wait" = "events";
    const fn = async (input: RequestInfo | URL): Promise<Response> => {
      const url = String(input);
      if (url.includes("/events")) {
        phase = "wait";
        return new Response("", {
          status: 200,
          headers: { "Content-Type": "text/event-stream" },
        });
      }
      // wait phase → 404
      void phase;
      return new Response(
        JSON.stringify({ status: 404, title: "Resource not found", detail: "gone" }),
        { status: 404, headers: { "Content-Type": "application/json" } },
      );
    };
    const handle = await submitAndStream(
      () => Promise.resolve({ job_id: "j_x", task_ids: [] }),
      { baseUrl: "http://x", fetch: fn },
    );
    // Drain events (empty body → no events).
    for await (const _ of handle.events) void _;
    await expect(handle.result).rejects.toBeInstanceOf(NotFoundError);
  });
});
