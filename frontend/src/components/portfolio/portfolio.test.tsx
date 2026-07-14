import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { AuthProvider } from "../../auth/AuthContext";
import { PortfolioWorkspace } from "./PortfolioWorkspace";

function json(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

const USER = { id: "u1", email: "owner@x.pt", name: "Owner" };
const PAGE_SIZE = 2; // pequeno, para exercitar a paginação com poucos itens.

let clock = 0;
function stamp(): string {
  return `2026-07-13T00:00:${String(clock++).padStart(2, "0")}Z`;
}

type P = Record<string, unknown>;
function product(overrides: P = {}): P {
  const t = stamp();
  return {
    id: "p1",
    organisation: "o1",
    name: "Produto",
    purpose: "Propósito",
    status: "active",
    responsible: "u1",
    last_reviewed_at: "2026-07-13T09:00:00Z",
    target_audience: "",
    phase: "",
    next_review_at: null,
    notes: "",
    version: 1,
    created_at: t,
    updated_at: t,
    ...overrides,
  };
}

interface MockState {
  user: typeof USER | null;
  products: P[];
  postCount: number;
  postGate?: Promise<void>;
  conflictOnce?: boolean;
  archiveConflictOnce?: boolean;
}

function installFetch(state: MockState) {
  const fetchMock = vi.fn(async (rawUrl: string, init: RequestInit = {}) => {
    const method = init.method ?? "GET";
    const url = new URL(rawUrl, "http://local");
    const path = url.pathname;

    if (path.endsWith("/v1/auth/csrf")) return json({ detail: "ok" });
    if (path.endsWith("/v1/auth/session"))
      return json({ authenticated: !!state.user, user: state.user ?? undefined });

    // A ficha do produto compõe a área documental (F1-P04-PR03): responde com
    // uma lista vazia para que abrir a ficha não gere erro nos testes do
    // portefólio (o comportamento documental é testado em documents.test.tsx).
    if (
      (path.endsWith("/v1/documents") ||
        path.endsWith("/v1/decisions") ||
        path.endsWith("/v1/work-items") ||
        path.endsWith("/v1/executions") ||
        path.endsWith("/v1/functions")) &&
      method === "GET"
    ) {
      return json({
        results: [],
        count: 0,
        page: 1,
        page_size: 20,
        num_pages: 1,
      });
    }

    if (path.endsWith("/v1/products") && method === "GET") {
      const status = url.searchParams.get("status") ?? "active";
      const responsible = url.searchParams.get("responsible");
      const page = parseInt(url.searchParams.get("page") ?? "1", 10);
      let items = [...state.products];
      if (status === "active") items = items.filter((p) => p.status === "active");
      else if (status === "archived")
        items = items.filter((p) => p.status === "archived");
      if (responsible)
        items = items.filter((p) => p.responsible === responsible);
      items.sort((a, b) =>
        (a.updated_at as string) < (b.updated_at as string) ? 1 : -1,
      );
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
    if (path.endsWith("/v1/products") && method === "POST") {
      state.postCount += 1;
      if (state.postGate) await state.postGate;
      const body = JSON.parse(init.body as string);
      const created = product({
        id: `new${state.products.length + 1}`,
        ...body,
        responsible: state.user?.id,
      });
      state.products.push(created);
      return json(created, 201);
    }

    const match = path.match(
      /\/v1\/products\/([^/]+?)(?:\/(archive|reactivate|mark-reviewed))?$/,
    );
    if (match) {
      const [, id, action] = match;
      const p = state.products.find((x) => x.id === id);
      if (!p) return json({ detail: "nf" }, 404);

      if (method === "GET") return json(p);
      if (method === "PATCH") {
        if (state.conflictOnce) {
          state.conflictOnce = false;
          return json({ detail: "conflito" }, 409);
        }
        const body = JSON.parse(init.body as string) as P;
        delete body.expected_version;
        Object.assign(p, body, {
          version: (p.version as number) + 1,
          updated_at: stamp(),
        }); // edição comum: last_reviewed_at NÃO muda
        return json(p);
      }
      if (method === "POST" && action === "archive") {
        if (state.archiveConflictOnce) {
          state.archiveConflictOnce = false;
          return json({ detail: "conflito" }, 409);
        }
        Object.assign(p, {
          status: "archived",
          version: (p.version as number) + 1,
          updated_at: stamp(),
        });
        return json(p);
      }
      if (method === "POST" && action === "reactivate") {
        Object.assign(p, {
          status: "active",
          version: (p.version as number) + 1,
          updated_at: stamp(),
        });
        return json(p);
      }
      if (method === "POST" && action === "mark-reviewed") {
        Object.assign(p, {
          last_reviewed_at: "2026-08-01T10:00:00Z",
          version: (p.version as number) + 1,
          updated_at: stamp(),
        });
        return json(p);
      }
    }
    return json({ detail: "nf" }, 404);
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

function renderWorkspace() {
  return render(
    <AuthProvider>
      <PortfolioWorkspace />
    </AuthProvider>,
  );
}

async function openDetail(name: string) {
  fireEvent.click(await screen.findByRole("button", { name }));
  await screen.findByRole("heading", { name });
}

describe("PortfolioWorkspace (experiência completa)", () => {
  beforeEach(() => {
    clock = 0;
  });
  afterEach(() => {
    vi.restoreAllMocks();
    document.cookie = "csrftoken=t";
  });

  it("mostra o estado vazio quando não há produtos", async () => {
    installFetch({ user: USER, products: [], postCount: 0 });
    renderWorkspace();
    // Timeout generoso: o 1.º teste do ficheiro suporta o custo de arranque.
    await screen.findByText(/ainda não tem produtos/i, undefined, {
      timeout: 5000,
    });
    expect(screen.getByText(/ainda não tem produtos/i)).toBeInTheDocument();
  });

  it("cria um produto só com nome e propósito e mostra os defaults", async () => {
    installFetch({ user: USER, products: [], postCount: 0 });
    renderWorkspace();
    fireEvent.click(await screen.findByRole("button", { name: /novo produto/i }));
    fireEvent.change(screen.getByLabelText("Nome"), {
      target: { value: "Produto Novo" },
    });
    fireEvent.change(screen.getByLabelText("Propósito"), {
      target: { value: "Fazer algo útil" },
    });
    fireEvent.click(screen.getByRole("button", { name: /criar produto/i }));

    await screen.findByRole("heading", { name: "Produto Novo" });
    expect(screen.getByText("Activo")).toBeInTheDocument();
    expect(screen.getByText("owner@x.pt")).toBeInTheDocument();
  });

  it("evita submissão duplicada na criação", async () => {
    let release!: () => void;
    const gate = new Promise<void>((r) => (release = r));
    const state: MockState = {
      user: USER,
      products: [],
      postCount: 0,
      postGate: gate,
    };
    installFetch(state);
    renderWorkspace();
    fireEvent.click(await screen.findByRole("button", { name: /novo produto/i }));
    fireEvent.change(screen.getByLabelText("Nome"), { target: { value: "P" } });
    fireEvent.change(screen.getByLabelText("Propósito"), {
      target: { value: "x" },
    });
    const submit = screen.getByRole("button", { name: /criar produto/i });
    fireEvent.click(submit);
    fireEvent.click(submit);
    expect(state.postCount).toBe(1);
    release();
    await screen.findByRole("heading", { name: "P" });
  });

  it("trata erro da API na listagem e permite tentar novamente", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (rawUrl: string) => {
        const path = new URL(rawUrl, "http://local").pathname;
        if (path.endsWith("/v1/auth/csrf")) return json({ detail: "ok" });
        if (path.endsWith("/v1/auth/session"))
          return json({ authenticated: true, user: USER });
        return json({ detail: "erro" }, 500); // GET de produtos falha
      }),
    );
    renderWorkspace();
    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent(/não foi possível carregar o portefólio/i);
    expect(
      screen.getByRole("button", { name: /tentar novamente/i }),
    ).toBeInTheDocument();
  });

  // 1/2/3 — filtros por estado
  it("filtra por activos, arquivados e todos", async () => {
    installFetch({
      user: USER,
      products: [
        product({ id: "a", name: "Activo1", status: "active" }),
        product({ id: "b", name: "Arquivado1", status: "archived" }),
      ],
      postCount: 0,
    });
    renderWorkspace();
    // Por defeito: activos.
    await screen.findByRole("button", { name: "Activo1" });
    expect(screen.queryByRole("button", { name: "Arquivado1" })).toBeNull();

    // Arquivados.
    fireEvent.change(screen.getByLabelText("Estado"), {
      target: { value: "archived" },
    });
    await screen.findByRole("button", { name: "Arquivado1" });
    expect(screen.queryByRole("button", { name: "Activo1" })).toBeNull();

    // Todos.
    fireEvent.change(screen.getByLabelText("Estado"), {
      target: { value: "all" },
    });
    await screen.findByRole("button", { name: "Activo1" });
    expect(screen.getByRole("button", { name: "Arquivado1" })).toBeInTheDocument();
  });

  // 4 — paginação
  it("pagina de forma estável", async () => {
    installFetch({
      user: USER,
      products: [
        product({ id: "p1", name: "Um" }),
        product({ id: "p2", name: "Dois" }),
        product({ id: "p3", name: "Tres" }),
      ],
      postCount: 0,
    });
    renderWorkspace();
    await screen.findByText(/página 1 de 2/i);
    // Página 1 tem 2 itens (os mais recentes: Tres, Dois).
    expect(screen.getByRole("button", { name: "Tres" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Dois" })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Um" })).toBeNull();

    fireEvent.click(screen.getByRole("button", { name: /seguinte/i }));
    await screen.findByText(/página 2 de 2/i);
    expect(screen.getByRole("button", { name: "Um" })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Tres" })).toBeNull();
  });

  // 5 — arquivo com confirmação
  it("arquiva apenas após confirmação explícita", async () => {
    installFetch({
      user: USER,
      products: [product({ id: "p1", name: "Alpha", status: "active" })],
      postCount: 0,
    });
    renderWorkspace();
    await openDetail("Alpha");

    fireEvent.click(screen.getByRole("button", { name: "Arquivar" }));
    // Ainda não arquivado: só apareceu a confirmação.
    expect(screen.getByText("Activo")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /confirmar arquivo/i }));
    await screen.findByText("Arquivado");
    expect(screen.getByText(/produto arquivado/i)).toBeInTheDocument();
  });

  // 6 — produto arquivado deixa de ser editável
  it("um produto arquivado não pode ser editado", async () => {
    installFetch({
      user: USER,
      products: [product({ id: "p1", name: "Arq", status: "archived" })],
      postCount: 0,
    });
    renderWorkspace();
    fireEvent.change(screen.getByLabelText("Estado"), {
      target: { value: "archived" },
    });
    await openDetail("Arq");
    expect(screen.queryByRole("button", { name: "Editar" })).toBeNull();
    expect(
      screen.queryByRole("button", { name: /marcar como revisto/i }),
    ).toBeNull();
    expect(screen.getByRole("button", { name: "Reactivar" })).toBeInTheDocument();
  });

  // 7 — reactivação
  it("reactiva um produto arquivado", async () => {
    installFetch({
      user: USER,
      products: [product({ id: "p1", name: "Arq", status: "archived" })],
      postCount: 0,
    });
    renderWorkspace();
    fireEvent.change(screen.getByLabelText("Estado"), {
      target: { value: "archived" },
    });
    await openDetail("Arq");
    fireEvent.click(screen.getByRole("button", { name: "Reactivar" }));
    await screen.findByText("Activo");
    expect(screen.getByRole("button", { name: "Editar" })).toBeInTheDocument();
  });

  // 8 — marcação explícita como revisto
  it("marca como revisto com confirmação e actualiza a data", async () => {
    installFetch({
      user: USER,
      products: [product({ id: "p1", name: "Alpha", status: "active" })],
      postCount: 0,
    });
    renderWorkspace();
    await openDetail("Alpha");
    expect(screen.getByText("2026-07-13")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: /marcar como revisto/i }));
    // Explica que confirma uma revisão real.
    expect(screen.getByText(/reviu realmente esta ficha/i)).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /confirmar revisão/i }));
    await screen.findByText("2026-08-01");
  });

  // 9 — edição comum não muda a data de revisão apresentada
  it("a edição comum não muda a data de revisão", async () => {
    installFetch({
      user: USER,
      products: [product({ id: "p1", name: "Alpha", purpose: "Antigo" })],
      postCount: 0,
    });
    renderWorkspace();
    await openDetail("Alpha");
    fireEvent.click(screen.getByRole("button", { name: "Editar" }));
    fireEvent.change(screen.getByLabelText("Notas"), {
      target: { value: "uma nota" },
    });
    fireEvent.click(
      screen.getByRole("button", { name: /guardar alterações/i }),
    );
    await screen.findByRole("heading", { name: "Alpha" });
    // Data de última revisão inalterada.
    expect(screen.getByText("2026-07-13")).toBeInTheDocument();
    expect(screen.queryByText("2026-08-01")).toBeNull();
  });

  // 10 — conflito 409 permite recarregar
  it("um conflito 409 numa acção permite recarregar sem sobrescrever", async () => {
    installFetch({
      user: USER,
      products: [product({ id: "p1", name: "Alpha", status: "active" })],
      postCount: 0,
      archiveConflictOnce: true,
    });
    renderWorkspace();
    await openDetail("Alpha");
    fireEvent.click(screen.getByRole("button", { name: "Arquivar" }));
    fireEvent.click(screen.getByRole("button", { name: /confirmar arquivo/i }));

    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent(/alterado por outra operação/i);
    fireEvent.click(screen.getByRole("button", { name: /recarregar dados/i }));
    await waitFor(() =>
      expect(screen.queryByRole("alert")).toBeNull(),
    );
    // Continua activo (não foi sobrescrito).
    expect(screen.getByText("Activo")).toBeInTheDocument();
  });

  // 11 — campos opcionais editáveis
  it("permite editar os campos opcionais da ficha", async () => {
    installFetch({
      user: USER,
      products: [product({ id: "p1", name: "Alpha" })],
      postCount: 0,
    });
    renderWorkspace();
    await openDetail("Alpha");
    fireEvent.click(screen.getByRole("button", { name: "Editar" }));
    fireEvent.change(screen.getByLabelText("Público-alvo"), {
      target: { value: "Fundadores" },
    });
    fireEvent.change(screen.getByLabelText("Notas"), {
      target: { value: "acompanhar" },
    });
    fireEvent.click(
      screen.getByRole("button", { name: /guardar alterações/i }),
    );
    await screen.findByRole("heading", { name: "Alpha" });
    expect(screen.getByText("Fundadores")).toBeInTheDocument();
    expect(screen.getByText("acompanhar")).toBeInTheDocument();
  });

  // 12 — estado e responsável apresentados correctamente
  it("apresenta estado e responsável na lista", async () => {
    installFetch({
      user: USER,
      products: [product({ id: "p1", name: "Alpha", status: "active" })],
      postCount: 0,
    });
    renderWorkspace();
    await screen.findByRole("button", { name: "Alpha" });
    expect(screen.getByText("Activo")).toBeInTheDocument();
    expect(screen.getByText("owner@x.pt")).toBeInTheDocument();
  });

  // 12b — filtro por responsável (apenas os meus)
  it("filtra por responsável (apenas os meus)", async () => {
    installFetch({
      user: USER,
      products: [
        product({ id: "meu", name: "Meu", responsible: "u1" }),
        product({ id: "dele", name: "Dele", responsible: "u2" }),
      ],
      postCount: 0,
    });
    renderWorkspace();
    // status=all para incluir ambos independentemente do estado.
    fireEvent.change(screen.getByLabelText("Estado"), {
      target: { value: "all" },
    });
    await screen.findByRole("button", { name: "Meu" });
    expect(screen.getByRole("button", { name: "Dele" })).toBeInTheDocument();

    fireEvent.click(screen.getByLabelText("Apenas os meus"));
    await waitFor(() =>
      expect(screen.queryByRole("button", { name: "Dele" })).toBeNull(),
    );
    expect(screen.getByRole("button", { name: "Meu" })).toBeInTheDocument();
  });

  // 13 — nenhum agregado futuro é simulado
  it("não simula agregados futuros na ficha", async () => {
    installFetch({
      user: USER,
      products: [product({ id: "p1", name: "Alpha" })],
      postCount: 0,
    });
    renderWorkspace();
    await openDetail("Alpha");
    // As quatro áreas relacionadas são reais (execuções agora incluídas).
    expect(
      screen.getByRole("heading", { name: "Execuções", level: 4 }),
    ).toBeInTheDocument();
    await screen.findByText(/ainda não há execuções/i);
    // Sem contagens simuladas do tipo "Documentos (0)".
    expect(screen.queryByText(/\(\d+\)/)).toBeNull();
  });
});
