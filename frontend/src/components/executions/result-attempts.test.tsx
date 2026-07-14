import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import type { ExecutionDetail as Execution } from "../../api/executions";
import { ExecutionDetail } from "./ExecutionDetail";

const EXEC_ID = "exec-1";
const HOSTILE = "<script>alert('x')</script>";

function json(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

function makeExec(over: Partial<Execution> = {}): Execution {
  return {
    id: EXEC_ID,
    organisation: "org-1",
    product: "prod-1",
    function_profile: "fn-1",
    requested_by: "user-1",
    title: "Execução",
    execution_mode: "manual_local",
    status: "prepared",
    document_count: 1,
    version: 1,
    created_at: "2026-07-14T10:00:00Z",
    updated_at: "2026-07-14T10:00:00Z",
    objective: "obj",
    request_instructions: "req",
    constraints: "",
    expected_output_format: "md",
    function_snapshot: {
      id: "fn-1", name: "Analista", actor_type: "human", purpose: "p",
      responsibilities: "r", constraints: "", requires_approval: false,
    },
    product_snapshot: { id: "prod-1", name: "Produto A", purpose: "p", status: "active" },
    instruction_version: null,
    context_documents: [],
    ...over,
  };
}

interface Attempt {
  attempt_number: number;
  source_tool: string;
  source_model: string;
  source_mode: string;
  source_notes: string;
  content: string;
  version_number: number;
  checksum: string;
  byte_size: number;
  created_at: string;
}

interface State {
  execution: Execution;
  attempts: Attempt[];
  calls: string[];
  reviews?: unknown[];
  importResponder?: (body: any) => Response;
}

function attemptJson(a: Attempt, extra: Record<string, unknown> = {}) {
  return {
    id: `att-${a.attempt_number}`,
    organisation: "org-1",
    execution: EXEC_ID,
    attempt_number: a.attempt_number,
    source_mode: a.source_mode,
    source_tool: a.source_tool,
    source_model: a.source_model,
    source_notes: a.source_notes,
    imported_by: "user-1",
    document: `doc-${a.attempt_number}`,
    document_version: `ver-${a.attempt_number}`,
    version_number: a.version_number,
    checksum: a.checksum,
    byte_size: a.byte_size,
    created_at: a.created_at,
    ...extra,
  };
}

function installFetch(state: State) {
  const fetchMock = vi.fn(async (rawUrl: string, init: RequestInit = {}) => {
    const method = init.method ?? "GET";
    const url = new URL(rawUrl, "http://local");
    const path = url.pathname;
    state.calls.push(`${method} ${path}`);
    const isForm = init.body instanceof FormData;
    const body = init.body && !isForm ? JSON.parse(init.body as string) : {};

    if (path.endsWith("/v1/documents/preview") && method === "POST") {
      // Backend devolve HTML sanitizado (script neutralizado como texto).
      return json({ html: "<p>resultado seguro</p>" });
    }
    if (path === `/api/v1/executions/${EXEC_ID}` && method === "GET") {
      return json(state.execution);
    }
    // Lista de tentativas.
    if (path.endsWith("/result-attempts") && method === "GET") {
      return json({
        results: state.attempts.map((a) => attemptJson(a)),
      });
    }
    // Lista de revisões (histórico mínimo; usado pelo ValidationPanel).
    if (path.endsWith("/reviews") && method === "GET") {
      return json({ results: state.reviews ?? [] });
    }
    // Detalhe de uma tentativa (conteúdo da versão exacta).
    const dm = path.match(/\/result-attempts\/(\d+)$/);
    if (dm && method === "GET") {
      const a = state.attempts.find((x) => x.attempt_number === Number(dm[1]));
      if (!a) return json({ detail: "nf" }, 404);
      return json(
        attemptJson(a, {
          content: a.content,
          execution_context: {
            status: state.execution.status,
            version: state.execution.version,
            title: state.execution.title,
            current_result_attempt: `att-${a.attempt_number}`,
          },
        }),
      );
    }
    // Importação.
    if (path.endsWith("/result-attempts") && method === "POST") {
      if (state.importResponder) {
        const parsed = isForm ? Object.fromEntries((init.body as FormData).entries()) : body;
        return state.importResponder(parsed);
      }
      const n = state.attempts.length + 1;
      const content = isForm
        ? "conteúdo de ficheiro"
        : (body.content ?? "");
      const tool = isForm ? (init.body as FormData).get("source_tool") : body.source_tool;
      const mode = isForm ? "file" : "pasted";
      const a: Attempt = {
        attempt_number: n, source_tool: String(tool), source_model: "",
        source_mode: mode, source_notes: "", content: String(content),
        version_number: 1, checksum: "abcdef012345", byte_size: 10,
        created_at: "2026-07-14T11:00:00Z",
      };
      state.attempts.push(a);
      state.execution = {
        ...state.execution,
        status: "result_pending_validation",
        version: state.execution.version + 1,
      };
      return json(
        attemptJson(a, {
          execution: {
            status: "result_pending_validation",
            version: state.execution.version,
            title: state.execution.title,
            current_result_attempt: `att-${n}`,
          },
        }),
        201,
      );
    }
    return json({ detail: "nf" }, 404);
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

function baseState(over: Partial<State> = {}): State {
  return { execution: makeExec(), attempts: [], calls: [], ...over };
}

async function fillAndImportText(content = "resultado colado", tool = "ChatGPT") {
  fireEvent.click(await screen.findByRole("button", { name: /^importar…$/i }));
  fireEvent.change(screen.getByLabelText(/resultado \(markdown/i), {
    target: { value: content },
  });
  fireEvent.change(screen.getByLabelText(/ferramenta de origem/i), {
    target: { value: tool },
  });
  // A submissão do formulário abre a confirmação.
  fireEvent.click(screen.getByRole("button", { name: /^importar…$/i }));
}

describe("ResultAttemptsPanel (resultados)", () => {
  beforeEach(() => {
    document.cookie = "csrftoken=t";
  });
  afterEach(() => {
    vi.restoreAllMocks();
  });

  // 1 — formulário só em prepared
  it("mostra o formulário só em prepared", async () => {
    installFetch(baseState());
    const { rerender } = render(
      <ExecutionDetail execution={makeExec()} onBack={() => {}} />,
    );
    expect(await screen.findByTestId("result-import-form")).toBeInTheDocument();
    installFetch(baseState({ execution: makeExec({ status: "approved" }) }));
    rerender(
      <ExecutionDetail
        execution={makeExec({ status: "approved" })}
        onBack={() => {}}
      />,
    );
    await waitFor(() =>
      expect(screen.queryByTestId("result-import-form")).toBeNull(),
    );
  });

  // 4 — source_tool obrigatório
  it("exige source_tool", async () => {
    installFetch(baseState());
    render(<ExecutionDetail execution={makeExec()} onBack={() => {}} />);
    fireEvent.click(await screen.findByRole("button", { name: /^importar…$/i }));
    fireEvent.change(screen.getByLabelText(/resultado \(markdown/i), {
      target: { value: "x" },
    });
    fireEvent.click(screen.getByRole("button", { name: /^importar…$/i }));
    expect((await screen.findByRole("alert")).textContent).toMatch(/ferramenta/i);
  });

  // 5 — content e file não coexistem (modo exclusivo)
  it("apresenta uma única origem de cada vez", async () => {
    installFetch(baseState());
    render(<ExecutionDetail execution={makeExec()} onBack={() => {}} />);
    fireEvent.click(await screen.findByRole("button", { name: /^importar…$/i }));
    expect(screen.getByLabelText(/resultado \(markdown/i)).toBeInTheDocument();
    expect(screen.queryByLabelText(/^ficheiro/i)).toBeNull();
    fireEvent.click(screen.getByLabelText(/carregar ficheiro/i));
    expect(screen.getByLabelText(/^ficheiro/i)).toBeInTheDocument();
    expect(screen.queryByLabelText(/resultado \(markdown/i)).toBeNull();
  });

  // 6 — confirmação explica importar ≠ aprovar ≠ aplicar
  it("a confirmação explica importar ≠ aprovar ≠ aplicar", async () => {
    installFetch(baseState());
    render(<ExecutionDetail execution={makeExec()} onBack={() => {}} />);
    await fillAndImportText();
    const confirm = await screen.findByTestId("import-confirm");
    expect(confirm.textContent).toMatch(/não.*aprova/i);
    expect(confirm.textContent).toMatch(/não.*aplica/i);
    expect(confirm.textContent).toMatch(/imutável/i);
  });

  // 2 + 10 + 11 — importar por texto → pending → tentativa actual apresentada
  it("importa por texto e mostra result_pending_validation", async () => {
    installFetch(baseState());
    render(<ExecutionDetail execution={makeExec()} onBack={() => {}} />);
    await fillAndImportText("meu resultado");
    fireEvent.click(await screen.findByRole("button", { name: /confirmar importação/i }));
    // Estado da execução actualizado.
    await waitFor(() =>
      expect(screen.getByTestId("execution-status").textContent).toBe(
        "Resultado por validar",
      ),
    );
    // Em result_pending_validation o painel de revisão assume.
    expect(screen.getByTestId("validation-panel")).toBeInTheDocument();
    // Tentativa actual aberta.
    await screen.findByTestId("result-attempt-view");
    expect(screen.getByTestId("attempt-current")).toBeInTheDocument();
  });

  // 3 — importar por ficheiro
  it("importa por ficheiro (multipart)", async () => {
    const state = baseState();
    installFetch(state);
    render(<ExecutionDetail execution={makeExec()} onBack={() => {}} />);
    fireEvent.click(await screen.findByRole("button", { name: /^importar…$/i }));
    fireEvent.click(screen.getByLabelText(/carregar ficheiro/i));
    const file = new File(["conteúdo md"], "r.md", { type: "text/markdown" });
    fireEvent.change(screen.getByLabelText(/ficheiro \(markdown/i), {
      target: { files: [file] },
    });
    expect(screen.getByTestId("file-name").textContent).toMatch(/r\.md/);
    fireEvent.change(screen.getByLabelText(/ferramenta de origem/i), {
      target: { value: "Claude" },
    });
    fireEvent.click(screen.getByRole("button", { name: /^importar…$/i }));
    fireEvent.click(await screen.findByRole("button", { name: /confirmar importação/i }));
    await waitFor(() =>
      expect(screen.getByTestId("execution-status").textContent).toBe(
        "Resultado por validar",
      ),
    );
    // Foi um POST multipart ao endpoint de tentativas.
    expect(state.calls).toContain(`POST /api/v1/executions/${EXEC_ID}/result-attempts`);
  });

  // 7 — submissão duplicada evitada
  it("evita submissão duplicada", async () => {
    let release!: () => void;
    const gate = new Promise<void>((r) => (release = r));
    const state = baseState({
      importResponder: () => {
        throw new Error("unused");
      },
    });
    // Substitui o responder por um que espera antes de responder 201.
    state.importResponder = undefined;
    installFetch(state);
    // Intercepta o POST para atrasar.
    const original = globalThis.fetch as any;
    vi.stubGlobal("fetch", async (u: string, init: RequestInit = {}) => {
      if (u.endsWith("/result-attempts") && (init.method ?? "GET") === "POST") {
        await gate;
      }
      return original(u, init);
    });
    render(<ExecutionDetail execution={makeExec()} onBack={() => {}} />);
    await fillAndImportText("r");
    const confirm = await screen.findByRole("button", { name: /confirmar importação/i });
    fireEvent.click(confirm);
    await waitFor(() => expect(confirm).toBeDisabled());
    fireEvent.click(confirm); // ignorado
    release();
    await waitFor(() =>
      expect(screen.getByTestId("execution-status").textContent).toBe(
        "Resultado por validar",
      ),
    );
    const posts = state.calls.filter(
      (c) => c === `POST /api/v1/executions/${EXEC_ID}/result-attempts`,
    );
    expect(posts.length).toBe(1);
  });

  // 8 — erro 413 apresentado
  it("apresenta o erro 413", async () => {
    const state = baseState({
      importResponder: () => json({ content: "grande" }, 413),
    });
    installFetch(state);
    render(<ExecutionDetail execution={makeExec()} onBack={() => {}} />);
    await fillAndImportText("r");
    fireEvent.click(await screen.findByRole("button", { name: /confirmar importação/i }));
    expect((await screen.findByRole("alert")).textContent).toMatch(/413|limite/i);
  });

  // 9 — erro 409 recarrega o estado
  it("recarrega o estado em 409", async () => {
    const state = baseState({
      importResponder: () => json({ detail: "estado mudou" }, 409),
    });
    installFetch(state);
    render(<ExecutionDetail execution={makeExec()} onBack={() => {}} />);
    await fillAndImportText("r");
    fireEvent.click(await screen.findByRole("button", { name: /confirmar importação/i }));
    expect(await screen.findByTestId("import-conflict")).toBeInTheDocument();
    // Recarregou a execução (GET do detalhe).
    expect(state.calls).toContain(`GET /api/v1/executions/${EXEC_ID}`);
  });

  // 12 + 11 — histórico lista várias; tentativa actual identificada
  it("lista o histórico com a tentativa actual identificada", async () => {
    const state = baseState({
      execution: makeExec({ status: "result_pending_validation", version: 3 }),
      attempts: [
        { attempt_number: 1, source_tool: "T1", source_model: "", source_mode: "pasted",
          source_notes: "", content: "c1", version_number: 1, checksum: "aaa111222333",
          byte_size: 2, created_at: "2026-07-14T10:00:00Z" },
        { attempt_number: 2, source_tool: "T2", source_model: "", source_mode: "file",
          source_notes: "", content: "c2", version_number: 1, checksum: "bbb111222333",
          byte_size: 2, created_at: "2026-07-14T10:30:00Z" },
      ],
    });
    installFetch(state);
    render(
      <ExecutionDetail
        execution={makeExec({ status: "result_pending_validation", version: 3 })}
        onBack={() => {}}
      />,
    );
    const history = await screen.findByTestId("attempt-history");
    expect(within(history).getByRole("button", { name: "Tentativa 1" })).toBeInTheDocument();
    expect(within(history).getByRole("button", { name: "Tentativa 2" })).toBeInTheDocument();
    expect(screen.getByTestId("history-current")).toBeInTheDocument();
  });

  // 13 — abrir tentativa histórica usa conteúdo exacto
  it("abre a tentativa histórica com o conteúdo exacto", async () => {
    const state = baseState({
      execution: makeExec({ status: "result_pending_validation", version: 3 }),
      attempts: [
        { attempt_number: 1, source_tool: "T1", source_model: "", source_mode: "pasted",
          source_notes: "", content: "CONTEUDO_V1_EXACTO", version_number: 1,
          checksum: "aaa111222333", byte_size: 2, created_at: "2026-07-14T10:00:00Z" },
        { attempt_number: 2, source_tool: "T2", source_model: "", source_mode: "file",
          source_notes: "", content: "conteudo v2", version_number: 1,
          checksum: "bbb111222333", byte_size: 2, created_at: "2026-07-14T10:30:00Z" },
      ],
    });
    installFetch(state);
    render(
      <ExecutionDetail
        execution={makeExec({ status: "result_pending_validation", version: 3 })}
        onBack={() => {}}
      />,
    );
    const history = await screen.findByTestId("attempt-history");
    fireEvent.click(within(history).getByRole("button", { name: "Tentativa 1" }));
    const view = await screen.findByTestId("result-attempt-view");
    expect(within(view).getByTestId("attempt-text").textContent).toContain(
      "CONTEUDO_V1_EXACTO",
    );
  });

  // 14/15/20 — sem editar/eliminar/aplicar (a revisão existe em PR03, a aplicação não)
  it("não oferece editar, eliminar nem aplicar", async () => {
    const state = baseState({
      execution: makeExec({ status: "result_pending_validation", version: 2 }),
      attempts: [
        { attempt_number: 1, source_tool: "T", source_model: "", source_mode: "pasted",
          source_notes: "", content: "c", version_number: 1, checksum: "aaa111222333",
          byte_size: 1, created_at: "2026-07-14T10:00:00Z" },
      ],
    });
    installFetch(state);
    render(
      <ExecutionDetail
        execution={makeExec({ status: "result_pending_validation", version: 2 })}
        onBack={() => {}}
      />,
    );
    await screen.findByTestId("attempt-history");
    // A aplicação (e edição/eliminação/recuperação/conclusão) NÃO existe aqui.
    for (const forbidden of [
      /aplicar/i, /editar resultado/i, /eliminar/i, /apagar/i,
      /recuperar vers/i, /concluir/i,
    ]) {
      expect(screen.queryByRole("button", { name: forbidden })).toBeNull();
    }
  });

  // 16 + 17 + 18 — preview segura (backend), hostil não executa, texto como texto
  it("mostra texto original e pré-visualização segura do backend", async () => {
    const state = baseState({
      execution: makeExec({ status: "result_pending_validation", version: 2 }),
      attempts: [
        { attempt_number: 1, source_tool: "T", source_model: "", source_mode: "pasted",
          source_notes: "", content: `Nota\n${HOSTILE}`, version_number: 1,
          checksum: "aaa111222333", byte_size: 5, created_at: "2026-07-14T10:00:00Z" },
      ],
    });
    installFetch(state);
    render(
      <ExecutionDetail
        execution={makeExec({ status: "result_pending_validation", version: 2 })}
        onBack={() => {}}
      />,
    );
    const history = await screen.findByTestId("attempt-history");
    fireEvent.click(within(history).getByRole("button", { name: "Tentativa 1" }));
    const view = await screen.findByTestId("result-attempt-view");
    // Texto original como TEXTO (script literal, não executado).
    const text = within(view).getByTestId("attempt-text");
    expect(text.tagName).toBe("PRE");
    expect(text.textContent).toContain(HOSTILE);
    expect(document.querySelector("script")).toBeNull();
    // Pré-visualização usa o backend.
    fireEvent.click(within(view).getByRole("button", { name: /pré-visualização segura/i }));
    await within(view).findByTestId("document-preview-html");
    expect(state.calls).toContain("POST /api/v1/documents/preview");
  });

  // 21 — importar não chama Product/documentos/decisões/pendências
  it("importar só toca em resultados/execução/preview", async () => {
    const state = baseState();
    installFetch(state);
    render(<ExecutionDetail execution={makeExec()} onBack={() => {}} />);
    await fillAndImportText("r");
    fireEvent.click(await screen.findByRole("button", { name: /confirmar importação/i }));
    await waitFor(() =>
      expect(screen.getByTestId("execution-status").textContent).toBe(
        "Resultado por validar",
      ),
    );
    for (const c of state.calls) {
      expect(c).toMatch(
        /result-attempts|\/executions\/exec-1$|\/reviews$|\/documents\/preview/,
      );
    }
    expect(state.calls.some((c) => /products|decisions|work-items/.test(c))).toBe(false);
  });
});
