import { useState, type FormEvent } from "react";

import {
  importResult,
  type ExecutionDetail,
  type ImportedExecutionState,
  type ResultAttempt,
} from "../../api/executions";

interface Props {
  execution: ExecutionDetail;
  onImported: (attempt: ResultAttempt, execution: ImportedExecutionState) => void;
  onConflict: (detail: string) => void;
}

type Mode = "paste" | "file";

// Limite informativo (autoridade é o servidor, que devolve 413 se excedido).
const LIMIT_HINT = "até ~25 MB";
const ACCEPT = ".md,.markdown,.txt,text/markdown,text/plain";

// Importação manual de um resultado externo. Escolha explícita entre colar texto
// e carregar ficheiro (nunca ambos). Confirmação explica importar ≠ aprovar ≠
// aplicar e que a tentativa fica imutável. Evita submissão duplicada.
export function ResultImportForm({ execution, onImported, onConflict }: Props) {
  const [mode, setMode] = useState<Mode>("paste");
  const [content, setContent] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [sourceTool, setSourceTool] = useState("");
  const [sourceModel, setSourceModel] = useState("");
  const [sourceNotes, setSourceNotes] = useState("");
  const [confirming, setConfirming] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function validate(): string | null {
    if (!sourceTool.trim()) return "Indique a ferramenta de origem (obrigatória).";
    if (mode === "paste" && content.trim() === "") return "Cole o resultado.";
    if (mode === "file" && file === null) return "Escolha um ficheiro.";
    return null;
  }

  function requestConfirm(event: FormEvent) {
    event.preventDefault();
    const err = validate();
    if (err) {
      setError(err);
      return;
    }
    setError(null);
    setConfirming(true);
  }

  async function doImport() {
    if (busy) return; // evita submissão duplicada
    setBusy(true);
    setError(null);
    try {
      const outcome = await importResult(execution.id, {
        expected_version: execution.version,
        source_tool: sourceTool.trim(),
        source_model: sourceModel.trim() || undefined,
        source_notes: sourceNotes.trim() || undefined,
        // Só a origem do modo activo é enviada — nunca content e file juntos.
        content: mode === "paste" ? content : undefined,
        file: mode === "file" ? file ?? undefined : undefined,
      });
      if (outcome.kind === "ok") {
        onImported(outcome.attempt, outcome.execution);
        return; // o painel assume a partir daqui
      }
      if (outcome.kind === "conflict") {
        setConfirming(false);
        onConflict(outcome.detail); // recarrega a execução; conteúdo preservado
      } else if (outcome.kind === "too_large") {
        setError("O resultado excede o limite permitido (erro 413).");
        setConfirming(false);
      } else if (outcome.kind === "invalid") {
        setError(outcome.detail);
        setConfirming(false);
      } else {
        setError("Não foi possível importar o resultado.");
        setConfirming(false);
      }
    } catch {
      setError("Falha de comunicação com o servidor.");
      setConfirming(false);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section aria-labelledby="result-import-title" data-testid="result-import-form">
      <h6 id="result-import-title">Importar resultado</h6>
      {error && <p role="alert">{error}</p>}

      {confirming ? (
        <div role="group" aria-label="Confirmar importação" data-testid="import-confirm">
          <p>Confirma a importação deste resultado? Ao importar:</p>
          <ul>
            <li>regista-se uma <strong>tentativa</strong> imutável;</li>
            <li>
              <strong>não</strong> aprova o resultado;
            </li>
            <li>
              <strong>não</strong> aplica quaisquer alterações;
            </li>
            <li>a tentativa fica <strong>imutável</strong> após a criação.</li>
          </ul>
          <button type="button" onClick={doImport} disabled={busy}>
            {busy ? "A importar…" : "Confirmar importação"}
          </button>{" "}
          <button
            type="button"
            onClick={() => setConfirming(false)}
            disabled={busy}
          >
            Cancelar
          </button>
        </div>
      ) : (
        <form onSubmit={requestConfirm}>
          <div role="radiogroup" aria-label="Origem do resultado">
            <label>
              <input
                type="radio"
                name="import-mode"
                checked={mode === "paste"}
                onChange={() => setMode("paste")}
              />
              Colar resultado
            </label>{" "}
            <label>
              <input
                type="radio"
                name="import-mode"
                checked={mode === "file"}
                onChange={() => setMode("file")}
              />
              Carregar ficheiro
            </label>
          </div>

          {mode === "paste" ? (
            <p>
              <label>
                Resultado (Markdown/texto)
                <textarea
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  rows={6}
                />
              </label>
            </p>
          ) : (
            <p>
              <label>
                Ficheiro (Markdown/texto)
                <input
                  type="file"
                  accept={ACCEPT}
                  onChange={(e) => setFile(e.target.files?.[0] ?? null)}
                />
              </label>
              {file && (
                <span data-testid="file-name"> — {file.name}</span>
              )}
            </p>
          )}

          <p>
            <small>Limite de tamanho: {LIMIT_HINT} (validado no servidor).</small>
          </p>

          <p>
            <label>
              Ferramenta de origem (obrigatória)
              <input
                value={sourceTool}
                onChange={(e) => setSourceTool(e.target.value)}
              />
            </label>
          </p>
          <p>
            <label>
              Modelo (opcional)
              <input
                value={sourceModel}
                onChange={(e) => setSourceModel(e.target.value)}
              />
            </label>
          </p>
          <p>
            <label>
              Notas de origem (opcional)
              <input
                value={sourceNotes}
                onChange={(e) => setSourceNotes(e.target.value)}
              />
            </label>
          </p>

          <button type="submit">Importar…</button>
        </form>
      )}
    </section>
  );
}
