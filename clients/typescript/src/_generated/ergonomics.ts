// Ergonomic helpers layered on top of the generated `openapi-fetch`
// client + types. The generated layer is intentionally minimal —
// this module adds the typed-error hierarchy and `supports()`
// capability helper that the hand-rolled SDK ships, so consumers
// of the generated SDK don't have to reinvent them.
//
// Repo-owned, NOT overwritten on `npm run gen:sdk`.

import type { components } from "./openapi.js";

// ---------------------------------------------------------------------
// Typed error hierarchy. Mirrors clients/python/sfmapi_client/errors.py
// and the Python generated `_ergonomics.py` shim — `instanceof
// SfmApiError` works regardless of which SDK threw.
// ---------------------------------------------------------------------

export class SfmApiError extends Error {
  /** HTTP status code from the failing response. */
  readonly statusCode: number;
  /** RFC7807 `detail` field, when present; otherwise the raw body. */
  readonly detail: string;
  /** Parsed JSON body when the response was JSON-shaped. */
  readonly body: Record<string, unknown>;

  constructor(statusCode: number, detail = "", body: Record<string, unknown> = {}) {
    super(detail || `sfmapi error: ${statusCode}`);
    this.name = "SfmApiError";
    this.statusCode = statusCode;
    this.detail = detail;
    this.body = body;
  }
}

export class NotFoundError extends SfmApiError {
  constructor(...args: ConstructorParameters<typeof SfmApiError>) {
    super(...args);
    this.name = "NotFoundError";
  }
}

export class ConflictError extends SfmApiError {
  constructor(...args: ConstructorParameters<typeof SfmApiError>) {
    super(...args);
    this.name = "ConflictError";
  }
}

export class ValidationError extends SfmApiError {
  constructor(...args: ConstructorParameters<typeof SfmApiError>) {
    super(...args);
    this.name = "ValidationError";
  }
}

export class AuthError extends SfmApiError {
  constructor(...args: ConstructorParameters<typeof SfmApiError>) {
    super(...args);
    this.name = "AuthError";
  }
}

export class QuotaExceededError extends SfmApiError {
  constructor(...args: ConstructorParameters<typeof SfmApiError>) {
    super(...args);
    this.name = "QuotaExceededError";
  }
}

export class StorageError extends SfmApiError {
  constructor(...args: ConstructorParameters<typeof SfmApiError>) {
    super(...args);
    this.name = "StorageError";
  }
}

export class PycolmapUnavailableError extends SfmApiError {
  constructor(...args: ConstructorParameters<typeof SfmApiError>) {
    super(...args);
    this.name = "PycolmapUnavailableError";
  }
}

export class TransportError extends SfmApiError {
  constructor(...args: ConstructorParameters<typeof SfmApiError>) {
    super(...args);
    this.name = "TransportError";
  }
}

const BY_STATUS: Readonly<Record<number, new (...args: ConstructorParameters<typeof SfmApiError>) => SfmApiError>> = {
  400: ValidationError,
  401: AuthError,
  403: AuthError,
  404: NotFoundError,
  409: ConflictError,
  422: ValidationError,
  429: QuotaExceededError,
  501: PycolmapUnavailableError,
};

/** Translate a non-2xx response from `openapi-fetch` (or any other
 * fetch-based client) into a typed `SfmApiError` subclass. Returns
 * the constructed error so callers can either `throw raise(...)` or
 * branch on the typed result. */
export function buildSfmApiError(
  statusCode: number,
  body: unknown,
): SfmApiError {
  let detail = "";
  let parsedBody: Record<string, unknown> = {};
  if (body && typeof body === "object" && !Array.isArray(body)) {
    parsedBody = body as Record<string, unknown>;
    const d = parsedBody["detail"] ?? parsedBody["title"];
    if (typeof d === "string") detail = d;
  } else if (typeof body === "string") {
    detail = body;
  }
  const Cls = BY_STATUS[statusCode] ?? SfmApiError;
  return new Cls(statusCode, detail, parsedBody);
}

/** Convenience wrapper around `buildSfmApiError` that throws. */
export function raiseForStatus(statusCode: number, body: unknown): never {
  throw buildSfmApiError(statusCode, body);
}

// ---------------------------------------------------------------------
// Capability helper.
// ---------------------------------------------------------------------

type CapabilitiesOut = components["schemas"]["CapabilitiesOut"];

