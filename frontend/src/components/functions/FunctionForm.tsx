import { useEffect, useMemo, useState, type FormEvent } from "react";

import { ApiError } from "../../api/client";
import { listDocuments, type DocumentSummary } from "../../api/documents";
import {
  ACTOR_TYPES,
  createFunction,
  updateFunction,
  type ActorType,
  type FunctionProfile,
} from "../../api/functions";
import { actorTypeLabel } from "./labels";

interface Props {
  // Quando presente, edita a função existente (pode estar activa ou inactiva).
  fn?: FunctionProfile;
  onDone: (fn: FunctionProfile) => void;
  onCancel: () => void;
}

// Funções de IA/híbridas exigem sempre aprovação humana (SEC-HUM): o servidor
// força requires_approval=true. A UI reflecte essa regra (checkbox marcada e
// desactivada) para não sugerir uma escolha que seria rejeitada.
function approvalIsForced(actorType: ActorType): boolean {
  return actorType === "ai" || actorType === "hybrid";
}

// Formulário de função organizacional (criar e editar). Tipos vêm da enumeração
// fechada. O documento de instruções é opcional e só oferece documentos
// empresariais do tipo `instrucoes` com versão válida (o servidor revalida).
export function FunctionForm({ fn, onDone, onCancel }: Props) {
  const isEdit = fn !== undefined;
  const [name, setName] = useState(fn?.name ?? "");
  const [actorType, setActorType] = useState<ActorType>(fn?.actor_type ?? "human");
  const [purpose, setPurpose] = useState(fn?.purpose ?? "");
  const [responsibilities, setResponsibilities] = useState(
    fn?.responsibilities ?? "",
  );
  const [constraints, setConstraints] = useState(fn?.constraints ?? "");
  const [requiresApproval, setRequiresApproval] = useState(
    fn?.requires_approval ?? false,
  );
  const [instructionDocument, setInstructionDocument] = useState(
    fn?.instruction_document ?? "",
  );
  const [docOptions, setDocOptions] = useState<DocumentSummary[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [conflict, setConflict] = useState(false);
  const [busy, setBusy] = useState(false);

  const forced = approvalIsForced(actorType);
  const effectiveApproval = forced ? true : requiresApproval;

  // Só documentos empresariais (sem produto) de instruções com versão válida
  // são elegíveis; a função é reutilizável entre produtos.
  const eligibleDocs = useMemo(
    () =>
      docOptions.filter(
        (d) => d.product === null && d.current_version_number !== null,
      ),
    [docOptions],
  );

  useEffect(() => {
    let cancelled = false;
    listDocuments({ document_type: "instrucoes" })
      .then((res) => {
        if (!cancelled) setDocOptions(res.results);
      })
      .catch(() => {
        /* sem documentos elegíveis: o campo fica com a opção "nenhum" */
      });
    return () => {
      cancelled = true;
    };
  }, []);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (busy) return;
    setBusy(true);
    setError(null);
    setConflict(false);

    try {
      let result: FunctionProfile;
      if (isEdit) {
        result = await updateFunction(fn!.id, {
          expected_version: fn!.version,
          name: name.trim(),
          actor_type: actorType,
          purpose: purpose.trim(),
          responsibilities: responsibilities.trim(),
          constraints: constraints.trim(),
          requires_approval: effectiveApproval,
          instruction_document: instructionDocument || null,
        });
      } else {
        result = await createFunction({
          name: name.trim(),
          actor_type: actorType,
          purpose: purpose.trim(),
          responsibilities: responsibilities.trim(),
          constraints: constraints.trim() || undefined,
          requires_approval: effectiveApproval,
          instruction_document: instructionDocument || null,
        });
      }
      onDone(result);
    } catch (e: unknown) {
      if (e instanceof ApiError && e.status === 409) {
        setConflict(true);
      } else if (e instanceof ApiError && e.status === 400) {
        setError(
          "Verifique os campos. O documento de instruções tem de ser empresarial, do tipo instruções e com versão válida.",
        );
      } else {
        setError("Não foi possível guardar a função.");
      }
      setBusy(false);
    }
  }

  return (
    <section aria-labelledby="function-form-title">
      <h4 id="function-form-title">
        {isEdit ? "Editar função" : "Nova função"}
      </h4>
      {conflict && (
        <div role="alert">
          <p>
            A função foi alterada por outra operação. Os seus dados não foram
            sobrescritos; recarregue e tente novamente.
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
            Nome
            <input value={name} onChange={(e) => setName(e.target.value)} required />
          </label>
        </p>
        <p>
          <label>
            Tipo
            <select
              value={actorType}
              onChange={(e) => setActorType(e.target.value as ActorType)}
            >
              {ACTOR_TYPES.map((t) => (
                <option key={t} value={t}>
                  {actorTypeLabel(t)}
                </option>
              ))}
            </select>
          </label>
        </p>
        <p>
          <label>
            Propósito
            <textarea
              value={purpose}
              onChange={(e) => setPurpose(e.target.value)}
              required
            />
          </label>
        </p>
        <p>
          <label>
            Responsabilidades
            <textarea
              value={responsibilities}
              onChange={(e) => setResponsibilities(e.target.value)}
              required
            />
          </label>
        </p>
        <p>
          <label>
            Limites (opcional)
            <textarea
              value={constraints}
              onChange={(e) => setConstraints(e.target.value)}
            />
          </label>
        </p>
        <p>
          <label>
            <input
              type="checkbox"
              checked={effectiveApproval}
              disabled={forced}
              onChange={(e) => setRequiresApproval(e.target.checked)}
            />
            Requer aprovação humana
          </label>
          {forced && (
            <span role="note">
              {" "}
              Obrigatório para funções de IA ou híbridas.
            </span>
          )}
        </p>
        <p>
          <label>
            Documento de instruções (opcional)
            <select
              value={instructionDocument}
              onChange={(e) => setInstructionDocument(e.target.value)}
            >
              <option value="">— Nenhum —</option>
              {eligibleDocs.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.title}
                </option>
              ))}
            </select>
          </label>
        </p>
        <p>
          <button type="submit" disabled={busy}>
            {busy ? "A guardar…" : isEdit ? "Guardar alterações" : "Criar função"}
          </button>{" "}
          <button type="button" onClick={onCancel} disabled={busy}>
            Cancelar
          </button>
        </p>
      </form>
    </section>
  );
}
