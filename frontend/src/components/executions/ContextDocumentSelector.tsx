import { useCallback, useEffect, useMemo, useState } from "react";

import {
  listDocuments,
  listVersions,
  type DocumentSummary,
  type DocumentVersionSummary,
} from "../../api/documents";
import { documentTypeLabel } from "../documents/labels";
import { abbrevChecksum } from "./labels";

// Uma versão documental exacta seleccionada para o contexto (com os metadados
// necessários à apresentação e ao envio). A `order` deriva da posição na lista.
export interface SelectedVersion {
  document: string;
  document_version: string;
  version_number: number;
  title: string;
  document_type: string;
  checksum: string;
  export_policy: string;
  is_outdated: boolean;
  purpose: string;
}

interface Props {
  productId: string;
  // Documento de instruções da função (apresentado à parte; não duplicável).
  instructionDocumentId: string | null;
  value: SelectedVersion[];
  onChange: (next: SelectedVersion[]) => void;
}

type LoadState = "loading" | "ready" | "error";

// Selecção de contexto por versões documentais exactas. Candidatos = documentos
// empresariais (sem produto) + documentos do produto actual; nunca documentos de
// outros produtos. `denied` fica desactivado; `confirm` e `is_outdated` avisam
// mas permanecem seleccionáveis. O documento de instruções da função é mostrado
// à parte e não pode ser duplicado nos dados.
export function ContextDocumentSelector({
  productId,
  instructionDocumentId,
  value,
  onChange,
}: Props) {
  const [candidates, setCandidates] = useState<DocumentSummary[]>([]);
  const [instructionDoc, setInstructionDoc] = useState<DocumentSummary | null>(
    null,
  );
  const [loadState, setLoadState] = useState<LoadState>("loading");

  const [expanded, setExpanded] = useState<string | null>(null);
  const [versions, setVersions] = useState<DocumentVersionSummary[]>([]);
  const [versionsState, setVersionsState] = useState<LoadState>("ready");
  const [chosenVersion, setChosenVersion] = useState<string>("");

  const selectedIds = useMemo(
    () => new Set(value.map((v) => v.document_version)),
    [value],
  );

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoadState("loading");
      try {
        const [product, empresarial] = await Promise.all([
          listDocuments({ product: productId, page_size: 100 }),
          listDocuments({ empresarial: true, page_size: 100 }),
        ]);
        if (cancelled) return;
        const byId = new Map<string, DocumentSummary>();
        for (const d of [...empresarial.results, ...product.results]) {
          byId.set(d.id, d);
        }
        // Documento de instruções da função: mostrado à parte, fora dos dados.
        let instruction: DocumentSummary | null = null;
        if (instructionDocumentId && byId.has(instructionDocumentId)) {
          instruction = byId.get(instructionDocumentId)!;
          byId.delete(instructionDocumentId);
        }
        setInstructionDoc(instruction);
        setCandidates([...byId.values()]);
        setLoadState("ready");
      } catch {
        if (!cancelled) setLoadState("error");
      }
    }
    void load();
    return () => {
      cancelled = true;
    };
  }, [productId, instructionDocumentId]);

  const openVersions = useCallback(async (doc: DocumentSummary) => {
    setExpanded(doc.id);
    setVersions([]);
    setChosenVersion("");
    setVersionsState("loading");
    try {
      const res = await listVersions(doc.id);
      setVersions(res.results);
      // Por defeito, a versão actual (número mais alto) já vem primeiro.
      setChosenVersion(res.results[0]?.id ?? "");
      setVersionsState("ready");
    } catch {
      setVersionsState("error");
    }
  }, []);

  function addVersion(doc: DocumentSummary) {
    const version = versions.find((v) => v.id === chosenVersion);
    if (!version || selectedIds.has(version.id)) return;
    const next: SelectedVersion = {
      document: doc.id,
      document_version: version.id,
      version_number: version.version_number,
      title: doc.title,
      document_type: doc.document_type,
      checksum: version.checksum,
      export_policy: doc.export_policy,
      is_outdated: doc.is_outdated,
      purpose: "",
    };
    onChange([...value, next]);
    setExpanded(null);
  }

  function move(index: number, delta: number) {
    const target = index + delta;
    if (target < 0 || target >= value.length) return;
    const next = [...value];
    [next[index], next[target]] = [next[target], next[index]];
    onChange(next);
  }

  function remove(index: number) {
    onChange(value.filter((_, i) => i !== index));
  }

  function setPurpose(index: number, purpose: string) {
    const next = value.map((item, i) => (i === index ? { ...item, purpose } : item));
    onChange(next);
  }

  return (
    <fieldset>
      <legend>Documentos de contexto (versões exactas)</legend>

      {instructionDoc && (
        <p role="note" data-testid="instruction-doc-note">
          Instruções da função: <strong>{instructionDoc.title}</strong>. Usadas
          separadamente como instruções — não podem ser duplicadas nos dados.
        </p>
      )}

      {loadState === "loading" && <p role="status">A carregar documentos…</p>}
      {loadState === "error" && (
        <p role="alert">Não foi possível carregar os documentos candidatos.</p>
      )}

      {loadState === "ready" && (
        <>
          <h5>Documentos candidatos</h5>
          {candidates.length === 0 ? (
            <p>Não há documentos empresariais nem do produto para seleccionar.</p>
          ) : (
            <ul>
              {candidates.map((doc) => {
                const denied = doc.export_policy === "denied";
                return (
                  <li key={doc.id} data-testid={`candidate-${doc.id}`}>
                    <span>{doc.title}</span>{" "}
                    <span>({documentTypeLabel(doc.document_type)})</span>{" "}
                    {denied && (
                      <span data-testid="denied-badge">
                        <strong>Não seleccionável</strong> — exportação recusada
                        (denied).
                      </span>
                    )}
                    {doc.export_policy === "confirm" && (
                      <span data-testid="confirm-badge">
                        {" "}
                        Exigirá confirmação antes da geração.
                      </span>
                    )}
                    {doc.is_outdated && (
                      <span data-testid="outdated-badge">
                        {" "}
                        Documento desactualizado (aviso).
                      </span>
                    )}{" "}
                    {!denied && (
                      <button
                        type="button"
                        onClick={() => void openVersions(doc)}
                        aria-label={`Escolher versão de ${doc.title}`}
                      >
                        Escolher versão
                      </button>
                    )}
                    {expanded === doc.id && !denied && (
                      <span>
                        {versionsState === "loading" && (
                          <span role="status"> A carregar versões…</span>
                        )}
                        {versionsState === "ready" && (
                          <>
                            {" "}
                            <label>
                              Versão
                              <select
                                value={chosenVersion}
                                onChange={(e) => setChosenVersion(e.target.value)}
                              >
                                {versions.map((v) => (
                                  <option key={v.id} value={v.id}>
                                    v{v.version_number} — {abbrevChecksum(v.checksum)}
                                  </option>
                                ))}
                              </select>
                            </label>{" "}
                            <button
                              type="button"
                              onClick={() => addVersion(doc)}
                              disabled={
                                !chosenVersion || selectedIds.has(chosenVersion)
                              }
                            >
                              Adicionar
                            </button>
                          </>
                        )}
                      </span>
                    )}
                  </li>
                );
              })}
            </ul>
          )}

          <h5>Contexto seleccionado (por ordem)</h5>
          {value.length === 0 ? (
            <p role="note">
              Seleccione pelo menos uma versão documental de contexto.
            </p>
          ) : (
            <ol data-testid="selected-context">
              {value.map((item, index) => (
                <li key={item.document_version}>
                  <span data-testid="selected-title">{item.title}</span>{" "}
                  <span>
                    v{item.version_number} · {abbrevChecksum(item.checksum)}
                  </span>
                  {item.export_policy === "confirm" && (
                    <span data-testid="selected-confirm">
                      {" "}
                      (confirmação exigida na geração)
                    </span>
                  )}
                  {item.is_outdated && (
                    <span data-testid="selected-outdated"> (desactualizado)</span>
                  )}
                  <br />
                  <label>
                    Papel (opcional)
                    <input
                      value={item.purpose}
                      onChange={(e) => setPurpose(index, e.target.value)}
                    />
                  </label>{" "}
                  <button
                    type="button"
                    onClick={() => move(index, -1)}
                    disabled={index === 0}
                    aria-label={`Subir ${item.title}`}
                  >
                    Subir
                  </button>{" "}
                  <button
                    type="button"
                    onClick={() => move(index, 1)}
                    disabled={index === value.length - 1}
                    aria-label={`Descer ${item.title}`}
                  >
                    Descer
                  </button>{" "}
                  <button
                    type="button"
                    onClick={() => remove(index)}
                    aria-label={`Remover ${item.title}`}
                  >
                    Remover
                  </button>
                </li>
              ))}
            </ol>
          )}
        </>
      )}
    </fieldset>
  );
}
