import { useEffect, useState, type FormEvent } from "react";

import { ApiError } from "../../api/client";
import { listDecisions, type Decision } from "../../api/decisions";
import {
  createWorkItem,
  updateWorkItem,
  WORK_TYPES,
  PRIORITIES,
  type Priority,
  type WorkItem,
  type WorkType,
} from "../../api/workItems";
import { priorityLabel, workTypeLabel } from "./labels";

interface Props {
  productId: string;
  // Quando presente, edita a pendência existente (só válida enquanto aberta).
  item?: WorkItem;
  onDone: (item: WorkItem) => void;
  onCancel: () => void;
}

// Formulário de pendência (criar e editar). Tipos e prioridades vêm de
// enumerações fechadas (sem valores arbitrários). A decisão é opcional (ligação
// à Decision do produto). Product deriva da ficha; empresa nunca é escolhida.
export function WorkItemForm({ productId, item, onDone, onCancel }: Props) {
  const isEdit = item !== undefined;
  const [title, setTitle] = useState(item?.title ?? "");
  const [workType, setWorkType] = useState<WorkType>(item?.work_type ?? "action");
  const [priority, setPriority] = useState<Priority>(item?.priority ?? "medium");
  const [dueAt, setDueAt] = useState(item?.due_at ? item.due_at.slice(0, 10) : "");
  const [notes, setNotes] = useState(item?.notes ?? "");
  const [decision, setDecision] = useState(item?.decision ?? "");
  const [decisionOptions, setDecisionOptions] = useState<Decision[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [conflict, setConflict] = useState(false);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    let cancelled = false;
    listDecisions({ product: productId })
      .then((res) => {
        if (!cancelled) setDecisionOptions(res.results);
      })
      .catch(() => {
        /* sem decisões elegíveis: o campo fica vazio (opcional) */
      });
    return () => {
      cancelled = true;
    };
  }, [productId]);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (busy) return; // evita submissão duplicada
    setBusy(true);
    setError(null);
    setConflict(false);

    // Data (YYYY-MM-DD) → ISO com hora final do dia (prazo do dia inteiro).
    const dueIso = dueAt ? new Date(`${dueAt}T23:59:59`).toISOString() : null;

    try {
      let result: WorkItem;
      if (isEdit) {
        result = await updateWorkItem(item!.id, {
          expected_version: item!.version,
          title: title.trim(),
          work_type: workType,
          priority,
          due_at: dueIso,
          notes: notes.trim(),
          decision: decision || null,
        });
      } else {
        result = await createWorkItem({
          product: productId,
          title: title.trim(),
          work_type: workType,
          priority,
          due_at: dueIso,
          notes: notes.trim() || undefined,
          decision: decision || null,
        });
      }
      onDone(result);
    } catch (e: unknown) {
      if (e instanceof ApiError && e.status === 409) {
        setConflict(true);
      } else if (e instanceof ApiError && e.status === 400) {
        setError("Verifique os campos e as associações.");
      } else {
        setError("Não foi possível guardar a pendência.");
      }
      setBusy(false);
    }
  }

  return (
    <section aria-labelledby="workitem-form-title">
      <h4 id="workitem-form-title">
        {isEdit ? "Editar pendência" : "Nova pendência"}
      </h4>
      {conflict && (
        <div role="alert">
          <p>
            A pendência foi alterada por outra operação (por exemplo, já
            concluída ou cancelada). Os seus dados não foram sobrescritos.
          </p>
          <button type="button" onClick={onCancel} disabled={busy}>
            Voltar
          </button>
        </div>
      )}
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
              value={workType}
              onChange={(e) => setWorkType(e.target.value as WorkType)}
            >
              {WORK_TYPES.map((t) => (
                <option key={t} value={t}>
                  {workTypeLabel(t)}
                </option>
              ))}
            </select>
          </label>
        </p>
        <p>
          <label>
            Prioridade
            <select
              value={priority}
              onChange={(e) => setPriority(e.target.value as Priority)}
            >
              {PRIORITIES.map((p) => (
                <option key={p} value={p}>
                  {priorityLabel(p)}
                </option>
              ))}
            </select>
          </label>
        </p>
        <p>
          <label>
            Prazo (opcional)
            <input
              type="date"
              value={dueAt}
              onChange={(e) => setDueAt(e.target.value)}
            />
          </label>
        </p>
        <p>
          <label>
            Notas (opcional)
            <textarea value={notes} onChange={(e) => setNotes(e.target.value)} />
          </label>
        </p>
        <p>
          <label>
            Decisão associada (opcional)
            <select
              value={decision}
              onChange={(e) => setDecision(e.target.value)}
            >
              <option value="">— Nenhuma —</option>
              {decisionOptions.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.title}
                </option>
              ))}
            </select>
          </label>
        </p>
        <p>
          <button type="submit" disabled={busy}>
            {busy ? "A guardar…" : isEdit ? "Guardar alterações" : "Criar pendência"}
          </button>{" "}
          <button type="button" onClick={onCancel} disabled={busy}>
            Cancelar
          </button>
        </p>
      </form>
    </section>
  );
}
