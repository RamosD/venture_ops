import { useEffect, useState } from "react";

import { getResultAttempt, type ResultAttemptDetail } from "../../api/executions";
import { DocumentPreview } from "../documents/DocumentPreview";
import { abbrevChecksum, sourceModeLabel } from "./labels";

interface Props {
  executionId: string;
  attemptNumber: number;
  isCurrent: boolean;
  onBack: () => void;
}

function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleString("pt-PT");
  } catch {
    return iso;
  }
}

// Vista (só leitura) de uma tentativa de resultado. Carrega o conteúdo da versão
// EXACTA da tentativa (o backend nunca usa `current_version` para substituir). Duas
// vistas: texto original (não executável) e pré-visualização SEGURA (HTML
// sanitizado devolvido pelo backend). Sem editar, eliminar, recuperar, aprovar ou
// aplicar.
export function ResultAttemptView({
  executionId,
  attemptNumber,
  isCurrent,
  onBack,
}: Props) {
  const [detail, setDetail] = useState<ResultAttemptDetail | null>(null);
  const [state, setState] = useState<"loading" | "ready" | "error">("loading");
  const [view, setView] = useState<"text" | "preview">("text");

  useEffect(() => {
    let cancelled = false;
    setState("loading");
    getResultAttempt(executionId, attemptNumber)
      .then((res) => {
        if (cancelled) return;
        setDetail(res);
        setState("ready");
      })
      .catch(() => {
        if (!cancelled) setState("error");
      });
    return () => {
      cancelled = true;
    };
  }, [executionId, attemptNumber]);

  return (
    <section aria-labelledby="attempt-view-title" data-testid="result-attempt-view">
      <h6 id="attempt-view-title">
        Tentativa {attemptNumber}
        {isCurrent && <span data-testid="attempt-current"> (actual)</span>}
      </h6>

      {state === "loading" && <p role="status">A carregar tentativa…</p>}
      {state === "error" && (
        <p role="alert">Não foi possível carregar a tentativa.</p>
      )}

      {state === "ready" && detail && (
        <>
          <dl>
            <dt>Origem (ferramenta)</dt>
            <dd>{detail.source_tool}</dd>
            {detail.source_model && (
              <>
                <dt>Modelo</dt>
                <dd>{detail.source_model}</dd>
              </>
            )}
            <dt>Modo</dt>
            <dd>{sourceModeLabel(detail.source_mode)}</dd>
            <dt>Versão documental</dt>
            <dd>
              v{detail.version_number} · {abbrevChecksum(detail.checksum)} ·{" "}
              {detail.byte_size} bytes
            </dd>
            <dt>Importado em</dt>
            <dd>{formatDate(detail.created_at)}</dd>
            {detail.source_notes && (
              <>
                <dt>Notas</dt>
                <dd>{detail.source_notes}</dd>
              </>
            )}
          </dl>

          <p role="note">
            <small>
              Conteúdo importado — <strong>não confiável</strong> e{" "}
              <strong>não oficial</strong>. Ainda não foi revisto nem aplicado.
            </small>
          </p>

          <div role="group" aria-label="Vista do resultado">
            <button
              type="button"
              onClick={() => setView("text")}
              disabled={view === "text"}
            >
              Texto original
            </button>{" "}
            <button
              type="button"
              onClick={() => setView("preview")}
              disabled={view === "preview"}
            >
              Pré-visualização segura
            </button>
          </div>

          {view === "text" ? (
            // Texto como TEXTO não executável (nunca renderizado como HTML).
            <pre data-testid="attempt-text" style={{ whiteSpace: "pre-wrap" }}>
              {detail.content}
            </pre>
          ) : (
            // Pré-visualização: só o HTML sanitizado do backend é inserido.
            <div data-testid="attempt-preview">
              <DocumentPreview content={detail.content} />
            </div>
          )}
        </>
      )}

      <p>
        <button type="button" onClick={onBack}>
          Fechar tentativa
        </button>
      </p>
    </section>
  );
}
