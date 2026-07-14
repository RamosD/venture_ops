import { useState } from "react";

import { ApiError } from "../../api/client";
import {
  cancelWorkItem,
  completeWorkItem,
  type WorkItem,
} from "../../api/workItems";
import { formatDate } from "../portfolio/format";
import { priorityLabel, workStatusLabel, workTypeLabel } from "./labels";

interface Props {
  item: WorkItem;
  onEdit: (item: WorkItem) => void;
  onChanged: (item: WorkItem) => void;
  onBack: () => void;
}

// Detalhe da pendência com as acções do ciclo de vida. "Editar" e "Concluir"
// só quando aberta; "Cancelar" exige confirmação explícita. Estados finais são
// imutáveis (não se reabre no MVP). O sinal de vencida é calculado no servidor.
export function WorkItemDetail({ item: initial, onEdit, onChanged, onBack }: Props) {
  const [item, setItem] = useState<WorkItem>(initial);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conflict, setConflict] = useState(false);
  const [confirmingCancel, setConfirmingCancel] = useState(false);

  const isOpen = item.status === "open";

  async function run(op: (id: string, v: number) => Promise<WorkItem>) {
    if (busy) return;
    setBusy(true);
    setError(null);
    setConflict(false);
    setConfirmingCancel(false);
    try {
      const updated = await op(item.id, item.version);
      setItem(updated);
      onChanged(updated);
    } catch (e: unknown) {
      if (e instanceof ApiError && e.status === 409) {
        setConflict(true);
      } else {
        setError("Não foi possível concluir a operação.");
      }
    } finally {
      setBusy(false);
    }
  }

  return (
    <section aria-labelledby="workitem-detail-title">
      <h4 id="workitem-detail-title">{item.title}</h4>

      {conflict && (
        <div role="alert">
          <p>
            A pendência foi alterada por outra operação. Os seus dados não foram
            sobrescritos.
          </p>
          <button type="button" onClick={onBack} disabled={busy}>
            Voltar às pendências
          </button>
        </div>
      )}
      {error && <p role="alert">{error}</p>}

      <dl>
        <dt>Tipo</dt>
        <dd>{workTypeLabel(item.work_type)}</dd>
        <dt>Prioridade</dt>
        <dd>{priorityLabel(item.priority)}</dd>
        <dt>Prazo</dt>
        <dd>
          {formatDate(item.due_at)}
          {item.is_overdue && (
            <>
              {" "}
              <strong data-testid="overdue-badge">(Vencida)</strong>
            </>
          )}
        </dd>
        <dt>Estado</dt>
        <dd>{workStatusLabel(item.status)}</dd>
        <dt>Decisão associada</dt>
        <dd>{item.decision ?? "—"}</dd>
        <dt>Notas</dt>
        <dd>{item.notes ? <pre>{item.notes}</pre> : "—"}</dd>
      </dl>

      <div>
        {isOpen ? (
          <>
            <button type="button" onClick={() => onEdit(item)} disabled={busy}>
              Editar
            </button>{" "}
            <button
              type="button"
              onClick={() => void run(completeWorkItem)}
              disabled={busy}
            >
              Concluir
            </button>{" "}
            {confirmingCancel ? (
              <span role="group" aria-label="Confirmar cancelamento">
                <span>Cancelar esta pendência? Esta acção é definitiva.</span>{" "}
                <button
                  type="button"
                  onClick={() => void run(cancelWorkItem)}
                  disabled={busy}
                >
                  Confirmar cancelamento
                </button>{" "}
                <button
                  type="button"
                  onClick={() => setConfirmingCancel(false)}
                  disabled={busy}
                >
                  Manter
                </button>
              </span>
            ) : (
              <button
                type="button"
                onClick={() => setConfirmingCancel(true)}
                disabled={busy}
              >
                Cancelar pendência
              </button>
            )}
          </>
        ) : (
          <p role="note">
            Esta pendência está num estado final ({workStatusLabel(item.status)})
            e não pode ser alterada nem reaberta.
          </p>
        )}{" "}
        <button type="button" onClick={onBack} disabled={busy}>
          Voltar às pendências
        </button>
      </div>
    </section>
  );
}
