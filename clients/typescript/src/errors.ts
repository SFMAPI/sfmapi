// Client-side error hierarchy. Mirrors the server's `app.core.errors`.

export interface ProblemJson {
  type?: string;
  title?: string;
  status?: number;
  detail?: string;
  instance?: string;
  [extra: string]: unknown;
}

export class SfmApiError extends Error {
  statusCode: number;
  problem: ProblemJson;
  response: Response | undefined;

  constructor(
    message: string,
    opts: { statusCode?: number; problem?: ProblemJson; response?: Response } = {},
  ) {
    super(message);
    this.name = new.target.name;
    this.statusCode = opts.statusCode ?? opts.problem?.status ?? 0;
    this.problem = opts.problem ?? {};
    this.response = opts.response;
    // Preserve prototype chain across transpilation targets.
    Object.setPrototypeOf(this, new.target.prototype);
  }
}

export class NotFoundError extends SfmApiError {}
export class ConflictError extends SfmApiError {}
export class ValidationError extends SfmApiError {}
export class AuthError extends SfmApiError {}
export class QuotaExceededError extends SfmApiError {}
export class StorageError extends SfmApiError {}
export class PycolmapUnavailableError extends SfmApiError {}
export class TransportError extends SfmApiError {}

const STATUS_MAP: Record<number, new (msg: string, opts?: object) => SfmApiError> = {
  403: AuthError,
  404: NotFoundError,
  409: ConflictError,
  413: QuotaExceededError,
  422: ValidationError,
  429: QuotaExceededError,
  501: PycolmapUnavailableError,
  507: StorageError,
};

export async function raiseForResponse(resp: Response): Promise<void> {
  if (resp.ok) return;
  let problem: ProblemJson = {};
  const contentType = resp.headers.get("content-type") ?? "";
  if (contentType.includes("json")) {
    try {
      problem = (await resp.clone().json()) as ProblemJson;
    } catch {
      problem = { title: resp.statusText, status: resp.status };
    }
  }
  const message =
    problem.detail ?? problem.title ?? (await resp.clone().text()) ?? resp.statusText;
  const Cls = STATUS_MAP[resp.status] ?? SfmApiError;
  throw new Cls(message, { statusCode: resp.status, problem, response: resp });
}
