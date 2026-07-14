import { useCallback, useEffect, useMemo, useState } from "react";

import {
  applyDecision,
  applyDocument,
  applyWorkItem,
  closeWithoutApplication,
  getResultAttempt,
  listResultAttempts,
  listReviews,
  type ApplyOutcome,
  type ExecutionDetail,
  type ResultApplication,
  type ResultAttempt,
  type ResultReview,
} from "../../api/executions";
import {
  getDocument,
  listDocuments,
  type DocumentDetail,
  type DocumentSummary,
} from "../../api/documents";
import { listDecisions, type Decision } from "../../api/decisions";
import { listWorkItems, type WorkItem } from "../../api/workItems";
import { documentTypeLabel } from "../documents/labels";
import { abbrevChecksum, reviewDecisionLabel } from "./labels";

interface Props {
  execution: ExecutionDetail;
  onReload: () => void | Promise<void>;
}

type Mode = "document" | "decision" | "work_item" | "no_change" | null;

// Painel de aplicação controlada (MVP-15.C1/C2). Aparece **apenas** em `approved`.
// Oferece **quatro** caminhos mutuamente exclusivos — nova versão documental,
// substituir decisão, concluir pendência, fechar sem alteração — e conclui a
// execução exactamente uma vez (uma aplicação por execução). Nenhum formulário é
// preenchido por parsing do resultado; o utilizador fornece e confirma os campos.
// Deixa claro que a aprovação anterior NÃO aplicou nada; antes de confirmar mostra
// o resumo exacto da mutação; um 409 recarrega os dados sem sobrescrever.
export function ApplicationPanel({ execution, onReload }: Props) {
  const [attempts, setAttempts] = useState<ResultAttempt[]>([]);
  const [reviews, setReviews] = useState<ResultReview[]>([]);
  const [docs, setDocs] = useState<DocumentSummary[]>([]);
  const [decisions, setDecisions] = useState<Decision[]>([]);
  const [workItems, setWorkItems] = useState<WorkItem[]>([]);
  const [loadState, setLoadState] = useState<"loading" | "ready" | "error">(
    "loading",
  );
  const [resultContent, setResultContent] = useState<string>("");

  const [mode, setMode] = useState<Mode>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conflict, setConflict] = useState<string | null>(null);
  const [confirming, setConfirming] = useState(false);
  const [applied, setApplied] = useState<ResultApplication | null>(null);

  // Document
  const [docId, setDocId] = useState("");
  const [docTarget, setDocTarget] = useState<DocumentDetail | null>(null);
  const [docContent, setDocContent] = useState("");
  const [changeSummary, setChangeSummary] = useState("");
  // Decision
  const [decId, setDecId] = useState("");
  const [decTitle, setDecTitle] = useState("");
  const [decContext, setDecContext] = useState("");
  const [decText, setDecText] = useState("");
  const [decImpact, setDecImpact] = useState("");
  // Work item
  const [wiId, setWiId] = useState("");
  // No change
  const [rationale, setRationale] = useState("");

  const currentAttemptNumber = useMemo(
    () => attempts.reduce((m, a) => Math.max(m, a.attempt_number), 0) || null,
    [attempts],
  );
  const approvedReview = useMemo(
    () => reviews.find((r) => r.decision === "approved") ?? null,
    [reviews],
  );
  const selectedDecision = useMemo(
    () => decisions.find((d) => d.id === decId) ?? null,
    [decisions, decId],
  );
  const selectedWorkItem = useMemo(
    () => workItems.find((w) => w.id === wiId) ?? null,
    [workItems, wiId],
  );

  const load = useCallback(async () => {
    setLoadState("loading");
    try {
      const [a, r, d, dec, wi] = await Promise.all([
        listResultAttempts(execution.id),
        listReviews(execution.id),
        listDocuments({ product: execution.product, page_size: 100 }),
        listDecisions({ product: execution.product, status: "active" }),
        listWorkItems({ product: execution.product, status: "open" }),
      ]);
      setAttempts(a.results);
      setReviews(r.results);
      setDocs(d.results.filter((x) => x.document_type !== "resultado"));
      setDecisions(dec.results);
      setWorkItems(wi.results);
      setLoadState("ready");
    } catch {
      setLoadState("error");
    }
  }, [execution.id, execution.product]);

  useEffect(() => {
    void load();
  }, [load, execution.version]);

  useEffect(() => {
    if (currentAttemptNumber === null) return;
    let cancelled = false;
    getResultAttempt(execution.id, currentAttemptNumber)
      .then((res) => !cancelled && setResultContent(res.content))
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [execution.id, currentAttemptNumber]);

  async function selectDoc(id: string) {
    setDocId(id);
    setDocTarget(null);
    setError(null);
    if (!id) return;
    try {
      setDocTarget(await getDocument(id));
    } catch {
      setError("Não foi possível carregar o documento alvo.");
    }
  }

  function resetForms() {
    setConfirming(false);
    setError(null);
  }

  function chooseMode(m: Mode) {
    resetForms();
    setConflict(null);
    setMode(m);
  }

  async function reloadAfterConflict(detail: string) {
    setConflict(detail);
    resetForms();
    if (mode === "document" && docId) {
      try {
        setDocTarget(await getDocument(docId));
      } catch {
        /* mantém */
      }
    }
    await onReload();
    await load();
  }

  function handleOutcome(outcome: ApplyOutcome): boolean {
    // Devolve true se aplicado com sucesso.
    if (outcome.kind === "ok") {
      setApplied(outcome.application);
      setConfirming(false);
      return true;
    }
    if (outcome.kind === "conflict") {
      void reloadAfterConflict(outcome.detail);
    } else if (outcome.kind === "forbidden") {
      setError(outcome.detail || "Só um Owner pode aplicar.");
      setConfirming(false);
    } else if (outcome.kind === "not_eligible") {
      setError(outcome.detail || "Alvo não elegível.");
      setConfirming(false);
    } else if (outcome.kind === "too_large") {
      setError("O conteúdo excede o limite permitido (413).");
      setConfirming(false);
    } else if (outcome.kind === "invalid") {
      setError(outcome.detail);
      setConfirming(false);
    } else if (outcome.kind === "not_found") {
      setError("A execução ou o alvo já não está disponível.");
      setConfirming(false);
      void onReload();
    } else {
      setError("Não foi possível concluir a aplicação.");
      setConfirming(false);
    }
    return false;
  }

  async function submit() {
    if (busy || currentAttemptNumber === null) return;
    setBusy(true);
    setError(null);
    try {
      let outcome: ApplyOutcome;
      if (mode === "document") {
        if (!docTarget) return;
        outcome = await applyDocument(execution.id, {
          target_document: docTarget.id,
          expected_execution_version: execution.version,
          expected_document_version: docTarget.version,
          content: docContent,
          change_summary: changeSummary.trim(),
          attempt_number: currentAttemptNumber,
        });
      } else if (mode === "decision") {
        if (!selectedDecision) return;
        outcome = await applyDecision(execution.id, {
          target_decision: selectedDecision.id,
          expected_execution_version: execution.version,
          expected_decision_version: selectedDecision.version,
          title: decTitle.trim(),
          context: decContext.trim(),
          decision_text: decText.trim(),
          impact: decImpact.trim() || undefined,
          attempt_number: currentAttemptNumber,
        });
      } else if (mode === "work_item") {
        if (!selectedWorkItem) return;
        outcome = await applyWorkItem(execution.id, {
          target_work_item: selectedWorkItem.id,
          expected_execution_version: execution.version,
          expected_work_item_version: selectedWorkItem.version,
          attempt_number: currentAttemptNumber,
        });
      } else if (mode === "no_change") {
        outcome = await closeWithoutApplication(execution.id, {
          expected_execution_version: execution.version,
          rationale: rationale.trim(),
          attempt_number: currentAttemptNumber,
        });
      } else {
        return;
      }
      handleOutcome(outcome);
    } catch {
      setError("Falha de comunicação com o servidor.");
      setConfirming(false);
    } finally {
      setBusy(false);
    }
  }

  function openConfirm() {
    setError(null);
    if (mode === "document") {
      if (!docTarget) return setError("Escolha um documento alvo.");
      if (docContent.trim() === "")
        return setError("O conteúdo a aplicar é obrigatório.");
      if (changeSummary.trim() === "")
        return setError("O resumo da alteração é obrigatório.");
    } else if (mode === "decision") {
      if (!selectedDecision) return setError("Escolha a decisão a substituir.");
      if (!(decTitle.trim() && decContext.trim() && decText.trim()))
        return setError("Título, contexto e decisão são obrigatórios.");
    } else if (mode === "work_item") {
      if (!selectedWorkItem) return setError("Escolha a pendência a concluir.");
    } else if (mode === "no_change") {
      if (rationale.trim() === "")
        return setError("A justificação é obrigatória.");
    }
    setConfirming(true);
  }

  // --- Estado pós-aplicação -------------------------------------------------
  if (applied) {
    return (
      <section aria-labelledby="application-done-title" data-testid="application-done">
        <h5 id="application-done-title">Resultado aplicado</h5>
        <p role="status">
          A aplicação (<strong>{applied.application_type}</strong>) foi registada e a
          execução será concluída.
        </p>
        <dl>
          {applied.application_type === "document" && (
            <>
              <dt>Documento alvo</dt>
              <dd>{applied.target_document}</dd>
              <dt>Versão base → criada</dt>
              <dd>
                v{applied.base_version_number} → v{applied.created_version_number} ·{" "}
                {abbrevChecksum(applied.created_version_checksum ?? "")}
              </dd>
            </>
          )}
          {applied.application_type === "decision" && (
            <>
              <dt>Decisão substituída</dt>
              <dd>{applied.target_decision}</dd>
              <dt>Decisão criada (activa)</dt>
              <dd>{applied.created_decision}</dd>
            </>
          )}
          {applied.application_type === "work_item" && (
            <>
              <dt>Pendência concluída</dt>
              <dd>{applied.target_work_item}</dd>
            </>
          )}
          {applied.application_type === "no_change" && (
            <>
              <dt>Fecho sem alteração</dt>
              <dd>Nenhuma fonte oficial foi alterada.</dd>
            </>
          )}
          <dt>Ligação à execução</dt>
          <dd>{applied.execution}</dd>
        </dl>
        <button
          type="button"
          data-testid="application-finish"
          onClick={() => void onReload()}
        >
          Ver execução concluída
        </button>
      </section>
    );
  }

  return (
    <section aria-labelledby="application-panel-title" data-testid="application-panel">
      <h5 id="application-panel-title">Aplicar resultado aprovado</h5>

      <p role="note" data-testid="approval-did-not-apply">
        <strong>A aprovação não aplicou nada.</strong> Escolha <strong>um</strong>{" "}
        caminho para concluir a execução — uma execução produz{" "}
        <strong>no máximo uma</strong> aplicação. Os campos são fornecidos e
        confirmados por si; o resultado <strong>não</strong> é aplicado
        automaticamente.
      </p>

      {conflict && (
        <p role="alert" data-testid="application-conflict">
          O estado mudou entretanto ({conflict}). Os dados foram recarregados;
          reveja antes de aplicar de novo.
        </p>
      )}

      {loadState === "loading" && <p role="status">A carregar…</p>}
      {loadState === "error" && (
        <p role="alert">Não foi possível carregar os dados de aplicação.</p>
      )}

      {loadState === "ready" && (
        <>
          <dl>
            <dt>Tentativa aprovada</dt>
            <dd data-testid="approved-attempt">
              {currentAttemptNumber !== null ? `Tentativa ${currentAttemptNumber}` : "—"}
            </dd>
            <dt>Revisão</dt>
            <dd data-testid="approved-review">
              {approvedReview ? reviewDecisionLabel(approvedReview.decision) : "—"}
            </dd>
          </dl>

          <details data-testid="original-result">
            <summary>Resultado original (referência)</summary>
            <pre style={{ whiteSpace: "pre-wrap" }}>{resultContent}</pre>
          </details>

          {/* Quatro opções. */}
          <div role="group" aria-label="Caminhos de aplicação" data-testid="apply-options">
            <button type="button" data-testid="option-document"
              disabled={mode === "document"} onClick={() => chooseMode("document")}>
              Criar nova versão documental
            </button>{" "}
            <button type="button" data-testid="option-decision"
              disabled={mode === "decision"} onClick={() => chooseMode("decision")}>
              Substituir decisão
            </button>{" "}
            <button type="button" data-testid="option-work_item"
              disabled={mode === "work_item"} onClick={() => chooseMode("work_item")}>
              Concluir pendência
            </button>{" "}
            <button type="button" data-testid="option-no_change"
              disabled={mode === "no_change"} onClick={() => chooseMode("no_change")}>
              Fechar sem alteração
            </button>
          </div>

          {error && <p role="alert">{error}</p>}

          {/* --- Documento --- */}
          {mode === "document" && (
            <div data-testid="form-document">
              <p>
                <label>
                  Documento alvo (do produto)
                  <select data-testid="target-select" value={docId}
                    onChange={(e) => void selectDoc(e.target.value)}>
                    <option value="">— escolher —</option>
                    {docs.map((d) => (
                      <option key={d.id} value={d.id}>
                        {d.title} ({documentTypeLabel(d.document_type)}) · v
                        {d.current_version_number ?? "—"}
                      </option>
                    ))}
                  </select>
                </label>
              </p>
              {docTarget && (
                <>
                  <p data-testid="target-current">
                    Versão actual: <strong>v{docTarget.version}</strong> ·{" "}
                    {abbrevChecksum(docTarget.checksum)}
                  </p>
                  <p>
                    <button type="button" data-testid="use-result-as-start"
                      onClick={() => setDocContent(resultContent)}>
                      Usar resultado como ponto de partida
                    </button>
                  </p>
                  <p>
                    <label>
                      Conteúdo a aplicar (revisto)
                      <textarea data-testid="apply-content" rows={6}
                        value={docContent}
                        onChange={(e) => setDocContent(e.target.value)} />
                    </label>
                  </p>
                  <p>
                    <label>
                      Resumo da alteração
                      <input data-testid="apply-change-summary" value={changeSummary}
                        onChange={(e) => setChangeSummary(e.target.value)} />
                    </label>
                  </p>
                </>
              )}
            </div>
          )}

          {/* --- Decisão --- */}
          {mode === "decision" && (
            <div data-testid="form-decision">
              <p>
                <label>
                  Decisão a substituir (activa)
                  <select data-testid="decision-select" value={decId}
                    onChange={(e) => setDecId(e.target.value)}>
                    <option value="">— escolher —</option>
                    {decisions.map((d) => (
                      <option key={d.id} value={d.id}>
                        {d.title} · v{d.version}
                      </option>
                    ))}
                  </select>
                </label>
              </p>
              {selectedDecision && (
                <p data-testid="decision-current">
                  Será substituída: <strong>{selectedDecision.title}</strong>
                </p>
              )}
              <p>
                <label>Título<input data-testid="decision-title" value={decTitle}
                  onChange={(e) => setDecTitle(e.target.value)} /></label>
              </p>
              <p>
                <label>Contexto<textarea data-testid="decision-context" rows={2}
                  value={decContext} onChange={(e) => setDecContext(e.target.value)} /></label>
              </p>
              <p>
                <label>Decisão<textarea data-testid="decision-text" rows={2}
                  value={decText} onChange={(e) => setDecText(e.target.value)} /></label>
              </p>
              <p>
                <label>Impacto (opcional)<input data-testid="decision-impact"
                  value={decImpact} onChange={(e) => setDecImpact(e.target.value)} /></label>
              </p>
            </div>
          )}

          {/* --- Pendência --- */}
          {mode === "work_item" && (
            <div data-testid="form-work_item">
              <p>
                <label>
                  Pendência a concluir (aberta)
                  <select data-testid="work-item-select" value={wiId}
                    onChange={(e) => setWiId(e.target.value)}>
                    <option value="">— escolher —</option>
                    {workItems.map((w) => (
                      <option key={w.id} value={w.id}>
                        {w.title} · v{w.version}
                      </option>
                    ))}
                  </select>
                </label>
              </p>
              {selectedWorkItem && (
                <p data-testid="work-item-current">
                  Será concluída: <strong>{selectedWorkItem.title}</strong> (os outros
                  campos não são alterados).
                </p>
              )}
            </div>
          )}

          {/* --- Fecho sem alteração --- */}
          {mode === "no_change" && (
            <div data-testid="form-no_change">
              <p>
                <label>
                  Justificação (obrigatória)
                  <textarea data-testid="no-change-rationale" rows={3}
                    value={rationale} onChange={(e) => setRationale(e.target.value)} />
                </label>
              </p>
            </div>
          )}

          {/* --- Confirmação (resumo exacto da mutação) --- */}
          {mode !== null && (
            confirming ? (
              <div role="group" aria-label="Confirmar aplicação" data-testid="apply-confirm">
                {mode === "document" && (
                  <p>Será criada uma <strong>nova versão oficial</strong> do documento;
                    o conteúdo foi revisto por si; a execução ficará concluída.</p>
                )}
                {mode === "decision" && (
                  <p>Será <strong>substituída</strong> a decisão «{selectedDecision?.title}»
                    (fica <em>superseded</em>); a nova decisão fica <strong>activa</strong>;
                    a execução ficará concluída.</p>
                )}
                {mode === "work_item" && (
                  <p>Será <strong>concluída</strong> a pendência «{selectedWorkItem?.title}»
                    (os outros campos não mudam); a execução ficará concluída.</p>
                )}
                {mode === "no_change" && (
                  <ul>
                    <li>o resultado foi <strong>aprovado</strong>;</li>
                    <li><strong>nenhuma</strong> fonte oficial será alterada;</li>
                    <li>a execução será <strong>concluída</strong>.</li>
                  </ul>
                )}
                <button type="button" data-testid="apply-confirm-button"
                  onClick={() => void submit()} disabled={busy}>
                  {busy ? "A aplicar…" : "Confirmar"}
                </button>{" "}
                <button type="button" onClick={() => setConfirming(false)} disabled={busy}>
                  Cancelar
                </button>
              </div>
            ) : (
              <button type="button" data-testid="apply-open-confirm" onClick={openConfirm}>
                {mode === "no_change" ? "Fechar sem alteração…" : "Aplicar…"}
              </button>
            )
          )}
        </>
      )}
    </section>
  );
}
