import { useCallback, useEffect, useMemo, useState } from "react";

import {
  listResultAttempts,
  listReviews,
  reviewResult,
  type ExecutionDetail,
  type ResultAttempt,
  type ResultReview,
  type ReviewOperation,
} from "../../api/executions";
import { abbrevChecksum, reviewDecisionLabel, sourceModeLabel } from "./labels";
import { ResultAttemptView } from "./ResultAttemptView";

interface Props {
  execution: ExecutionDetail;
  onReload: () => void | Promise<void>;
}

function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleString("pt-PT");
  } catch {
    return iso;
  }
}

type Action = "approve" | "reject" | "request-correction" | null;

// Painel de revisão humana (MVP-14). Aparece **apenas** em
// `result_pending_validation`. Apresenta a tentativa actual e o histórico
// (tentativas + revisões) em leitura, com a origem, o conteúdo original e a
// pré-visualização SEGURA de cada tentativa (via `ResultAttemptView`; os snapshots
// e as versões documentais de contexto ficam no detalhe da execução, acima). Três
// acções separadas — Aprovar, Rejeitar e Pedir correcção. **Aprovar ≠ aplicar**: a
// aprovação exige confirmação explícita que deixa claro que validar o resultado
// NÃO aplica nenhuma alteração (a aplicação é uma operação posterior). Rejeição e
// correcção exigem observações. Os botões ficam desactivados durante a submissão;
// um 409 recarrega o estado. Não há qualquer acção de aplicação nesta etapa.
export function ValidationPanel({ execution, onReload }: Props) {
  const [attempts, setAttempts] = useState<ResultAttempt[]>([]);
  const [reviews, setReviews] = useState<ResultReview[]>([]);
  const [loadState, setLoadState] = useState<"loading" | "ready" | "error">(
    "loading",
  );
  const [openAttempt, setOpenAttempt] = useState<number | null>(null);
  const [action, setAction] = useState<Action>(null);
  const [observations, setObservations] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conflict, setConflict] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoadState((prev) => (prev === "ready" ? prev : "loading"));
    try {
      const [a, r] = await Promise.all([
        listResultAttempts(execution.id),
        listReviews(execution.id),
      ]);
      setAttempts(a.results);
      setReviews(r.results);
      setLoadState("ready");
    } catch {
      setLoadState("error");
    }
  }, [execution.id]);

  useEffect(() => {
    void load();
  }, [load, execution.version]);

  // A tentativa actual é a de número mais alto (cada importação cria a nova actual).
  const currentAttemptNumber = useMemo(
    () =>
      attempts.reduce((max, a) => Math.max(max, a.attempt_number), 0) || null,
    [attempts],
  );

  // Por defeito abre a tentativa actual (a que está a ser revista).
  useEffect(() => {
    if (openAttempt === null && currentAttemptNumber !== null) {
      setOpenAttempt(currentAttemptNumber);
    }
  }, [openAttempt, currentAttemptNumber]);

  function reset() {
    setAction(null);
    setObservations("");
    setError(null);
  }

  async function submit(operation: ReviewOperation) {
    if (busy || currentAttemptNumber === null) return;
    if (operation !== "approve" && observations.trim() === "") {
      setError("As observações são obrigatórias.");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const outcome = await reviewResult(
        execution.id,
        currentAttemptNumber,
        operation,
        {
          expected_version: execution.version,
          observations:
            operation === "approve" ? undefined : observations.trim(),
        },
      );
      if (outcome.kind === "ok") {
        reset();
        await onReload(); // a execução muda de estado (approved/rejected/prepared)
        return;
      }
      if (outcome.kind === "conflict") {
        // 409: recarrega o estado; não repete automaticamente.
        setConflict(outcome.detail);
        reset();
        await onReload();
        await load();
      } else if (outcome.kind === "forbidden") {
        setError(outcome.detail || "Só um Owner pode rever o resultado.");
      } else if (outcome.kind === "invalid") {
        setError(outcome.detail);
      } else if (outcome.kind === "not_found") {
        setError("A execução ou tentativa já não está disponível.");
        await onReload();
      } else {
        setError("Não foi possível concluir a revisão.");
      }
    } catch {
      setError("Falha de comunicação com o servidor.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section
      aria-labelledby="validation-panel-title"
      data-testid="validation-panel"
    >
      <h5 id="validation-panel-title">Revisão do resultado</h5>
      <p role="status" data-testid="validation-pending-note">
        <strong>Resultado por validar.</strong> Reveja a tentativa actual e
        decida. Nada foi aprovado nem aplicado até aqui.
      </p>

      {conflict && (
        <p role="alert" data-testid="review-conflict">
          O estado da execução mudou entretanto ({conflict}). Foi recarregado;
          reveja o estado actual.
        </p>
      )}

      {/* Histórico de tentativas (crescente), sempre em leitura; abrível. */}
      {loadState === "loading" && <p role="status">A carregar…</p>}
      {loadState === "error" && (
        <p role="alert">
          Não foi possível carregar as tentativas/revisões.{" "}
          <button type="button" onClick={() => void load()}>
            Tentar novamente
          </button>
        </p>
      )}
      {loadState === "ready" && attempts.length > 0 && (
        <ol data-testid="attempt-history">
          {attempts.map((a) => (
            <li key={a.id}>
              <button
                type="button"
                onClick={() => setOpenAttempt(a.attempt_number)}
              >
                Tentativa {a.attempt_number}
              </button>{" "}
              <span>
                {formatDate(a.created_at)} · {a.source_tool}
                {a.source_model ? ` (${a.source_model})` : ""} ·{" "}
                {sourceModeLabel(a.source_mode)} · v{a.version_number} ·{" "}
                {abbrevChecksum(a.checksum)}
              </span>
              {a.attempt_number === currentAttemptNumber && (
                <span data-testid="history-current"> · actual</span>
              )}
            </li>
          ))}
        </ol>
      )}

      {/* Tentativa aberta: origem, conteúdo original e pré-visualização segura. */}
      {openAttempt !== null && openAttempt > 0 && (
        <ResultAttemptView
          executionId={execution.id}
          attemptNumber={openAttempt}
          isCurrent={openAttempt === currentAttemptNumber}
          onBack={() => setOpenAttempt(currentAttemptNumber)}
        />
      )}

      {/* Acções separadas: Aprovar / Rejeitar / Pedir correcção. */}
      <div role="group" aria-label="Acções de revisão" data-testid="review-actions">
        {action === null && (
          <>
            <button
              type="button"
              data-testid="action-approve"
              onClick={() => {
                reset();
                setAction("approve");
              }}
            >
              Aprovar…
            </button>{" "}
            <button
              type="button"
              data-testid="action-reject"
              onClick={() => {
                reset();
                setAction("reject");
              }}
            >
              Rejeitar…
            </button>{" "}
            <button
              type="button"
              data-testid="action-request-correction"
              onClick={() => {
                reset();
                setAction("request-correction");
              }}
            >
              Pedir correcção…
            </button>
          </>
        )}
      </div>

      {error && <p role="alert">{error}</p>}

      {/* Confirmação de aprovação: deixa explícito que aprovar NÃO aplica nada. */}
      {action === "approve" && (
        <div
          role="group"
          aria-label="Confirmar aprovação"
          data-testid="approve-confirm"
        >
          <p>Confirma a aprovação deste resultado?</p>
          <ul>
            <li>aprovar <strong>valida</strong> o resultado;</li>
            <li>aprovar <strong>não</strong> aplica quaisquer alterações;</li>
            <li>a aplicação será uma <strong>operação posterior</strong>.</li>
          </ul>
          <p>
            <label>
              Observações (opcional)
              <textarea
                value={observations}
                onChange={(e) => setObservations(e.target.value)}
                rows={3}
              />
            </label>
          </p>
          <button
            type="button"
            data-testid="approve-confirm-button"
            onClick={() => void submit("approve")}
            disabled={busy}
          >
            {busy ? "A aprovar…" : "Confirmar aprovação"}
          </button>{" "}
          <button type="button" onClick={reset} disabled={busy}>
            Cancelar
          </button>
        </div>
      )}

      {/* Rejeição / pedido de correcção: observações obrigatórias. */}
      {(action === "reject" || action === "request-correction") && (
        <div
          role="group"
          aria-label={
            action === "reject" ? "Rejeitar resultado" : "Pedir correcção"
          }
          data-testid={
            action === "reject" ? "reject-form" : "request-correction-form"
          }
        >
          <p>
            {action === "reject"
              ? "Rejeitar é uma decisão final: a execução fica rejeitada e nenhuma alteração oficial é aplicada."
              : "Pedir correcção devolve a execução ao estado Preparada para uma nova importação. A tentativa e esta revisão são preservadas."}
          </p>
          <p>
            <label>
              Observações (obrigatórias)
              <textarea
                value={observations}
                onChange={(e) => setObservations(e.target.value)}
                rows={3}
                data-testid="observations-input"
              />
            </label>
          </p>
          <button
            type="button"
            data-testid={
              action === "reject"
                ? "reject-confirm-button"
                : "request-correction-confirm-button"
            }
            onClick={() =>
              void submit(action === "reject" ? "reject" : "request-correction")
            }
            disabled={busy}
          >
            {busy
              ? "A submeter…"
              : action === "reject"
                ? "Confirmar rejeição"
                : "Confirmar pedido de correcção"}
          </button>{" "}
          <button type="button" onClick={reset} disabled={busy}>
            Cancelar
          </button>
        </div>
      )}

      {/* Histórico de revisões (só leitura). */}
      <section aria-labelledby="review-history-title">
        <h6 id="review-history-title">Histórico de revisões</h6>
        {loadState === "ready" &&
          (reviews.length === 0 ? (
            <p>Ainda não há revisões.</p>
          ) : (
            <ol data-testid="review-history">
              {reviews.map((r) => (
                <li key={r.id}>
                  <strong>{reviewDecisionLabel(r.decision)}</strong> · tentativa{" "}
                  {r.attempt_number} · {formatDate(r.created_at)}
                  {r.observations && <span> · {r.observations}</span>}
                </li>
              ))}
            </ol>
          ))}
      </section>

      {/* Recordatório: nesta etapa não existe qualquer acção de aplicação. */}
      <p role="note" data-testid="no-application-note">
        <small>
          Esta etapa é apenas de revisão. A aplicação de um resultado aprovado é
          uma operação posterior e explícita (ainda não disponível aqui).
        </small>
      </p>
    </section>
  );
}
