// Verifies the generated SDK's `uploadBytes()` chunked-upload helper
// drives init -> patch -> finalize and returns the blob_sha. Uses a
// stubbed `fetch` so the test runs without a live server; the
// behavior matches what the Python `_ergonomics.upload_bytes()` does
// against a real ephemeral app (see test_e_generated_ergonomics.py).

import { describe, expect, it } from "vitest";

import {
  uploadBytes,
  NotFoundError,
  SfmApiError,
} from "../src/_generated/client.js";

interface RecordedCall {
  url: string;
  method: string;
  headers: Record<string, string>;
  body: Uint8Array | string | null;
}

function recordingFetch(
  responder: (call: RecordedCall) => { status: number; body: unknown },
) {
  const calls: RecordedCall[] = [];
  const fn = async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
    const url = typeof input === "string" ? input : input.toString();
    const headers: Record<string, string> = {};
    if (init?.headers) {
      const h = new Headers(init.headers);
      h.forEach((v, k) => {
        headers[k.toLowerCase()] = v;
      });
    }
    let body: Uint8Array | string | null = null;
    if (init?.body) {
      const raw = init.body as unknown;
      if (raw instanceof Uint8Array) {
        body = raw;
      } else if (typeof raw === "string") {
        body = raw;
      }
    }
    const call = { url, method: (init?.method ?? "GET").toUpperCase(), headers, body };
    calls.push(call);
    const { status, body: respBody } = responder(call);
    const blob =
      typeof respBody === "string" ? respBody : JSON.stringify(respBody);
    return new Response(blob, {
      status,
      headers: { "Content-Type": "application/json" },
    });
  };
  return { fn, calls };
}

describe("generated TS uploadBytes helper", () => {
  it("drives init -> patch chunks -> finalize and returns blob_sha", async () => {
    const payload = new Uint8Array(32).map((_, i) => i);
    const expectedSha = "deadbeef".repeat(8); // server returns whatever; we just check the call shape

    const { fn, calls } = recordingFetch((call) => {
      if (call.method === "POST" && call.url.endsWith("/v1/uploads")) {
        return { status: 201, body: { upload_id: "01HZTESTUPLOAD0000000000000" } };
      }
      if (call.method === "PATCH" && call.url.includes("/v1/uploads/")) {
        return { status: 200, body: { received: true } };
      }
      if (call.method === "POST" && call.url.endsWith(":finalize")) {
        return { status: 200, body: { blob_sha: expectedSha } };
      }
      return { status: 500, body: { detail: "unrouted" } };
    });

    const sha = await uploadBytes(payload, {
      baseUrl: "http://test.invalid",
      chunkSize: 8,
      fetch: fn,
    });

    expect(sha).toBe(expectedSha);
    // 1 init + 4 patch chunks (32 / 8) + 1 finalize = 6 calls
    expect(calls.length).toBe(6);
    const init = calls[0]!;
    const fin = calls[5]!;
    expect(init.method).toBe("POST");
    expect(init.url).toBe("http://test.invalid/v1/uploads");
    expect(fin.method).toBe("POST");
    expect(fin.url).toBe(
      "http://test.invalid/v1/uploads/01HZTESTUPLOAD0000000000000:finalize",
    );
    // Each PATCH carries a Content-Range covering the right window.
    for (let i = 1; i <= 4; i++) {
      const patch = calls[i]!;
      expect(patch.method).toBe("PATCH");
      expect(patch.headers["content-range"]).toBe(
        `bytes ${(i - 1) * 8}-${i * 8 - 1}/32`,
      );
    }
  });

  it("strips trailing slashes from baseUrl", async () => {
    const { fn, calls } = recordingFetch((call) => {
      if (call.method === "POST" && call.url.endsWith("/v1/uploads")) {
        return { status: 201, body: { upload_id: "u1" } };
      }
      if (call.method === "PATCH") return { status: 200, body: {} };
      return { status: 200, body: { blob_sha: "abc" } };
    });
    await uploadBytes(new Uint8Array([1, 2, 3]), {
      baseUrl: "http://test.invalid///",
      fetch: fn,
    });
    expect(calls[0]!.url).toBe("http://test.invalid/v1/uploads");
  });

  it("attaches Authorization header when apiKey is given", async () => {
    const { fn, calls } = recordingFetch((call) => {
      if (call.method === "POST" && call.url.endsWith("/v1/uploads")) {
        return { status: 201, body: { upload_id: "u1" } };
      }
      if (call.method === "PATCH") return { status: 200, body: {} };
      return { status: 200, body: { blob_sha: "abc" } };
    });
    await uploadBytes(new Uint8Array([1]), {
      baseUrl: "http://x",
      apiKey: "secret",
      fetch: fn,
    });
    for (const c of calls) {
      expect(c.headers["authorization"]).toBe("Bearer secret");
    }
  });

  it("translates a 404 from init into NotFoundError", async () => {
    const { fn } = recordingFetch(() => ({
      status: 404,
      body: { status: 404, title: "Resource not found", detail: "no upload" },
    }));
    await expect(
      uploadBytes(new Uint8Array([1]), { baseUrl: "http://x", fetch: fn }),
    ).rejects.toBeInstanceOf(NotFoundError);
  });

  it("translates a 500 with raw text body into bare SfmApiError", async () => {
    const { fn } = recordingFetch(() => ({
      status: 500,
      body: "internal kaboom",
    }));
    try {
      await uploadBytes(new Uint8Array([1]), { baseUrl: "http://x", fetch: fn });
      throw new Error("expected throw");
    } catch (e) {
      expect(e).toBeInstanceOf(SfmApiError);
      if (e instanceof SfmApiError) {
        expect(e.statusCode).toBe(500);
      }
    }
  });

  it("rejects empty payload", async () => {
    await expect(
      uploadBytes(new Uint8Array(0), { baseUrl: "http://x" }),
    ).rejects.toThrow(/non-empty/);
  });
});
