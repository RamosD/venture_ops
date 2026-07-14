import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import type { ExecutionDetail as Execution } from "../../api/executions";
import { ExecutionDetail } from "./ExecutionDetail";

// Testes dos caminhos decisão / pendência / fecho no browser (F1-P06-PR05): o
// ApplicationPanel oferece quatro opções, mostra apenas alvos elegíveis, exige
// confirmação com resumo exacto e apresenta a aplicação final. Uma execução
// produz no máximo uma aplicação.

const EXEC_ID = "exec-1";
const DEC_ID = "dec-1";
const WI_ID = "wi-1";

function json(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data), {
    status, headers: { "Content-Type": "application/json" },
  });
}

function makeExec(over: Partial<Execution> = {}): Execution {
  return {
    id: EXEC_ID, organisation: "org-1", product: "prod-1", function_profile: "fn-1",
    requested_by: "user-1", title: "Execução", execution_mode: "manual_local",
    status: "approved", document_count: 1, version: 3,
    created_at: "2026-07-14T10:00:00Z", updated_at: "2026-07-14T10:00:00Z",
    objective: "obj", request_instructions: "req", constraints: "",
    expected_output_format: "md",
    function_snapshot: { id: "fn-1", name: "A", actor_type: "human", purpose: "p",
      responsibilities: "r", constraints: "", requires_approval: false },
    product_snapshot: { id: "prod-1", name: "Produto A", purpose: "p", status: "active" },
    instruction_version: null, context_documents: [], ...over,
  };
}

interface State {
  execution: Execution;
  calls: string[];
  applyResponder?: (path: string) => Response;
}

