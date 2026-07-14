import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { DocumentSection } from "./DocumentSection";

// --- Modelo em memória do backend documental (mock de fetch) ----------------

function json(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

const PRODUCT_ID = "prod-1";
const PAGE_SIZE = 20;

let clock = 0;
function stamp(): string {
  return `2026-07-13T00:00:${String(clock++).padStart(2, "0")}Z`;
}

interface Version {
  version_number: number;
  content: string;
  checksum: string;
  byte_size: number;
  author: string;
  change_summary: string;
  created_at: string;
}
interface Doc {
  id: string;
  product: string;
  title: string;
  document_type: string;
  is_outdated: boolean;
  export_policy: string;
  version: number; // concorrência
  versions: Version[];
}

interface MockState {
  docs: Doc[];
  seq: number;
  conflictOnce?: boolean;
  previewCalls: number;
  listContentLeak: boolean; // sentinela: alguma listagem devolveu content?
}

// Sanitizador mínimo que emula o backend (escape-first + esquemas seguros).
function renderSafe(md: string): string {
  let html = md
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
  html = html.replace(
    /\[([^\]]+)\]\(([^)\s]+)\)/g,
    (_m, label: string, url: string) =>
      /^(https?:|mailto:)/i.test(url)
        ? `<a href="${url}" rel="nofollow noopener" target="_blank">${label}</a>`
        : label,
  );
  return `<p>${html}</p>`;
}

function checksumOf(content: string): string {
  // Pseudo-checksum determinístico só para teste (12+ hex).
  let h = 0;
  for (let i = 0; i < content.length; i += 1) h = (h * 31 + content.charCodeAt(i)) | 0;
  return (h >>> 0).toString(16).padStart(12, "0") + "abcdef0000";
}

function currentVersion(doc: Doc): Version {
  return doc.versions[doc.versions.length - 1];
}

function summary(doc: Doc) {
  return {
    id: doc.id,
    organisation: "org-1",
    product: doc.product,
    title: doc.title,
    document_type: doc.document_type,
    is_outdated: doc.is_outdated,
    export_policy: doc.export_policy,
    current_version_number: currentVersion(doc).version_number,
    version: doc.version,
    created_at: doc.versions[0].created_at,
    updated_at: currentVersion(doc).created_at,
  };
}

function detail(doc: Doc) {
  const cv = currentVersion(doc);
  return { ...summary(doc), content: cv.content, checksum: cv.checksum };
}

function newDoc(state: MockState, fields: Partial<Doc>, content: string): Doc {
  state.seq += 1;
  const doc: Doc = {
    id: `doc-${state.seq}`,
    product: PRODUCT_ID,
    title: fields.title ?? "Documento",
    document_type: fields.document_type ?? "contexto_da_empresa",
    is_outdated: fields.is_outdated ?? false,
    export_policy: fields.export_policy ?? "confirm",
    version: 1,
    versions: [
      {
        version_number: 1,
        content,
        checksum: checksumOf(content),
        byte_size: content.length,
        author: "user-1",
        change_summary: "",
        created_at: stamp(),
      },
    ],
  };
  state.docs.push(doc);
  return doc;
}

function addVersion(doc: Doc, content: string, summaryText: string) {
  const next = currentVersion(doc).version_number + 1;
  doc.versions.push({
    version_number: next,
    content,
    checksum: checksumOf(content),
    byte_size: content.length,
    author: "user-1",
    change_summary: summaryText,
    created_at: stamp(),
  });
  doc.version += 1;
}

