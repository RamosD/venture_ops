import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import type { ExecutionDetail as Execution } from "../../api/executions";
import { ExecutionDetail } from "./ExecutionDetail";

// Testes da revisão humana no browser (F1-P06-PR03, MVP-14): o ValidationPanel
// aparece em `result_pending_validation` e permite Aprovar (com confirmação
// explícita de que aprovar NÃO aplica), Rejeitar e Pedir correcção (ambos exigem
// observações), mostrando o histórico de tentativas e revisões. Nenhuma acção de
// aplicação existe nesta etapa.

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
    status: "result_pending_validation",
    document_count: 1,
    version: 2,
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
  source_mode: string;
  content: string;
  checksum: string;
  created_at?: string;
}

interface Review {
  id: string;
  attempt_number: number;
  decision: string;
  observations: string;
  created_at: string;
}

interface State {
  execution: Execution;
  attempts: Attempt[];
  reviews: Review[];
  calls: string[];
}

function attemptJson(a: Attempt, extra: Record<string, unknown> = {}) {
  return {
    id: `att-${a.attempt_number}`,
    organisation: "org-1",
    execution: EXEC_ID,
    attempt_number: a.attempt_number,
    source_mode: a.source_mode,
    source_tool: a.source_tool,
    source_model: "",
    source_notes: "",
    imported_by: "user-1",
    document: `doc-${a.attempt_number}`,
    document_version: `ver-${a.attempt_number}`,
    version_number: 1,
    checksum: a.checksum,
    byte_size: 10,
    created_at: a.created_at ?? "2026-07-14T11:00:00Z",
    ...extra,
  };
}

