import type { ExecutionDetail as Execution } from "../../api/executions";
import { documentTypeLabel } from "../documents/labels";
import { ContextPackagePanel } from "./ContextPackagePanel";
import { FunctionSnapshotView } from "./FunctionSnapshotView";
import {
  abbrevChecksum,
  executionModeLabel,
  executionStatusLabel,
} from "./labels";

interface Props {
  execution: Execution;
  onBack: () => void;
}

// Detalhe da execução: metadados do pedido + contexto CONGELADO (snapshots e
// versões documentais exactas). Não há edição, eliminação nem transições de
// estado nesta etapa — apenas leitura. Distingue claramente o snapshot (retrato
// no momento da criação) dos marcadores actuais dos documentos.
export function ExecutionDetail({ execution, onBack }: Props) {
  const snap = execution.product_snapshot;
  return (
    <section aria-labelledby="execution-detail-title">
      <h4 id="execution-detail-title">{execution.title}</h4>

      <dl>
        <dt>Estado</dt>
        <dd data-testid="execution-status">
          {executionStatusLabel(execution.status)}
        </dd>
        <dt>Modo</dt>
        <dd>{executionModeLabel(execution.execution_mode)}</dd>
        <dt>Objectivo</dt>
        <dd>{execution.objective}</dd>
        <dt>Instruções do pedido</dt>
        <dd>{execution.request_instructions}</dd>
        <dt>Restrições</dt>
        <dd>{execution.constraints || "—"}</dd>
        <dt>Formato esperado</dt>
        <dd>{execution.expected_output_format}</dd>
      </dl>

      <section aria-labelledby="exec-fn-snapshot-title">
        <h5 id="exec-fn-snapshot-title">Função (snapshot)</h5>
        <FunctionSnapshotView snapshot={execution.function_snapshot} />
      </section>

      <section aria-labelledby="exec-prod-snapshot-title">
        <h5 id="exec-prod-snapshot-title">Produto (snapshot)</h5>
        <div data-testid="product-snapshot">
          <p>
            <small>Retrato congelado do produto no momento da criação.</small>
          </p>
          <dl>
            <dt>Nome</dt>
            <dd>{snap.name}</dd>
            <dt>Propósito</dt>
            <dd>{snap.purpose}</dd>
            <dt>Estado</dt>
            <dd>{snap.status}</dd>
            {snap.phase && (
              <>
                <dt>Fase</dt>
                <dd>{snap.phase}</dd>
              </>
            )}
            {snap.target_audience && (
              <>
                <dt>Público-alvo</dt>
                <dd>{snap.target_audience}</dd>
              </>
            )}
          </dl>
        </div>
      </section>

      <section aria-labelledby="exec-instruction-title">
        <h5 id="exec-instruction-title">Versão de instruções</h5>
        <p data-testid="instruction-version">
          {execution.instruction_version
            ? `Versão exacta: ${execution.instruction_version}`
            : "A função não tem documento de instruções."}
        </p>
      </section>

      <section aria-labelledby="exec-context-title">
        <h5 id="exec-context-title">Documentos de contexto (versões exactas)</h5>
        <p>
          <small>
            Os marcadores (exportação, desactualizado) são o estado ACTUAL dos
            documentos e podem ter mudado desde a criação; as versões referenciadas
            permanecem congeladas.
          </small>
        </p>
        <ol data-testid="context-documents">
          {execution.context_documents.map((doc) => (
            <li key={doc.document_version}>
              <strong>{doc.order}.</strong> {doc.title}{" "}
              <span>({documentTypeLabel(doc.document_type)})</span> — v
              <span data-testid="ctx-version">{doc.version_number}</span> ·{" "}
              <span data-testid="ctx-checksum">{abbrevChecksum(doc.checksum)}</span>
              {doc.purpose && <span> · {doc.purpose}</span>}
              {doc.export_policy === "confirm" && (
                <span> · confirmação exigida na geração</span>
              )}
              {doc.export_policy === "denied" && (
                <span> · exportação recusada (será bloqueada na geração)</span>
              )}
              {doc.is_outdated && <span> · desactualizado (aviso)</span>}
            </li>
          ))}
        </ol>
      </section>

      {/* Pacote de contexto: só para execuções preparadas. Não altera o estado,
          não chama IA nem importa resultado (handoff manual). */}
      {execution.status === "prepared" ? (
        <ContextPackagePanel execution={execution} />
      ) : (
        <p role="note" data-testid="package-unavailable">
          O pacote de contexto só pode ser preparado enquanto a execução está no
          estado <strong>Preparada</strong>.
        </p>
      )}

      <p>
        <button type="button" onClick={onBack}>
          Voltar às execuções
        </button>
      </p>
    </section>
  );
}
