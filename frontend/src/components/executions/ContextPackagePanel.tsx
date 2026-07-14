import { useMemo, useState } from "react";

import { ApiError } from "../../api/client";
import {
  downloadContextPackage,
  previewContextPackage,
  type ContextPackageBlocked,
  type ContextPackageFormat,
  type ContextPackagePreview,
  type ExecutionDetail,
} from "../../api/executions";
import { documentTypeLabel } from "../documents/labels";
import { abbrevChecksum, exportPolicyLabel } from "./labels";

interface Props {
  execution: ExecutionDetail;
}

// Painel de preparação e handoff MANUAL do pacote de contexto. Não chama IA, não
// importa resultado, não altera o estado da execução. Só aparece em execuções
// `prepared`. As confirmações vivem apenas em memória (nunca localStorage) e são
// reavaliadas a cada geração; a análise de política é sempre a do servidor (a UI
// não confia apenas no estado local).
export function ContextPackagePanel({ execution }: Props) {
  const [format, setFormat] = useState<ContextPackageFormat>("single_markdown");
  const [confirmed, setConfirmed] = useState<Set<string>>(new Set());
  const [blocked, setBlocked] = useState<ContextPackageBlocked | null>(null);
  const [preview, setPreview] = useState<ContextPackagePreview | null>(null);
  const [copied, setCopied] = useState(false);
  const [downloaded, setDownloaded] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [showConfirmAll, setShowConfirmAll] = useState(false);
  const [destination, setDestination] = useState("");

  const isExternal = execution.execution_mode === "manual_external";

  const deniedIds = useMemo(
    () => new Set(blocked?.denied_document_ids ?? []),
    [blocked],
  );
  const needConfirmIds = useMemo(
    () => new Set(blocked?.confirmation_required_document_ids ?? []),
    [blocked],
  );
  const contextDocIds = useMemo(
    () => new Set(execution.context_documents.map((d) => d.document)),
    [execution],
  );

  // Documentos de instruções da função sinalizados pela análise do backend (não
  // constam da lista de contexto). Aparecem na mesma análise de políticas.
  const extraDenied = [...deniedIds].filter((id) => !contextDocIds.has(id));
  const extraConfirm = [...needConfirmIds].filter(
    (id) => !contextDocIds.has(id),
  );

  // Conjunto de documentos que exigem confirmação (base `confirm` + os que o
  // servidor sinalizou). Usado por "Confirmar todos".
  const confirmDocIds = useMemo(() => {
    const ids = new Set<string>();
    for (const d of execution.context_documents) {
      if (d.export_policy === "confirm") ids.add(d.document);
    }
    for (const id of extraConfirm) ids.add(id);
    return ids;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [execution, blocked]);

  function toggle(id: string, on: boolean) {
    setConfirmed((prev) => {
      const next = new Set(prev);
      if (on) next.add(id);
      else next.delete(id);
      return next;
    });
  }

  function confirmAll() {
    setConfirmed((prev) => {
      const next = new Set(prev);
      for (const id of confirmDocIds) next.add(id);
      return next;
    });
    setShowConfirmAll(false);
  }

  async function handleGenerate() {
    if (busy) return;
    setBusy(true);
    setError(null);
    setCopied(false);
    setDownloaded(false);
    try {
      const outcome = await previewContextPackage(execution.id, {
        format,
        confirmed_document_ids: [...confirmed],
        operation: "preview",
      });
      if (outcome.kind === "ok") {
        setPreview(outcome.preview);
        setBlocked(null);
      } else if (outcome.kind === "blocked") {
        setPreview(null);
        setBlocked(outcome.blocked);
      } else if (outcome.kind === "too_large") {
        setPreview(null);
        setError("O pacote excede o limite permitido.");
      } else {
        setError("Não foi possível gerar o pacote.");
      }
    } catch {
      setError("Falha de comunicação com o servidor.");
    } finally {
      setBusy(false);
    }
  }

  async function handleCopy() {
    if (busy) return;
    setBusy(true);
    setError(null);
    setCopied(false);
    try {
      // Reavalia no servidor e regista a cópia (operation=copy); nunca confia só
      // no conteúdo local.
      const outcome = await previewContextPackage(execution.id, {
        format: "single_markdown",
        confirmed_document_ids: [...confirmed],
        operation: "copy",
      });
      if (outcome.kind !== "ok" || !outcome.preview.content) {
        if (outcome.kind === "blocked") setBlocked(outcome.blocked);
        setPreview(outcome.kind === "ok" ? outcome.preview : null);
        setError("A geração foi bloqueada; reveja a análise de política.");
        return;
      }
      setPreview(outcome.preview);
      setBlocked(null);
      try {
        await navigator.clipboard.writeText(outcome.preview.content);
        setCopied(true);
      } catch {
        setError(
          "Não foi possível copiar automaticamente. Copie manualmente o texto apresentado.",
        );
      }
    } catch {
      setError("Falha de comunicação com o servidor.");
    } finally {
      setBusy(false);
    }
  }

  async function handleDownload() {
    if (busy) return;
    setBusy(true);
    setError(null);
    setCopied(false);
    try {
      const { blob, filename } = await downloadContextPackage(execution.id, {
        format,
        confirmed_document_ids: [...confirmed],
        destination_label: destination.trim() || undefined,
      });
      // Descarga sem biblioteca externa; revoga a URL temporária.
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = filename;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      URL.revokeObjectURL(url);
      setDownloaded(true);
    } catch (e: unknown) {
      if (e instanceof ApiError && e.status === 409) {
        // A política mudou entretanto: reavalia a análise (fonte no servidor).
        await handleGenerate();
        setError(
          "A política de exportação mudou; reveja a análise antes de descarregar.",
        );
      } else {
        setError("Não foi possível descarregar o pacote.");
      }
    } finally {
      setBusy(false);
    }
  }

  return (
    <section aria-labelledby="context-package-title" data-testid="context-package-panel">
      <h5 id="context-package-title">Pacote de contexto (handoff manual)</h5>

      <p role="note">
        Ao gerar o pacote, o conteúdo poderá <strong>sair da aplicação</strong> para
        uso manual numa IA. Nenhum envio é automático.
      </p>
      {isExternal ? (
        <p role="note" data-testid="mode-warning-external">
          Modo <strong>manual externo</strong>: irá partilhar este conteúdo com um
          serviço externo. Confirme que não inclui dados sensíveis.
        </p>
      ) : (
        <p role="note" data-testid="mode-warning-local">
          Modo <strong>manual local</strong>: o pacote deve permanecer no ambiente
          autorizado; não o envie para serviços externos.
        </p>
      )}

      <div role="group" aria-label="Formato do pacote">
        <label>
          Formato
          <select
            value={format}
            onChange={(e) => {
              setFormat(e.target.value as ContextPackageFormat);
              setPreview(null);
              setCopied(false);
            }}
          >
            <option value="single_markdown">Markdown único (.md)</option>
            <option value="separate_files">Ficheiros separados (.zip)</option>
          </select>
        </label>{" "}
        <label>
          Destino (opcional)
          <input
            value={destination}
            onChange={(e) => setDestination(e.target.value)}
            placeholder="ex.: ferramenta/modelo"
          />
        </label>
      </div>

      {error && <p role="alert">{error}</p>}

      {/* Análise de política por documento (contexto + instruções). */}
      <fieldset>
        <legend>Análise de política de exportação</legend>
        <ul data-testid="policy-analysis">
          {execution.context_documents.map((doc) => {
            const isDenied =
              deniedIds.has(doc.document) || doc.export_policy === "denied";
            const isConfirm =
              !isDenied &&
              (doc.export_policy === "confirm" ||
                needConfirmIds.has(doc.document));
            return (
              <li key={doc.document} data-testid={`policy-${doc.document}`}>
                <strong>{doc.title}</strong>{" "}
                <span>({documentTypeLabel(doc.document_type)})</span> —{" "}
                <span>{exportPolicyLabel(doc.export_policy)}</span>
                {doc.is_outdated && (
                  <span data-testid="outdated-warning">
                    {" "}
                    · desactualizado (aviso)
                  </span>
                )}
                {isDenied && (
                  <span data-testid="denied-blocked">
                    {" "}
                    · <strong>Bloqueado</strong> — exportação recusada (sem
                    contorno).
                  </span>
                )}
                {isConfirm && (
                  <label data-testid="confirm-checkbox">
                    {" "}
                    <input
                      type="checkbox"
                      checked={confirmed.has(doc.document)}
                      onChange={(e) => toggle(doc.document, e.target.checked)}
                    />
                    Confirmo a inclusão deste documento
                  </label>
                )}
              </li>
            );
          })}

          {/* Documento de instruções da função sinalizado pela análise. */}
          {execution.instruction_version && extraDenied.length === 0 &&
            extraConfirm.length === 0 && (
              <li data-testid="instruction-policy">
                Documento de instruções da função: incluído.
              </li>
            )}
          {extraDenied.map((id) => (
            <li key={id} data-testid="instruction-policy">
              Documento de instruções da função —{" "}
              <span data-testid="denied-blocked">
                <strong>Bloqueado</strong> (denied).
              </span>
            </li>
          ))}
          {extraConfirm.map((id) => (
            <li key={id} data-testid="instruction-policy">
              Documento de instruções da função —{" "}
              <label data-testid="confirm-checkbox">
                <input
                  type="checkbox"
                  checked={confirmed.has(id)}
                  onChange={(e) => toggle(id, e.target.checked)}
                />
                Confirmo a inclusão das instruções
              </label>
            </li>
          ))}
        </ul>

        {confirmDocIds.size > 0 && (
          <div>
            {showConfirmAll ? (
              <div role="group" aria-label="Confirmar todos">
                <p>
                  Vai confirmar a inclusão de{" "}
                  <strong>{confirmDocIds.size}</strong> documento(s) que exigem
                  confirmação. Esta acção é deliberada.
                </p>
                <button type="button" onClick={confirmAll} disabled={busy}>
                  Confirmar inclusão de todos
                </button>{" "}
                <button
                  type="button"
                  onClick={() => setShowConfirmAll(false)}
                  disabled={busy}
                >
                  Cancelar
                </button>
              </div>
            ) : (
              <button
                type="button"
                onClick={() => setShowConfirmAll(true)}
                disabled={busy}
              >
                Confirmar todos…
              </button>
            )}
          </div>
        )}
      </fieldset>

      {blocked && (
        <p role="alert" data-testid="blocked-reason">
          {blocked.reason === "denied"
            ? "Geração bloqueada: há documentos com exportação recusada (denied)."
            : "Geração bloqueada: há documentos que exigem confirmação explícita."}
        </p>
      )}

      <p>
        <button type="button" onClick={handleGenerate} disabled={busy}>
          {busy ? "A processar…" : "Gerar pré-visualização"}
        </button>
      </p>

      {preview && (
        <PackagePreviewView
          preview={preview}
          format={format}
          copied={copied}
          downloaded={downloaded}
          busy={busy}
          onCopy={handleCopy}
          onDownload={handleDownload}
        />
      )}
    </section>
  );
}

function PackagePreviewView({
  preview,
  format,
  copied,
  downloaded,
  busy,
  onCopy,
  onDownload,
}: {
  preview: ContextPackagePreview;
  format: ContextPackageFormat;
  copied: boolean;
  downloaded: boolean;
  busy: boolean;
  onCopy: () => void;
  onDownload: () => void;
}) {
  return (
    <section aria-labelledby="package-preview-title" data-testid="package-preview">
      <h6 id="package-preview-title">Pré-visualização</h6>

      <p>
        Checksum (SHA-256):{" "}
        <code data-testid="package-checksum">{preview.checksum}</code>
      </p>

      {preview.warnings.length > 0 && (
        <ul data-testid="package-warnings" role="note">
          {preview.warnings.map((w, i) => (
            <li key={i}>{w}</li>
          ))}
        </ul>
      )}

      {/* Manifesto: apenas identificadores e versões (sem comparar documentos). */}
      <details data-testid="package-manifest">
        <summary>Manifesto ({preview.manifest.sections.length} secções)</summary>
        <ol>
          {preview.manifest.documents.map((d) => (
            <li key={d.document_version}>
              #{d.order} — {d.title} · v{d.version_number} ·{" "}
              {abbrevChecksum(d.checksum)} · {d.export_policy}
            </li>
          ))}
        </ol>
      </details>

      {format === "single_markdown" && preview.content !== undefined && (
        <>
          {/* Conteúdo como TEXTO não executável — nunca dangerouslySetInnerHTML. */}
          <pre data-testid="package-content" style={{ whiteSpace: "pre-wrap" }}>
            {preview.content}
          </pre>
          <p>
            <button type="button" onClick={onCopy} disabled={busy}>
              Copiar Markdown
            </button>{" "}
            <button type="button" onClick={onDownload} disabled={busy}>
              Descarregar .md
            </button>{" "}
            {copied && <span role="status">Copiado para a área de transferência.</span>}
          </p>
        </>
      )}

      {format === "separate_files" && (
        <>
          <p>Ficheiros do pacote (ZIP):</p>
          <ul data-testid="package-files">
            {(preview.files ?? []).map((name) => (
              <li key={name}>{name}</li>
            ))}
          </ul>
          <p>
            <button type="button" onClick={onDownload} disabled={busy}>
              Descarregar .zip
            </button>
          </p>
        </>
      )}
      {downloaded && <p role="status">Descarga iniciada.</p>}
    </section>
  );
}