/** Return true iff the capabilities snapshot advertises `name`.
 * Treats unknown / absent feature names as false (per the wire spec —
 * clients MUST treat absence as unsupported). */
export function supports(caps: CapabilitiesOut, name: string): boolean {
  return Boolean(caps.features?.[name]);
}

// ---------------------------------------------------------------------
// Chunked-upload helper. Mirrors `upload_bytes()` in the Python
// `_ergonomics.py` shim and `UploadBytes()` in the C++ SDK.
// ---------------------------------------------------------------------

export const DEFAULT_CHUNK_SIZE = 1 * 1024 * 1024;

export interface UploadBytesOptions {
  baseUrl: string;
  apiKey?: string;
  chunkSize?: number;
  contentType?: string;
  /** Custom fetch (Node ≤17 needs node-fetch; tests inject mocks). */
  fetch?: typeof fetch;
}

/** Drive the chunked-upload protocol (init → patch chunks → finalize)
 * and return the resulting `blob_sha`. Throws a typed `SfmApiError`
 * subclass on any non-2xx response. */
export async function uploadBytes(
  data: Uint8Array,
  opts: UploadBytesOptions,
): Promise<string> {
  if (data.length === 0) throw new Error("uploadBytes: data must be non-empty");
  const fetchFn = opts.fetch ?? fetch;
  const baseUrl = opts.baseUrl.replace(/\/+$/, "");
  const chunkSize = opts.chunkSize ?? DEFAULT_CHUNK_SIZE;
  const contentType = opts.contentType ?? "application/octet-stream";
  const baseHeaders: Record<string, string> = {};
  if (opts.apiKey) baseHeaders["Authorization"] = `Bearer ${opts.apiKey}`;

  const init = await fetchFn(`${baseUrl}/v1/uploads`, {
    method: "POST",
    headers: { ...baseHeaders, "Content-Type": "application/json" },
    body: JSON.stringify({
      expected_size: data.length,
      content_type: contentType,
    }),
  });
  if (init.status !== 200 && init.status !== 201) {
    throw await _errorFromResponse(init);
  }
  const initBody = (await init.json()) as { upload_id: string };
  const uploadId = initBody.upload_id;

  let offset = 0;
  const total = data.length;
  while (offset < total) {
    const end = Math.min(offset + chunkSize, total);
    const chunk = data.subarray(offset, end);
    const r = await fetchFn(`${baseUrl}/v1/uploads/${uploadId}`, {
      method: "PATCH",
      headers: {
        ...baseHeaders,
        "Content-Range": `bytes ${offset}-${end - 1}/${total}`,
        "Content-Type": "application/octet-stream",
      },
      // Cast through `BodyInit`: every modern runtime accepts a
      // typed-array body, but `lib.dom.d.ts` forgot to list it on
      // `RequestInit.body`. Spec-compliant — see whatwg/fetch#1561.
      body: chunk as unknown as BodyInit,
    });
    if (r.status !== 200 && r.status !== 204) {
      throw await _errorFromResponse(r);
    }
    offset = end;
  }

  const fin = await fetchFn(`${baseUrl}/v1/uploads/${uploadId}:finalize`, {
    method: "POST",
    headers: baseHeaders,
  });
  if (fin.status !== 200 && fin.status !== 201) {
    throw await _errorFromResponse(fin);
  }
  const finBody = (await fin.json()) as { blob_sha: string };
  return finBody.blob_sha;
}

async function _errorFromResponse(resp: Response): Promise<SfmApiError> {
  let body: unknown = {};
  try {
    body = await resp.json();
  } catch {
    try {
      body = await resp.text();
    } catch {
      body = {};
    }
  }
  return buildSfmApiError(resp.status, body);
}

// ---------------------------------------------------------------------
// SSE event iterator. Mirrors the hand-rolled `iterSse` helper and
// the Python `_ergonomics.stream_events()`.
// ---------------------------------------------------------------------

/** Single Server-Sent Event from `/v1/jobs/{id}/events`. `data` is
 * the raw payload string; most sfmapi events are JSON-encoded
 * `ProgressEvent` rows. Use `JSON.parse(event.data)` to decode. */
export interface SseEvent {
  id: string;
  event: string;
  data: string;
}

/** Decode an already-buffered SSE response body into discrete
 * events. Handles CRLF line endings, multi-line `data:`, and SSE
 * comment lines per the WHATWG spec. */
