import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import type { ExecutionDetail as Execution } from "../../api/executions";
import { ExecutionDetail } from "./ExecutionDetail";

// Testes da aplicação controlada no browser (F1-P06-PR04, MVP-15): o
// ApplicationPanel aparece em `approved`, exige escolha de documento + conteúdo
// revisto + confirmação explícita (aprovar não aplicou nada), trata 409 e mostra
// a versão criada. Não apresenta decisões nem pendências.

const EXEC_ID = "exec-1";
const DOC_ID = "doc-alvo-1";

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
    status: "approved",
    document_count: 1,
    version: 3,
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

interface State {
  execution: Execution;
  calls: string[];
  applyResponder?: () => Response;
}

function docSummary() {
  return {
    id: DOC_ID, organisation: "org-1", product: "prod-1", title: "Visão",
    document_type: "visao_de_produto", is_outdated: false, export_policy: "allowed",
    current_version_number: 1, version: 1,
    created_at: "2026-07-14T09:00:00Z", updated_at: "2026-07-14T09:00:00Z",
  };
}

function installFetch(state: State) {
  const fetchMock = vi.fn(async (rawUrl: string, init: RequestInit = {}) => {
    const method = init.method ?? "GET";
    const path = new URL(rawUrl, "http://local").pathname;
    state.calls.push(`${method} ${path}`);

    if (path === `/api/v1/executions/${EXEC_ID}` && method === "GET") {
      return json(state.execution);
    }
    if (path.endsWith("/result-attempts") && method === "GET") {
      return json({
        results: [{
          id: "att-1", organisation: "org-1", execution: EXEC_ID, attempt_number: 1,
          source_mode: "pasted", source_tool: "ChatGPT", source_model: "",
          source_notes: "", imported_by: "user-1", document: "doc-r-1",
          document_version: "ver-r-1", version_number: 1, checksum: "aaa111222333",
          byte_size: 5, created_at: "2026-07-14T10:00:00Z",
        }],
      });
    }
    if (path.endsWith("/reviews") && method === "GET") {
      return json({
        results: [{
          id: "rev-1", organisation: "org-1", execution: EXEC_ID,
          result_attempt: "att-1", attempt_number: 1, reviewer: "user-1",
          decision: "approved", observations: "", created_at: "2026-07-14T11:00:00Z",
        }],
      });
    }
    const am = path.match(/\/result-attempts\/(\d+)$/);
    if (am && method === "GET") {
      return json({ attempt_number: 1, content: "RESULTADO ORIGINAL",
        source_tool: "ChatGPT", source_mode: "pasted", version_number: 1,
        checksum: "aaa111222333", byte_size: 5, created_at: "2026-07-14T10:00:00Z",
        source_model: "", source_notes: "" });
    }
    if (path === "/api/v1/documents" && method === "GET") {
      return json({ results: [docSummary()], count: 1, page: 1, page_size: 100, num_pages: 1 });
    }
    if (path === "/api/v1/decisions" && method === "GET") {
      return json({ results: [], count: 0, page: 1, page_size: 100, num_pages: 1 });
    }
    if (path === "/api/v1/work-items" && method === "GET") {
      return json({ results: [], count: 0, page: 1, page_size: 100, num_pages: 1 });
    }
    if (path === `/api/v1/documents/${DOC_ID}` && method === "GET") {
      return json({ ...docSummary(), content: "conteúdo actual do alvo",
        checksum: "bbb111222333" });
    }
    if (path.endsWith("/apply/document") && method === "POST") {
      if (state.applyResponder) return state.applyResponder();
      state.execution = { ...state.execution, status: "completed", version: 4 };
      return json({
        application: {
          id: "app-1", organisation: "org-1", execution: EXEC_ID,
          result_attempt: "att-1", attempt_number: 1, review: "rev-1",
          application_type: "document", applied_by: "user-1",
          change_summary: "Aplica", target_document: DOC_ID,
          base_document_version: "ver-1", created_document_version: "ver-2",
          base_version_number: 1, created_version_number: 2,
          created_version_checksum: "ccc111222333", created_at: "2026-07-14T12:00:00Z",
        },
        execution: { status: "completed", version: 4, title: "Execução",
          current_result_attempt: "att-1" },
      }, 201);
    }
    return json({ detail: "nf" }, 404);
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

function baseState(over: Partial<State> = {}): State {
  return { execution: makeExec(), calls: [], ...over };
}

async function selectTargetAndFill(content = "conteúdo final revisto") {
  const view = await screen.findByTestId("application-panel");
  fireEvent.click(await within(view).findByTestId("option-document"));
  fireEvent.change(within(view).getByTestId("target-select"), {
    target: { value: DOC_ID },
  });
  await within(view).findByTestId("apply-content");
  fireEvent.change(within(view).getByTestId("apply-content"), {
    target: { value: content },
  });
  fireEvent.change(within(view).getByTestId("apply-change-summary"), {
    target: { value: "Aplica revisto" },
  });
}

describe("ApplicationPanel (aplicação controlada)", () => {
  beforeEach(() => {
    document.cookie = "csrftoken=t";
  });
  afterEach(() => {
    vi.restoreAllMocks();
  });

  // 30 — UI exige escolha e confirmação (aprovar não aplicou nada)
  it("exige escolha, conteúdo e confirmação explícita", async () => {
    const state = baseState();
    installFetch(state);
    render(<ExecutionDetail execution={makeExec()} onBack={() => {}} />);
    const view = await screen.findByTestId("application-panel");
    expect(within(view).getByTestId("approval-did-not-apply")).toBeInTheDocument();
    await selectTargetAndFill();
    // Abre a confirmação, que explica conteúdo revisto / nova versão / completed.
    fireEvent.click(within(view).getByTestId("apply-open-confirm"));
    const confirm = await within(view).findByTestId("apply-confirm");
    expect(confirm.textContent).toMatch(/revisto/i);
    expect(confirm.textContent).toMatch(/nova versão oficial/i);
    expect(confirm.textContent).toMatch(/conclu/i);
    fireEvent.click(within(view).getByTestId("apply-confirm-button"));
    await waitFor(() =>
      expect(
        state.calls.some((c) => c.endsWith("/apply/document")),
      ).toBe(true),
    );
  });

  // 30b — sem conteúdo não avança para confirmação
  it("não confirma sem conteúdo", async () => {
    installFetch(baseState());
    render(<ExecutionDetail execution={makeExec()} onBack={() => {}} />);
    const view = await screen.findByTestId("application-panel");
    fireEvent.click(await within(view).findByTestId("option-document"));
    fireEvent.change(within(view).getByTestId("target-select"), {
      target: { value: DOC_ID },
    });
    await within(view).findByTestId("apply-content");
    fireEvent.click(within(view).getByTestId("apply-open-confirm"));
    expect((await within(view).findByRole("alert")).textContent).toMatch(/conteúdo/i);
    expect(within(view).queryByTestId("apply-confirm")).toBeNull();
  });

  // 31 — UI trata conflito 409 (recarrega sem sobrescrever)
  it("trata um 409 recarregando o estado", async () => {
    const state = baseState({
      applyResponder: () => json({ detail: "Versão desactualizada." }, 409),
    });
    installFetch(state);
    render(<ExecutionDetail execution={makeExec()} onBack={() => {}} />);
    await selectTargetAndFill();
    const view = screen.getByTestId("application-panel");
    fireEvent.click(within(view).getByTestId("apply-open-confirm"));
    fireEvent.click(await within(view).findByTestId("apply-confirm-button"));
    expect(await screen.findByTestId("application-conflict")).toBeInTheDocument();
    // Recarregou o documento e a execução.
    expect(state.calls).toContain(`GET /api/v1/documents/${DOC_ID}`);
  });

  // 32 — UI mostra resultado aplicado (versão criada + ligação)
  it("mostra a versão criada após aplicar", async () => {
    installFetch(baseState());
    render(<ExecutionDetail execution={makeExec()} onBack={() => {}} />);
    await selectTargetAndFill();
    const view = screen.getByTestId("application-panel");
    fireEvent.click(within(view).getByTestId("apply-open-confirm"));
    fireEvent.click(await within(view).findByTestId("apply-confirm-button"));
    const done = await screen.findByTestId("application-done");
    expect(done.textContent).toMatch(/v1 → v2/);
    expect(done.textContent).toMatch(/document/i);
    expect(within(done).getByTestId("application-finish")).toBeInTheDocument();
  });

  // Extra — apresenta os quatro caminhos (PR05)
  it("apresenta os quatro caminhos de aplicação", async () => {
    installFetch(baseState());
    render(<ExecutionDetail execution={makeExec()} onBack={() => {}} />);
    const view = await screen.findByTestId("application-panel");
    expect(within(view).getByTestId("option-document")).toBeInTheDocument();
    expect(within(view).getByTestId("option-decision")).toBeInTheDocument();
    expect(within(view).getByTestId("option-work_item")).toBeInTheDocument();
    expect(within(view).getByTestId("option-no_change")).toBeInTheDocument();
  });
});
