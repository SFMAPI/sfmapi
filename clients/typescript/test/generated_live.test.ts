// End-to-end live-server contract test for the TypeScript generated
// SDK. Mirrors Python's
// `tests/contract/test_e_generated_ergonomics.py::test_chained_ergonomics_against_live_server`
// — spawns the ephemeral app via `uv run python -m uvicorn ...`,
// drives the full ergonomics chain through real HTTP, asserts the
// terminal JobDetail comes back.
//
// Skips automatically when:
//   - `uv` isn't on PATH (CI without Python toolchain),
//   - the spawn fails for any reason,
//   - `SFMAPI_LIVE_SKIP=1` is set (manual opt-out for fast loops).
//
// This is the symmetric gap to Python's live-server test — the
// stubbed-fetch suites prove each helper's wire shape; this proves
// they actually compose against the running server.

import { describe, it, expect } from "vitest";
import { spawn, type ChildProcessWithoutNullStreams } from "node:child_process";
import { existsSync } from "node:fs";
import { resolve } from "node:path";

import {
  createSfmApiClient,
  uploadBytes,
  streamEvents,
  submitAndStream,
  waitForJob,
  TERMINAL_JOB_STATES,
} from "../src/_generated/client.js";

const REPO_ROOT = resolve(__dirname, "../../..");

function uvAvailable(): boolean {
  // Node 20 doesn't ship a sync `which`. Cheapest signal: check
  // for the repo's .venv (always present after `uv venv`).
  return existsSync(resolve(REPO_ROOT, ".venv"));
}

function shouldSkip(): boolean {
  if (process.env["SFMAPI_LIVE_SKIP"] === "1") return true;
  if (!uvAvailable()) return true;
  return false;
}

interface ServerHandle {
  proc: ChildProcessWithoutNullStreams;
  baseUrl: string;
}

async function bootServer(): Promise<ServerHandle> {
  // Pick a random high port; uvicorn binds it within ~1s.
  const port = 30000 + Math.floor(Math.random() * 30000);
  const env = {
    ...process.env,
    SFMAPI_EPHEMERAL: "true",
    SFMAPI_LOG_LEVEL: "WARNING",
  };
  // Strip any inherited overrides that would defeat ephemeral mode.
  for (const k of [
    "SFMAPI_DB_URL",
    "SFMAPI_WORKSPACE_ROOT",
    "SFMAPI_BLOB_ROOT",
    "SFMAPI_S3_CACHE_ROOT",
    "SFMAPI_INLINE_TASKS",
    "SFMAPI_QUEUE_BACKEND",
    "SFMAPI_BLOB_BACKEND",
  ]) {
    delete (env as Record<string, string | undefined>)[k];
  }

  const proc = spawn(
    "uv",
    [
      "run",
      "python",
      "-m",
      "uvicorn",
      "app.main:app",
      "--host",
      "127.0.0.1",
      "--port",
      String(port),
      "--log-level",
      "warning",
    ],
    { cwd: REPO_ROOT, env, shell: true },
  );

  // Buffer stderr so test failures show why the server died.
  let stderrBuf = "";
  proc.stderr.on("data", (chunk: Buffer) => {
    stderrBuf += chunk.toString("utf-8");
  });

  // Wait for the server to accept connections (max 15s).
  const deadline = Date.now() + 15_000;
  while (Date.now() < deadline) {
    try {
      const r = await fetch(`http://127.0.0.1:${port}/healthz`);
      if (r.status === 200) {
        return { proc, baseUrl: `http://127.0.0.1:${port}` };
      }
    } catch {
      /* server not up yet */
    }
    await new Promise((r) => setTimeout(r, 200));
  }
  proc.kill("SIGKILL");
  throw new Error(
    `live server failed to come up within 15s. stderr:\n${stderrBuf}`,
  );
}

async function teardown(h: ServerHandle): Promise<void> {
  if (!h.proc.killed) {
    h.proc.kill("SIGTERM");
    // Give it 2s to exit cleanly, then SIGKILL.
    await new Promise<void>((res) => {
      const t = setTimeout(() => {
        if (!h.proc.killed) h.proc.kill("SIGKILL");
        res();
      }, 2000);
      h.proc.once("exit", () => {
        clearTimeout(t);
        res();
      });
    });
  }
}

async function bootstrapDataset(
  baseUrl: string,
): Promise<{ projectId: string; datasetId: string; sha: string }> {
  const c = createSfmApiClient({ baseUrl });
  const proj = await c.raw.POST("/v1/projects", {
    body: { name: "ts-live-helper" },
  });
  const projectId = (proj.data as { project_id: string }).project_id;
  const ds = await c.raw.POST("/v1/projects/{project_id}/datasets", {
    params: { path: { project_id: projectId } },
    body: {
      name: "ts-live-helper-ds",
      source: { kind: "upload", entries: [] },
      camera_model: "SIMPLE_RADIAL",
      intrinsics_mode: "single_camera",
      is_spherical: false,
      respect_exif_orientation: false,
    },
  });
  const datasetId = (ds.data as { dataset_id: string }).dataset_id;
  const sha = await uploadBytes(new Uint8Array([1, 2, 3, 4, 5, 6, 7, 8]), {
    baseUrl,
    chunkSize: 4,
  });
  await c.raw.POST("/v1/datasets/{dataset_id}/images", {
    params: { path: { dataset_id: datasetId } },
    body: { name: "live.jpg", blob_sha: sha, width: 1, height: 1 },
  });
  return { projectId, datasetId, sha };
}

