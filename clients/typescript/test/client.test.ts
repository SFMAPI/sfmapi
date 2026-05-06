import { describe, expect, it, beforeAll, afterAll, afterEach } from "vitest";
import { setupServer } from "msw/node";
import { http, HttpResponse } from "msw";

import {
  SfmApiClient,
  NotFoundError,
  ValidationError,
  AuthError,
} from "../src/index.js";
import { iterSse } from "../src/sse.js";

const BASE = "http://api.test";

const server = setupServer();

beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

function makeClient(opts: { apiKey?: string } = {}) {
  return new SfmApiClient({
    baseUrl: BASE,
    ...(opts.apiKey !== undefined ? { apiKey: opts.apiKey } : {}),
  });
}

describe("SfmApiClient", () => {
  it("createProject sends Authorization header and parses Project", async () => {
    let captured: Headers | null = null;
    server.use(
      http.post(`${BASE}/v1/projects`, ({ request }) => {
        captured = request.headers;
        return HttpResponse.json(
          {
            project_id: "P".repeat(26),
            tenant_id: "default",
            name: "alpha",
            description: null,
            created_at: "2026-05-02T00:00:00Z",
          },
          { status: 201 },
        );
      }),
    );
    const c = makeClient({ apiKey: "sfm_test" });
    const p = await c.createProject({ name: "alpha" });
    expect(p.name).toBe("alpha");
    expect(captured!.get("Authorization")).toBe("Bearer sfm_test");
  });

  it("404 raises NotFoundError with parsed problem body", async () => {
    server.use(
      http.get(`${BASE}/v1/projects/missing`, () =>
        HttpResponse.json(
          {
            type: "https://sfmapi/errors/not_found",
            title: "Resource not found",
            status: 404,
            detail: "Project missing not found",
          },
          { status: 404, headers: { "Content-Type": "application/problem+json" } },
        ),
      ),
    );
    const c = makeClient();
    await expect(c.getProject("missing")).rejects.toMatchObject({
      name: "NotFoundError",
      statusCode: 404,
      message: expect.stringContaining("missing"),
    });
    expect(NotFoundError).toBeDefined();
  });

  it("422 maps to ValidationError", async () => {
    server.use(
      http.post(`${BASE}/v1/datasets/DS/matches`, () =>
        HttpResponse.json(
          { title: "Validation error", status: 422, detail: "vocab missing" },
          { status: 422, headers: { "Content-Type": "application/problem+json" } },
        ),
      ),
    );
    const c = makeClient();
    await expect(
      c.submitMatches("DS", { pairs: { strategy: "vocabtree" } }),
    ).rejects.toBeInstanceOf(ValidationError);
  });

  it("403 maps to AuthError", async () => {
    server.use(
      http.get(`${BASE}/v1/projects/X`, () =>
        HttpResponse.json(
          { title: "Tenant boundary violation", status: 403 },
          { status: 403 },
        ),
      ),
    );
    const c = makeClient();
    await expect(c.getProject("X")).rejects.toBeInstanceOf(AuthError);
  });

  it("uploadBytes performs init → PATCH → finalize and verifies sha", async () => {
    const payload = new Uint8Array([0xff, 0xd8, 0xff, 0xe0, 1, 2, 3, 4, 5]);
    // sha256 of payload (precomputed)
    const expectedSha = await crypto.subtle
      .digest("SHA-256", payload)
      .then((d) =>
        Array.from(new Uint8Array(d))
          .map((b) => b.toString(16).padStart(2, "0"))
          .join(""),
      );

    let initBody: any = null;
    let patched = false;

    server.use(
      http.post(`${BASE}/v1/uploads`, async ({ request }) => {
        initBody = await request.json();
        return HttpResponse.json(
          {
            upload_id: "U".repeat(26),
            state: "open",
            expected_size: payload.byteLength,
            received_bytes: 0,
            blob_sha: null,
            expires_at: "2026-05-03T00:00:00Z",
          },
          { status: 201 },
        );
      }),
      http.patch(`${BASE}/v1/uploads/${"U".repeat(26)}`, async ({ request }) => {
        patched = true;
        expect(request.headers.get("Content-Range")).toMatch(/bytes 0-\d+\/\d+/);
        return HttpResponse.json({
          upload_id: "U".repeat(26),
          state: "received",
          expected_size: payload.byteLength,
          received_bytes: payload.byteLength,
          blob_sha: null,
          expires_at: "2026-05-03T00:00:00Z",
        });
      }),
      http.post(`${BASE}/v1/uploads/${"U".repeat(26)}:finalize`, () =>
        HttpResponse.json({
          upload_id: "U".repeat(26),
          state: "finalized",
          expected_size: payload.byteLength,
          received_bytes: payload.byteLength,
          blob_sha: expectedSha,
          expires_at: "2026-05-03T00:00:00Z",
        }),
      ),
    );

    const c = makeClient();
    const sha = await c.uploadBytes(payload);
    expect(sha).toBe(expectedSha);
    expect(initBody.expected_sha).toBe(expectedSha);
    expect(initBody.expected_size).toBe(payload.byteLength);
    expect(patched).toBe(true);
  });

  it("runPipeline routes to /pipelines/{kind}", async () => {
    let hitPath: string | null = null;
    server.use(
      http.post(`${BASE}/v1/projects/PR/pipelines/incremental`, ({ request }) => {
        hitPath = new URL(request.url).pathname;
        return HttpResponse.json(
          {
            job_id: "J".repeat(26),
            task_ids: ["T".repeat(26)],
            recon_id: "R".repeat(26),
          },
          { status: 202 },
        );
      }),
    );
    const c = makeClient();
    const result = await c.runPipeline("PR", {
      dataset_id: "DS",
      spec: { kind: "incremental" },
    });
    expect(hitPath).toBe("/v1/projects/PR/pipelines/incremental");
    expect(result.recon_id).toBe("R".repeat(26));
  });

  it("streamEvents parses SSE lines into ProgressEvent objects", async () => {
    server.use(
      http.get(`${BASE}/v1/jobs/JOB/events`, () => {
        const body = [
          "id: 1",
          'data: {"schema_version":1,"ts":"t","job_id":"JOB","seq":1,"kind":"phase_started","phase":"feature_extraction"}',
          "",
          "id: 2",
          'data: {"schema_version":1,"ts":"t","job_id":"JOB","seq":2,"kind":"phase_progress","phase":"feature_extraction","current":3,"total":4}',
          "",
        ].join("\n");
        return new HttpResponse(body, {
          status: 200,
          headers: { "Content-Type": "text/event-stream" },
        });
      }),
    );
    const c = makeClient();
    const events = [];
    for await (const e of c.streamEvents("JOB")) {
      events.push(e);
      if (events.length === 2) break;
    }
    expect(events).toHaveLength(2);
    expect(events[0]!.kind).toBe("phase_started");
    expect(events[1]!.kind).toBe("phase_progress");
    expect(events[1]!.current).toBe(3);
  });
});

describe("iterSse", () => {
  it("yields multi-line data fields concatenated with newlines", async () => {
    const body = ["data: line1", "data: line2", "", ""].join("\n");
    const stream = new ReadableStream<Uint8Array>({
      start(controller) {
        controller.enqueue(new TextEncoder().encode(body));
        controller.close();
      },
    });
    const out: string[] = [];
    for await (const msg of iterSse(stream)) out.push(msg.data);
    expect(out).toEqual(["line1\nline2"]);
  });
});
