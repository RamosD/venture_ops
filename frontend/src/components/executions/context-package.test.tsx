import { fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import type { ContextDocument, ExecutionDetail as Execution } from "../../api/executions";
import { ContextPackagePanel } from "./ContextPackagePanel";
import { ExecutionDetail } from "./ExecutionDetail";

const EXEC_ID = "exec-1";

const SEVEN_SECTIONS =
  "# PACOTE DE CONTEXTO\n" +
  "## SECÇÃO 1 — OBJECTIVO\nobj\n" +
  "## SECÇÃO 2 — FUNÇÃO (INSTRUÇÕES)\nfn\n" +
  "## SECÇÃO 3 — INSTRUÇÕES DO PEDIDO\nreq\n" +
  "## SECÇÃO 4 — PRODUTO\nprod\n" +
  "## SECÇÃO 5 — RESTRIÇÕES\nrestr\n" +
  "## SECÇÃO 6 — FORMATO ESPERADO\nfmt\n" +
  "## SECÇÃO 7 — DOCUMENTOS (DADOS)\n<script>alert(1)</script>\n";

function ctxDoc(over: Partial<ContextDocument> = {}): ContextDocument {
  return {
    document: "doc-1",
    document_version: "ver-1",
    order: 1,
    purpose: "",
    title: "Documento Empresa",
    document_type: "contexto_da_empresa",
    version_number: 1,
    checksum: "abcdef0123456789",
    export_policy: "allowed",
    is_outdated: false,
    ...over,
  };
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
      id: "fn-1",
      name: "Analista",
      actor_type: "human",
      purpose: "p",
      responsibilities: "r",
      constraints: "",
      requires_approval: false,
    },
    product_snapshot: { id: "prod-1", name: "Produto A", purpose: "p", status: "active" },
    instruction_version: null,
    context_documents: [ctxDoc()],
    ...over,
  };
}

function manifest() {
  return {
    execution_id: EXEC_ID,
    format: "single_markdown",
    sections: [1, 2, 3, 4, 5, 6, 7].map(String),
    instruction_version: null,
    documents: [
      {
        order: 1,
        document: "doc-1",
        document_version: "ver-1",
        title: "Documento Empresa",
        document_type: "contexto_da_empresa",
        version_number: 1,
        checksum: "abcdef0123456789",
        is_outdated: false,
        export_policy: "allowed",
      },
    ],
  };
}

