import type { DocumentSummary } from "../../api/documents";
import { documentTypeLabel, exportPolicyLabel } from "./labels";

interface Props {
  documents: DocumentSummary[];
  onSelect: (document: DocumentSummary) => void;
}

// Lista documental: título, tipo, versão actual, marcador de desactualizado e
// política de exportação. Não carrega conteúdo integral (a API de listagem só
// devolve metadados). O título abre o documento.
export function DocumentList({ documents, onSelect }: Props) {
  if (documents.length === 0) {
    return <p>Ainda não há documentos para este produto.</p>;
  }

  return (
    <table>
      <thead>
        <tr>
          <th scope="col">Título</th>
          <th scope="col">Tipo</th>
          <th scope="col">
            <abbr title="Versão actual do conteúdo">v.</abbr>
          </th>
          <th scope="col">Estado</th>
          <th scope="col">Exportação</th>
        </tr>
      </thead>
      <tbody>
        {documents.map((doc) => (
          <tr key={doc.id}>
            <td>
              <button type="button" onClick={() => onSelect(doc)}>
                {doc.title}
              </button>
            </td>
            <td>{documentTypeLabel(doc.document_type)}</td>
            <td>{doc.current_version_number ?? "—"}</td>
            <td>{doc.is_outdated ? "Desactualizado" : "Actual"}</td>
            <td>{exportPolicyLabel(doc.export_policy)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
