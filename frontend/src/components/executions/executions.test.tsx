import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { ExecutionSection } from "./ExecutionSection";

function json(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

const PRODUCT_ID = "prod-1";

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

interface Doc {
  id: string;
  organisation: string;
  product: string | null;
  title: string;
  document_type: string;
  is_outdated: boolean;
  export_policy: string;
  current_version_number: number | null;
  version: number;
  created_at: string;
  updated_at: string;
}

interface Ver {
  id: string;
  version_number: number;
  checksum: string;
  byte_size: number;
  author: string;
  change_summary: string;
  created_at: string;
}

interface State {
  functions: Fn[];
  documents: Doc[];
  versions: Record<string, Ver[]>;
  executions: any[];
  seq: number;
  postDelay?: () => Promise<void>;
  postCount: number;
}

function fn(over: Partial<Fn> = {}): Fn {
  return {
    id: "fn-1",
    organisation: "org-1",
    name: "Analista IA",
    actor_type: "ai",
    purpose: "Rever conteúdo",
    responsibilities: "Analisa",
    constraints: "",
    instruction_document: null,
    requires_approval: true,
    status: "active",
    version: 1,
    created_at: "2026-07-14T09:00:00Z",
    updated_at: "2026-07-14T09:00:00Z",
    ...over,
  };
}

function doc(over: Partial<Doc> = {}): Doc {
  return {
    id: "doc-1",
    organisation: "org-1",
    product: null,
    title: "Contexto da empresa",
    document_type: "contexto_da_empresa",
    is_outdated: false,
    export_policy: "allowed",
    current_version_number: 1,
    version: 1,
    created_at: "2026-07-14T09:00:00Z",
    updated_at: "2026-07-14T09:00:00Z",
    ...over,
  };
}

function ver(over: Partial<Ver> = {}): Ver {
  return {
    id: "ver-1",
    version_number: 1,
    checksum: "abcdef0123456789",
    byte_size: 10,
    author: "user-1",
    change_summary: "",
    created_at: "2026-07-14T09:00:00Z",
    ...over,
  };
}

function emptyPage(results: unknown[] = []) {
  return { results, count: results.length, page: 1, page_size: 20, num_pages: 1 };
}

function installFetch(state: State) {
  const fetchMock = vi.fn(async (rawUrl: string, init: RequestInit = {}) => {
    const method = init.method ?? "GET";
    const url = new URL(rawUrl, "http://local");
    const path = url.pathname;
    const body = init.body ? JSON.parse(init.body as string) : {};

    // Funções (filtro por status; o servidor só devolve active quando pedido).
    if (path.endsWith("/v1/functions") && method === "GET") {
      const status = url.searchParams.get("status");
      let items = [...state.functions];
      if (status && status !== "all") items = items.filter((f) => f.status === status);
      return json(emptyPage(items));
    }

    // Documentos candidatos: por produto ou empresariais (product null).
    if (path.endsWith("/v1/documents") && method === "GET") {
      const product = url.searchParams.get("product");
      const empresarial = url.searchParams.get("empresarial");
      let items = [...state.documents];
      if (product) items = items.filter((d) => d.product === product);
      else if (empresarial === "true") items = items.filter((d) => d.product === null);
      return json(emptyPage(items));
    }

    // Versões de um documento.
    const vm = path.match(/\/v1\/documents\/([^/]+)\/versions$/);
    if (vm && method === "GET") {
      return json({ results: state.versions[vm[1]] ?? [], count: 0 });
    }

    // Execuções: lista por produto.
    if (path.endsWith("/v1/executions") && method === "GET") {
      const product = url.searchParams.get("product");
      const items = state.executions.filter((e) => e.product === product);
      return json(emptyPage(items));
    }
    // Execuções: criação.
    if (path.endsWith("/v1/executions") && method === "POST") {
      state.postCount += 1;
      if (state.postDelay) await state.postDelay();
      state.seq += 1;
      const detail = buildDetail(state, body, `exec-${state.seq}`);
      state.executions.push(detail);
      return json(detail, 201);
    }
    // Execução: detalhe.
    const dm = path.match(/\/v1\/executions\/([^/]+)$/);
    if (dm && method === "GET") {
      const found = state.executions.find((e) => e.id === dm[1]);
      return found ? json(found) : json({ detail: "nf" }, 404);
    }

    return json({ detail: "nf" }, 404);
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

function buildDetail(state: State, body: any, id: string) {
  const f = state.functions.find((x) => x.id === body.function_profile)!;
  const context_documents = (body.context ?? []).map((item: any, i: number) => {
    // Resolve os metadados da versão exacta.
    let meta: Doc | undefined;
    let version: Ver | undefined;
    for (const d of state.documents) {
      const vs = state.versions[d.id] ?? [];
      const v = vs.find((x) => x.id === item.document_version);
      if (v) {
        meta = d;
        version = v;
        break;
      }
    }
    return {
      document: meta?.id ?? "?",
      document_version: item.document_version,
      order: i + 1,
      purpose: item.purpose ?? "",
      title: meta?.title ?? "?",
      document_type: meta?.document_type ?? "contexto_da_empresa",
      version_number: version?.version_number ?? 1,
      checksum: version?.checksum ?? "abcdef0123456789",
      export_policy: meta?.export_policy ?? "allowed",
      is_outdated: meta?.is_outdated ?? false,
    };
  });
  return {
    id,
    organisation: "org-1",
    product: body.product,
    function_profile: body.function_profile,
    requested_by: "user-1",
    title: body.title,
    objective: body.objective,
    request_instructions: body.request_instructions,
    constraints: body.constraints ?? "",
    expected_output_format: body.expected_output_format,
    execution_mode: body.execution_mode,
    status: "prepared",
    function_snapshot: {
      id: f.id,
      name: f.name,
      actor_type: f.actor_type,
      purpose: f.purpose,
      responsibilities: f.responsibilities,
      constraints: f.constraints,
      requires_approval: f.requires_approval,
    },
    product_snapshot: {
      id: body.product,
      name: "Produto A",
      purpose: "prop",
      status: "active",
      phase: "descoberta",
    },
    instruction_version: f.instruction_document ? "instr-ver-1" : null,
    context_documents,
    version: 1,
    created_at: "2026-07-14T10:00:00Z",
    updated_at: "2026-07-14T10:00:00Z",
  };
}

function baseState(over: Partial<State> = {}): State {
  return {
    functions: [fn()],
    documents: [doc({ id: "doc-1", title: "Doc Empresa", product: null })],
    versions: { "doc-1": [ver({ id: "ver-1", version_number: 1 })] },
    executions: [],
    seq: 0,
    postCount: 0,
    ...over,
  };
}

async function fillFormAndPickFunction() {
  fireEvent.click(await screen.findByRole("button", { name: /preparar execução/i }));
  fireEvent.change(await screen.findByLabelText("Título"), {
    target: { value: "Execução teste" },
  });
  fireEvent.change(screen.getByLabelText("Objectivo"), {
    target: { value: "obj" },
  });
  fireEvent.change(screen.getByLabelText("Instruções do pedido"), {
    target: { value: "faz x" },
  });
  fireEvent.change(screen.getByLabelText("Formato esperado"), {
    target: { value: "Markdown" },
  });
  fireEvent.change(screen.getByLabelText("Função"), { target: { value: "fn-1" } });
}

async function addContextVersion(docId: string, versionId?: string) {
  const candidate = await screen.findByTestId(`candidate-${docId}`);
  fireEvent.click(within(candidate).getByRole("button", { name: /escolher versão/i }));
  const select = await within(candidate).findByLabelText("Versão");
  if (versionId) fireEvent.change(select, { target: { value: versionId } });
  fireEvent.click(within(candidate).getByRole("button", { name: /adicionar/i }));
}

describe("ExecutionSection (execuções)", () => {
  beforeEach(() => {
    document.cookie = "csrftoken=t";
  });
  afterEach(() => {
    vi.restoreAllMocks();
  });

  // 1 — estado vazio
  it("mostra estado vazio", async () => {
    installFetch(baseState());
    render(<ExecutionSection productId={PRODUCT_ID} />);
    await screen.findByText(/ainda não há execuções/i, undefined, { timeout: 5000 });
  });

  // 2 — listagem
  it("lista execuções existentes", async () => {
    const state = baseState();
    state.executions.push(
      buildDetail(
        state,
        {
          product: PRODUCT_ID,
          function_profile: "fn-1",
          title: "Execução A",
          objective: "o",
          request_instructions: "i",
          expected_output_format: "md",
          execution_mode: "manual_local",
          context: [],
        },
        "exec-A",
      ),
    );
    installFetch(state);
    render(<ExecutionSection productId={PRODUCT_ID} />);
    await screen.findByRole("button", { name: "Execução A" });
    expect(screen.getByTestId("list-status").textContent).toBe("Preparada");
  });

  // 3 — apenas funções active
  it("só oferece funções activas", async () => {
    const state = baseState({
      functions: [
        fn({ id: "fn-1", name: "Activa" }),
        fn({ id: "fn-2", name: "Inactiva", status: "inactive" }),
      ],
    });
    installFetch(state);
    render(<ExecutionSection productId={PRODUCT_ID} />);
    fireEvent.click(await screen.findByRole("button", { name: /preparar execução/i }));
    const select = (await screen.findByLabelText("Função")) as HTMLSelectElement;
    const labels = Array.from(select.options).map((o) => o.textContent);
    expect(labels.some((l) => l?.includes("Activa"))).toBe(true);
    expect(labels.some((l) => l?.includes("Inactiva"))).toBe(false);
  });

  // 4 — denied indisponível
  it("apresenta documento denied como não seleccionável", async () => {
    const state = baseState({
      documents: [doc({ id: "doc-1", title: "Recusado", export_policy: "denied" })],
    });
    installFetch(state);
    render(<ExecutionSection productId={PRODUCT_ID} />);
    await fillFormAndPickFunction();
    const candidate = await screen.findByTestId("candidate-doc-1");
    expect(within(candidate).getByTestId("denied-badge")).toBeInTheDocument();
    expect(
      within(candidate).queryByRole("button", { name: /escolher versão/i }),
    ).toBeNull();
  });

  // 5 — confirm com aviso
  it("avisa que confirm exigirá confirmação", async () => {
    const state = baseState({
      documents: [doc({ id: "doc-1", title: "Confirmar", export_policy: "confirm" })],
    });
    installFetch(state);
    render(<ExecutionSection productId={PRODUCT_ID} />);
    await fillFormAndPickFunction();
    const candidate = await screen.findByTestId("candidate-doc-1");
    expect(within(candidate).getByTestId("confirm-badge")).toBeInTheDocument();
    // Continua seleccionável.
    expect(
      within(candidate).getByRole("button", { name: /escolher versão/i }),
    ).toBeInTheDocument();
  });

  // 6 — is_outdated com aviso, seleccionável
  it("avisa is_outdated mas mantém seleccionável", async () => {
    const state = baseState({
      documents: [doc({ id: "doc-1", title: "Velho", is_outdated: true })],
    });
    installFetch(state);
    render(<ExecutionSection productId={PRODUCT_ID} />);
    await fillFormAndPickFunction();
    const candidate = await screen.findByTestId("candidate-doc-1");
    expect(within(candidate).getByTestId("outdated-badge")).toBeInTheDocument();
    expect(
      within(candidate).getByRole("button", { name: /escolher versão/i }),
    ).toBeInTheDocument();
  });

  // 7 — selecção de versão exacta
  it("selecciona uma versão exacta", async () => {
    installFetch(baseState());
    render(<ExecutionSection productId={PRODUCT_ID} />);
    await fillFormAndPickFunction();
    await addContextVersion("doc-1");
    const selected = await screen.findByTestId("selected-context");
    expect(within(selected).getByText("Doc Empresa")).toBeInTheDocument();
  });

  // 8 — selecção de versão histórica
  it("selecciona uma versão histórica", async () => {
    const state = baseState({
      versions: {
        "doc-1": [
          ver({ id: "ver-2", version_number: 2, checksum: "22bbbb000000" }),
          ver({ id: "ver-1", version_number: 1, checksum: "11aaaa000000" }),
        ],
      },
    });
    installFetch(state);
    render(<ExecutionSection productId={PRODUCT_ID} />);
    await fillFormAndPickFunction();
    await addContextVersion("doc-1", "ver-1"); // histórica (v1, não a actual v2)
    const selected = await screen.findByTestId("selected-context");
    expect(within(selected).getByText(/v1 ·/)).toBeInTheDocument();
  });

  // 9 — ordenação Subir/Descer
  it("reordena com Subir/Descer", async () => {
    const state = baseState({
      documents: [
        doc({ id: "doc-1", title: "Primeiro", product: null }),
        doc({ id: "doc-2", title: "Segundo", product: null }),
      ],
      versions: {
        "doc-1": [ver({ id: "v1", version_number: 1 })],
        "doc-2": [ver({ id: "v2", version_number: 1 })],
      },
    });
    installFetch(state);
    render(<ExecutionSection productId={PRODUCT_ID} />);
    await fillFormAndPickFunction();
    await addContextVersion("doc-1");
    await addContextVersion("doc-2");
    let titles = screen.getAllByTestId("selected-title").map((n) => n.textContent);
    expect(titles).toEqual(["Primeiro", "Segundo"]);
    fireEvent.click(screen.getByRole("button", { name: /descer primeiro/i }));
    titles = screen.getAllByTestId("selected-title").map((n) => n.textContent);
    expect(titles).toEqual(["Segundo", "Primeiro"]);
  });

  // 10 — exige pelo menos um documento
  it("exige pelo menos um documento de contexto", async () => {
    installFetch(baseState());
    render(<ExecutionSection productId={PRODUCT_ID} />);
    await fillFormAndPickFunction();
    fireEvent.click(screen.getByRole("button", { name: /preparar execução/i }));
    const alert = await screen.findByRole("alert");
    expect(alert.textContent).toMatch(/pelo menos uma versão documental/i);
  });

  // 11 + 12 — criação em ambos os modos
  it.each(["manual_local", "manual_external"] as const)(
    "cria execução em %s",
    async (mode) => {
      installFetch(baseState());
      render(<ExecutionSection productId={PRODUCT_ID} />);
      await fillFormAndPickFunction();
      fireEvent.change(screen.getByLabelText("Modo"), { target: { value: mode } });
      await addContextVersion("doc-1");
      fireEvent.click(screen.getByRole("button", { name: /^preparar execução$/i }));
      // Abre o detalhe.
      await screen.findByRole("heading", { name: "Execução teste", level: 4 });
      expect(screen.getByTestId("execution-status").textContent).toBe("Preparada");
    },
  );

  // 13–17 — detalhe congelado
  it("apresenta status, snapshots, instruction_version, ordem/versão/checksum", async () => {
    const state = baseState({
      functions: [fn({ id: "fn-1", instruction_document: "instr-doc" })],
    });
    installFetch(state);
    render(<ExecutionSection productId={PRODUCT_ID} />);
    await fillFormAndPickFunction();
    await addContextVersion("doc-1");
    fireEvent.click(screen.getByRole("button", { name: /^preparar execução$/i }));

    await screen.findByRole("heading", { name: "Execução teste", level: 4 });
    // 13
    expect(screen.getByTestId("execution-status").textContent).toBe("Preparada");
    // 14
    expect(screen.getByTestId("function-snapshot")).toBeInTheDocument();
    expect(within(screen.getByTestId("function-snapshot")).getByText("Analista IA"))
      .toBeInTheDocument();
    // 15
    expect(screen.getByTestId("product-snapshot")).toBeInTheDocument();
    // 16
    expect(screen.getByTestId("instruction-version").textContent).toMatch(
      /instr-ver-1/,
    );
    // 17
    const ctx = screen.getByTestId("context-documents");
    expect(within(ctx).getByTestId("ctx-version").textContent).toBe("1");
    expect(within(ctx).getByTestId("ctx-checksum").textContent).toBe("abcdef012345");
  });

  // 18 — submissão duplicada evitada
  it("evita submissão duplicada", async () => {
    let release!: () => void;
    const gate = new Promise<void>((r) => {
      release = r;
    });
    const state = baseState({ postDelay: () => gate });
    installFetch(state);
    render(<ExecutionSection productId={PRODUCT_ID} />);
    await fillFormAndPickFunction();
    await addContextVersion("doc-1");
    const submit = screen.getByRole("button", { name: /^preparar execução$/i });
    fireEvent.click(submit);
    // Enquanto pendente: botão desactivado (não permite segunda submissão).
    await waitFor(() => expect(submit).toBeDisabled());
    fireEvent.click(submit); // segundo clique é ignorado
    release();
    await screen.findByRole("heading", { name: "Execução teste", level: 4 });
    expect(state.postCount).toBe(1); // apenas uma criação
  });

  // 19 — erros tratados
  it("trata erro 400 na criação", async () => {
    const state = baseState();
    installFetch(state);
    // Sobrepõe o POST para devolver 400.
    const original = globalThis.fetch as any;
    vi.stubGlobal("fetch", async (u: string, init: RequestInit = {}) => {
      if (u.includes("/v1/executions") && (init.method ?? "GET") === "POST") {
        return json({ context: "inválido" }, 400);
      }
      return original(u, init);
    });
    render(<ExecutionSection productId={PRODUCT_ID} />);
    await fillFormAndPickFunction();
    await addContextVersion("doc-1");
    fireEvent.click(screen.getByRole("button", { name: /^preparar execução$/i }));
    await screen.findByRole("alert");
  });

  // 20 — nenhuma transição/resultado/IA no detalhe
  it("não apresenta transições, resultados nem chamadas a IA", async () => {
    installFetch(baseState());
    render(<ExecutionSection productId={PRODUCT_ID} />);
    await fillFormAndPickFunction();
    await addContextVersion("doc-1");
    fireEvent.click(screen.getByRole("button", { name: /^preparar execução$/i }));
    await screen.findByRole("heading", { name: "Execução teste", level: 4 });
    for (const forbidden of [
      /aprovar/i,
      /rejeitar/i,
      /importar resultado/i,
      /pedir correcção/i,
      /concluir/i,
      /gerar pacote/i,
      /chamar ia/i,
    ]) {
      expect(screen.queryByRole("button", { name: forbidden })).toBeNull();
    }
  });
});