function json(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

interface Handlers {
  preview?: (body: any) => Response;
  download?: (body: any) => Response;
}

function installFetch(handlers: Handlers) {
  const calls: { url: string; method: string; body: any }[] = [];
  const fetchMock = vi.fn(async (rawUrl: string, init: RequestInit = {}) => {
    const method = init.method ?? "GET";
    const body = init.body ? JSON.parse(init.body as string) : {};
    calls.push({ url: rawUrl, method, body });
    if (rawUrl.match(/\/result-attempts$/) && method === "GET") {
      return json({ results: [] });
    }
    if (rawUrl.includes("/context-package/preview")) {
      return handlers.preview
        ? handlers.preview(body)
        : json({ format: "single_markdown", checksum: "c", warnings: [], manifest: manifest(), content: SEVEN_SECTIONS });
    }
    if (rawUrl.includes("/context-package/download")) {
      if (handlers.download) return handlers.download(body);
      return new Response(new Blob(["bytes"]), {
        status: 200,
        headers: {
          "Content-Disposition": 'attachment; filename="pacote-contexto-exec-1.md"',
          "X-Package-Checksum": "deadbeef",
        },
      });
    }
    return json({ detail: "nf" }, 404);
  });
  vi.stubGlobal("fetch", fetchMock);
  return { fetchMock, calls };
}

function okPreview(over: any = {}) {
  return json({
    format: "single_markdown",
    checksum: "checksum-abc",
    warnings: [],
    manifest: manifest(),
    content: SEVEN_SECTIONS,
    ...over,
  });
}

describe("ContextPackagePanel (pacote de contexto)", () => {
  beforeEach(() => {
    document.cookie = "csrftoken=t";
    // jsdom não implementa object URLs nem clipboard por defeito.
    (URL as any).createObjectURL = vi.fn(() => "blob:mock");
    (URL as any).revokeObjectURL = vi.fn();
    Object.assign(navigator, {
      clipboard: { writeText: vi.fn().mockResolvedValue(undefined) },
    });
  });
  afterEach(() => {
    vi.restoreAllMocks();
  });

  // 1 — painel só aparece em prepared / 22 — estado permanece prepared
  it("mostra o painel só em prepared", () => {
    installFetch({});
    const { rerender } = render(
      <ExecutionDetail execution={makeExec()} onBack={() => {}} />,
    );
    expect(screen.getByTestId("context-package-panel")).toBeInTheDocument();
    rerender(
      <ExecutionDetail
        execution={makeExec({ status: "approved" })}
        onBack={() => {}}
      />,
    );
    expect(screen.queryByTestId("context-package-panel")).toBeNull();
    expect(screen.getByTestId("package-unavailable")).toBeInTheDocument();
  });

  // 3 — allowed não exige confirmação
  it("allowed não exige confirmação", () => {
    installFetch({});
    render(<ContextPackagePanel execution={makeExec()} />);
    expect(screen.queryByTestId("confirm-checkbox")).toBeNull();
  });

  // 4 — confirm exige checkbox
  it("confirm exige checkbox", () => {
    installFetch({});
    render(
      <ContextPackagePanel
        execution={makeExec({ context_documents: [ctxDoc({ export_policy: "confirm" })] })}
      />,
    );
    expect(screen.getByTestId("confirm-checkbox")).toBeInTheDocument();
  });

  // 5 — denied bloqueia
  it("denied bloqueia sem contorno", () => {
    installFetch({});
    render(
      <ContextPackagePanel
        execution={makeExec({ context_documents: [ctxDoc({ export_policy: "denied" })] })}
      />,
    );
    expect(screen.getByTestId("denied-blocked")).toBeInTheDocument();
    expect(screen.queryByTestId("confirm-checkbox")).toBeNull();
  });

  // 6 — alteração para denied apresentada após 409
  it("apresenta denied superveniente após 409", async () => {
    installFetch({
      preview: () =>
        json(
          {
            detail: "bloqueado",
            reason: "denied",
            denied_document_ids: ["doc-1"],
            confirmation_required_document_ids: [],
          },
          409,
        ),
    });
    render(<ContextPackagePanel execution={makeExec()} />); // doc allowed no detalhe
    expect(screen.queryByTestId("denied-blocked")).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: /gerar pré-visualização/i }));
    await screen.findByTestId("blocked-reason");
    expect(screen.getByTestId("denied-blocked")).toBeInTheDocument();
  });

  // 7 — is_outdated mostra aviso
  it("mostra aviso is_outdated", () => {
    installFetch({});
    render(
      <ContextPackagePanel
        execution={makeExec({ context_documents: [ctxDoc({ is_outdated: true })] })}
      />,
    );
    expect(screen.getByTestId("outdated-warning")).toBeInTheDocument();
  });

  // 8 — instruction_document aparece na política
  it("apresenta o documento de instruções na análise após 409", async () => {
    installFetch({
      preview: () =>
        json(
          {
            detail: "confirmar",
            reason: "confirmation_required",
            denied_document_ids: [],
            confirmation_required_document_ids: ["instr-doc"],
          },
          409,
        ),
    });
    render(
      <ContextPackagePanel
        execution={makeExec({ instruction_version: "instr-ver" })}
      />,
    );
    fireEvent.click(screen.getByRole("button", { name: /gerar pré-visualização/i }));
    const items = await screen.findAllByTestId("instruction-policy");
    expect(items.some((n) => /instruções da função/i.test(n.textContent ?? ""))).toBe(
      true,
    );
  });

  // 9 — manual_external mostra aviso externo
  it("manual_external mostra aviso externo", () => {
    installFetch({});
    render(
      <ContextPackagePanel execution={makeExec({ execution_mode: "manual_external" })} />,
    );
    expect(screen.getByTestId("mode-warning-external")).toBeInTheDocument();
  });

  // 10 — manual_local mostra aviso local
  it("manual_local mostra aviso local", () => {
    installFetch({});
    render(<ContextPackagePanel execution={makeExec({ execution_mode: "manual_local" })} />);
    expect(screen.getByTestId("mode-warning-local")).toBeInTheDocument();
  });

  // 2 + 11 + 17 — sete secções, texto não executável, checksum e manifesto
  it("mostra as sete secções como texto não executável, com checksum e manifesto", async () => {
    installFetch({ preview: () => okPreview() });
    render(<ContextPackagePanel execution={makeExec()} />);
    fireEvent.click(screen.getByRole("button", { name: /gerar pré-visualização/i }));
    const content = await screen.findByTestId("package-content");
    expect(content.tagName).toBe("PRE"); // texto, não HTML executável
    expect(content.textContent).toContain("SECÇÃO 1");
    expect(content.textContent).toContain("SECÇÃO 7");
    expect(content.textContent).toContain("<script>alert(1)</script>"); // literal
    expect(document.querySelector("script")).toBeNull(); // nunca executado/injectado
    expect(screen.getByTestId("package-checksum").textContent).toBe("checksum-abc");
    expect(screen.getByTestId("package-manifest")).toBeInTheDocument();
  });

  // 12 — copy usa Clipboard API
  it("copia via Clipboard API", async () => {
    installFetch({ preview: () => okPreview() });
    render(<ContextPackagePanel execution={makeExec()} />);
    fireEvent.click(screen.getByRole("button", { name: /gerar pré-visualização/i }));
    await screen.findByTestId("package-content");
    fireEvent.click(screen.getByRole("button", { name: /copiar markdown/i }));
    await screen.findByText(/copiado para a área de transferência/i);
    expect(navigator.clipboard.writeText).toHaveBeenCalledWith(SEVEN_SECTIONS);
  });

  // 13 — falha de clipboard é tratada
  it("trata falha do clipboard", async () => {
    (navigator.clipboard.writeText as any).mockRejectedValueOnce(new Error("no"));
    installFetch({ preview: () => okPreview() });
    render(<ContextPackagePanel execution={makeExec()} />);
    fireEvent.click(screen.getByRole("button", { name: /gerar pré-visualização/i }));
    await screen.findByTestId("package-content");
    fireEvent.click(screen.getByRole("button", { name: /copiar markdown/i }));
    await screen.findByRole("alert");
    expect(screen.queryByText(/copiado para/i)).toBeNull();
  });

  // 14 + 16 — download Markdown e revogação de URL temporária
  it("descarrega .md e revoga a URL temporária", async () => {
    installFetch({ preview: () => okPreview() });
    render(<ContextPackagePanel execution={makeExec()} />);
    fireEvent.click(screen.getByRole("button", { name: /gerar pré-visualização/i }));
    await screen.findByTestId("package-content");
    fireEvent.click(screen.getByRole("button", { name: /descarregar \.md/i }));
    await screen.findByText(/descarga iniciada/i);
    expect(URL.createObjectURL).toHaveBeenCalled();
    expect(URL.revokeObjectURL).toHaveBeenCalledWith("blob:mock");
  });

  // 15 — download ZIP
  it("descarrega .zip em separate_files", async () => {
    installFetch({
      preview: () =>
        json({
          format: "separate_files",
          checksum: "zipsum",
          warnings: [],
          manifest: manifest(),
          files: ["manifest.json", "01_objectivo.md"],
        }),
      download: () =>
        new Response(new Blob(["PK"]), {
          status: 200,
          headers: {
            "Content-Disposition": 'attachment; filename="pacote-contexto-exec-1.zip"',
            "X-Package-Checksum": "zipsum",
          },
        }),
    });
    render(<ContextPackagePanel execution={makeExec()} />);
    fireEvent.change(screen.getByLabelText("Formato"), {
      target: { value: "separate_files" },
    });
    fireEvent.click(screen.getByRole("button", { name: /gerar pré-visualização/i }));
    await screen.findByTestId("package-files");
    fireEvent.click(screen.getByRole("button", { name: /descarregar \.zip/i }));
    await screen.findByText(/descarga iniciada/i);
    expect(URL.createObjectURL).toHaveBeenCalled();
  });

  // 18 — confirmação não é persistida
  it("não persiste confirmações em localStorage", () => {
    const spy = vi.spyOn(Storage.prototype, "setItem");
    installFetch({});
    render(
      <ContextPackagePanel
        execution={makeExec({ context_documents: [ctxDoc({ export_policy: "confirm" })] })}
      />,
    );
    fireEvent.click(within(screen.getByTestId("confirm-checkbox")).getByRole("checkbox"));
    expect(spy).not.toHaveBeenCalled();
    expect(window.localStorage.length).toBe(0);
  });

  // 19 — nova geração reavalia políticas (confirm → confirmado → inclui)
  it("nova geração reavalia após confirmação", async () => {
    let confirmedSeen = false;
    installFetch({
      preview: (body) => {
        const ids: string[] = body.confirmed_document_ids ?? [];
        if (ids.includes("doc-1")) {
          confirmedSeen = true;
          return okPreview();
        }
        return json(
          {
            detail: "confirmar",
            reason: "confirmation_required",
            denied_document_ids: [],
            confirmation_required_document_ids: ["doc-1"],
          },
          409,
        );
      },
    });
    render(
      <ContextPackagePanel
        execution={makeExec({ context_documents: [ctxDoc({ export_policy: "confirm" })] })}
      />,
    );
    // 1.ª geração sem confirmar → bloqueada.
    fireEvent.click(screen.getByRole("button", { name: /gerar pré-visualização/i }));
    await screen.findByTestId("blocked-reason");
    // Confirma e regenera → inclui.
    fireEvent.click(within(screen.getByTestId("confirm-checkbox")).getByRole("checkbox"));
    fireEvent.click(screen.getByRole("button", { name: /gerar pré-visualização/i }));
    await screen.findByTestId("package-content");
    expect(confirmedSeen).toBe(true);
  });

  // 20 + 21 + 22 — nenhuma chamada a IA / resultado / mudança de estado
  it("só chama endpoints do pacote (sem IA, resultado ou transições)", async () => {
    const { calls } = installFetch({ preview: () => okPreview() });
    render(<ContextPackagePanel execution={makeExec()} />);
    fireEvent.click(screen.getByRole("button", { name: /gerar pré-visualização/i }));
    await screen.findByTestId("package-content");
    fireEvent.click(screen.getByRole("button", { name: /descarregar \.md/i }));
    await screen.findByText(/descarga iniciada/i);
    for (const c of calls) {
      expect(c.url).toMatch(/\/context-package\/(preview|download)/);
      expect(c.method).toBe("POST");
    }
    // Nenhuma chamada a resultados/aprovação/transições/IA.
    expect(calls.some((c) => /result|approve|transition|ai|generate/i.test(c.url))).toBe(
      false,
    );
  });

  // Confirmar todos exige lista + confirmação adicional
  it("Confirmar todos mostra a lista e exige confirmação adicional", () => {
    installFetch({});
    render(
      <ContextPackagePanel
        execution={makeExec({ context_documents: [ctxDoc({ export_policy: "confirm" })] })}
      />,
    );
    fireEvent.click(screen.getByRole("button", { name: /confirmar todos…/i }));
    // Mostra a contagem e um botão de confirmação adicional.
    expect(
      screen.getByRole("button", { name: /confirmar inclusão de todos/i }),
    ).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /confirmar inclusão de todos/i }));
    const checkbox = within(screen.getByTestId("confirm-checkbox")).getByRole(
      "checkbox",
    ) as HTMLInputElement;
    expect(checkbox.checked).toBe(true);
  });
});
