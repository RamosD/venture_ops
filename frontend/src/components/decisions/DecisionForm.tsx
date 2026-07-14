import { useEffect, useState, type FormEvent } from "react";

import { ApiError } from "../../api/client";
import {
  createDecision,
  supersedeDecision,
  type Decision,
  type DecisionCreateInput,
} from "../../api/decisions";
import { listDocuments, type DocumentSummary } from "../../api/documents";

interface Props {
  productId: string;
  // Quando presente, o formulário substitui a decisão anterior (cria nova active).
  supersedes?: Decision;
  onDone: (decision: Decision) => void;
  onCancel: () => void;
}

// Formulário de decisão, usado para criar e para substituir. Na substituição,
// explica que se cria uma NOVA decisão activa e a anterior fica substituída
// (nunca apaga o histórico). Product deriva da ficha; empresa nunca é escolhida.
export function DecisionForm({ productId, supersedes, onDone, onCancel }: Props) {
  const isSupersede = supersedes !== undefined;
  const [title, setTitle] = useState(isSupersede ? supersedes!.title : "");
  const [context, setContext] = useState("");
  const [decisionText, setDecisionText] = useState("");
  const [impact, setImpact] = useState("");
  const [detailDocument, setDetailDocument] = useState("");
  const [docOptions, setDocOptions] = useState<DocumentSummary[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [conflict, setConflict] = useState(false);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    let cancelled = false;
    // Documentos de detalhe elegíveis: tipo `decisao_detalhada` deste produto.
    listDocuments({ product: productId, document_type: "decisao_detalhada" })
      .then((res) => {
        if (!cancelled) setDocOptions(res.results);
      })
      .catch(() => {
        /* opcional: sem documentos elegíveis, o campo fica vazio */
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

    const payload: DecisionCreateInput = {
      title: title.trim(),
      context: context.trim(),
      decision_text: decisionText.trim(),
      product: productId,
    };
    if (impact.trim()) payload.impact = impact.trim();
    if (detailDocument) payload.detail_document = detailDocument;

    try {
      const result = isSupersede
        ? await supersedeDecision(supersedes!.id, {
            ...payload,
            expected_version: supersedes!.version,
          })
        : await createDecision(payload);
      onDone(result);
    } catch (e: unknown) {
      if (e instanceof ApiError && e.status === 409) {
        setConflict(true);
      } else if (e instanceof ApiError && e.status === 400) {
        setError("Verifique os campos e as associações.");
      } else {
        setError("Não foi possível guardar a decisão.");
      }
      setBusy(false);
    }
  }

  return (
    <section aria-labelledby="decision-form-title">
      <h4 id="decision-form-title">
        {isSupersede ? "Substituir decisão" : "Nova decisão"}
      </h4>
      {isSupersede && (
        <p role="note">
          Vai criar uma <strong>nova decisão activa</strong>. A decisão anterior
          fica <strong>substituída</strong> e é preservada no histórico (não é
          apagada nem reescrita).
        </p>
      )}
      {conflict && (
        <div role="alert">
          <p>
            A decisão foi alterada por outra operação (por exemplo, já
            substituída). Os seus dados não foram sobrescritos.
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
            Contexto
            <textarea
              value={context}
              onChange={(e) => setContext(e.target.value)}
              required
            />
          </label>
        </p>
        <p>
          <label>
            Decisão
            <textarea
              value={decisionText}
              onChange={(e) => setDecisionText(e.target.value)}
              required
            />
          </label>
        </p>
        <p>
          <label>
            Impacto (opcional)
            <textarea value={impact} onChange={(e) => setImpact(e.target.value)} />
          </label>
        </p>
        <p>
          <label>
            Documento de detalhe (opcional)
            <select
              value={detailDocument}
              onChange={(e) => setDetailDocument(e.target.value)}
            >
              <option value="">— Nenhum —</option>
              {docOptions.map((doc) => (
                <option key={doc.id} value={doc.id}>
                  {doc.title}
                </option>
              ))}
            </select>
          </label>
        </p>
        <p>
          <button type="submit" disabled={busy}>
            {busy
              ? "A guardar…"
              : isSupersede
                ? "Confirmar substituição"
                : "Criar decisão"}
          </button>{" "}
          <button type="button" onClick={onCancel} disabled={busy}>
            Cancelar
          </button>
        </p>
      </form>
    </section>
  );
}