describe.skipIf(shouldSkip())(
  "TS live-server contract: chained ergonomics",
  () => {
    it(
      "uploadBytes -> create image -> submitAndWait returns terminal JobDetail",
      { timeout: 60_000 },
      async () => {
        const h = await bootServer();
        try {
          const c = createSfmApiClient({ baseUrl: h.baseUrl });

          // 1. Create project + dataset via the raw typed paths client.
          const proj = await c.raw.POST("/v1/projects", {
            body: { name: "ts-live-chain" },
          });
          expect([200, 201]).toContain(proj.response.status);
          // openapi-fetch's typed responses surface the parsed body
          // on `data` for 2xx codes.
          const projectId = (proj.data as { project_id: string }).project_id;
          expect(projectId).toMatch(/^[0-9A-Z]{26}$/);

          const ds = await c.raw.POST(
            "/v1/projects/{project_id}/datasets",
            {
              params: { path: { project_id: projectId } },
              body: {
                name: "ts-live-ds",
                source: { kind: "upload", entries: [] },
                camera_model: "SIMPLE_RADIAL",
                intrinsics_mode: "single_camera",
                is_spherical: false,
                respect_exif_orientation: false,
              },
            },
          );
          expect([200, 201]).toContain(ds.response.status);
          const datasetId = (ds.data as { dataset_id: string }).dataset_id;
          expect(datasetId).toMatch(/^[0-9A-Z]{26}$/);

          // 2. Upload bytes via the standalone helper, then attach as image.
          const sha = await uploadBytes(new Uint8Array([1, 2, 3, 4, 5, 6, 7, 8]), {
            baseUrl: h.baseUrl,
            chunkSize: 4,
          });
          expect(sha).toHaveLength(64);

          const img = await c.raw.POST(
            "/v1/datasets/{dataset_id}/images",
            {
              params: { path: { dataset_id: datasetId } },
              body: { name: "live.jpg", blob_sha: sha, width: 1, height: 1 },
            },
          );
          expect([200, 201]).toContain(img.response.status);

          // 3. Submit features stage + wait for terminal status via the
          //    OO client method (binds baseUrl + apiKey + fetch).
          const detail = await c.submitAndWait(
            async () => {
              const r = await c.raw.POST(
                "/v1/datasets/{dataset_id}/features",
                {
                  params: { path: { dataset_id: datasetId } },
                  body: {
                    spec: {
                      version: 1,
                      type: "sift",
                      max_num_features: 16,
                      use_gpu: false,
                      seed: 0,
                    },
                  },
                },
              );
              expect([200, 201, 202]).toContain(r.response.status);
              return r.data as Record<string, unknown>;
            },
            { pollInterval: 0.05, timeout: 30 },
          );
          expect(TERMINAL_JOB_STATES.has(String(detail["status"]))).toBe(true);
          expect(detail["job_id"]).toMatch(/^[0-9A-Z]{26}$/);
        } finally {
          await teardown(h);
        }
      },
    );

    it(
      "SSE stream terminates after job reaches terminal status",
      { timeout: 60_000 },
      async () => {
        // Mirror of Python's
        // test_sse_stream_terminates_after_job_reaches_terminal — a
        // handler regression to `while True: yield; sleep` would
        // make streamEvents() hang until the global timeout instead
        // of returning cleanly. The timer-based assertion here
        // catches that explicitly.
        const h = await bootServer();
        try {
          const { datasetId } = await bootstrapDataset(h.baseUrl);
          const c = createSfmApiClient({ baseUrl: h.baseUrl });
          const submit = await c.raw.POST(
            "/v1/datasets/{dataset_id}/features",
            {
              params: { path: { dataset_id: datasetId } },
              body: {
                spec: {
                  version: 1,
                  type: "sift",
                  max_num_features: 16,
                  use_gpu: false,
                  seed: 0,
                },
              },
            },
          );
          const jobId = (submit.data as { job_id: string }).job_id;
          // Wait for the inline-queue worker to mark Job terminal.
          const final = await waitForJob(jobId, {
            baseUrl: h.baseUrl,
            pollInterval: 0.05,
            timeout: 30,
          });
          expect(TERMINAL_JOB_STATES.has(String(final["status"]))).toBe(true);

          // Now drain the SSE stream — MUST return cleanly. Time it
          // so we can assert it didn't rely on the global timeout.
          const drainStarted = Date.now();
          const events: { id: string }[] = [];
          for await (const ev of streamEvents(jobId, {
            baseUrl: h.baseUrl,
            // Vitest test timeout is 60s; keep this lower so a stuck
            // stream surfaces as a focused failure rather than a
            // generic vitest timeout.
            // (streamEvents itself doesn't enforce a timeout on the
            // fetch — the AbortSignal would. Plain drain time check
            // is sufficient: server polls at 1s + one final drain.)
          })) {
            events.push({ id: ev.id });
          }
          const drainElapsed = (Date.now() - drainStarted) / 1000;
          expect(drainElapsed).toBeLessThan(5.0);
          // Don't assert on event count — a stage-failure job may
          // emit zero events depending on where it crashes. Contract
          // is just "stream closes cleanly".
          expect(events).toBeDefined();
        } finally {
          await teardown(h);
        }
      },
    );

    it(
      "two parallel jobs both reach terminal + drain SSE concurrently",
      { timeout: 60_000 },
      async () => {
        // Submit two features-stage jobs in parallel against the
        // same dataset, drain both SSE streams concurrently. Catches
        // race conditions in the terminal-then-drain protocol that
        // sequential single-job tests miss — e.g. a worker that
        // accidentally rolls Job.status up based on cross-job task
        // counts, or a SSE handler that closes streams keyed on a
        // process-level singleton.
        const h = await bootServer();
        try {
          const { datasetId } = await bootstrapDataset(h.baseUrl);
          const c = createSfmApiClient({ baseUrl: h.baseUrl });

          async function submitFeatures(): Promise<string> {
            const r = await c.raw.POST(
              "/v1/datasets/{dataset_id}/features",
              {
                params: { path: { dataset_id: datasetId } },
                body: {
                  spec: {
                    version: 1,
                    type: "sift",
                    max_num_features: 16,
                    use_gpu: false,
                    seed: 0,
                  },
                },
              },
            );
            return (r.data as { job_id: string }).job_id;
          }

          // Submit serially (httpx is fine with bursts; the inline
          // queue runs them sequentially anyway, but each gets its
          // own Job row + SSE stream).
          const jobA = await submitFeatures();
          const jobB = await submitFeatures();
          expect(jobA).not.toBe(jobB);

          // Wait for both terminal in parallel.
          const [finalA, finalB] = await Promise.all([
            waitForJob(jobA, {
              baseUrl: h.baseUrl,
              pollInterval: 0.05,
              timeout: 30,
            }),
            waitForJob(jobB, {
              baseUrl: h.baseUrl,
              pollInterval: 0.05,
              timeout: 30,
            }),
          ]);
          expect(TERMINAL_JOB_STATES.has(String(finalA["status"]))).toBe(true);
          expect(TERMINAL_JOB_STATES.has(String(finalB["status"]))).toBe(true);
          // Job IDs and statuses must be independent — a regression
          // that crosses job state would manifest here as identical
          // values or one job stuck in pending.
          expect(finalA["job_id"]).toBe(jobA);
          expect(finalB["job_id"]).toBe(jobB);

          // Drain both SSE streams concurrently — both must close
          // cleanly, neither should hang waiting for the other.
          const drainStarted = Date.now();
          const [eventsA, eventsB] = await Promise.all([
            (async () => {
              const out: { id: string }[] = [];
              for await (const ev of streamEvents(jobA, { baseUrl: h.baseUrl })) {
                out.push({ id: ev.id });
              }
              return out;
            })(),
            (async () => {
              const out: { id: string }[] = [];
              for await (const ev of streamEvents(jobB, { baseUrl: h.baseUrl })) {
                out.push({ id: ev.id });
              }
              return out;
            })(),
          ]);
          const drainElapsed = (Date.now() - drainStarted) / 1000;
          // Concurrent drains share the polling cadence; allow more
          // headroom than the single-job test (~5s -> ~7s) to avoid
          // flakes on slow machines.
          expect(drainElapsed).toBeLessThan(7.0);
          expect(eventsA).toBeDefined();
          expect(eventsB).toBeDefined();
        } finally {
          await teardown(h);
        }
      },
    );

    it(
      "submitAndStream yields events live and resolves terminal JobDetail",
      { timeout: 60_000 },
      async () => {
        const h = await bootServer();
        try {
          const { datasetId } = await bootstrapDataset(h.baseUrl);
          const c = createSfmApiClient({ baseUrl: h.baseUrl });
          const handle = await c.submitAndStream(async () => {
            const r = await c.raw.POST(
              "/v1/datasets/{dataset_id}/features",
              {
                params: { path: { dataset_id: datasetId } },
                body: {
                  spec: {
                    version: 1,
                    type: "sift",
                    max_num_features: 16,
                    use_gpu: false,
                    seed: 0,
                  },
                },
              },
            );
            return r.data as Record<string, unknown>;
          });
          const drained: string[] = [];
          for await (const ev of handle.events) drained.push(ev.id);
          const final = await handle.result;
          expect(TERMINAL_JOB_STATES.has(String(final["status"]))).toBe(true);
          // `drained` may be empty (stage-fail emits zero events) —
          // we only assert iteration completed without hanging.
          expect(drained).toBeDefined();
        } finally {
          await teardown(h);
        }
      },
    );
  },
);
