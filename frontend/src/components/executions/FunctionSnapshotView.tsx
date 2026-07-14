import type { FunctionSnapshot } from "../../api/executions";
import { actorTypeLabel } from "../functions/labels";

// Apresenta o snapshot IMUTÁVEL da função capturado no instante da criação.
// Deixa explícito que é um retrato congelado (não reflecte alterações posteriores
// à função).
export function FunctionSnapshotView({
  snapshot,
}: {
  snapshot: FunctionSnapshot;
}) {
  return (
    <div data-testid="function-snapshot">
      <p>
        <small>
          Retrato congelado da função no momento da criação (não reflecte
          alterações posteriores).
        </small>
      </p>
      <dl>
        <dt>Nome</dt>
        <dd>{snapshot.name}</dd>
        <dt>Tipo</dt>
        <dd>{actorTypeLabel(snapshot.actor_type)}</dd>
        <dt>Propósito</dt>
        <dd>{snapshot.purpose}</dd>
        <dt>Responsabilidades</dt>
        <dd>{snapshot.responsibilities}</dd>
        <dt>Limites</dt>
        <dd>{snapshot.constraints || "—"}</dd>
        <dt>Requer aprovação humana</dt>
        <dd>{snapshot.requires_approval ? "Sim" : "Não"}</dd>
      </dl>
    </div>
  );
}
