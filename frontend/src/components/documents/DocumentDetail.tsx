import { useState } from "react";

import { ApiError } from "../../api/client";
import {
  EXPORT_POLICIES,
  getDocument,
  updateDocument,
  type DocumentDetail as DocumentDetailData,
  type ExportPolicy,
} from "../../api/documents";
import { documentTypeLabel, exportPolicyLabel } from "./labels";

interface Props {
  document: DocumentDetailData;
  onEdit: (document: DocumentDetailData) => void;
  onHistory: (document: DocumentDetailData) => void;
  onBack: () => void;
  onChanged: (document: DocumentDetailData) => void;
}

// Detalhe do documento: metadados + conteúdo da versão actual (texto simples; a
// pré-visualização segura está no editor/criação). Permite editar os marcadores
// (`is_outdated`, `export_policy`) com concorrência coerente (envia
// `expected_version`; 409 → aviso e recarregar). O conteúdo edita-se no editor.
export function DocumentDetail({
  document: initial,
  onEdit,
  onHistory,
  onBack,
  onChanged,
}: Props) {
  const [document, setDocument] = useState<DocumentDetailData>(initial);
  const [isOutdated, setIsOutdated] = useState(initial.is_outdated);
  const [exportPolicy, setExportPolicy] = useState<ExportPolicy>(
    initial.export_policy,
  );
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conflict, setConflict] = useState(false);
  const [saved, setSaved] = useState(false);

  const markersDirty =
    isOutdated !== document.is_outdated ||
    exportPolicy !== document.export_policy;

  function resetTo(next: DocumentDetailData) {
    setDocument(next);
    setIsOutdated(next.is_outdated);
    setExportPolicy(next.export_policy);
  }

  async function saveMarkers() {
    if (busy || !markersDirty) return;
    setBusy(true);
    setError(null);
    setConflict(false);
    setSaved(false);
    try {
      const updated = await updateDocument(document.id, {
        expected_version: document.version,
        is_outdated: isOutdated,
        export_policy: exportPolicy,
      });
      resetTo(updated);
      setSaved(true);
      onChanged(updated);
    } catch (e: unknown) {
      if (e instanceof ApiError && e.status === 409) {
        setConflict(true);
      } else {
        setError("Não foi possível guardar os marcadores.");
      }
    } finally {
      setBusy(false);
    }
  }

  async function handleReload() {
    if (busy) return;
    setBusy(true);
    setError(null);
    try {
      const fresh = await getDocument(document.id);
      resetTo(fresh);
      setConflict(false);
      onChanged(fresh);
    } catch {
      setError("Não foi possível recarregar o documento.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section aria-labelledby="document-detail-title">
      <h4 id="document-detail-title">{document.title}</h4>

      {conflict && (
        <div role="alert">
          <p>
            O documento foi alterado por outra operação. Os seus dados não foram
            sobrescritos.
          </p>
          <button type="button" onClick={handleReload} disabled={busy}>
            Recarregar dados
          </button>
        </div>
      )}
      {error && <p role="alert">{error}</p>}
      {saved && <p role="status">Marcadores guardados.</p>}

      <dl>
        <dt>Tipo</dt>
        <dd>{documentTypeLabel(document.document_type)}</dd>
        <dt>Versão actual</dt>
        <dd>{document.current_version_number ?? "—"}</dd>
        <dt>Estado</dt>
        <dd>{document.is_outdated ? "Desactualizado" : "Actual"}</dd>
        <dt>Exportação</dt>
        <dd>{exportPolicyLabel(document.export_policy)}</dd>
      </dl>

      <section aria-labelledby="document-content-title">
        <h5 id="document-content-title">Conteúdo</h5>
        <pre>{document.content}</pre>
      </section>

      <fieldset>
        <legend>Marcadores</legend>
        <label>
          <input
            type="checkbox"
            checked={isOutdated}
            onChange={(e) => setIsOutdated(e.target.checked)}
            disabled={busy}
          />
          Marcar como desactualizado
        </label>
        <p>
          <label>
            Política de exportação
            <select
              value={exportPolicy}
              onChange={(e) => setExportPolicy(e.target.value as ExportPolicy)}
              disabled={busy}
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
            Com exportação recusada, este documento não poderá ser seleccionado
            para um pacote de contexto. Continua visível e utilizável na
            aplicação.
          </p>
        )}
        <button
          type="button"
          onClick={() => void saveMarkers()}
          disabled={busy || !markersDirty}
        >
          {busy ? "A guardar…" : "Guardar marcadores"}
        </button>
      </fieldset>

      <div>
        <button type="button" onClick={() => onEdit(document)} disabled={busy}>
          Editar conteúdo
        </button>{" "}
        <button
          type="button"
          onClick={() => onHistory(document)}
          disabled={busy}
        >
          Histórico
        </button>{" "}
        <button type="button" onClick={onBack} disabled={busy}>
          Voltar aos documentos
        </button>
      </div>
    </section>
  );
}