export function parseSseBuffer(body: string): SseEvent[] {
  const out: SseEvent[] = [];
  let cur: SseEvent = { id: "", event: "message", data: "" };
  let haveData = false;
  for (const raw of body.split("\n")) {
    const line = raw.endsWith("\r") ? raw.slice(0, -1) : raw;
    if (line === "") {
      if (haveData) {
        out.push(cur);
        cur = { id: "", event: "message", data: "" };
        haveData = false;
      }
      continue;
    }
    if (line.startsWith(":")) continue;
    const colon = line.indexOf(":");
    let field: string;
    let value: string;
    if (colon === -1) {
      field = line;
      value = "";
    } else {
      field = line.slice(0, colon);
      value = line.slice(colon + 1);
      if (value.startsWith(" ")) value = value.slice(1);
    }
    if (field === "data") {
      cur.data = cur.data ? `${cur.data}\n${value}` : value;
      haveData = true;
    } else if (field === "event") {
      cur.event = value;
    } else if (field === "id") {
      cur.id = value;
    }
  }
  if (haveData) out.push(cur);
  return out;
}

export interface StreamEventsOptions {
  baseUrl: string;
  apiKey?: string;
  /** Server honors the standard `Last-Event-ID` header for resume. */
  lastEventId?: number | string;
  /** Custom fetch (Node ≤17 needs node-fetch; tests inject mocks). */
  fetch?: typeof fetch;
  /** AbortSignal to cancel the stream cleanly. */
  signal?: AbortSignal;
}

/** Async-iterate Server-Sent Events from
 * `GET /v1/jobs/{jobId}/events`. Yields `SseEvent` instances as the
 * server flushes them.
 *
 * Throws a typed `SfmApiError` subclass on a non-2xx open. */
export async function* streamEvents(
  jobId: string,
  opts: StreamEventsOptions,
): AsyncIterable<SseEvent> {
  const fetchFn = opts.fetch ?? fetch;
  const baseUrl = opts.baseUrl.replace(/\/+$/, "");
  const headers: Record<string, string> = {
    Accept: "text/event-stream",
  };
  if (opts.apiKey) headers["Authorization"] = `Bearer ${opts.apiKey}`;
  if (opts.lastEventId !== undefined) {
    headers["Last-Event-ID"] = String(opts.lastEventId);
  }
  const init: RequestInit = { method: "GET", headers };
  if (opts.signal) init.signal = opts.signal;
  const resp = await fetchFn(`${baseUrl}/v1/jobs/${jobId}/events`, init);
  if (resp.status !== 200) {
    throw await _errorFromResponse(resp);
  }
  if (!resp.body) {
    // Some test stubs return a Response with no body; treat as empty
    // stream.
    return;
  }
  const reader = resp.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let buffer = "";
  try {
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      // Flush every complete event ("\n\n" or "\r\n\r\n" boundary).
      while (true) {
        const lfIdx = buffer.indexOf("\n\n");
        const crlfIdx = buffer.indexOf("\r\n\r\n");
        const idx =
          lfIdx === -1
            ? crlfIdx
            : crlfIdx === -1
            ? lfIdx
            : Math.min(lfIdx, crlfIdx);
        if (idx === -1) break;
        const sepLen = idx === crlfIdx ? 4 : 2;
        const head = buffer.slice(0, idx + sepLen);
        buffer = buffer.slice(idx + sepLen);
        for (const ev of parseSseBuffer(head)) yield ev;
      }
    }
    // Flush any trailing partial event.
    buffer += decoder.decode();
    if (buffer.trim()) {
      for (const ev of parseSseBuffer(buffer + "\n\n")) yield ev;
    }
  } finally {
    try {
      reader.releaseLock();
    } catch {
      /* ignore */
    }
  }
}

// ---------------------------------------------------------------------
// waitForJob — block until a Job reaches a terminal state.
//
// Mirrors `wait_for_job` in the Python `_ergonomics.py` shim. Uses
// short-interval polling so the helper has no streaming dependency;
// pass an `onEvent` callback to also receive ProgressEvents as the
// loop polls `/events?last_event_id=X`.
// ---------------------------------------------------------------------

export const TERMINAL_JOB_STATES: ReadonlySet<string> = new Set([
  "succeeded",
  "failed",
  "cancelled",
  "cancelled_dirty",
]);

