import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { App } from "../App";

const USER = { id: "u1", email: "owner@x.pt", name: "Dono" };

function json(data: unknown, status = 200): Response {
  return new Response(status === 204 ? null : JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

function createBackend() {
  let authed = false;
  const fetchMock = vi.fn(async (url: string, init: RequestInit = {}) => {
    const method = init.method ?? "GET";
    if (url.endsWith("/v1/auth/csrf")) return json({ detail: "ok" });
    if (url.endsWith("/v1/auth/session")) {
      return json(authed ? { authenticated: true, user: USER } : { authenticated: false });
    }
    if (url.endsWith("/v1/auth/login") && method === "POST") {
      const body = JSON.parse(init.body as string);
      if (body.email === USER.email && body.password === "correct") {
        authed = true;
        return json(USER);
      }
      return json({ detail: "Credenciais inválidas." }, 401);
    }
    if (url.endsWith("/v1/auth/logout") && method === "POST") {
      authed = false;
      return json(null, 204);
    }
    if (url.endsWith("/v1/profile")) return json(USER);
    if (url.endsWith("/v1/organisation")) {
      return json({ organisation: null, onboarding_required: true });
    }
    if (url.endsWith("/system/ping")) return json({ status: "ok" });
    return json({ detail: "not found" }, 404);
  });
  return { fetchMock, setExpired: () => (authed = false) };
}

async function signInWith(email: string, password: string) {
  fireEvent.change(await screen.findByLabelText("Email"), {
    target: { value: email },
  });
  fireEvent.change(screen.getByLabelText("Palavra-passe"), {
    target: { value: password },
  });
  fireEvent.click(screen.getByRole("button", { name: /entrar/i }));
}

describe("Autenticação pela interface (e2e mínimo)", () => {
  beforeEach(() => {
    document.cookie = "csrftoken=test-token";
  });
  afterEach(() => {
    vi.restoreAllMocks();
    window.localStorage.clear();
    window.sessionStorage.clear();
  });

  it("mostra o login e não a área autenticada quando anónimo", async () => {
    vi.stubGlobal("fetch", createBackend().fetchMock);
    render(<App />);
    expect(await screen.findByRole("button", { name: /entrar/i })).toBeInTheDocument();
    expect(screen.queryByText("Área autenticada")).not.toBeInTheDocument();
  });

  it("login → área autenticada → logout", async () => {
    vi.stubGlobal("fetch", createBackend().fetchMock);
    render(<App />);
    await signInWith(USER.email, "correct");
    expect(await screen.findByText("Área autenticada")).toBeInTheDocument();
    expect(screen.getByText(USER.email)).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /terminar sessão/i }));
    expect(await screen.findByRole("button", { name: /entrar/i })).toBeInTheDocument();
  });

  it("login inválido mostra erro genérico e mantém o login", async () => {
    vi.stubGlobal("fetch", createBackend().fetchMock);
    render(<App />);
    await signInWith(USER.email, "errada");
    expect(await screen.findByRole("alert")).toHaveTextContent("Credenciais inválidas.");
    expect(screen.getByRole("button", { name: /entrar/i })).toBeInTheDocument();
  });

  it("envia o token CSRF no login", async () => {
    const backend = createBackend();
    vi.stubGlobal("fetch", backend.fetchMock);
    render(<App />);
    await signInWith(USER.email, "correct");
    await screen.findByText("Área autenticada");
    const loginCall = backend.fetchMock.mock.calls.find(
      ([url, init]) =>
        String(url).endsWith("/v1/auth/login") && init?.method === "POST",
    );
    expect(loginCall).toBeDefined();
    const headers = (loginCall![1] as RequestInit).headers as Record<string, string>;
    expect(headers["X-CSRFToken"]).toBe("test-token");
  });

  it("não persiste credenciais no browser", async () => {
    vi.stubGlobal("fetch", createBackend().fetchMock);
    render(<App />);
    await signInWith(USER.email, "correct");
    await screen.findByText("Área autenticada");
    expect(window.localStorage.length).toBe(0);
    expect(window.sessionStorage.length).toBe(0);
  });

  it("trata a sessão expirada", async () => {
    const backend = createBackend();
    vi.stubGlobal("fetch", backend.fetchMock);
    render(<App />);
    await signInWith(USER.email, "correct");
    await screen.findByText("Área autenticada");
    backend.setExpired();
    fireEvent.click(screen.getByRole("button", { name: /verificar sessão/i }));
    expect(await screen.findByText(/sessão expirou/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /entrar/i })).toBeInTheDocument();
  });
});
