import type { Decision } from "../../api/decisions";
import { formatDate } from "../portfolio/format";
import { decisionStatusLabel } from "./labels";

interface Props {
  decisions: Decision[];
  onSelect: (decision: Decision) => void;
}

// Lista de decisões: título, data, estado e se substitui/foi substituída. Não
// há eliminação — o histórico (substituídas) permanece visível.
export function DecisionList({ decisions, onSelect }: Props) {
  if (decisions.length === 0) {
    return <p>Ainda não há decisões para este produto.</p>;
  }

  return (
    <table>
      <thead>
        <tr>
          <th scope="col">Título</th>
          <th scope="col">Data</th>
          <th scope="col">Estado</th>
          <th scope="col">Cadeia</th>
        </tr>
      </thead>
      <tbody>
        {decisions.map((decision) => (
          <tr key={decision.id}>
            <td>
              <button type="button" onClick={() => onSelect(decision)}>
                {decision.title}
              </button>
            </td>
            <td>{formatDate(decision.decided_at)}</td>
            <td>{decisionStatusLabel(decision.status)}</td>
            <td>
              {decision.supersedes ? "substitui anterior" : ""}
              {decision.supersedes && decision.replaced_by ? " · " : ""}
              {decision.replaced_by ? "foi substituída" : ""}
              {!decision.supersedes && !decision.replaced_by ? "—" : ""}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