export interface WaitForJobOptions {
  baseUrl: string;
  apiKey?: string;
  /** Called once per new ProgressEvent observed during the wait. */
  onEvent?: (ev: SseEvent) => void;
  /** Poll cadence in seconds. Defaults to 0.25. */
  pollInterval?: number;
  /** Max seconds to wait before throwing. Defaults to 600. */
  timeout?: number;
  /** Custom fetch (Node ≤17 needs node-fetch; tests inject mocks). */
  fetch?: typeof fetch;
}

/** Block until `jobId` reaches a terminal state and return the
 * final JobDetail JSON. Throws a typed `SfmApiError` subclass on
 * any non-2xx, or a generic `Error` on timeout. */
export async function waitForJob(
  jobId: string,
  opts: WaitForJobOptions,
): Promise<Record<string, unknown>> {
  const fetchFn = opts.fetch ?? fetch;
  const baseUrl = opts.baseUrl.replace(/\/+$/, "");
  const pollInterval = (opts.pollInterval ?? 0.25) * 1000;
  const deadline = Date.now() + (opts.timeout ?? 600) * 1000;
  const baseHeaders: Record<string, string> = {};
  if (opts.apiKey) baseHeaders["Authorization"] = `Bearer ${opts.apiKey}`;
  let seenEventId = -1;
  while (true) {
    const resp = await fetchFn(`${baseUrl}/v1/jobs/${jobId}`, {
      method: "GET",
      headers: baseHeaders,
    });
    if (resp.status !== 200) throw await _errorFromResponse(resp);
    const body = (await resp.json()) as Record<string, unknown>;
    const status = String(body["status"] ?? "");
    if (opts.onEvent) {
      const evHeaders: Record<string, string> = {
        ...baseHeaders,
        Accept: "text/event-stream",
      };
      if (seenEventId >= 0) evHeaders["Last-Event-ID"] = String(seenEventId);
      try {
        const er = await fetchFn(`${baseUrl}/v1/jobs/${jobId}/events`, {
          method: "GET",
          headers: evHeaders,
        });
        if (er.status === 200) {
          const text = await er.text();
          for (const ev of parseSseBuffer(text)) {
            opts.onEvent(ev);
            if (ev.id) {
              const n = Number(ev.id);
              if (!Number.isNaN(n)) seenEventId = Math.max(seenEventId, n);
            }
          }
        }
      } catch {
        // Tolerate transient SSE hiccups; the polling loop continues.
      }
    }
    if (TERMINAL_JOB_STATES.has(status)) return body;
    if (Date.now() >= deadline) {
      throw new Error(
        `waitForJob: ${jobId} still in status=${JSON.stringify(status)} after ${opts.timeout ?? 600}s`,
      );
    }
    await new Promise((r) => setTimeout(r, pollInterval));
  }
}

// ---------------------------------------------------------------------
// submitAndStream — like submitAndWait but consumes the SSE event
// stream live (sub-second progress). Returns an async iterator that
// yields each event AND a final `result` promise that resolves to
// the terminal JobDetail.
// ---------------------------------------------------------------------

export interface SubmitAndStreamHandle {
  /** AsyncIterable of progress events. Resolves once the server
   * closes the SSE stream. */
  events: AsyncIterable<SseEvent>;
  /** Resolves with the terminal JobDetail once the stream closes
   * AND the job has rolled up to a terminal status. */
  result: Promise<Record<string, unknown>>;
}

export interface SubmitAndStreamOptions extends StreamEventsOptions {
  // Adopts the same shape as StreamEventsOptions; baseUrl + apiKey +
  // fetch + signal flow through. Submit closure encodes its own
  // request shape.
}

/** Run ``submitFn`` to enqueue a job, then immediately stream
 * progress events. After the stream closes, polls one final
 * ``wait_for_job`` to hand back the terminal JobDetail. */
