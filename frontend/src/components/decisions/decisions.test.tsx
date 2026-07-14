import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { DecisionSection } from "./DecisionSection";

function json(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

const PRODUCT_ID = "prod-1";
const PAGE_SIZE = 20;

interface Dec {
  id: string;
  organisation: string;
  title: string;
  context: string;
  decision_text: string;
  responsible: string;
  decided_at: string;
  impact: string;
  status: "active" | "superseded";
  product: string | null;
  detail_document: string | null;
  supersedes: string | null;
  replaced_by: string | null;
  version: number;
  created_at: string;
  updated_at: string;
}

interface MockState {
  decs: Dec[];
  seq: number;
}

function newDecision(state: MockState, body: Record<string, unknown>): Dec {
  state.seq += 1;
  const id = `dec-${state.seq}`;
  const dec: Dec = {
    id,
    organisation: "org-1",
    title: (body.title as string) ?? "Decisão",
    context: (body.context as string) ?? "",
    decision_text: (body.decision_text as string) ?? "",
    responsible: "user-1",
    decided_at: "2026-07-13T09:00:00Z",
    impact: (body.impact as string) ?? "",
    status: "active",
    product: (body.product as string) ?? null,
    detail_document: (body.detail_document as string) ?? null,
    supersedes: null,
    replaced_by: null,
    version: 1,
    created_at: "2026-07-13T09:00:00Z",
    updated_at: "2026-07-13T09:00:00Z",
  };
  state.decs.push(dec);
  return dec;
}

function installFetch(state: MockState) {
  const fetchMock = vi.fn(async (rawUrl: string, init: RequestInit = {}) => {
    const method = init.method ?? "GET";
    const url = new URL(rawUrl, "http://local");
    const path = url.pathname;
    const body = init.body ? JSON.parse(init.body as string) : {};

    // Opções de documento de detalhe (o formulário procura-as).
    if (path.endsWith("/v1/documents") && method === "GET") {
      return json({
        results: [],
        count: 0,
        page: 1,
        page_size: 20,
        num_pages: 1,
      });
    }

    if (path.endsWith("/v1/decisions") && method === "GET") {
      const status = url.searchParams.get("status");
      const page = parseInt(url.searchParams.get("page") ?? "1", 10);
      let items = state.decs.filter((d) => d.product === PRODUCT_ID);
      if (status) items = items.filter((d) => d.status === status);
      const count = items.length;
      const num_pages = Math.max(1, Math.ceil(count / PAGE_SIZE));
      const start = (page - 1) * PAGE_SIZE;
      return json({
        results: items.slice(start, start + PAGE_SIZE),
        count,
        page,
        page_size: PAGE_SIZE,
        num_pages,
      });
    }
    if (path.endsWith("/v1/decisions") && method === "POST") {
      return json(newDecision(state, body), 201);
    }

    const m = path.match(/\/v1\/decisions\/([^/]+?)(?:\/(supersede))?$/);
    if (m) {
      const [, id, action] = m;
      const dec = state.decs.find((d) => d.id === id);
      if (!dec) return json({ detail: "nf" }, 404);
      if (!action && method === "GET") return json(dec);
      if (action === "supersede" && method === "POST") {
        if (dec.status !== "active") return json({ detail: "conflito" }, 409);
        if (body.expected_version !== dec.version)
          return json({ detail: "conflito" }, 409);
        const created = newDecision(state, body);
        created.supersedes = dec.id;
        dec.status = "superseded";
        dec.replaced_by = created.id;
        dec.version += 1;
        return json(created, 201);
      }
    }
    return json({ detail: "nf" }, 404);
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

function renderSection() {
  return render(<DecisionSection productId={PRODUCT_ID} />);
}

describe("DecisionSection (gestão de decisões)", () => {
  beforeEach(() => {
    document.cookie = "csrftoken=t";
  });
  afterEach(() => {
    vi.restoreAllMocks();
  });

  // estado vazio
  it("mostra estado vazio quando não há decisões", async () => {
    installFetch({ decs: [], seq: 0 });
    renderSection();
    await screen.findByText(/ainda não há decisões/i, undefined, { timeout: 5000 });
  });

  // 17 — UI cria e consulta decisão
  it("cria uma decisão e consulta o detalhe", async () => {
    installFetch({ decs: [], seq: 0 });
    renderSection();
    fireEvent.click(await screen.findByRole("button", { name: /nova decisão/i }));

    fireEvent.change(screen.getByLabelText("Título"), {
      target: { value: "Adoptar PostgreSQL" },
    });
    fireEvent.change(screen.getByLabelText("Contexto"), {
      target: { value: "Precisamos de transacções fiáveis" },
    });
    fireEvent.change(screen.getByLabelText("Decisão"), {
      target: { value: "Usar PostgreSQL 16" },
    });
    fireEvent.click(screen.getByRole("button", { name: /criar decisão/i }));

    await screen.findByRole("heading", { name: "Adoptar PostgreSQL", level: 4 });
    // Detalhe mostra estado activa e o texto da decisão.
    const estado = screen.getByText("Estado");
    expect(estado.nextElementSibling?.textContent).toBe("Activa");
    expect(screen.getByText("Usar PostgreSQL 16")).toBeInTheDocument();
  });

  // 18 — UI substitui e mostra a cadeia
  it("substitui uma decisão e apresenta a cadeia", async () => {
    const state: MockState = {
      decs: [
        {
          id: "dec-1",
          organisation: "org-1",
          title: "Decisão original",
          context: "ctx",
          decision_text: "texto original",
          responsible: "user-1",
          decided_at: "2026-07-13T09:00:00Z",
          impact: "",
          status: "active",
          product: PRODUCT_ID,
          detail_document: null,
          supersedes: null,
          replaced_by: null,
          version: 1,
          created_at: "2026-07-13T09:00:00Z",
          updated_at: "2026-07-13T09:00:00Z",
        },
      ],
      seq: 1,
    };
    installFetch(state);
    renderSection();

    fireEvent.click(await screen.findByRole("button", { name: "Decisão original" }));
    await screen.findByRole("heading", { name: "Decisão original", level: 4 });
    // Substituir explica a criação de nova decisão.
    fireEvent.click(screen.getByRole("button", { name: /^substituir$/i }));
    expect(screen.getByText(/nova decisão activa/i)).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText("Título"), {
      target: { value: "Decisão revista" },
    });
    fireEvent.change(screen.getByLabelText("Contexto"), {
      target: { value: "novo contexto" },
    });
    fireEvent.change(screen.getByLabelText("Decisão"), {
      target: { value: "texto revisto" },
    });
    fireEvent.click(
      screen.getByRole("button", { name: /confirmar substituição/i }),
    );

    // Detalhe da nova decisão (activa) com ligação à anterior.
    await screen.findByRole("heading", { name: "Decisão revista", level: 4 });
    const estado = screen.getByText("Estado");
    expect(estado.nextElementSibling?.textContent).toBe("Activa");
    const prevLink = screen.getByRole("button", {
      name: /ver decisão anterior/i,
    });
    expect(prevLink).toBeInTheDocument();

    // Navega para a anterior: agora substituída, com ligação à seguinte.
    fireEvent.click(prevLink);
    await screen.findByRole("heading", { name: "Decisão original", level: 4 });
    const estado2 = screen.getByText("Estado");
    expect(estado2.nextElementSibling?.textContent).toBe("Substituída");
    expect(
      screen.getByRole("button", { name: /ver decisão seguinte/i }),
    ).toBeInTheDocument();
    // Uma decisão substituída não pode ser substituída de novo.
    expect(screen.queryByRole("button", { name: /^substituir$/i })).toBeNull();
  });

  // filtro por estado
  it("filtra por estado", async () => {
    const state: MockState = {
      decs: [
        {
          id: "a",
          organisation: "org-1",
          title: "Activa1",
          context: "c",
          decision_text: "d",
          responsible: "user-1",
          decided_at: "2026-07-13T09:00:00Z",
          impact: "",
          status: "active",
          product: PRODUCT_ID,
          detail_document: null,
          supersedes: null,
          replaced_by: null,
          version: 1,
          created_at: "2026-07-13T09:00:00Z",
          updated_at: "2026-07-13T09:00:00Z",
        },
        {
          id: "b",
          organisation: "org-1",
          title: "Substituida1",
          context: "c",
          decision_text: "d",
          responsible: "user-1",
          decided_at: "2026-07-13T09:00:00Z",
          impact: "",
          status: "superseded",
          product: PRODUCT_ID,
          detail_document: null,
          supersedes: null,
          replaced_by: null,
          version: 2,
          created_at: "2026-07-13T09:00:00Z",
          updated_at: "2026-07-13T09:00:00Z",
        },
      ],
      seq: 2,
    };
    installFetch(state);
    renderSection();
    await screen.findByRole("button", { name: "Activa1" });
    expect(screen.getByRole("button", { name: "Substituida1" })).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText("Estado"), {
      target: { value: "active" },
    });
    await waitFor(() =>
      expect(screen.queryByRole("button", { name: "Substituida1" })).toBeNull(),
    );
    expect(screen.getByRole("button", { name: "Activa1" })).toBeInTheDocument();
  });
});
