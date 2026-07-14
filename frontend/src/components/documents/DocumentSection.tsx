import { useCallback, useEffect, useState } from "react";

import {
  DOCUMENT_TYPES,
  getDocument,
  listDocuments,
  type DocumentDetail,
  type DocumentSummary,
  type DocumentType,
} from "../../api/documents";
import { documentTypeLabel } from "./labels";
import { DocumentCreateForm } from "./DocumentCreateForm";
import { DocumentDetail as DocumentDetailView } from "./DocumentDetail";
import { DocumentEditor } from "./DocumentEditor";
import { DocumentHistory } from "./DocumentHistory";
import { DocumentList } from "./DocumentList";

interface Props {
  productId: string;
}

type View =
  | { kind: "list" }
  | { kind: "create" }
  | { kind: "detail"; document: DocumentDetail }
  | { kind: "edit"; document: DocumentDetail }
  | { kind: "history"; document: DocumentDetail };

type LoadState = "loading" | "ready" | "error";

interface PageInfo {
  count: number;
  page: number;
  page_size: number;
  num_pages: number;
}

// Área documental da ficha do produto. Container local e explícito (sem store
// global nem router), alternando entre lista, criação, detalhe, edição e
// histórico. A listagem filtra sempre pelo produto actual e nunca carrega
// conteúdo integral.
export function DocumentSection({ productId }: Props) {
  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [loadState, setLoadState] = useState<LoadState>("loading");
  const [view, setView] = useState<View>({ kind: "list" });
  const [typeFilter, setTypeFilter] = useState<DocumentType | "all">("all");
  const [page, setPage] = useState(1);
  const [pageInfo, setPageInfo] = useState<PageInfo>({
    count: 0,
    page: 1,
    page_size: 20,
    num_pages: 1,
  });

  const reload = useCallback(async () => {
    setLoadState((prev) => (prev === "ready" ? prev : "loading"));
    try {
      const response = await listDocuments({
        product: productId,
        document_type: typeFilter === "all" ? undefined : typeFilter,
        page,
      });
      setDocuments(response.results);
      setPageInfo({
        count: response.count ?? response.results.length,
        page: response.page ?? 1,
        page_size: response.page_size ?? response.results.length,
        num_pages: response.num_pages ?? 1,
      });
      setLoadState("ready");
    } catch {
      setLoadState("error");
    }
  }, [productId, typeFilter, page]);

  useEffect(() => {
    void reload();
  }, [reload]);

  const openDetail = useCallback(async (summary: DocumentSummary) => {
    // Só aqui se carrega o conteúdo integral (a lista tem apenas metadados).
    const detail = await getDocument(summary.id);
    setView({ kind: "detail", document: detail });
  }, []);

  function changeType(next: DocumentType | "all") {
    setTypeFilter(next);
    setPage(1);
  }

  return (
    <section aria-labelledby="documents-title">
      <h4 id="documents-title">Documentos</h4>

      {view.kind === "list" && (
        <>
          <button type="button" onClick={() => setView({ kind: "create" })}>
            Novo documento
          </button>

          <div role="group" aria-label="Filtros de documentos">
            <label>
              Tipo
              <select
                value={typeFilter}
                onChange={(e) =>
                  changeType(e.target.value as DocumentType | "all")
                }
              >
                <option value="all">Todos os tipos</option>
                {DOCUMENT_TYPES.map((type) => (
                  <option key={type} value={type}>
                    {documentTypeLabel(type)}
                  </option>
                ))}
              </select>
            </label>
          </div>

          {loadState === "loading" && (
            <p role="status">A carregar documentos…</p>
          )}
          {loadState === "error" && (
            <p role="alert">
              Não foi possível carregar os documentos.{" "}
              <button type="button" onClick={() => void reload()}>
                Tentar novamente
              </button>
            </p>
          )}
          {loadState === "ready" && (
            <>
              <DocumentList
                documents={documents}
                onSelect={(doc) => void openDetail(doc)}
              />
              <div role="group" aria-label="Paginação de documentos">
                <button
                  type="button"
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={pageInfo.page <= 1}
                >
                  Anterior
                </button>{" "}
                <span>
                  Página {pageInfo.page} de {pageInfo.num_pages}
                </span>{" "}
                <button
                  type="button"
                  onClick={() => setPage((p) => p + 1)}
                  disabled={pageInfo.page >= pageInfo.num_pages}
                >
                  Seguinte
                </button>
              </div>
            </>
          )}
        </>
      )}

      {view.kind === "create" && (
        <DocumentCreateForm
          productId={productId}
          onCreated={(document) => {
            void reload();
            setView({ kind: "detail", document });
          }}
          onCancel={() => setView({ kind: "list" })}
        />
      )}

      {view.kind === "detail" && (
        <DocumentDetailView
          document={view.document}
          onEdit={(document) => setView({ kind: "edit", document })}
          onHistory={(document) => setView({ kind: "history", document })}
          onBack={() => {
            void reload();
            setView({ kind: "list" });
          }}
          onChanged={(document) => {
            void reload();
            setView({ kind: "detail", document });
          }}
        />
      )}

      {view.kind === "edit" && (
        <DocumentEditor
          document={view.document}
          onSaved={(document) => {
            void reload();
            setView({ kind: "detail", document });
          }}
          onCancel={() => setView({ kind: "detail", document: view.document })}
        />
      )}

      {view.kind === "history" && (
        <DocumentHistory
          document={view.document}
          onRestored={(document) => {
            void reload();
            setView({ kind: "detail", document });
          }}
          onBack={() => setView({ kind: "detail", document: view.document })}
        />
      )}
    </section>
  );
}
