import { useEffect, useMemo, useState, type FormEvent } from "react";

import { ApiError } from "../../api/client";
import {
  createExecution,
  EXECUTION_MODES,
  type ExecutionDetail,
  type ExecutionMode,
} from "../../api/executions";
import { listFunctions, type FunctionProfile } from "../../api/functions";
import { actorTypeLabel } from "../functions/labels";
import {
  ContextDocumentSelector,
  type SelectedVersion,
} from "./ContextDocumentSelector";
import { executionModeLabel } from "./labels";

interface Props {
  productId: string;
  onCreated: (execution: ExecutionDetail) => void;
  onCancel: () => void;
}

// Formulário de preparação da execução. Só permite escolher funções ACTIVE e
// versões documentais exactas (empresariais ou do produto actual). Não cria nem
// edita funções (o catálogo vive na sua área própria). A execução nasce sempre
// `prepared`; não há escolha de estado. Evita submissão duplicada (busy).
export function ExecutionCreateForm({ productId, onCreated, onCancel }: Props) {
  const [functions, setFunctions] = useState<FunctionProfile[]>([]);
  const [functionsLoaded, setFunctionsLoaded] = useState(false);
  const [functionId, setFunctionId] = useState("");

  const [title, setTitle] = useState("");
  const [objective, setObjective] = useState("");
  const [requestInstructions, setRequestInstructions] = useState("");
  const [constraints, setConstraints] = useState("");
  const [expectedOutputFormat, setExpectedOutputFormat] = useState("");
  const [executionMode, setExecutionMode] =
    useState<ExecutionMode>("manual_local");
  const [context, setContext] = useState<SelectedVersion[]>([]);

  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    let cancelled = false;
    // Só funções active são seleccionáveis em novas execuções (filtro no servidor).
    listFunctions({ status: "active", page_size: 100 })
      .then((res) => {
        if (!cancelled) {
          setFunctions(res.results);
          setFunctionsLoaded(true);
        }
      })
      .catch(() => {
        if (!cancelled) setFunctionsLoaded(true);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const selectedFunction = useMemo(
    () => functions.find((f) => f.id === functionId) ?? null,
    [functions, functionId],
  );

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (busy) return; // evita submissão duplicada
    if (!functionId) {
      setError("Escolha uma função activa.");
      return;
    }
    if (context.length === 0) {
      setError("Seleccione pelo menos uma versão documental de contexto.");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const execution = await createExecution({
        product: productId,
        function_profile: functionId,
        title: title.trim(),
        objective: objective.trim(),
        request_instructions: requestInstructions.trim(),
        constraints: constraints.trim() || undefined,
        expected_output_format: expectedOutputFormat.trim(),
        execution_mode: executionMode,
        // A ordem enviada corresponde à ordem visível (posição na lista).
        context: context.map((c) => ({
          document_version: c.document_version,
          purpose: c.purpose.trim() || undefined,
        })),
      });
      onCreated(execution);
    } catch (e: unknown) {
      if (e instanceof ApiError && e.status === 409) {
        setError("Conflito de versão; recarregue os dados e tente novamente.");
      } else if (e instanceof ApiError && e.status === 400) {
        setError(
          "Verifique os campos e a selecção de contexto (documento recusado, de outro produto ou repetido).",
        );
      } else if (e instanceof ApiError && (e.status === 403 || e.status === 404)) {
        setError("Sem acesso ou recurso inexistente.");
      } else {
        setError("Não foi possível preparar a execução.");
      }
      setBusy(false);
    }
  }

  return (
    <section aria-labelledby="execution-form-title">
      <h4 id="execution-form-title">Preparar execução</h4>
      {error && <p role="alert">{error}</p>}
      <form onSubmit={handleSubmit}>
        <p>
          <label>
            Título
            <input value={title} onChange={(e) => setTitle(e.target.value)} required />
          </label>
        </p>
        <p>
          <label>
            Objectivo
            <textarea
              value={objective}
              onChange={(e) => setObjective(e.target.value)}
              required
            />
          </label>
        </p>
        <p>
          <label>
            Instruções do pedido
            <textarea
              value={requestInstructions}
              onChange={(e) => setRequestInstructions(e.target.value)}
              required
            />
          </label>
        </p>
        <p>
          <label>
            Restrições (opcional)
            <textarea
              value={constraints}
              onChange={(e) => setConstraints(e.target.value)}
            />
          </label>
        </p>
        <p>
          <label>
            Formato esperado
            <input
              value={expectedOutputFormat}
              onChange={(e) => setExpectedOutputFormat(e.target.value)}
              required
            />
          </label>
        </p>
        <p>
          <label>
            Modo
            <select
              value={executionMode}
              onChange={(e) => setExecutionMode(e.target.value as ExecutionMode)}
            >
              {EXECUTION_MODES.map((m) => (
                <option key={m} value={m}>
                  {executionModeLabel(m)}
                </option>
              ))}
            </select>
          </label>
        </p>

        <fieldset>
          <legend>Função (apenas activas)</legend>
          {functionsLoaded && functions.length === 0 ? (
            <p role="note">
              Não há funções activas. Crie uma função na área <em>Funções</em>.
            </p>
          ) : (
            <label>
              Função
              <select
                value={functionId}
                onChange={(e) => setFunctionId(e.target.value)}
              >
                <option value="">— Escolher função —</option>
                {functions.map((f) => (
                  <option key={f.id} value={f.id}>
                    {f.name} · {actorTypeLabel(f.actor_type)}
                  </option>
                ))}
              </select>
            </label>
          )}
          {selectedFunction && (
            <div data-testid="selected-function-info">
              <p>{selectedFunction.purpose}</p>
              <p>
                Requer aprovação humana:{" "}
                <strong>{selectedFunction.requires_approval ? "Sim" : "Não"}</strong>
              </p>
            </div>
          )}
        </fieldset>

        <ContextDocumentSelector
          productId={productId}
          instructionDocumentId={selectedFunction?.instruction_document ?? null}
          value={context}
          onChange={setContext}
        />

        <p>
          <button type="submit" disabled={busy}>
            {busy ? "A preparar…" : "Preparar execução"}
          </button>{" "}
          <button type="button" onClick={onCancel} disabled={busy}>
            Cancelar
          </button>
        </p>
      </form>
    </section>
  );
}
