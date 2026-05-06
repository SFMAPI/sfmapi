// Thin runtime wrapper around `openapi-fetch` bound to the generated
// OpenAPI types. Consumers prefer this over the hand-rolled
// `SfmApiClient` when they want fully typed paths/params/responses
// derived directly from the live server spec.
//
// Regenerate via `npm run gen:sdk` (or `uv run python
// scripts/regen_sdk.py` from the repo root, which dumps a fresh
// OpenAPI document and then rebuilds both Python + TS generated SDKs).

import createClient, { type Client } from "openapi-fetch";
import type { paths } from "./openapi.js";

import {
  parseSseBuffer,
  streamEvents,
  submitAndStream,
  submitAndWait,
  uploadBytes,
  waitForJob,
  type SseEvent,
  type StreamEventsOptions,
  type SubmitAndStreamHandle,
  type SubmitAndStreamOptions,
  type SubmitAndWaitOptions,
  type UploadBytesOptions,
  type WaitForJobOptions,
} from "./ergonomics.js";

/// The raw `openapi-fetch` typed paths client. Use for any
/// non-ergonomic typed call: `client.raw.GET("/v1/projects", {})`.
export type SfmApiRawClient = Client<paths>;

/// OO wrapper that exposes the ergonomics helpers as instance
/// methods bound to the configured `baseUrl` / `apiKey` / `fetch`
/// — saves callers from re-passing those on every helper invocation.
export interface SfmApiGeneratedClient {
  /** Underlying typed paths client (raw `openapi-fetch`). */
  readonly raw: SfmApiRawClient;
  /** Effective `baseUrl` after trailing-slash stripping. */
  readonly baseUrl: string;
  uploadBytes(
    data: Uint8Array,
    opts?: Omit<UploadBytesOptions, "baseUrl" | "apiKey" | "fetch">,
  ): Promise<string>;
  streamEvents(
    jobId: string,
    opts?: Omit<StreamEventsOptions, "baseUrl" | "apiKey" | "fetch">,
  ): AsyncIterable<SseEvent>;
  waitForJob(
    jobId: string,
    opts?: Omit<WaitForJobOptions, "baseUrl" | "apiKey" | "fetch">,
  ): Promise<Record<string, unknown>>;
  submitAndWait(
    submitFn: () => Promise<{ job_id?: string } | Record<string, unknown>> | { job_id?: string } | Record<string, unknown>,
    opts?: Omit<SubmitAndWaitOptions, "baseUrl" | "apiKey" | "fetch">,
  ): Promise<Record<string, unknown>>;
  submitAndStream(
    submitFn: () => Promise<{ job_id?: string } | Record<string, unknown>> | { job_id?: string } | Record<string, unknown>,
    opts?: Omit<SubmitAndStreamOptions, "baseUrl" | "apiKey" | "fetch">,
  ): Promise<SubmitAndStreamHandle>;
  parseEventsBuffer(body: string): SseEvent[];
}

export interface GeneratedClientOptions {
  baseUrl: string;
  apiKey?: string;
  /** Overrides the global `fetch` — useful for tests + Node ≤ 17. */
  fetch?: typeof fetch;
  /** Extra headers merged onto every request. */
  headers?: Record<string, string>;
}

export function createSfmApiClient(opts: GeneratedClientOptions): SfmApiGeneratedClient {
  const headers: Record<string, string> = { ...(opts.headers ?? {}) };
  if (opts.apiKey) headers["Authorization"] = `Bearer ${opts.apiKey}`;
  const raw = createClient<paths>({
    baseUrl: opts.baseUrl,
    headers,
    ...(opts.fetch ? { fetch: opts.fetch } : {}),
  });
  const baseUrl = opts.baseUrl.replace(/\/+$/, "");

  // Each method merges the client's bound config (baseUrl, apiKey,
  // fetch) onto the per-call options. Callers may still override
  // any of those by passing them explicitly.
  function bind<
    T extends
      | UploadBytesOptions
      | StreamEventsOptions
      | WaitForJobOptions
      | SubmitAndWaitOptions
      | SubmitAndStreamOptions,
  >(
    extra: Omit<T, "baseUrl" | "apiKey" | "fetch"> | undefined,
  ): T {
    return {
      baseUrl,
      ...(opts.apiKey !== undefined ? { apiKey: opts.apiKey } : {}),
      ...(opts.fetch !== undefined ? { fetch: opts.fetch } : {}),
      ...(extra ?? {}),
    } as T;
  }

  return {
    raw,
    baseUrl,
    uploadBytes(data, options) {
      return uploadBytes(data, bind<UploadBytesOptions>(options));
    },
    streamEvents(jobId, options) {
      return streamEvents(jobId, bind<StreamEventsOptions>(options));
    },
    waitForJob(jobId, options) {
      return waitForJob(jobId, bind<WaitForJobOptions>(options));
    },
    submitAndWait(submitFn, options) {
      return submitAndWait(submitFn, bind<SubmitAndWaitOptions>(options));
    },
    submitAndStream(submitFn, options) {
      return submitAndStream(submitFn, bind<SubmitAndStreamOptions>(options));
    },
    parseEventsBuffer(body) {
      return parseSseBuffer(body);
    },
  };
}

export type { paths, components, operations } from "./openapi.js";

export {
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
  uploadBytes,
  DEFAULT_CHUNK_SIZE,
  parseSseBuffer,
  streamEvents,
  TERMINAL_JOB_STATES,
  waitForJob,
  submitAndWait,
  submitAndStream,
  parsePointsBinary,
  parseDepthMap,
  parseNormalMap,
  WireFormatError,
  POINTS_MEDIA_TYPE,
  DEPTH_MEDIA_TYPE,
  NORMAL_MEDIA_TYPE,
} from "./ergonomics.js";
export type {
  UploadBytesOptions,
  SseEvent,
  StreamEventsOptions,
  WaitForJobOptions,
  SubmitAndWaitOptions,
  SubmitAndStreamOptions,
  SubmitAndStreamHandle,
  Point3DRecord,
  PointsBinary,
  DepthMap,
  NormalMap,
} from "./ergonomics.js";
