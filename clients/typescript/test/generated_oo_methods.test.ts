// Verifies the OO methods on the generated TS client. Each method
// should bind its baseUrl / apiKey / fetch to the underlying
// helper without callers passing them again.

import { describe, expect, it } from "vitest";

import { createSfmApiClient } from "../src/_generated/client.js";

function recordingFetch(
  responder: (url: string, init?: RequestInit) => { status: number; body: unknown },
) {
  const calls: { url: string; method: string; headers: Record<string, string> }[] = [];
  const fn = async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
    const url = typeof input === "string" ? input : input.toString();
    const headers: Record<string, string> = {};
    if (init?.headers) {
      const h = new Headers(init.headers);
      h.forEach((v, k) => {
        headers[k.toLowerCase()] = v;
      });
    }
    calls.push({ url, method: (init?.method ?? "GET").toUpperCase(), headers });
    const { status, body } = responder(url, init);
    return new Response(typeof body === "string" ? body : JSON.stringify(body), {
      status,
      headers: { "Content-Type": "application/json" },
    });
  };
  return { fn, calls };
}

describe("OO methods on generated TS client", () => {
  it("client.waitForJob binds baseUrl + apiKey + fetch", async () => {
    let i = 0;
    const states = ["pending", "succeeded"];
    const { fn, calls } = recordingFetch(() => ({
      status: 200,
      body: {
        job_id: "j_oo",
        status: states[Math.min(i++, states.length - 1)],
      },
    }));
    const c = createSfmApiClient({
      baseUrl: "http://oo.test",
      apiKey: "k1",
      fetch: fn,
    });
    const out = await c.waitForJob("j_oo", { pollInterval: 0.001 });
    expect(out.status).toBe("succeeded");
    // Every call should have hit the bound baseUrl + Authorization header.
    expect(calls[0]!.url.startsWith("http://oo.test/v1/jobs/j_oo")).toBe(true);
    for (const call of calls) {
      expect(call.headers["authorization"]).toBe("Bearer k1");
    }
  });

  it("client.uploadBytes binds baseUrl + apiKey + fetch", async () => {
    const { fn, calls } = recordingFetch((url) => {
      if (url.endsWith("/v1/uploads")) return { status: 201, body: { upload_id: "u1" } };
      if (url.includes(":finalize"))
        return { status: 200, body: { blob_sha: "abc" } };
      return { status: 200, body: { received: true } };
    });
    const c = createSfmApiClient({
      baseUrl: "http://oo.test",
      apiKey: "k1",
      fetch: fn,
    });
    const sha = await c.uploadBytes(new Uint8Array([1, 2, 3, 4]));
    expect(sha).toBe("abc");
    for (const call of calls) {
      expect(call.headers["authorization"]).toBe("Bearer k1");
    }
  });

  it("client.submitAndWait chains submit then wait", async () => {
    let polled = 0;
    const { fn } = recordingFetch((url) => {
      if (url.includes("/v1/jobs/j_chain")) {
        const states = ["pending", "succeeded"];
        return {
          status: 200,
          body: { job_id: "j_chain", status: states[Math.min(polled++, 1)] },
        };
      }
      return { status: 202, body: { job_id: "j_chain", task_ids: ["t1"] } };
    });
    const c = createSfmApiClient({ baseUrl: "http://oo.test", fetch: fn });
    const detail = await c.submitAndWait(
      () => Promise.resolve({ job_id: "j_chain", task_ids: ["t1"] }),
      { pollInterval: 0.001 },
    );
    expect(detail.status).toBe("succeeded");
  });

  it("client.parseEventsBuffer is a synchronous SSE decoder", () => {
    const c = createSfmApiClient({ baseUrl: "http://x" });
    const events = c.parseEventsBuffer("id: 1\ndata: ok\n\n");
    expect(events).toHaveLength(1);
    expect(events[0]!.id).toBe("1");
    expect(events[0]!.data).toBe("ok");
  });

  it("client.submitAndStream binds baseUrl + apiKey + fetch", async () => {
    let pollIdx = 0;
    const { fn, calls } = recordingFetch((url) => {
      if (url.includes("/events")) {
        return {
          status: 200,
          body: "id: 1\ndata: hi\n\n",
        };
      }
      if (url.includes("/v1/jobs/")) {
        const states = ["pending", "succeeded"];
        const status = states[Math.min(pollIdx++, 1)];
        return { status: 200, body: { job_id: "j_oo_stream", status } };
      }
      return { status: 404, body: { detail: "unrouted" } };
    });
    const c = createSfmApiClient({
      baseUrl: "http://oo.test",
      apiKey: "k_oo",
      fetch: fn,
    });
    const handle = await c.submitAndStream(() =>
      Promise.resolve({ job_id: "j_oo_stream", task_ids: ["t1"] }),
    );
    const seen: string[] = [];
    for await (const ev of handle.events) seen.push(ev.id);
    const final = await handle.result;
    expect(seen).toEqual(["1"]);
    expect(final.status).toBe("succeeded");
    // Every call carries the bound Authorization header.
    for (const call of calls) {
      expect(call.headers["authorization"]).toBe("Bearer k_oo");
    }
  });

  it("client.raw is the underlying openapi-fetch client", () => {
    const c = createSfmApiClient({ baseUrl: "http://x" });
    expect(typeof c.raw.GET).toBe("function");
    expect(typeof c.raw.POST).toBe("function");
  });

  it("baseUrl is exposed as the trailing-slash-stripped value", () => {
    const c = createSfmApiClient({ baseUrl: "http://x///" });
    expect(c.baseUrl).toBe("http://x");
  });
});
