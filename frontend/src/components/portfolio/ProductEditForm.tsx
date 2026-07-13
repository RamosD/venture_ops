import { useState, type FormEvent } from "react";

import { ApiError } from "../../api/client";
import {
  getProduct,
  updateProduct,
  type Product,
  type ProductUpdateInput,
} from "../../api/products";

interface Props {
  product: Product;
  onSaved: (product: Product) => void;
  onCancel: () => void;
}

// Edição comum da ficha. Envia sempre a `version` actual (concorrência
// optimista). Um 409 é tratado como conflito: nunca sobrescreve silenciosamente o
// servidor — informa e oferece recarregar os dados actuais.
export function ProductEditForm({ product, onSaved, onCancel }: Props) {
  const [current, setCurrent] = useState<Product>(product);
  const [name, setName] = useState(product.name);
  const [purpose, setPurpose] = useState(product.purpose);
  const [targetAudience, setTargetAudience] = useState(product.target_audience);
  const [phase, setPhase] = useState(product.phase);
  const [nextReviewAt, setNextReviewAt] = useState(
    product.next_review_at ? product.next_review_at.slice(0, 10) : "",
  );
  const [notes, setNotes] = useState(product.notes);
  const [error, setError] = useState<string | null>(null);
  const [conflict, setConflict] = useState(false);
  const [busy, setBusy] = useState(false);

  function resetTo(next: Product) {
    setCurrent(next);
    setName(next.name);
    setPurpose(next.purpose);
    setTargetAudience(next.target_audience);
    setPhase(next.phase);
    setNextReviewAt(next.next_review_at ? next.next_review_at.slice(0, 10) : "");
    setNotes(next.notes);
  }

  async function handleReload() {
    if (busy) return;
    setBusy(true);
    setError(null);
    try {
      const fresh = await getProduct(current.id);
      resetTo(fresh);
      setConflict(false);
    } catch {
      setError("Não foi possível recarregar o produto.");
    } finally {
      setBusy(false);
    }
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (busy) return; // evita submissão duplicada
    setBusy(true);
    setError(null);
    setConflict(false);

    const payload: ProductUpdateInput = {
      expected_version: current.version,
      name: name.trim(),
      purpose: purpose.trim(),
      target_audience: targetAudience.trim(),
      phase: phase.trim(),
      next_review_at: nextReviewAt ? nextReviewAt : null,
      notes: notes.trim(),
    };

    try {
      const updated = await updateProduct(current.id, payload);
      onSaved(updated);
    } catch (e: unknown) {
      if (e instanceof ApiError && e.status === 409) {
        setConflict(true);
      } else {
        setError("Não foi possível guardar as alterações.");
      }
      setBusy(false);
    }
  }

  return (
    <section aria-labelledby="product-edit-title">
      <h3 id="product-edit-title">Editar ficha</h3>
      {conflict && (
        <div role="alert">
          <p>
            O produto foi alterado por outra operação. Os seus dados não foram
            sobrescritos.
          </p>
          <button type="button" onClick={handleReload} disabled={busy}>
            Recarregar dados
          </button>
        </div>
      )}
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
            <textarea value={notes} onChange={(e) => setNotes(e.target.value)} />
          </label>
        </p>
        <button type="submit" disabled={busy}>
          {busy ? "A guardar…" : "Guardar alterações"}
        </button>{" "}
        <button type="button" onClick={onCancel} disabled={busy}>
          Cancelar
        </button>
      </form>
    </section>
  );
}
