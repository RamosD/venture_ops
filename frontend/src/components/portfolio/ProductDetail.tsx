import { useState } from "react";

import { ApiError } from "../../api/client";
import {
  archiveProduct,
  getProduct,
  markReviewed,
  reactivateProduct,
  type Product,
} from "../../api/products";
import { DecisionSection } from "../decisions/DecisionSection";
import { DocumentSection } from "../documents/DocumentSection";
import { ExecutionSection } from "../executions/ExecutionSection";
import { WorkItemSection } from "../workitems/WorkItemSection";
import { formatDate, responsibleLabel, statusLabel } from "./format";

interface Props {
  product: Product;
  currentUser: { id: string; email: string } | null;
  onEdit: (product: Product) => void;
  onBack: () => void;
  onChanged: () => void;
}

// Ficha de visão geral. Só leitura para os campos; as alterações de estado e a
// revisão são acções explícitas e separadas da edição. Vistas agregadas
// (documentos, decisões, pendências, execuções) e nível de atenção NÃO são
// apresentados — apenas se reserva uma área com aviso claro de ausência.
export function ProductDetail({
  product: initial,
  currentUser,
  onEdit,
  onBack,
  onChanged,
}: Props) {
  const [product, setProduct] = useState<Product>(initial);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conflict, setConflict] = useState(false);
  const [confirming, setConfirming] = useState<null | "archive" | "review">(null);

  const isArchived = product.status === "archived";

  async function run(
    operation: (id: string, version: number) => Promise<Product>,
  ) {
    if (busy) return;
    setBusy(true);
    setError(null);
    setConflict(false);
    setConfirming(null);
    try {
      const updated = await operation(product.id, product.version);
      setProduct(updated);
      onChanged(); // actualiza a lista em segundo plano
    } catch (e: unknown) {
      if (e instanceof ApiError && e.status === 409) {
        setConflict(true);
      } else {
        setError("Não foi possível concluir a operação.");
      }
    } finally {
      setBusy(false);
    }
  }

  async function handleReload() {
    if (busy) return;
    setBusy(true);
    setError(null);
    try {
      const fresh = await getProduct(product.id);
      setProduct(fresh);
      setConflict(false);
      onChanged();
    } catch {
      setError("Não foi possível recarregar o produto.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section aria-labelledby="product-detail-title">
      <h3 id="product-detail-title">{product.name}</h3>

      {isArchived && (
        <p role="status">
          <strong>Produto arquivado.</strong> A edição normal está indisponível;
          reactive-o para voltar a editar.
        </p>
      )}
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

      <dl>
        <dt>Propósito</dt>
        <dd>{product.purpose}</dd>
        <dt>Estado</dt>
        <dd>{statusLabel(product.status)}</dd>
        <dt>Responsável</dt>
        <dd>{responsibleLabel(product, currentUser)}</dd>
        <dt>Última revisão</dt>
        <dd>{formatDate(product.last_reviewed_at)}</dd>
        <dt>Público-alvo</dt>
        <dd>{product.target_audience || "—"}</dd>
        <dt>Fase</dt>
        <dd>{product.phase || "—"}</dd>
        <dt>Próxima revisão</dt>
        <dd>{formatDate(product.next_review_at)}</dd>
        <dt>Notas</dt>
        <dd>{product.notes || "—"}</dd>
      </dl>
      <p>
        <small>Versão {product.version} (controlo técnico)</small>
      </p>

      {/* Acções: editar/revisão só quando active; reactivar quando archived. */}
      <div>
        {!isArchived && (
          <>
            <button
              type="button"
              onClick={() => onEdit(product)}
              disabled={busy}
            >
              Editar
            </button>{" "}
            {confirming === "review" ? (
              <span role="group" aria-label="Confirmar revisão">
                <span>
                  Confirma que reviu realmente esta ficha? Isto actualiza a data
                  de última revisão (não é o mesmo que guardar uma edição).
                </span>{" "}
                <button
                  type="button"
                  onClick={() => void run(markReviewed)}
                  disabled={busy}
                >
                  Confirmar revisão
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
                onClick={() => setConfirming("review")}
                disabled={busy}
              >
                Marcar como revisto
              </button>
            )}{" "}
            {confirming === "archive" ? (
              <span role="group" aria-label="Confirmar arquivo">
                <span>Arquivar este produto? Poderá reactivá-lo depois.</span>{" "}
                <button
                  type="button"
                  onClick={() => void run(archiveProduct)}
                  disabled={busy}
                >
                  Confirmar arquivo
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
                onClick={() => setConfirming("archive")}
                disabled={busy}
              >
                Arquivar
              </button>
            )}
          </>
        )}
        {isArchived && (
          <button
            type="button"
            onClick={() => void run(reactivateProduct)}
            disabled={busy}
          >
            Reactivar
          </button>
        )}{" "}
        <button type="button" onClick={onBack} disabled={busy}>
          Voltar ao portefólio
        </button>
      </div>

      {/* Contexto relacionado: documentos, decisões, pendências e execuções
          reais (execuções: F1-P05-PR03). */}
      <section aria-labelledby="product-related-title">
        <h4 id="product-related-title">Contexto relacionado</h4>
        <DocumentSection productId={product.id} />
        <DecisionSection productId={product.id} />
        <WorkItemSection productId={product.id} />
        <ExecutionSection productId={product.id} />
      </section>
    </section>
  );
}