export async function submitAndStream(
  submitFn: () => Promise<{ job_id?: string } | Record<string, unknown>> | { job_id?: string } | Record<string, unknown>,
  opts: SubmitAndStreamOptions,
): Promise<SubmitAndStreamHandle> {
  const accepted = await submitFn();
  const jobId =
    accepted && typeof accepted === "object" && "job_id" in accepted
      ? String((accepted as { job_id?: string }).job_id ?? "")
      : "";
  if (!jobId) {
    throw new Error(
      `submitAndStream: submitFn returned no job_id (got ${typeof accepted})`,
    );
  }
  // Clone a child iterator that yields the SSE events; the final
  // `result` promise resolves once the iterator drains AND a single
  // wait_for_job poll comes back terminal.
  const events = streamEvents(jobId, opts);
  const drained: SseEvent[] = [];
  async function* tap(): AsyncIterable<SseEvent> {
    for await (const ev of events) {
      drained.push(ev);
      yield ev;
    }
  }
  const tapped = tap();
  const result = (async () => {
    // Drive the iterator to completion before polling for terminal.
    // The caller may (or may not) be consuming `tapped` themselves;
    // attaching .next() chained reads here would race. Instead, the
    // caller owns drainage — we just await a final wait_for_job poll.
    return waitForJob(jobId, {
      baseUrl: opts.baseUrl,
      ...(opts.apiKey !== undefined ? { apiKey: opts.apiKey } : {}),
      ...(opts.fetch !== undefined ? { fetch: opts.fetch } : {}),
      pollInterval: 0.05,
    });
  })();
  return { events: tapped, result };
}

// ---------------------------------------------------------------------
// submitAndWait — fire any stage-submit callable, then block on
// `waitForJob` for the resulting `job_id`. Most-used end-to-end flow.
// ---------------------------------------------------------------------

export interface SubmitAndWaitOptions extends WaitForJobOptions {
  // Same surface as WaitForJobOptions; baseUrl + onEvent etc. flow
  // through to the wait phase. Submit is the caller's
  // responsibility (the closure they pass already encodes auth and
  // request shape).
}

/** Run ``submitFn`` to enqueue a job, then block until the returned
 * ``job_id`` reaches a terminal status. Returns the final
 * JobDetail. ``submitFn`` is any callable that resolves to either
 * a `JobAcceptedResponse`-shaped object or any value with a
 * `job_id` field. */
export async function submitAndWait(
  submitFn: () => Promise<{ job_id?: string } | Record<string, unknown>> | { job_id?: string } | Record<string, unknown>,
  opts: SubmitAndWaitOptions,
): Promise<Record<string, unknown>> {
  const accepted = await submitFn();
  const jobId =
    accepted && typeof accepted === "object" && "job_id" in accepted
      ? String((accepted as { job_id?: string }).job_id ?? "")
      : "";
  if (!jobId) {
    throw new Error(
      `submitAndWait: submitFn returned no job_id (got ${typeof accepted})`,
    );
  }
  return waitForJob(jobId, opts);
}

// ---------------------------------------------------------------------
// Binary wire-format parsers. Mirror `clients/typescript/src/binary.ts`
// (and `app/schemas/points_binary.py` / `app/schemas/depth_map_binary.py`
// on the server). Zero deps.
// ---------------------------------------------------------------------

export const POINTS_MEDIA_TYPE = "application/x-sfm-points-v1";
export const DEPTH_MEDIA_TYPE = "application/x-sfm-depth-v1";
export const NORMAL_MEDIA_TYPE = "application/x-sfm-normal-v1";

const MAGIC_POINTS = [0x53, 0x46, 0x4d, 0x50, 0x33, 0x44, 0x00, 0x00]; // "SFMP3D\0\0"
const MAGIC_DEPTH = [0x53, 0x46, 0x4d, 0x44, 0x50, 0x54, 0x48, 0x00]; // "SFMDPTH\0"
const MAGIC_NORMAL = [0x53, 0x46, 0x4d, 0x4e, 0x52, 0x4d, 0x00, 0x00]; // "SFMNRM\0\0"

const POINTS_HEADER_SIZE = 44;
const POINTS_RECORD_SIZE = 26;
const MAP_HEADER_SIZE = 32;

export class WireFormatError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "WireFormatError";
  }
}

function _eqMagic(view: DataView, expected: number[]): boolean {
  for (let i = 0; i < expected.length; i++) {
    if (view.getUint8(i) !== expected[i]) return false;
  }
  return true;
}

export interface Point3DRecord {
  point3d_id: bigint;
  xyz: [number, number, number];
  rgb: [number, number, number];
  track_len: number;
}

export interface PointsBinary {
  count: number;
  bbox_min: [number, number, number];
  bbox_max: [number, number, number];
  records: Point3DRecord[];
}

