import { useCallback, useEffect, useState } from "react";

import { ApiError } from "../../api/client";
import {
  getVersion,
  listVersions,
  restoreVersion,
  type DocumentDetail,
  type DocumentVersionDetail,
  type DocumentVersionSummary,
} from "../../api/documents";
import { formatDate } from "../portfolio/format";

interface Props {
  document: DocumentDetail;
  onRestored: (document: DocumentDetail) => void;
  onBack: () => void;
}

// Histórico de versões: número, autor, data e checksum abreviado/resumo seguro.
// Permite abrir o conteúdo de uma versão exacta e recuperar uma versão anterior.
// A recuperação é explicada como criação de uma NOVA versão (nunca eliminação do
// histórico) e exige confirmação explícita.
export function DocumentHistory({ document, onRestored, onBack }: Props) {
  const [versions, setVersions] = useState<DocumentVersionSummary[]>([]);
  const [state, setState] = useState<"loading" | "ready" | "error">("loading");
  const [opened, setOpened] = useState<DocumentVersionDetail | null>(null);
  const [confirming, setConfirming] = useState<number | null>(null);
  const [expectedVersion, setExpectedVersion] = useState(document.version);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setState("loading");
    try {
      const response = await listVersions(document.id);
      setVersions(response.results);
      setState("ready");
    } catch {
      setState("error");
    }
  }, [document.id]);

  useEffect(() => {
    void load();
  }, [load]);

  async function openVersion(versionNumber: number) {
    if (busy) return;
    setBusy(true);
    setError(null);
    try {
      const detail = await getVersion(document.id, versionNumber);
      setOpened(detail);
    } catch {
      setError("Não foi possível abrir a versão.");
    } finally {
      setBusy(false);
    }
  }

  async function confirmRestore(versionNumber: number) {
    if (busy) return;
    setBusy(true);
    setError(null);
    try {
      const updated = await restoreVersion(
        document.id,
        versionNumber,
        expectedVersion,
      );
      setConfirming(null);
      onRestored(updated); // a versão actual passa a ser a nova versão criada
    } catch (e: unknown) {
      if (e instanceof ApiError && e.status === 409) {
        setError(
          "O documento foi alterado entretanto. Recarregue o histórico e tente novamente.",
        );
        setExpectedVersion((v) => v); // mantém; o utilizador recarrega
        void load();
      } else {
        setError("Não foi possível recuperar a versão.");
      }
      setBusy(false);
    }
  }

  return (
    <section aria-labelledby="document-history-title">
      <h4 id="document-history-title">Histórico de versões</h4>
      <p>
        Recuperar uma versão <strong>cria uma nova versão</strong> com o
        conteúdo dessa versão anterior. O histórico é preservado — nada é
        eliminado.
      </p>
      {error && <p role="alert">{error}</p>}

      {state === "loading" && <p role="status">A carregar histórico…</p>}
      {state === "error" && (
        <p role="alert">
          Não foi possível carregar o histórico.{" "}
          <button type="button" onClick={() => void load()}>
            Tentar novamente
          </button>
        </p>
      )}
      {state === "ready" && (
        <table>
          <thead>
            <tr>
              <th scope="col">Versão</th>
              <th scope="col">Autor</th>
              <th scope="col">Data</th>
              <th scope="col">Integridade</th>
              <th scope="col">Resumo</th>
              <th scope="col">Acções</th>
            </tr>
          </thead>
          <tbody>
            {versions.map((v) => (
              <tr key={v.version_number}>
                <td>{v.version_number}</td>
                <td>{v.author}</td>
                <td>{formatDate(v.created_at)}</td>
                <td>
                  <code>{v.checksum.slice(0, 12)}</code>
                </td>
                <td>{v.change_summary || "—"}</td>
                <td>
                  <button
                    type="button"
                    onClick={() => void openVersion(v.version_number)}
                    disabled={busy}
                  >
                    Abrir
                  </button>{" "}
                  {confirming === v.version_number ? (
                    <span role="group" aria-label="Confirmar recuperação">
                      <span>
                        Recuperar a versão {v.version_number} cria uma nova
                        versão actual. Confirma?
                      </span>{" "}
                      <button
                        type="button"
                        onClick={() => void confirmRestore(v.version_number)}
                        disabled={busy}
                      >
                        Confirmar recuperação
                      </button>{" "}
                      <button
                        type="button"
                        onClick={() => setConfirming(null)}
                        disabled={busy}
                      >
                        Cancelar
                      </button>
                    </span>
                  ) : (
                    <button
                      type="button"
                      onClick={() => setConfirming(v.version_number)}
                      disabled={busy}
                    >
                      Recuperar
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {opened && (
        <section aria-labelledby="opened-version-title">
          <h5 id="opened-version-title">
            Conteúdo da versão {opened.version_number}
          </h5>
          <pre>{opened.content}</pre>
          <button type="button" onClick={() => setOpened(null)}>
            Fechar versão
          </button>
        </section>
      )}

      <p>
        <button type="button" onClick={onBack} disabled={busy}>
          Voltar ao documento
        </button>
      </p>
    </section>
  );
}