function installFetch(state: State) {
  const fetchMock = vi.fn(async (rawUrl: string, init: RequestInit = {}) => {
    const method = init.method ?? "GET";
    const path = new URL(rawUrl, "http://local").pathname;
    state.calls.push(`${method} ${path}`);
    const body = init.body ? JSON.parse(init.body as string) : {};

    if (path.endsWith("/v1/documents/preview") && method === "POST") {
      return json({ html: "<p>resultado seguro</p>" });
    }
    if (path === `/api/v1/executions/${EXEC_ID}` && method === "GET") {
      return json(state.execution);
    }
    if (path.endsWith("/result-attempts") && method === "GET") {
      return json({ results: state.attempts.map((a) => attemptJson(a)) });
    }
    if (path.endsWith("/reviews") && method === "GET") {
      return json({
        results: state.reviews.map((r) => ({
          id: r.id, organisation: "org-1", execution: EXEC_ID,
          result_attempt: `att-${r.attempt_number}`, attempt_number: r.attempt_number,
          reviewer: "user-1", decision: r.decision, observations: r.observations,
          created_at: r.created_at,
        })),
      });
    }
    const dm = path.match(/\/result-attempts\/(\d+)$/);
    if (dm && method === "GET") {
      const a = state.attempts.find((x) => x.attempt_number === Number(dm[1]));
      if (!a) return json({ detail: "nf" }, 404);
      return json(
        attemptJson(a, {
          content: a.content,
          execution_context: {
            status: state.execution.status, version: state.execution.version,
            title: state.execution.title, current_result_attempt: `att-${a.attempt_number}`,
          },
        }),
      );
    }
    // Comandos de revisão.
    const rm = path.match(/\/result-attempts\/(\d+)\/(approve|reject|request-correction)$/);
    if (rm && method === "POST") {
      const attemptNumber = Number(rm[1]);
      const op = rm[2];
      const decision =
        op === "approve" ? "approved" : op === "reject" ? "rejected" : "correction_requested";
      const nextStatus =
        op === "approve" ? "approved" : op === "reject" ? "rejected" : "prepared";
      const review: Review = {
        id: `rev-${state.reviews.length + 1}`, attempt_number: attemptNumber,
        decision, observations: body.observations ?? "",
        created_at: "2026-07-14T12:00:00Z",
      };
      state.reviews.push(review);
      state.execution = {
        ...state.execution,
        status: nextStatus as Execution["status"],
        version: state.execution.version + 1,
      };
      return json(
        {
          review: {
            id: review.id, organisation: "org-1", execution: EXEC_ID,
            result_attempt: `att-${attemptNumber}`, attempt_number: attemptNumber,
            reviewer: "user-1", decision, observations: review.observations,
            created_at: review.created_at,
          },
          execution: {
            status: nextStatus, version: state.execution.version,
            title: state.execution.title, current_result_attempt: `att-${attemptNumber}`,
          },
          attempt: attemptJson(
            state.attempts.find((x) => x.attempt_number === attemptNumber)!,
          ),
        },
        201,
      );
    }
    return json({ detail: "nf" }, 404);
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

function baseState(over: Partial<State> = {}): State {
  return {
    execution: makeExec(),
    attempts: [
      { attempt_number: 1, source_tool: "ChatGPT", source_mode: "pasted",
        content: `Nota\n${HOSTILE}`, checksum: "aaa111222333" },
    ],
    reviews: [],
    calls: [],
    ...over,
  };
}

describe("ValidationPanel (revisão humana)", () => {
  beforeEach(() => {
    document.cookie = "csrftoken=t";
  });
  afterEach(() => {
    vi.restoreAllMocks();
  });

  // 25 — UI apresenta contexto completo (tentativa actual, conteúdo, preview, histórico)
  it("apresenta a tentativa actual, o conteúdo e a pré-visualização segura", async () => {
    installFetch(baseState());
    render(<ExecutionDetail execution={makeExec()} onBack={() => {}} />);
    expect(await screen.findByTestId("validation-panel")).toBeInTheDocument();
    // Tentativa actual aberta por defeito.
    const view = await screen.findByTestId("result-attempt-view");
    expect(within(view).getByTestId("attempt-current")).toBeInTheDocument();
    // Texto original como TEXTO (script literal, não executado).
    const text = await within(view).findByTestId("attempt-text");
    expect(text.tagName).toBe("PRE");
    expect(text.textContent).toContain(HOSTILE);
    expect(document.querySelector("script")).toBeNull();
    // Pré-visualização usa o backend.
    fireEvent.click(within(view).getByRole("button", { name: /pré-visualização segura/i }));
    await within(view).findByTestId("document-preview-html");
  });

  // 26 — UI aprova com confirmação explícita (aprovar ≠ aplicar)
  it("aprova com confirmação que explica que aprovar não aplica", async () => {
    const state = baseState();
    installFetch(state);
    render(<ExecutionDetail execution={makeExec()} onBack={() => {}} />);
    fireEvent.click(await screen.findByTestId("action-approve"));
    const confirm = await screen.findByTestId("approve-confirm");
    expect(confirm.textContent).toMatch(/valida/i);
    expect(confirm.textContent).toMatch(/não.*aplica/i);
    expect(confirm.textContent).toMatch(/posterior/i);
    fireEvent.click(screen.getByTestId("approve-confirm-button"));
    await waitFor(() =>
      expect(screen.getByTestId("execution-status").textContent).toBe("Aprovada"),
    );
    expect(state.calls).toContain(
      `POST /api/v1/executions/${EXEC_ID}/result-attempts/1/approve`,
    );
  });

  // 27 — UI rejeita (observações obrigatórias)
  it("rejeita exigindo observações", async () => {
    const state = baseState();
    installFetch(state);
    render(<ExecutionDetail execution={makeExec()} onBack={() => {}} />);
    fireEvent.click(await screen.findByTestId("action-reject"));
    // Submeter sem observações → erro, sem POST.
    fireEvent.click(screen.getByTestId("reject-confirm-button"));
    expect((await screen.findByRole("alert")).textContent).toMatch(/observações/i);
    expect(
      state.calls.some((c) => c.includes("/reject")),
    ).toBe(false);
    // Com observações → rejeita.
    fireEvent.change(screen.getByTestId("observations-input"), {
      target: { value: "Não serve." },
    });
    fireEvent.click(screen.getByTestId("reject-confirm-button"));
    await waitFor(() =>
      expect(screen.getByTestId("execution-status").textContent).toBe("Rejeitada"),
    );
    expect(state.calls).toContain(
      `POST /api/v1/executions/${EXEC_ID}/result-attempts/1/reject`,
    );
  });

  // 28 — UI pede correcção → volta ao formulário de importação (prepared)
  it("pede correcção e regressa ao estado Preparada", async () => {
    const state = baseState();
    installFetch(state);
    render(<ExecutionDetail execution={makeExec()} onBack={() => {}} />);
    fireEvent.click(await screen.findByTestId("action-request-correction"));
    fireEvent.change(screen.getByTestId("observations-input"), {
      target: { value: "Corrige X." },
    });
    fireEvent.click(screen.getByTestId("request-correction-confirm-button"));
    await waitFor(() =>
      expect(screen.getByTestId("execution-status").textContent).toBe("Preparada"),
    );
    // Depois de correcção, o formulário de importação reaparece.
    expect(await screen.findByTestId("result-import-form")).toBeInTheDocument();
    expect(state.calls).toContain(
      `POST /api/v1/executions/${EXEC_ID}/result-attempts/1/request-correction`,
    );
  });

  // 29 — UI mostra histórico de tentativas e revisões
  it("mostra o histórico de tentativas e de revisões", async () => {
    const state = baseState({
      execution: makeExec({ version: 3 }),
      attempts: [
        { attempt_number: 1, source_tool: "T1", source_mode: "pasted",
          content: "c1", checksum: "aaa111222333" },
        { attempt_number: 2, source_tool: "T2", source_mode: "file",
          content: "c2", checksum: "bbb111222333" },
      ],
      reviews: [
        { id: "rev-1", attempt_number: 1, decision: "correction_requested",
          observations: "corrige", created_at: "2026-07-14T10:30:00Z" },
      ],
    });
    installFetch(state);
    render(<ExecutionDetail execution={makeExec({ version: 3 })} onBack={() => {}} />);
    const attemptHistory = await screen.findByTestId("attempt-history");
    expect(within(attemptHistory).getByRole("button", { name: "Tentativa 1" })).toBeInTheDocument();
    expect(within(attemptHistory).getByRole("button", { name: "Tentativa 2" })).toBeInTheDocument();
    const reviewHistory = screen.getByTestId("review-history");
    expect(reviewHistory.textContent).toMatch(/correcção pedida/i);
    // Abrir a tentativa histórica usa o conteúdo exacto.
    fireEvent.click(within(attemptHistory).getByRole("button", { name: "Tentativa 1" }));
    const view = await screen.findByTestId("result-attempt-view");
    expect(within(view).getByTestId("attempt-text").textContent).toContain("c1");
  });

  // 30 — UI não contém aplicação
  it("não oferece qualquer acção de aplicação", async () => {
    installFetch(baseState());
    render(<ExecutionDetail execution={makeExec()} onBack={() => {}} />);
    await screen.findByTestId("validation-panel");
    expect(screen.getByTestId("no-application-note")).toBeInTheDocument();
    for (const forbidden of [/aplicar/i, /criar vers/i, /concluir/i, /substituir/i]) {
      expect(screen.queryByRole("button", { name: forbidden })).toBeNull();
    }
  });

  // Extra — 409 recarrega o estado sem repetir
  it("um 409 recarrega o estado", async () => {
    const state = baseState();
    // Mock completo que devolve 409 no comando de aprovação (o resto normal).
    const fetchMock = vi.fn(async (rawUrl: string, init: RequestInit = {}) => {
      const method = init.method ?? "GET";
      const path = new URL(rawUrl, "http://local").pathname;
      state.calls.push(`${method} ${path}`);
      if (/\/approve$/.test(path) && method === "POST") {
        return json({ detail: "Versão desactualizada." }, 409);
      }
      if (path === `/api/v1/executions/${EXEC_ID}` && method === "GET") {
        return json(state.execution);
      }
      if (path.endsWith("/result-attempts") && method === "GET") {
        return json({ results: state.attempts.map((a) => attemptJson(a)) });
      }
      if (path.endsWith("/reviews") && method === "GET") {
        return json({ results: [] });
      }
      const dm = path.match(/\/result-attempts\/(\d+)$/);
      if (dm && method === "GET") {
        const a = state.attempts.find((x) => x.attempt_number === Number(dm[1]))!;
        return json(attemptJson(a, { content: a.content }));
      }
      return json({ detail: "nf" }, 404);
    });
    vi.stubGlobal("fetch", fetchMock);
    render(<ExecutionDetail execution={makeExec()} onBack={() => {}} />);
    await screen.findByTestId("validation-panel");
    fireEvent.click(await screen.findByTestId("action-approve"));
    fireEvent.click(await screen.findByTestId("approve-confirm-button"));
    expect(await screen.findByTestId("review-conflict")).toBeInTheDocument();
    // Recarregou o detalhe da execução (não repetiu o approve automaticamente).
    expect(
      state.calls.filter((c) => c.endsWith("/approve")).length,
    ).toBe(1);
  });
});
