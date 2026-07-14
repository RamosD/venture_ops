import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { FunctionsWorkspace } from "./FunctionsWorkspace";

function json(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

const PAGE_SIZE = 20;

interface Fn {
  id: string;
  organisation: string;
  name: string;
  actor_type: string;
  purpose: string;
  responsibilities: string;
  constraints: string;
  instruction_document: string | null;
  requires_approval: boolean;
  status: string;
  version: number;
  created_at: string;
  updated_at: string;
}

interface MockState {
  fns: Fn[];
  seq: number;
}

function base(overrides: Partial<Fn> = {}): Fn {
  return {
    id: "fn-1",
    organisation: "org-1",
    name: "Analista de produto",
    actor_type: "human",
    purpose: "Redigir documentação",
    responsibilities: "Produz rascunhos",
    constraints: "",
    instruction_document: null,
    requires_approval: false,
    status: "active",
    version: 1,
    created_at: "2026-07-13T09:00:00Z",
    updated_at: "2026-07-13T09:00:00Z",
    ...overrides,
  };
}

function installFetch(state: MockState) {
  const fetchMock = vi.fn(async (rawUrl: string, init: RequestInit = {}) => {
    const method = init.method ?? "GET";
    const url = new URL(rawUrl, "http://local");
    const path = url.pathname;
    const body = init.body ? JSON.parse(init.body as string) : {};

    // Documentos de instruções para o formulário.
    if (path.endsWith("/v1/documents") && method === "GET") {
      return json({ results: [], count: 0, page: 1, page_size: 20, num_pages: 1 });
    }

    if (path.endsWith("/v1/functions") && method === "GET") {
      const status = url.searchParams.get("status") ?? "active";
      const actorType = url.searchParams.get("actor_type");
      const page = parseInt(url.searchParams.get("page") ?? "1", 10);
      let fns = [...state.fns];
      if (status !== "all") fns = fns.filter((f) => f.status === status);
      if (actorType) fns = fns.filter((f) => f.actor_type === actorType);
      const count = fns.length;
      const num_pages = Math.max(1, Math.ceil(count / PAGE_SIZE));
      const start = (page - 1) * PAGE_SIZE;
      return json({
        results: fns.slice(start, start + PAGE_SIZE),
        count,
        page,
        page_size: PAGE_SIZE,
        num_pages,
      });
    }
    if (path.endsWith("/v1/functions") && method === "POST") {
      // Política requires_approval: ai/hybrid → sempre true (servidor).
      const forced = body.actor_type === "ai" || body.actor_type === "hybrid";
      state.seq += 1;
      const fn = base({
        id: `fn-${state.seq}`,
        name: body.name,
        actor_type: body.actor_type,
        purpose: body.purpose,
        responsibilities: body.responsibilities,
        constraints: body.constraints ?? "",
        instruction_document: body.instruction_document ?? null,
        requires_approval: forced ? true : Boolean(body.requires_approval),
      });
      state.fns.push(fn);
      return json(fn, 201);
    }

    const m = path.match(
      /\/v1\/functions\/([^/]+?)(?:\/(deactivate|reactivate))?$/,
    );
    if (m) {
      const [, id, action] = m;
      const fn = state.fns.find((f) => f.id === id);
      if (!fn) return json({ detail: "nf" }, 404);
      if (!action && method === "GET") return json(fn);
      if (!action && method === "PATCH") {
        if (body.expected_version !== fn.version)
          return json({ detail: "conflito" }, 409);
        Object.assign(fn, {
          name: body.name ?? fn.name,
          actor_type: body.actor_type ?? fn.actor_type,
          purpose: body.purpose ?? fn.purpose,
          responsibilities: body.responsibilities ?? fn.responsibilities,
          constraints: body.constraints ?? fn.constraints,
          requires_approval:
            body.requires_approval ?? fn.requires_approval,
          version: fn.version + 1,
        });
        return json(fn);
      }
      if (action && method === "POST") {
        if (body.expected_version !== fn.version)
          return json({ detail: "conflito" }, 409);
        const wantsActive = action === "reactivate";
        const isActive = fn.status === "active";
        if (wantsActive === isActive) return json({ detail: "transição" }, 409);
        fn.status = wantsActive ? "active" : "inactive";
        fn.version += 1;
        return json(fn);
      }
    }
    return json({ detail: "nf" }, 404);
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

async function openFn(name: string) {
  fireEvent.click(await screen.findByRole("button", { name }));
  await screen.findByRole("heading", { name, level: 3 });
}

describe("FunctionsWorkspace (funções)", () => {
  beforeEach(() => {
    document.cookie = "csrftoken=t";
  });
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("mostra estado vazio quando não há funções", async () => {
    installFetch({ fns: [], seq: 0 });
    render(<FunctionsWorkspace />);
    await screen.findByText(/ainda não há funções/i, undefined, { timeout: 5000 });
  });

  // 21 (parte 1) — UI cria função
  it("cria uma função humana", async () => {
    const state: MockState = { fns: [], seq: 0 };
    installFetch(state);
    render(<FunctionsWorkspace />);
    fireEvent.click(await screen.findByRole("button", { name: /nova função/i }));

    const typeSelect = screen.getByLabelText("Tipo") as HTMLSelectElement;
    expect(typeSelect.options).toHaveLength(3); // três tipos fechados
    fireEvent.change(screen.getByLabelText("Nome"), {
      target: { value: "Analista IA" },
    });
    fireEvent.change(screen.getByLabelText("Propósito"), {
      target: { value: "Rever conteúdo" },
    });
    fireEvent.change(screen.getByLabelText("Responsabilidades"), {
      target: { value: "Analisa" },
    });
    fireEvent.click(screen.getByRole("button", { name: /criar função/i }));

    await screen.findByRole("heading", { name: "Analista IA", level: 3 });
  });

  // política requires_approval na UI: ai força aprovação (checkbox marcada e desactivada)
  it("força aprovação humana para funções de IA", async () => {
    installFetch({ fns: [], seq: 0 });
    render(<FunctionsWorkspace />);
    fireEvent.click(await screen.findByRole("button", { name: /nova função/i }));

    const approval = screen.getByLabelText(/requer aprovação humana/i) as HTMLInputElement;
    expect(approval.checked).toBe(false);
    expect(approval.disabled).toBe(false);
    fireEvent.change(screen.getByLabelText("Tipo"), { target: { value: "ai" } });
    expect(approval.checked).toBe(true);
    expect(approval.disabled).toBe(true);
  });

  // 21 (parte 2) — UI edita função
  it("edita uma função existente", async () => {
    installFetch({ fns: [base({ id: "fn-1", name: "Antes" })], seq: 1 });
    render(<FunctionsWorkspace />);
    await openFn("Antes");
    fireEvent.click(screen.getByRole("button", { name: "Editar" }));
    fireEvent.change(screen.getByLabelText("Nome"), {
      target: { value: "Depois" },
    });
    fireEvent.click(screen.getByRole("button", { name: /guardar alterações/i }));
    await screen.findByRole("heading", { name: "Depois", level: 3 });
  });

  // 21 (parte 3) — UI inactiva com confirmação
  it("inactiva uma função com confirmação explícita", async () => {
    installFetch({ fns: [base({ id: "fn-1", name: "Para inactivar" })], seq: 1 });
    render(<FunctionsWorkspace />);
    await openFn("Para inactivar");
    fireEvent.click(screen.getByRole("button", { name: /^inactivar$/i }));
    // Pediu confirmação; ainda activa.
    expect(screen.getByText("Activa")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /confirmar inactivação/i }));
    await waitFor(() =>
      expect(screen.getByTestId("inactive-badge")).toBeInTheDocument(),
    );
  });

  // 21 (parte 4) — UI reactiva
  it("reactiva uma função inactiva", async () => {
    installFetch({
      fns: [base({ id: "fn-1", name: "Inactiva", status: "inactive" })],
      seq: 1,
    });
    render(<FunctionsWorkspace />);
    // Filtro por defeito é "active"; muda para ver inactivas.
    fireEvent.change(await screen.findByLabelText("Estado"), {
      target: { value: "inactive" },
    });
    await openFn("Inactiva");
    fireEvent.click(screen.getByRole("button", { name: /reactivar/i }));
    await waitFor(() =>
      expect(screen.getByText("Activa")).toBeInTheDocument(),
    );
  });

  // 16 — função inactive não aparece na lista active (default)
  it("não mostra funções inactivas na lista activa por defeito", async () => {
    installFetch({
      fns: [
        base({ id: "a", name: "ActivaX", status: "active" }),
        base({ id: "b", name: "InactivaY", status: "inactive" }),
      ],
      seq: 2,
    });
    render(<FunctionsWorkspace />);
    await screen.findByRole("button", { name: "ActivaX" });
    expect(screen.queryByRole("button", { name: "InactivaY" })).toBeNull();
    // Todas: aparece a inactiva também.
    fireEvent.change(screen.getByLabelText("Estado"), { target: { value: "all" } });
    await screen.findByRole("button", { name: "InactivaY" });
  });

  it("filtra por tipo de actor", async () => {
    installFetch({
      fns: [
        base({ id: "a", name: "Humana1", actor_type: "human" }),
        base({ id: "b", name: "IA1", actor_type: "ai", requires_approval: true }),
      ],
      seq: 2,
    });
    render(<FunctionsWorkspace />);
    await screen.findByRole("button", { name: "Humana1" });
    fireEvent.change(screen.getByLabelText("Tipo"), { target: { value: "ai" } });
    await waitFor(() =>
      expect(screen.queryByRole("button", { name: "Humana1" })).toBeNull(),
    );
    expect(screen.getByRole("button", { name: "IA1" })).toBeInTheDocument();
  });
});
