import { useState, type FormEvent } from "react";

import { ApiError } from "../../api/client";
import {
  DOCUMENT_TYPES,
  EXPORT_POLICIES,
  createDocument,
  type DocumentCreateInput,
  type DocumentDetail,
  type DocumentType,
  type ExportPolicy,
} from "../../api/documents";
import { DocumentPreview } from "./DocumentPreview";
import { documentTypeLabel, exportPolicyLabel } from "./labels";

interface Props {
  productId: string;
  onCreated: (document: DocumentDetail) => void;
  onCancel: () => void;
}

// Criação de documento associado ao produto actual. O tipo é escolhido de entre
// os cinco tipos fechados (labels PT); não há tipos arbitrários nem escolha de
// empresa (derivada no servidor). A pré-visualização usa o endpoint seguro.
export function DocumentCreateForm({ productId, onCreated, onCancel }: Props) {
  const [title, setTitle] = useState("");
  const [documentType, setDocumentType] = useState<DocumentType>(
    "contexto_da_empresa",
  );
  const [content, setContent] = useState("");
  const [isOutdated, setIsOutdated] = useState(false);
  const [exportPolicy, setExportPolicy] = useState<ExportPolicy>("confirm");
  const [showPreview, setShowPreview] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (busy) return; // evita submissão duplicada
    setBusy(true);
    setError(null);

    const payload: DocumentCreateInput = {
      title: title.trim(),
      document_type: documentType,
      content,
      product: productId,
    };
    if (isOutdated) payload.is_outdated = true;
    if (exportPolicy !== "confirm") payload.export_policy = exportPolicy;

    try {
      const created = await createDocument(payload);
      onCreated(created);
    } catch (e: unknown) {
      if (e instanceof ApiError && e.status === 413) {
        setError("O conteúdo excede o limite permitido.");
      } else if (e instanceof ApiError && e.status === 400) {
        setError("Verifique o título, o tipo e o conteúdo.");
      } else {
        setError("Não foi possível criar o documento.");
      }
      setBusy(false);
    }
  }

  return (
    <section aria-labelledby="document-create-title">
      <h4 id="document-create-title">Novo documento</h4>
      {error && <p role="alert">{error}</p>}
      <form onSubmit={handleSubmit}>
        <p>
          <label>
            Título
            <input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
          </label>
        </p>
        <p>
          <label>
            Tipo
            <select
              value={documentType}
              onChange={(e) => setDocumentType(e.target.value as DocumentType)}
            >
              {DOCUMENT_TYPES.map((type) => (
                <option key={type} value={type}>
                  {documentTypeLabel(type)}
                </option>
              ))}
            </select>
          </label>
        </p>
        <p>
          <label>
            Conteúdo (Markdown)
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              rows={10}
            />
          </label>
        </p>

        <fieldset>
          <legend>Marcadores</legend>
          <label>
            <input
              type="checkbox"
              checked={isOutdated}
              onChange={(e) => setIsOutdated(e.target.checked)}
            />
            Marcar como desactualizado
          </label>
          <p>
            <label>
              Política de exportação
              <select
                value={exportPolicy}
                onChange={(e) =>
                  setExportPolicy(e.target.value as ExportPolicy)
                }
              >
                {EXPORT_POLICIES.map((policy) => (
                  <option key={policy} value={policy}>
                    {exportPolicyLabel(policy)}
                  </option>
                ))}
              </select>
            </label>
          </p>
          {exportPolicy === "denied" && (
            <p role="status">
              Com exportação recusada, este documento não poderá ser
              seleccionado para um pacote de contexto. Continua visível e
              utilizável na aplicação.
            </p>
          )}
        </fieldset>

        <p>
          <button
            type="button"
            onClick={() => setShowPreview((v) => !v)}
            disabled={busy}
          >
            {showPreview ? "Ocultar pré-visualização" : "Pré-visualizar"}
          </button>
        </p>
        {showPreview && <DocumentPreview content={content} />}

        <p>
          <button type="submit" disabled={busy}>
            {busy ? "A criar…" : "Criar documento"}
          </button>{" "}
          <button type="button" onClick={onCancel} disabled={busy}>
            Cancelar
          </button>
        </p>
      </form>
    </section>
  );
}
