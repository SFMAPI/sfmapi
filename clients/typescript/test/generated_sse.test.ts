// Verifies the generated SDK's `streamEvents()` SSE iterator parses
// canonical and CRLF event streams correctly. Uses a stubbed `fetch`
// so the test runs without a live server; behavior matches the
// Python `_ergonomics.stream_events()` against a real ephemeral app.

import { describe, expect, it } from "vitest";

import {
  parseSseBuffer,
  streamEvents,
  NotFoundError,
} from "../src/_generated/client.js";

describe("generated TS parseSseBuffer", () => {
  it("handles canonical id/event/data stream", () => {
    const body =
      "id: 1\nevent: progress\ndata: {\"phase\":\"extract\",\"current\":5}\n\n" +
      ": comment\n" +
      "id: 2\ndata: line1\ndata: line2\n\n";
    const events = parseSseBuffer(body);
    expect(events).toHaveLength(2);
    expect(events[0]!.id).toBe("1");
    expect(events[0]!.event).toBe("progress");
    expect(JSON.parse(events[0]!.data)).toEqual({ phase: "extract", current: 5 });
    expect(events[1]!.id).toBe("2");
    expect(events[1]!.data).toBe("line1\nline2");
  });

  it("handles CRLF line endings", () => {
    const body = "id: 7\r\nevent: msg\r\ndata: hello\r\n\r\n";
    const events = parseSseBuffer(body);
    expect(events).toHaveLength(1);
    expect(events[0]!.id).toBe("7");
    expect(events[0]!.event).toBe("msg");
    expect(events[0]!.data).toBe("hello");
  });

  it("returns no events when there's no data field", () => {
    const body = ": just a comment\n\n";
    expect(parseSseBuffer(body)).toEqual([]);
  });
});

function streamingFetch(
  status: number,
  chunks: string[],
  recorder?: { headers?: Headers; lastInit?: RequestInit | undefined },
): typeof fetch {
  return async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
    if (recorder) {
      recorder.headers = new Headers(init?.headers ?? {});
      recorder.lastInit = init;
    }
    void input;
    if (status !== 200) {
      return new Response(JSON.stringify({ detail: "missing", status }), {
        status,
        headers: { "Content-Type": "application/json" },
      });
    }
    const encoder = new TextEncoder();
    const body = new ReadableStream<Uint8Array>({
      start(controller) {
        for (const c of chunks) controller.enqueue(encoder.encode(c));
        controller.close();
      },
    });
    return new Response(body, {
      status: 200,
      headers: { "Content-Type": "text/event-stream" },
    });
  };
}

describe("generated TS streamEvents", () => {
  it("yields events as the server flushes them", async () => {
    const chunks = [
      "id: 1\nevent: progress\ndata: ",
      "{\"phase\":\"extract\"}\n\n",
      "id: 2\ndata: line1\ndata: line2\n\n",
    ];
    const fn = streamingFetch(200, chunks);
    const out: { id: string; data: string }[] = [];
    for await (const ev of streamEvents("j_test", {
      baseUrl: "http://test.invalid",
      fetch: fn,
    })) {
      out.push({ id: ev.id, data: ev.data });
    }
    expect(out).toHaveLength(2);
    expect(out[0]!.id).toBe("1");
    expect(JSON.parse(out[0]!.data)).toEqual({ phase: "extract" });
    expect(out[1]!.id).toBe("2");
    expect(out[1]!.data).toBe("line1\nline2");
  });

  it("attaches Last-Event-ID header when given", async () => {
    const recorder: { headers?: Headers } = {};
    const fn = streamingFetch(200, [], recorder);
    const it = streamEvents("j_test", {
      baseUrl: "http://x",
      lastEventId: 42,
      fetch: fn,
    });
    // Drain — empty stream completes immediately.
    for await (const _ of it) void _;
    expect(recorder.headers?.get("Last-Event-ID")).toBe("42");
    expect(recorder.headers?.get("Accept")).toBe("text/event-stream");
  });

  it("attaches Authorization header when apiKey is given", async () => {
    const recorder: { headers?: Headers } = {};
    const fn = streamingFetch(200, [], recorder);
    const it = streamEvents("j_test", {
      baseUrl: "http://x",
      apiKey: "secret",
      fetch: fn,
    });
    for await (const _ of it) void _;
    expect(recorder.headers?.get("Authorization")).toBe("Bearer secret");
  });

  it("translates a 404 into NotFoundError", async () => {
    const fn = streamingFetch(404, []);
    const it = streamEvents("j_missing", {
      baseUrl: "http://x",
      fetch: fn,
    });
    await expect(async () => {
      for await (const _ of it) void _;
    }).rejects.toBeInstanceOf(NotFoundError);
  });
});