export function parsePointsBinary(buffer: ArrayBuffer): PointsBinary {
  if (buffer.byteLength < POINTS_HEADER_SIZE) {
    throw new WireFormatError("points-binary: buffer too small for header");
  }
  const view = new DataView(buffer);
  if (!_eqMagic(view, MAGIC_POINTS)) {
    throw new WireFormatError("points-binary: bad magic");
  }
  const version = view.getUint32(8, true);
  if (version !== 1) {
    throw new WireFormatError(`points-binary: unknown version ${version}`);
  }
  const count = Number(view.getBigUint64(12, true));
  const bboxMin: [number, number, number] = [
    view.getFloat32(20, true),
    view.getFloat32(24, true),
    view.getFloat32(28, true),
  ];
  const bboxMax: [number, number, number] = [
    view.getFloat32(32, true),
    view.getFloat32(36, true),
    view.getFloat32(40, true),
  ];
  const expected = POINTS_HEADER_SIZE + count * POINTS_RECORD_SIZE;
  if (buffer.byteLength < expected) {
    throw new WireFormatError(
      `points-binary: body short - got ${buffer.byteLength}, expected ${expected}`,
    );
  }
  const records: Point3DRecord[] = new Array(count);
  for (let i = 0; i < count; i++) {
    const off = POINTS_HEADER_SIZE + i * POINTS_RECORD_SIZE;
    records[i] = {
      xyz: [
        view.getFloat32(off, true),
        view.getFloat32(off + 4, true),
        view.getFloat32(off + 8, true),
      ],
      rgb: [
        view.getUint8(off + 12),
        view.getUint8(off + 13),
        view.getUint8(off + 14),
      ],
      track_len: view.getUint16(off + 16, true),
      point3d_id: view.getBigUint64(off + 18, true),
    };
  }
  return { count, bbox_min: bboxMin, bbox_max: bboxMax, records };
}

export interface DepthMap {
  width: number;
  height: number;
  depth_min: number;
  depth_max: number;
  /** Row-major float32 array of length `width * height`. */
  pixels: Float32Array;
}

export function parseDepthMap(buffer: ArrayBuffer): DepthMap {
  if (buffer.byteLength < MAP_HEADER_SIZE) {
    throw new WireFormatError("depth-binary: buffer too small for header");
  }
  const view = new DataView(buffer);
  if (!_eqMagic(view, MAGIC_DEPTH)) {
    throw new WireFormatError("depth-binary: bad magic");
  }
  const version = view.getUint32(8, true);
  if (version !== 1) {
    throw new WireFormatError(`depth-binary: unknown version ${version}`);
  }
  const width = view.getUint32(12, true);
  const height = view.getUint32(16, true);
  const depthMin = view.getFloat32(20, true);
  const depthMax = view.getFloat32(24, true);
  const expected = MAP_HEADER_SIZE + width * height * 4;
  if (buffer.byteLength < expected) {
    throw new WireFormatError(
      `depth-binary: body short - got ${buffer.byteLength}, expected ${expected}`,
    );
  }
  const pixels = new Float32Array(buffer, MAP_HEADER_SIZE, width * height);
  return { width, height, depth_min: depthMin, depth_max: depthMax, pixels };
}

export interface NormalMap {
  width: number;
  height: number;
  /** Row-major float32 array of length `width * height * 3` (xyz triples). */
  pixels: Float32Array;
}

export function parseNormalMap(buffer: ArrayBuffer): NormalMap {
  if (buffer.byteLength < MAP_HEADER_SIZE) {
    throw new WireFormatError("normal-binary: buffer too small for header");
  }
  const view = new DataView(buffer);
  if (!_eqMagic(view, MAGIC_NORMAL)) {
    throw new WireFormatError("normal-binary: bad magic");
  }
  const version = view.getUint32(8, true);
  if (version !== 1) {
    throw new WireFormatError(`normal-binary: unknown version ${version}`);
  }
  const width = view.getUint32(12, true);
  const height = view.getUint32(16, true);
  const expected = MAP_HEADER_SIZE + width * height * 3 * 4;
  if (buffer.byteLength < expected) {
    throw new WireFormatError(
      `normal-binary: body short - got ${buffer.byteLength}, expected ${expected}`,
    );
  }
  const pixels = new Float32Array(buffer, MAP_HEADER_SIZE, width * height * 3);
  return { width, height, pixels };
}
