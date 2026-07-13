import { useState, type FormEvent } from "react";

import { ApiError } from "../../api/client";
import {
  createProduct,
  type Product,
  type ProductCreateInput,
} from "../../api/products";

interface Props {
  onCreated: (product: Product) => void;
  onCancel: () => void;
}

// Criação com esforço mínimo: só Nome e Propósito são exigidos visualmente. Os
// defaults (estado, responsável, data de revisão, versão) são aplicados pelo
// backend. Os opcionais ficam numa área claramente opcional e recolhida.
export function ProductCreateForm({ onCreated, onCancel }: Props) {
  const [name, setName] = useState("");
  const [purpose, setPurpose] = useState("");
  const [targetAudience, setTargetAudience] = useState("");
  const [phase, setPhase] = useState("");
  const [nextReviewAt, setNextReviewAt] = useState("");
  const [notes, setNotes] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (busy) return; // evita submissão duplicada
    setBusy(true);
    setError(null);

    const payload: ProductCreateInput = { name: name.trim(), purpose: purpose.trim() };
    if (targetAudience.trim()) payload.target_audience = targetAudience.trim();
    if (phase.trim()) payload.phase = phase.trim();
    if (nextReviewAt) payload.next_review_at = nextReviewAt;
    if (notes.trim()) payload.notes = notes.trim();

    try {
      const product = await createProduct(payload);
      onCreated(product);
    } catch (e: unknown) {
      setError(
        e instanceof ApiError && e.status === 400
          ? "Verifique o nome e o propósito."
          : "Não foi possível criar o produto.",
      );
      setBusy(false);
    }
  }

  return (
    <section aria-labelledby="product-create-title">
      <h3 id="product-create-title">Novo produto</h3>
      {error && <p role="alert">{error}</p>}
      <form onSubmit={handleSubmit}>
        <p>
          <label>
            Nome
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
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

        <details>
          <summary>Campos opcionais</summary>
          <p>
            <label>
              Público-alvo
              <input
                value={targetAudience}
                onChange={(e) => setTargetAudience(e.target.value)}
              />
            </label>
          </p>
          <p>
            <label>
              Fase
              <input value={phase} onChange={(e) => setPhase(e.target.value)} />
            </label>
          </p>
          <p>
            <label>
              Próxima revisão
              <input
                type="date"
                value={nextReviewAt}
                onChange={(e) => setNextReviewAt(e.target.value)}
              />
            </label>
          </p>
          <p>
            <label>
              Notas
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
              />
            </label>
          </p>
        </details>

        <button type="submit" disabled={busy}>
          {busy ? "A criar…" : "Criar produto"}
        </button>{" "}
        <button type="button" onClick={onCancel} disabled={busy}>
          Cancelar
        </button>
      </form>
    </section>
  );
}
