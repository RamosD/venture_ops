import type { Decision } from "../../api/decisions";
import { formatDate } from "../portfolio/format";
import { decisionStatusLabel } from "./labels";

interface Props {
  decision: Decision;
  onSupersede: (decision: Decision) => void;
  onOpenChain: (decisionId: string) => void;
  onBack: () => void;
}

// Detalhe da decisão: campos, associações e cadeia de substituição navegável.
// "Substituir" só está disponível para decisões activas (uma substituída não
// pode voltar a ser substituída). O documento de detalhe é apresentado quando
// associado.
export function DecisionDetail({
  decision,
  onSupersede,
  onOpenChain,
  onBack,
}: Props) {
  const isActive = decision.status === "active";

  return (
    <section aria-labelledby="decision-detail-title">
      <h4 id="decision-detail-title">{decision.title}</h4>

      <dl>
        <dt>Estado</dt>
        <dd>{decisionStatusLabel(decision.status)}</dd>
        <dt>Data</dt>
        <dd>{formatDate(decision.decided_at)}</dd>
        <dt>Contexto</dt>
        <dd>
          <pre>{decision.context}</pre>
        </dd>
        <dt>Decisão</dt>
        <dd>
          <pre>{decision.decision_text}</pre>
        </dd>
        <dt>Impacto</dt>
        <dd>{decision.impact ? <pre>{decision.impact}</pre> : "—"}</dd>
        <dt>Documento de detalhe</dt>
        <dd>{decision.detail_document ?? "—"}</dd>
      </dl>

      {/* Cadeia de substituição navegável. */}
      <section aria-labelledby="decision-chain-title">
        <h5 id="decision-chain-title">Cadeia de substituição</h5>
        <p>
          {decision.supersedes ? (
            <button
              type="button"
              onClick={() => onOpenChain(decision.supersedes!)}
            >
              Ver decisão anterior (substituída por esta)
            </button>
          ) : (
            <span>Não substitui nenhuma decisão anterior.</span>
          )}
        </p>
        <p>
          {decision.replaced_by ? (
            <button
              type="button"
              onClick={() => onOpenChain(decision.replaced_by!)}
            >
              Ver decisão seguinte (que substituiu esta)
            </button>
          ) : (
            <span>Nenhuma decisão a substituiu (é a mais recente da cadeia).</span>
          )}
        </p>
      </section>

      <div>
        {isActive ? (
          <button type="button" onClick={() => onSupersede(decision)}>
            Substituir
          </button>
        ) : (
          <p role="note">
            Esta decisão foi substituída; não pode ser substituída de novo. Abra
            a decisão que a substituiu para a alterar.
          </p>
        )}{" "}
        <button type="button" onClick={onBack}>
          Voltar às decisões
        </button>
      </div>
    </section>
  );
}