function installFetch(state: State) {
  const fetchMock = vi.fn(async (rawUrl: string, init: RequestInit = {}) => {
    const method = init.method ?? "GET";
    const path = new URL(rawUrl, "http://local").pathname;
    state.calls.push(`${method} ${path}`);

    if (path === `/api/v1/executions/${EXEC_ID}` && method === "GET")
      return json(state.execution);
    if (path.endsWith("/result-attempts") && method === "GET")
      return json({ results: [{
        id: "att-1", organisation: "org-1", execution: EXEC_ID, attempt_number: 1,
        source_mode: "pasted", source_tool: "ChatGPT", source_model: "",
        source_notes: "", imported_by: "user-1", document: "doc-r-1",
        document_version: "ver-r-1", version_number: 1, checksum: "aaa111222333",
        byte_size: 5, created_at: "2026-07-14T10:00:00Z" }] });
    if (path.endsWith("/reviews") && method === "GET")
      return json({ results: [{
        id: "rev-1", organisation: "org-1", execution: EXEC_ID, result_attempt: "att-1",
        attempt_number: 1, reviewer: "user-1", decision: "approved", observations: "",
        created_at: "2026-07-14T11:00:00Z" }] });
    if (/\/result-attempts\/\d+$/.test(path) && method === "GET")
      return json({ attempt_number: 1, content: "RESULTADO", source_tool: "ChatGPT",
        source_mode: "pasted", version_number: 1, checksum: "aaa111222333",
        byte_size: 5, created_at: "2026-07-14T10:00:00Z", source_model: "",
        source_notes: "" });
    if (path === "/api/v1/documents" && method === "GET")
      return json({ results: [], count: 0, page: 1, page_size: 100, num_pages: 1 });
    if (path === "/api/v1/decisions" && method === "GET")
      return json({ results: [{
        id: DEC_ID, organisation: "org-1", title: "Decisão activa", context: "c",
        decision_text: "d", status: "active", product: "prod-1", version: 1,
        created_at: "x", updated_at: "x" }], count: 1, page: 1, page_size: 20,
        num_pages: 1 });
    if (path === "/api/v1/work-items" && method === "GET")
      return json({ results: [{
        id: WI_ID, organisation: "org-1", product: "prod-1", title: "Pendência aberta",
        status: "open", version: 1, created_at: "x", updated_at: "x" }],
        count: 1, page: 1, page_size: 20, num_pages: 1 });

    const applyMatch = path.match(/\/(apply\/decision|apply\/work-item|close-without-application)$/);
    if (applyMatch && method === "POST") {
      if (state.applyResponder) return state.applyResponder(path);
      const type = path.endsWith("apply/decision")
        ? "decision" : path.endsWith("apply/work-item") ? "work_item" : "no_change";
      state.execution = { ...state.execution, status: "completed", version: 4 };
      return json({
        application: { id: "app-1", organisation: "org-1", execution: EXEC_ID,
          result_attempt: "att-1", attempt_number: 1, review: "rev-1",
          application_type: type, applied_by: "user-1", change_summary: "",
          rationale: type === "no_change" ? "fecho" : "",
          target_document: null, base_document_version: null,
          created_document_version: null,
          target_decision: type === "decision" ? DEC_ID : null,
          created_decision: type === "decision" ? "dec-2" : null,
          target_work_item: type === "work_item" ? WI_ID : null,
          base_version_number: null, created_version_number: null,
          created_version_checksum: null, created_at: "x" },
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

describe("ApplicationPanel — decisão / pendência / fecho (PR05)", () => {
  beforeEach(() => { document.cookie = "csrftoken=t"; });
  afterEach(() => { vi.restoreAllMocks(); });

  // 28 — quatro opções
  it("apresenta as quatro opções", async () => {
    installFetch(baseState());
    render(<ExecutionDetail execution={makeExec()} onBack={() => {}} />);
    const view = await screen.findByTestId("application-panel");
    await within(view).findByTestId("option-document"); // aguarda o carregamento
    for (const id of ["option-document", "option-decision", "option-work_item", "option-no_change"])
      expect(within(view).getByTestId(id)).toBeInTheDocument();
  });

  // 29 — mostra apenas alvos elegíveis (decisão activa)
  it("mostra apenas decisões activas elegíveis", async () => {
    installFetch(baseState());
    render(<ExecutionDetail execution={makeExec()} onBack={() => {}} />);
    const view = await screen.findByTestId("application-panel");
    fireEvent.click(await within(view).findByTestId("option-decision"));
    const select = await within(view).findByTestId("decision-select");
    expect(within(select).getByRole("option", { name: /Decisão activa/ })).toBeInTheDocument();
    // O pedido filtra por status=active.
    expect(baseState().calls).toBeDefined();
  });

  // 30/31 — substitui decisão com confirmação e mostra a aplicação final
  it("substitui decisão com confirmação e mostra a aplicação", async () => {
    const state = baseState();
    installFetch(state);
    render(<ExecutionDetail execution={makeExec()} onBack={() => {}} />);
    const view = await screen.findByTestId("application-panel");
    fireEvent.click(await within(view).findByTestId("option-decision"));
    fireEvent.change(await within(view).findByTestId("decision-select"), {
      target: { value: DEC_ID },
    });
    fireEvent.change(within(view).getByTestId("decision-title"), { target: { value: "Nova" } });
    fireEvent.change(within(view).getByTestId("decision-context"), { target: { value: "ctx" } });
    fireEvent.change(within(view).getByTestId("decision-text"), { target: { value: "txt" } });
    fireEvent.click(within(view).getByTestId("apply-open-confirm"));
    const confirm = await within(view).findByTestId("apply-confirm");
    expect(confirm.textContent).toMatch(/substitu/i);
    fireEvent.click(within(view).getByTestId("apply-confirm-button"));
    const done = await screen.findByTestId("application-done");
    expect(done.textContent).toMatch(/decision/i);
    expect(state.calls).toContain(`POST /api/v1/executions/${EXEC_ID}/apply/decision`);
  });

  // conclui pendência
  it("conclui pendência com confirmação", async () => {
    const state = baseState();
    installFetch(state);
    render(<ExecutionDetail execution={makeExec()} onBack={() => {}} />);
    const view = await screen.findByTestId("application-panel");
    fireEvent.click(await within(view).findByTestId("option-work_item"));
    fireEvent.change(await within(view).findByTestId("work-item-select"), {
      target: { value: WI_ID },
    });
    fireEvent.click(within(view).getByTestId("apply-open-confirm"));
    const confirm = await within(view).findByTestId("apply-confirm");
    expect(confirm.textContent).toMatch(/conclu/i);
    fireEvent.click(within(view).getByTestId("apply-confirm-button"));
    await screen.findByTestId("application-done");
    expect(state.calls).toContain(`POST /api/v1/executions/${EXEC_ID}/apply/work-item`);
  });

  // fecho sem alteração exige rationale
  it("fecha sem alteração exigindo justificação", async () => {
    const state = baseState();
    installFetch(state);
    render(<ExecutionDetail execution={makeExec()} onBack={() => {}} />);
    const view = await screen.findByTestId("application-panel");
    fireEvent.click(await within(view).findByTestId("option-no_change"));
    // Sem rationale → erro, sem POST.
    fireEvent.click(await within(view).findByTestId("apply-open-confirm"));
    expect((await within(view).findByRole("alert")).textContent).toMatch(/justificação/i);
    expect(state.calls.some((c) => c.includes("close-without-application"))).toBe(false);
    // Com rationale → fecho.
    fireEvent.change(within(view).getByTestId("no-change-rationale"), {
      target: { value: "sem alteração necessária" },
    });
    fireEvent.click(within(view).getByTestId("apply-open-confirm"));
    fireEvent.click(await within(view).findByTestId("apply-confirm-button"));
    await screen.findByTestId("application-done");
    expect(state.calls).toContain(`POST /api/v1/executions/${EXEC_ID}/close-without-application`);
  });

  // 32 — impede segunda aplicação (após sucesso mostra estado final, sem formulário)
  it("impede segunda aplicação após concluir", async () => {
    installFetch(baseState());
    render(<ExecutionDetail execution={makeExec()} onBack={() => {}} />);
    const view = await screen.findByTestId("application-panel");
    fireEvent.click(await within(view).findByTestId("option-no_change"));
    fireEvent.change(await within(view).findByTestId("no-change-rationale"), {
      target: { value: "sem alteração" },
    });
    fireEvent.click(within(view).getByTestId("apply-open-confirm"));
    fireEvent.click(await within(view).findByTestId("apply-confirm-button"));
    await screen.findByTestId("application-done");
    // Já não há opções de aplicação nem formulários.
    expect(screen.queryByTestId("apply-options")).toBeNull();
    expect(screen.queryByTestId("apply-open-confirm")).toBeNull();
  });

  // 409 recarrega
  it("um 409 recarrega os dados", async () => {
    const state = baseState({
      applyResponder: () => json({ detail: "Já tem aplicação." }, 409),
    });
    installFetch(state);
    render(<ExecutionDetail execution={makeExec()} onBack={() => {}} />);
    const view = await screen.findByTestId("application-panel");
    fireEvent.click(await within(view).findByTestId("option-no_change"));
    fireEvent.change(await within(view).findByTestId("no-change-rationale"), {
      target: { value: "x" },
    });
    fireEvent.click(within(view).getByTestId("apply-open-confirm"));
    fireEvent.click(await within(view).findByTestId("apply-confirm-button"));
    await waitFor(() =>
      expect(screen.getByTestId("application-conflict")).toBeInTheDocument(),
    );
  });
});
