// Cliente HTTP central do VentureOps AI.
//
// - base da API por ambiente (VITE_API_BASE_URL; por defeito `/api`, mesma origem);
// - envia o cookie de sessão (credentials: same-origin) e o token CSRF
//   (cabeçalho X-CSRFToken) nas operações mutáveis;
// - tratamento central de erros (ApiError com estado);
// - de-duplicação de GETs idênticos em curso;
// - sinaliza 401/403 (sessão expirada) a um handler registado.
//
// Sem credenciais persistidas no browser (nada em localStorage/sessionStorage).

export class ApiError extends Error {
  readonly status?: number;

  constructor(message: string, status?: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "/api").replace(
  /\/+$/,
  "",
);

const UNSAFE_METHODS = new Set(["POST", "PUT", "PATCH", "DELETE"]);

let unauthorizedHandler: (() => void) | null = null;

export function setUnauthorizedHandler(handler: (() => void) | null): void {
  unauthorizedHandler = handler;
}

function getCookie(name: string): string | null {
  const match = document.cookie.match(
    new RegExp("(?:^|; )" + name + "=([^;]*)"),
  );
  return match ? decodeURIComponent(match[1]) : null;
}

const inFlightGets = new Map<string, Promise<unknown>>();

async function execute<T>(
  method: string,
  path: string,
  body?: unknown,
): Promise<T> {
  const url = `${API_BASE_URL}${path}`;
  const headers: Record<string, string> = { Accept: "application/json" };
  if (body !== undefined) headers["Content-Type"] = "application/json";
  if (UNSAFE_METHODS.has(method)) {
    const token = getCookie("csrftoken");
    if (token) headers["X-CSRFToken"] = token;
  }

  let response: Response;
  try {
    response = await fetch(url, {
      method,
      headers,
      credentials: "same-origin",
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new ApiError("Falha de comunicação com o servidor.");
  }

  if (response.status === 401 || response.status === 403) {
    unauthorizedHandler?.();
  }
  if (!response.ok) {
    throw new ApiError(mensagemDeErro(response.status), response.status);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}

function mensagemDeErro(status: number): string {
  if (status === 401 || status === 403) return "Sessão inválida ou expirada.";
  if (status >= 500) return "Erro no servidor. Tente novamente.";
  return `O servidor respondeu com o estado ${status}.`;
}

export function apiGet<T>(path: string): Promise<T> {
  const key = `GET ${path}`;
  const existing = inFlightGets.get(key);
  if (existing) return existing as Promise<T>;
  const promise = execute<T>("GET", path);
  inFlightGets.set(key, promise);
  return promise.finally(() => inFlightGets.delete(key)) as Promise<T>;
}

export function apiPost<T>(path: string, body?: unknown): Promise<T> {
  return execute<T>("POST", path, body);
}

// POST que NÃO lança em respostas de negócio esperadas (ex.: 409 do pacote de
// contexto, cujo corpo transporta a análise de política). Devolve estado + corpo;
// só lança `ApiError` em falha de comunicação. O chamador decide pelo estado.
export async function apiPostWithStatus<T>(
  path: string,
  body?: unknown,
): Promise<{ status: number; data: T }> {
  const url = `${API_BASE_URL}${path}`;
  const headers: Record<string, string> = {
    Accept: "application/json",
    "Content-Type": "application/json",
  };
  const token = getCookie("csrftoken");
  if (token) headers["X-CSRFToken"] = token;

  let response: Response;
  try {
    response = await fetch(url, {
      method: "POST",
      headers,
      credentials: "same-origin",
      body: JSON.stringify(body ?? {}),
    });
  } catch {
    throw new ApiError("Falha de comunicação com o servidor.");
  }
  if (response.status === 401 || response.status === 403) {
    unauthorizedHandler?.();
  }
  const data =
    response.status === 204 ? (undefined as T) : ((await response.json()) as T);
  return { status: response.status, data };
}

// POST que devolve um binário (descarga do pacote). Lê o nome do ficheiro do
// Content-Disposition (gerado/validado pelo servidor) e o checksum do header.
export async function apiPostBlob(
  path: string,
  body?: unknown,
): Promise<{ blob: Blob; filename: string; checksum: string }> {
  const url = `${API_BASE_URL}${path}`;
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  const token = getCookie("csrftoken");
  if (token) headers["X-CSRFToken"] = token;

  let response: Response;
  try {
    response = await fetch(url, {
      method: "POST",
      headers,
      credentials: "same-origin",
      body: JSON.stringify(body ?? {}),
    });
  } catch {
    throw new ApiError("Falha de comunicação com o servidor.");
  }
  if (response.status === 401 || response.status === 403) {
    unauthorizedHandler?.();
  }
  if (!response.ok) {
    throw new ApiError(mensagemDeErro(response.status), response.status);
  }
  const blob = await response.blob();
  const disposition = response.headers.get("Content-Disposition") ?? "";
  const match = disposition.match(/filename="([^"]+)"/);
  const filename = match ? match[1] : "pacote-contexto";
  const checksum = response.headers.get("X-Package-Checksum") ?? "";
  return { blob, filename, checksum };
}

export function apiPatch<T>(path: string, body?: unknown): Promise<T> {
  return execute<T>("PATCH", path, body);
}