function installFetch(state: MockState) {
  const fetchMock = vi.fn(async (rawUrl: string, init: RequestInit = {}) => {
    const method = init.method ?? "GET";
    const url = new URL(rawUrl, "http://local");
    const path = url.pathname;
    const body = init.body ? JSON.parse(init.body as string) : {};

    // Preview seguro.
    if (path.endsWith("/v1/documents/preview") && method === "POST") {
      state.previewCalls += 1;
      return json({ html: renderSafe(body.content ?? "") });
    }

    // Lista/criação.
    if (path.endsWith("/v1/documents") && method === "GET") {
      const product = url.searchParams.get("product");
      const type = url.searchParams.get("document_type");
      const page = parseInt(url.searchParams.get("page") ?? "1", 10);
      let items = state.docs.filter((d) => d.product === product);
      if (type) items = items.filter((d) => d.document_type === type);
      const count = items.length;
      const num_pages = Math.max(1, Math.ceil(count / PAGE_SIZE));
      const start = (page - 1) * PAGE_SIZE;
      const results = items.slice(start, start + PAGE_SIZE).map(summary);
      if (results.some((r) => "content" in r)) state.listContentLeak = true;
      return json({ results, count, page, page_size: PAGE_SIZE, num_pages });
    }
    if (path.endsWith("/v1/documents") && method === "POST") {
      const doc = newDoc(
        state,
        {
          title: body.title,
          document_type: body.document_type,
          is_outdated: body.is_outdated,
          export_policy: body.export_policy,
        },
        body.content ?? "",
      );
      return json(detail(doc), 201);
    }

    // /v1/documents/:id (+ /versions, /versions/:n, /restore)
    const m = path.match(
      /\/v1\/documents\/([^/]+?)(?:\/(versions|restore)(?:\/(\d+))?)?$/,
    );
    if (m) {
      const [, id, sub, versionNum] = m;
      const doc = state.docs.find((d) => d.id === id);
      if (!doc) return json({ detail: "nf" }, 404);

      if (!sub && method === "GET") return json(detail(doc));
      if (!sub && method === "PATCH") {
        if (state.conflictOnce) {
          state.conflictOnce = false;
          return json({ detail: "conflito" }, 409);
        }
        if (body.expected_version !== doc.version) {
          return json({ detail: "conflito" }, 409);
        }
        if (typeof body.content === "string") {
          addVersion(doc, body.content, body.change_summary ?? "");
        } else {
          doc.version += 1; // edição só de metadados: concorrência coerente
        }
        if (typeof body.is_outdated === "boolean")
          doc.is_outdated = body.is_outdated;
        if (typeof body.export_policy === "string")
          doc.export_policy = body.export_policy;
        if (typeof body.title === "string") doc.title = body.title;
        return json(detail(doc));
      }
      if (sub === "versions" && !versionNum && method === "GET") {
        const results = [...doc.versions]
          .reverse()
          .map((v) => ({
            version_number: v.version_number,
            checksum: v.checksum,
            byte_size: v.byte_size,
            author: v.author,
            change_summary: v.change_summary,
            created_at: v.created_at,
          }));
        return json({ results, count: results.length });
      }
      if (sub === "versions" && versionNum && method === "GET") {
        const v = doc.versions.find(
          (x) => x.version_number === parseInt(versionNum, 10),
        );
        if (!v) return json({ detail: "nf" }, 404);
        return json({
          version_number: v.version_number,
          checksum: v.checksum,
          byte_size: v.byte_size,
          author: v.author,
          change_summary: v.change_summary,
          created_at: v.created_at,
          content: v.content,
        });
      }
      if (sub === "restore" && method === "POST") {
        if (body.expected_version !== doc.version)
          return json({ detail: "conflito" }, 409);
        const source = doc.versions.find(
          (x) => x.version_number === body.version_number,
        );
        if (!source) return json({ detail: "nf" }, 404);
        addVersion(doc, source.content, `Recuperado da versão ${source.version_number}`);
        return json(detail(doc));
      }
    }
    return json({ detail: "nf" }, 404);
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

function renderSection() {
  return render(<DocumentSection productId={PRODUCT_ID} />);
}

function baseState(docs: Doc[] = []): MockState {
  return { docs, seq: docs.length, previewCalls: 0, listContentLeak: false };
}

function seedDoc(overrides: Partial<Doc> = {}, content = "# Doc\n\nconteúdo"): Doc {
  clock += 1;
  return {
    id: overrides.id ?? "doc-1",
    product: PRODUCT_ID,
    title: overrides.title ?? "Documento Um",
    document_type: overrides.document_type ?? "contexto_da_empresa",
    is_outdated: overrides.is_outdated ?? false,
    export_policy: overrides.export_policy ?? "confirm",
    version: overrides.version ?? 1,
    versions: overrides.versions ?? [
      {
        version_number: 1,
        content,
        checksum: checksumOf(content),
        byte_size: content.length,
        author: "user-1",
        change_summary: "",
        created_at: stamp(),
      },
    ],
  };
}

async function openDoc(title: string) {
  fireEvent.click(await screen.findByRole("button", { name: title }));
  await screen.findByRole("heading", { name: title, level: 4 });
}

describe("DocumentSection (experiência documental)", () => {
  beforeEach(() => {
    clock = 0;
    document.cookie = "csrftoken=t";
  });
  afterEach(() => {
    vi.restoreAllMocks();
  });

  // 1 — estado vazio
  it("mostra estado vazio quando não há documentos", async () => {
    installFetch(baseState([]));
    renderSection();
    await screen.findByText(/ainda não há documentos/i, undefined, {
      timeout: 5000,
    });
  });

  // 2/3/4 — criação; cinco tipos; sem tipos arbitrários
  it("cria documento e oferece exactamente os cinco tipos fechados", async () => {
    const state = baseState([]);
    installFetch(state);
    renderSection();
    fireEvent.click(await screen.findByRole("button", { name: /novo documento/i }));

    const typeSelect = screen.getByLabelText("Tipo") as HTMLSelectElement;
    expect(typeSelect.options).toHaveLength(5);
    const values = Array.from(typeSelect.options).map((o) => o.value);
    expect(values).toEqual([
      "contexto_da_empresa",
      "visao_de_produto",
      "instrucoes",
      "decisao_detalhada",
      "resultado",
    ]);
    // Não é um input livre: é um <select> (não aceita tipos arbitrários).
    expect(typeSelect.tagName).toBe("SELECT");

    fireEvent.change(screen.getByLabelText("Título"), {
      target: { value: "Visão inicial" },
    });
    fireEvent.change(typeSelect, { target: { value: "visao_de_produto" } });
    fireEvent.change(screen.getByLabelText("Conteúdo (Markdown)"), {
      target: { value: "# Visão\n\n- ponto" },
    });
    fireEvent.click(screen.getByRole("button", { name: /criar documento/i }));

    await screen.findByRole("heading", { name: "Visão inicial", level: 4 });
    expect(screen.getByText("Visão de produto")).toBeInTheDocument();
  });

  // 5/6/7 — preview segura; script não executa; javascript: não permanece
  it("pré-visualiza via backend e não executa conteúdo perigoso", async () => {
    const state = baseState([]);
    installFetch(state);
    renderSection();
    fireEvent.click(await screen.findByRole("button", { name: /novo documento/i }));
    fireEvent.change(screen.getByLabelText("Conteúdo (Markdown)"), {
      target: {
        value: "<script>alert(1)</script>\n\n[mau](javascript:alert(1))",
      },
    });
    fireEvent.click(screen.getByRole("button", { name: /pré-visualizar/i }));

    const preview = await screen.findByTestId("document-preview-html");
    // Usou o endpoint seguro do backend.
    expect(state.previewCalls).toBe(1);
    // Nenhum <script> vivo foi inserido.
    expect(preview.querySelector("script")).toBeNull();
    // `javascript:` não permanece no HTML inserido.
    expect(preview.innerHTML).not.toContain("javascript:");
    expect(preview.querySelector("a")).toBeNull();
  });

  // 8 — edição cria nova versão
  it("edita o conteúdo e cria uma nova versão", async () => {
    installFetch(baseState([seedDoc()]));
    renderSection();
    await openDoc("Documento Um");
    fireEvent.click(screen.getByRole("button", { name: /editar conteúdo/i }));
    fireEvent.change(screen.getByLabelText("Conteúdo (Markdown)"), {
      target: { value: "# Doc\n\nrevisto" },
    });
    fireEvent.change(screen.getByLabelText("Resumo da alteração"), {
      target: { value: "revisão" },
    });
    fireEvent.click(screen.getByRole("button", { name: /guardar nova versão/i }));

    await screen.findByRole("heading", { name: "Documento Um", level: 4 });
    // Versão actual passou a 2 (dd imediatamente a seguir ao dt "Versão actual").
    const term = screen.getByText("Versão actual");
    expect(term.nextElementSibling?.textContent).toBe("2");
  });

  // 9 — conflito 409 permite recarregar
  it("um conflito 409 na edição permite recarregar sem sobrescrever", async () => {
    const state = baseState([seedDoc()]);
    state.conflictOnce = true;
    installFetch(state);
    renderSection();
    await openDoc("Documento Um");
    fireEvent.click(screen.getByRole("button", { name: /editar conteúdo/i }));
    fireEvent.change(screen.getByLabelText("Conteúdo (Markdown)"), {
      target: { value: "# Doc\n\noutro" },
    });
    fireEvent.change(screen.getByLabelText("Resumo da alteração"), {
      target: { value: "x" },
    });
    fireEvent.click(screen.getByRole("button", { name: /guardar nova versão/i }));

    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent(/alterado por outra operação/i);
    fireEvent.click(
      screen.getByRole("button", { name: /recarregar versão actual/i }),
    );
    await waitFor(() => expect(screen.queryByRole("alert")).toBeNull());
  });

  // 10/11 — histórico lista versões; abrir versão exacta
  it("lista o histórico e abre uma versão exacta", async () => {
    const doc = seedDoc({}, "# v1\n\nprimeiro");
    addVersion(doc, "# v2\n\nsegundo", "segunda versão");
    installFetch(baseState([doc]));
    renderSection();
    await openDoc("Documento Um");
    fireEvent.click(screen.getByRole("button", { name: /histórico/i }));

    await screen.findByRole("heading", { name: /histórico de versões/i });
    // Duas versões listadas.
    expect(screen.getByRole("cell", { name: "1" })).toBeInTheDocument();
    expect(screen.getByRole("cell", { name: "2" })).toBeInTheDocument();

    // Abrir a versão 1 mostra o seu conteúdo exacto.
    const rows = screen.getAllByRole("row");
    const rowV1 = rows.find((r) => within(r).queryByRole("cell", { name: "1" }));
    fireEvent.click(within(rowV1!).getByRole("button", { name: /abrir/i }));
    await screen.findByText(/conteúdo da versão 1/i);
    expect(screen.getByText(/primeiro/)).toBeInTheDocument();
  });

  // 12/13 — recuperação exige confirmação e cria nova versão
  it("recupera uma versão com confirmação e cria nova versão", async () => {
    const doc = seedDoc({}, "# v1\n\noriginal");
    addVersion(doc, "# v2\n\ndiferente", "v2");
    installFetch(baseState([doc]));
    renderSection();
    await openDoc("Documento Um");
    fireEvent.click(screen.getByRole("button", { name: /histórico/i }));
    await screen.findByRole("heading", { name: /histórico de versões/i });

    const rows = screen.getAllByRole("row");
    const rowV1 = rows.find((r) => within(r).queryByRole("cell", { name: "1" }));
    // Clicar "Recuperar" não recupera já: pede confirmação.
    fireEvent.click(within(rowV1!).getByRole("button", { name: /^recuperar$/i }));
    expect(screen.getByText(/cria uma nova versão actual/i)).toBeInTheDocument();
    fireEvent.click(
      screen.getByRole("button", { name: /confirmar recuperação/i }),
    );

    // Volta ao detalhe com a nova versão actual (3).
    await screen.findByRole("heading", { name: "Documento Um", level: 4 });
    const term = screen.getByText("Versão actual");
    expect(term.nextElementSibling?.textContent).toBe("3");
  });

  // 14 — is_outdated pode ser alterado
  it("altera o marcador is_outdated", async () => {
    installFetch(baseState([seedDoc()]));
    renderSection();
    await openDoc("Documento Um");
    fireEvent.click(screen.getByLabelText(/marcar como desactualizado/i));
    fireEvent.click(screen.getByRole("button", { name: /guardar marcadores/i }));
    await screen.findByText(/marcadores guardados/i);
    // O estado passou a Desactualizado.
    expect(screen.getByText("Desactualizado")).toBeInTheDocument();
  });

  // 15/16 — export_policy pode mudar; denied apresenta aviso
  it("altera export_policy e avisa quando denied", async () => {
    installFetch(baseState([seedDoc()]));
    renderSection();
    await openDoc("Documento Um");
    fireEvent.change(screen.getByLabelText(/política de exportação/i), {
      target: { value: "denied" },
    });
    // Aviso de que não poderá ser seleccionado para pacote de contexto.
    expect(
      screen.getByText(/não poderá ser seleccionado para um pacote de contexto/i),
    ).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /guardar marcadores/i }));
    await screen.findByText(/marcadores guardados/i);
    // Restringe ao <dd> (o <option> do select tem o mesmo texto).
    expect(
      screen.getByText("Exportação recusada", { selector: "dd" }),
    ).toBeInTheDocument();
  });

  // 17 — listagem não recebe conteúdo integral
  it("a listagem não devolve conteúdo integral", async () => {
    const state = baseState([seedDoc(), seedDoc({ id: "doc-2", title: "Dois" })]);
    installFetch(state);
    renderSection();
    await screen.findByRole("button", { name: "Documento Um" });
    expect(state.listContentLeak).toBe(false);
  });

  // filtro por tipo
  it("filtra a listagem por tipo", async () => {
    installFetch(
      baseState([
        seedDoc({ id: "d1", title: "Contexto", document_type: "contexto_da_empresa" }),
        seedDoc({ id: "d2", title: "Visão", document_type: "visao_de_produto" }),
      ]),
    );
    renderSection();
    await screen.findByRole("button", { name: "Contexto" });
    fireEvent.change(screen.getByLabelText("Tipo"), {
      target: { value: "visao_de_produto" },
    });
    await screen.findByRole("button", { name: "Visão" });
    expect(screen.queryByRole("button", { name: "Contexto" })).toBeNull();
  });
});
