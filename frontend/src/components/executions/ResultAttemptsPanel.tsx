import { useCallback, useEffect, useMemo, useState } from "react";

import {
  listResultAttempts,
  type ExecutionDetail,
  type ResultAttempt,
} from "../../api/executions";
import { abbrevChecksum, sourceModeLabel } from "./labels";
import { ResultAttemptView } from "./ResultAttemptView";
import { ResultImportForm } from "./ResultImportForm";

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

// Área de resultados da execução. Depende do estado:
// - `prepared`: apresenta o formulário de importação (+ histórico, se houver);
// - `result_pending_validation`: tentativa actual + indicação de revisão pendente;
// - `approved`/`rejected`/`completed`: histórico em modo leitura.
// Não há acções de revisão nem de aplicação nesta etapa (só se reserva espaço).
export function ResultAttemptsPanel({ execution, onReload }: Props) {
  const [attempts, setAttempts] = useState<ResultAttempt[]>([]);
  const [loadState, setLoadState] = useState<"loading" | "ready" | "error">(
    "loading",
  );
  const [openAttempt, setOpenAttempt] = useState<number | null>(null);
  const [conflict, setConflict] = useState<string | null>(null);

  const loadAttempts = useCallback(async () => {
    setLoadState((prev) => (prev === "ready" ? prev : "loading"));
    try {
      const res = await listResultAttempts(execution.id);
      setAttempts(res.results);
      setLoadState("ready");
    } catch {
      setLoadState("error");
    }
  }, [execution.id]);

  useEffect(() => {
    void loadAttempts();
    // Recarrega quando a execução muda de versão (ex.: após importar).
  }, [loadAttempts, execution.version]);

  const isPrepared = execution.status === "prepared";
  const isPending = execution.status === "result_pending_validation";

  // A tentativa actual é a de número mais alto (cada importação cria a nova actual).
  const currentAttemptNumber = useMemo(
    () =>
      attempts.reduce((max, a) => Math.max(max, a.attempt_number), 0) || null,
    [attempts],
  );

  async function handleImported() {
    setOpenAttempt(null);
    setConflict(null);
    await onReload(); // actualiza o estado da execução (→ result_pending_validation)
    await loadAttempts();
    // Abre a tentativa recém-criada (a de número mais alto após recarregar).
    setOpenAttempt(-1); // sentinela: abrir a actual assim que a lista chegar
  }

  // Depois de importar, abrir a tentativa actual quando a lista estiver pronta.
  useEffect(() => {
    if (openAttempt === -1 && currentAttemptNumber !== null) {
      setOpenAttempt(currentAttemptNumber);
    }
  }, [openAttempt, currentAttemptNumber]);

  async function handleConflict(detail: string) {
    // 409: recarrega a execução e apresenta o estado actual, com aviso (o
    // conteúdo local do formulário não é descartado silenciosamente).
    setConflict(detail);
    await onReload();
    await loadAttempts();
  }

  return (
    <section aria-labelledby="result-attempts-title" data-testid="result-attempts-panel">
      <h5 id="result-attempts-title">Resultados</h5>

      {conflict && (
        <p role="alert" data-testid="import-conflict">
          O estado da execução mudou entretanto ({conflict}). A execução foi
          recarregada; reveja o estado actual antes de importar de novo.
        </p>
      )}

      {isPending && (
        <p role="status" data-testid="review-pending">
          <strong>Resultado por validar.</strong> A revisão humana está pendente
          (será disponibilizada num passo seguinte). Nada foi aprovado nem aplicado.
        </p>
      )}

      {/* Importação: só enquanto `prepared`. */}
      {isPrepared && (
        <ResultImportForm
          execution={execution}
          onImported={handleImported}
          onConflict={handleConflict}
        />
      )}

      {/* Histórico de tentativas (crescente), sempre em leitura. */}
      {loadState === "loading" && <p role="status">A carregar tentativas…</p>}
      {loadState === "error" && (
        <p role="alert">
          Não foi possível carregar as tentativas.{" "}
          <button type="button" onClick={() => void loadAttempts()}>
            Tentar novamente
          </button>
        </p>
      )}
      {loadState === "ready" && (
        <>
          {attempts.length === 0 ? (
            <p>Ainda não há resultados importados.</p>
          ) : (
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
        </>
      )}

      {openAttempt !== null && openAttempt > 0 && (
        <ResultAttemptView
          executionId={execution.id}
          attemptNumber={openAttempt}
          isCurrent={openAttempt === currentAttemptNumber}
          onBack={() => setOpenAttempt(null)}
        />
      )}
    </section>
  );
}
