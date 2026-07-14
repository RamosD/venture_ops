import { useState, type FormEvent } from "react";

import { ApiError } from "../../api/client";
import {
  getDocument,
  updateDocument,
  type DocumentDetail,
  type DocumentUpdateInput,
} from "../../api/documents";
import { DocumentPreview } from "./DocumentPreview";

interface Props {
  document: DocumentDetail;
  onSaved: (document: DocumentDetail) => void;
  onCancel: () => void;
}

// Editor simples de conteúdo (textarea; sem rich-text). Apresenta a versão base,
// envia `expected_version` e exige um resumo de alteração curto quando o conteúdo
// muda. Um 409 é tratado como conflito: nunca sobrescreve silenciosamente o
// servidor — informa e oferece recarregar a versão actual. A pré-visualização
// usa o endpoint seguro do backend.
export function DocumentEditor({ document, onSaved, onCancel }: Props) {
  const [current, setCurrent] = useState<DocumentDetail>(document);
  const [content, setContent] = useState(document.content);
  const [changeSummary, setChangeSummary] = useState("");
  const [showPreview, setShowPreview] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conflict, setConflict] = useState(false);
  const [busy, setBusy] = useState(false);

  const contentChanged = content !== current.content;
  const summaryMissing = contentChanged && changeSummary.trim() === "";

  async function handleReload() {
    if (busy) return;
    setBusy(true);
    setError(null);
    try {
      const fresh = await getDocument(current.id);
      setCurrent(fresh);
      setContent(fresh.content);
      setConflict(false);
    } catch {
      setError("Não foi possível recarregar o documento.");
    } finally {
      setBusy(false);
    }
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (busy) return; // evita submissão duplicada
    if (!contentChanged) {
      setError("Não há alterações de conteúdo para guardar.");
      return;
    }
    if (summaryMissing) {
      setError("Descreva brevemente a alteração.");
      return;
    }
    setBusy(true);
    setError(null);
    setConflict(false);

    const payload: DocumentUpdateInput = {
      expected_version: current.version,
      content,
      change_summary: changeSummary.trim(),
    };

    try {
      const updated = await updateDocument(current.id, payload);
      onSaved(updated);
    } catch (e: unknown) {
      if (e instanceof ApiError && e.status === 409) {
        setConflict(true);
      } else if (e instanceof ApiError && e.status === 413) {
        setError("O conteúdo excede o limite permitido.");
      } else {
        setError("Não foi possível guardar as alterações.");
      }
      setBusy(false);
    }
  }

  return (
    <section aria-labelledby="document-edit-title">
      <h4 id="document-edit-title">Editar documento</h4>
      <p>
        <small>
          A editar sobre a versão de conteúdo {current.current_version_number}{" "}
          (controlo técnico {current.version}).
        </small>
      </p>
      {conflict && (
        <div role="alert">
          <p>
            O documento foi alterado por outra operação. As suas alterações não
            foram sobrescritas.
          </p>
          <button type="button" onClick={handleReload} disabled={busy}>
            Recarregar versão actual
          </button>
        </div>
      )}
      {error && <p role="alert">{error}</p>}
      <form onSubmit={handleSubmit}>
        <p>
          <label>
            Conteúdo (Markdown)
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              rows={12}
            />
          </label>
        </p>
        <p>
          <label>
            Resumo da alteração
            <input
              value={changeSummary}
              onChange={(e) => setChangeSummary(e.target.value)}
              maxLength={255}
              required={contentChanged}
              placeholder="Ex.: revisão da secção de objectivos"
            />
          </label>
        </p>

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
          <button type="submit" disabled={busy || summaryMissing}>
            {busy ? "A guardar…" : "Guardar nova versão"}
          </button>{" "}
          <button type="button" onClick={onCancel} disabled={busy}>
            Cancelar
          </button>
        </p>
      </form>
    </section>
  );
}
