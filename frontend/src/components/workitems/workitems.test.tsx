import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { WorkItemSection } from "./WorkItemSection";

function json(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

const PRODUCT_ID = "prod-1";
const PAGE_SIZE = 20;

interface Item {
  id: string;
  organisation: string;
  product: string;
  decision: string | null;
  title: string;
  work_type: string;
  responsible: string;
  priority: string;
  due_at: string | null;
  notes: string;
  status: string;
  is_overdue: boolean;
  completed_at: string | null;
  cancelled_at: string | null;
  version: number;
  created_at: string;
  updated_at: string;
}

interface MockState {
  items: Item[];
  seq: number;
}

function base(overrides: Partial<Item> = {}): Item {
  return {
    id: "wi-1",
    organisation: "org-1",
    product: PRODUCT_ID,
    decision: null,
    title: "Rever contrato",
    work_type: "obligation",
    responsible: "user-1",
    priority: "medium",
    due_at: null,
    notes: "",
    status: "open",
    is_overdue: false,
    completed_at: null,
    cancelled_at: null,
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

    // Opções de decisão para o formulário.
    if (path.endsWith("/v1/decisions") && method === "GET") {
      return json({ results: [], count: 0, page: 1, page_size: 20, num_pages: 1 });
    }

    if (path.endsWith("/v1/work-items") && method === "GET") {
      const status = url.searchParams.get("status");
      const workType = url.searchParams.get("work_type");
      const overdue = url.searchParams.get("overdue");
      const page = parseInt(url.searchParams.get("page") ?? "1", 10);
      let items = state.items.filter((i) => i.product === PRODUCT_ID);
      if (status) items = items.filter((i) => i.status === status);
      if (workType) items = items.filter((i) => i.work_type === workType);
      if (overdue === "true") items = items.filter((i) => i.is_overdue);
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
    if (path.endsWith("/v1/work-items") && method === "POST") {
      state.seq += 1;
      const item = base({
        id: `wi-${state.seq}`,
        title: body.title,
        work_type: body.work_type,
        priority: body.priority ?? "medium",
        due_at: body.due_at ?? null,
        notes: body.notes ?? "",
        decision: body.decision ?? null,
      });
      state.items.push(item);
      return json(item, 201);
    }

    const m = path.match(
      /\/v1\/work-items\/([^/]+?)(?:\/(complete|cancel))?$/,
    );
    if (m) {
      const [, id, action] = m;
      const item = state.items.find((i) => i.id === id);
      if (!item) return json({ detail: "nf" }, 404);
      if (!action && method === "GET") return json(item);
      if (!action && method === "PATCH") {
        if (item.status !== "open") return json({ detail: "final" }, 409);
        if (body.expected_version !== item.version)
          return json({ detail: "conflito" }, 409);
        Object.assign(item, {
          title: body.title ?? item.title,
          priority: body.priority ?? item.priority,
          version: item.version + 1,
        });
        return json(item);
      }
      if (action && method === "POST") {
        if (item.status !== "open") return json({ detail: "final" }, 409);
        if (body.expected_version !== item.version)
          return json({ detail: "conflito" }, 409);
        item.status = action === "complete" ? "completed" : "cancelled";
        item.is_overdue = false;
        item.version += 1;
        if (action === "complete") item.completed_at = "2026-07-14T00:00:00Z";
        else item.cancelled_at = "2026-07-14T00:00:00Z";
        return json(item);
      }
    }
    return json({ detail: "nf" }, 404);
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

function renderSection() {
  return render(<WorkItemSection productId={PRODUCT_ID} />);
}

async function openItem(title: string) {
  fireEvent.click(await screen.findByRole("button", { name: title }));
  await screen.findByRole("heading", { name: title, level: 4 });
}

describe("WorkItemSection (pendências)", () => {
  beforeEach(() => {
    document.cookie = "csrftoken=t";
  });
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("mostra estado vazio quando não há pendências", async () => {
    installFetch({ items: [], seq: 0 });
    renderSection();
    await screen.findByText(/ainda não há pendências/i, undefined, { timeout: 5000 });
  });

  // 21 (parte 1) — UI cria pendência
  it("cria uma pendência com tipo e prioridade", async () => {
    const state: MockState = { items: [], seq: 0 };
    installFetch(state);
    renderSection();
    fireEvent.click(await screen.findByRole("button", { name: /nova pendência/i }));

    const typeSelect = screen.getByLabelText("Tipo") as HTMLSelectElement;
    expect(typeSelect.options).toHaveLength(5); // cinco tipos fechados
    fireEvent.change(screen.getByLabelText("Título"), {
      target: { value: "Renovar licença" },
    });
    fireEvent.change(typeSelect, { target: { value: "obligation" } });
    fireEvent.change(screen.getByLabelText("Prioridade"), {
      target: { value: "high" },
    });
    fireEvent.click(screen.getByRole("button", { name: /criar pendência/i }));

    await screen.findByRole("heading", { name: "Renovar licença", level: 4 });
    const tipo = screen.getByText("Tipo");
    expect(tipo.nextElementSibling?.textContent).toBe("Obrigação");
  });

  // 21 (parte 2) — UI conclui
  it("conclui uma pendência aberta", async () => {
    installFetch({ items: [base({ id: "wi-1", title: "Concluir isto" })], seq: 1 });
    renderSection();
    await openItem("Concluir isto");
    fireEvent.click(screen.getByRole("button", { name: /^concluir$/i }));
    await waitFor(() => {
      const estado = screen.getByText("Estado");
      expect(estado.nextElementSibling?.textContent).toBe("Concluída");
    });
    // Estado final: sem acções de edição/conclusão.
    expect(screen.queryByRole("button", { name: /^concluir$/i })).toBeNull();
    expect(screen.queryByRole("button", { name: "Editar" })).toBeNull();
  });

  // 21 (parte 3) — UI cancela com confirmação
  it("cancela uma pendência com confirmação explícita", async () => {
    installFetch({ items: [base({ id: "wi-1", title: "Cancelar isto" })], seq: 1 });
    renderSection();
    await openItem("Cancelar isto");
    fireEvent.click(screen.getByRole("button", { name: /cancelar pendência/i }));
    // Ainda não cancelou: pediu confirmação.
    const estado = screen.getByText("Estado");
    expect(estado.nextElementSibling?.textContent).toBe("Aberta");
    fireEvent.click(
      screen.getByRole("button", { name: /confirmar cancelamento/i }),
    );
    await waitFor(() => {
      const e2 = screen.getByText("Estado");
      expect(e2.nextElementSibling?.textContent).toBe("Cancelada");
    });
  });

  // 22 — UI apresenta vencimento (calculado no servidor)
  it("apresenta o sinal de vencida", async () => {
    installFetch({
      items: [
        base({ id: "wi-1", title: "Atrasada", due_at: "2020-01-01T00:00:00Z", is_overdue: true }),
      ],
      seq: 1,
    });
    renderSection();
    await screen.findByRole("button", { name: "Atrasada" });
    // Sinal visual de vencida na lista.
    expect(screen.getByTestId("overdue-badge")).toBeInTheDocument();
  });

  // filtro por estado
  it("filtra por estado", async () => {
    installFetch({
      items: [
        base({ id: "a", title: "Aberta1", status: "open" }),
        base({ id: "b", title: "Concluida1", status: "completed" }),
      ],
      seq: 2,
    });
    renderSection();
    await screen.findByRole("button", { name: "Aberta1" });
    expect(screen.getByRole("button", { name: "Concluida1" })).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText("Estado"), {
      target: { value: "open" },
    });
    await waitFor(() =>
      expect(screen.queryByRole("button", { name: "Concluida1" })).toBeNull(),
    );
    expect(screen.getByRole("button", { name: "Aberta1" })).toBeInTheDocument();
  });
});
