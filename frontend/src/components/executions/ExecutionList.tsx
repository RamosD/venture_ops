import type { ExecutionSummary } from "../../api/executions";
import { executionModeLabel, executionStatusLabel } from "./labels";

interface Props {
  executions: ExecutionSummary[];
  functionNames: Record<string, string>;
  onSelect: (execution: ExecutionSummary) => void;
}

function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleDateString("pt-PT");
  } catch {
    return iso;
  }
}

// Lista de execuções do produto actual: título, função, modo, estado e data.
// Sem estados nem resultados fictícios — apresenta apenas o que o servidor devolve.
export function ExecutionList({ executions, functionNames, onSelect }: Props) {
  if (executions.length === 0) {
    return <p>Ainda não há execuções para este produto.</p>;
  }
  return (
    <ul>
      {executions.map((execution) => (
        <li key={execution.id}>
          <button type="button" onClick={() => onSelect(execution)}>
            {execution.title}
          </button>{" "}
          <span>
            {functionNames[execution.function_profile] ?? "função"} ·{" "}
            {executionModeLabel(execution.execution_mode)} ·{" "}
            <span data-testid="list-status">
              {executionStatusLabel(execution.status)}
            </span>{" "}
            · {formatDate(execution.created_at)}
          </span>
        </li>
      ))}
    </ul>
  );
}
