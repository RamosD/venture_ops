import type { WorkItem } from "../../api/workItems";
import { formatDate } from "../portfolio/format";
import { priorityLabel, workStatusLabel, workTypeLabel } from "./labels";

interface Props {
  items: WorkItem[];
  onSelect: (item: WorkItem) => void;
}

// Lista curta de pendências: título, tipo, prioridade, responsável, prazo e
// estado, com sinal visual de vencida (calculado no servidor). Sem colunas de
// gestão de projectos (sem sprint, epic, dependências, etc.).
export function WorkItemList({ items, onSelect }: Props) {
  if (items.length === 0) {
    return <p>Ainda não há pendências para este produto.</p>;
  }

  return (
    <table>
      <thead>
        <tr>
          <th scope="col">Título</th>
          <th scope="col">Tipo</th>
          <th scope="col">Prioridade</th>
          <th scope="col">Prazo</th>
          <th scope="col">Estado</th>
        </tr>
      </thead>
      <tbody>
        {items.map((item) => (
          <tr key={item.id}>
            <td>
              <button type="button" onClick={() => onSelect(item)}>
                {item.title}
              </button>
              {item.is_overdue && (
                <>
                  {" "}
                  <strong data-testid="overdue-badge" aria-label="Vencida">
                    (Vencida)
                  </strong>
                </>
              )}
            </td>
            <td>{workTypeLabel(item.work_type)}</td>
            <td>{priorityLabel(item.priority)}</td>
            <td>{formatDate(item.due_at)}</td>
            <td>{workStatusLabel(item.status)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
