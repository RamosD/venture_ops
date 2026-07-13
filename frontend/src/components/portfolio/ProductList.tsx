import type { Product } from "../../api/products";
import { formatDate, responsibleLabel, statusLabel } from "./format";

interface Props {
  products: Product[];
  currentUser: { id: string; email: string } | null;
  onSelect: (product: Product) => void;
}

// Lista do portefólio: nome, estado, responsável e última revisão. A versão é
// apresentada apenas como controlo técnico discreto. Sem métricas nem nível de
// atenção (calculado, não inventado aqui).
export function ProductList({ products, currentUser, onSelect }: Props) {
  if (products.length === 0) {
    return <p>Ainda não tem produtos. Crie o primeiro para começar.</p>;
  }

  return (
    <table>
      <thead>
        <tr>
          <th scope="col">Nome</th>
          <th scope="col">Estado</th>
          <th scope="col">Responsável</th>
          <th scope="col">Última revisão</th>
          <th scope="col">
            <abbr title="Versão (controlo técnico)">v.</abbr>
          </th>
        </tr>
      </thead>
      <tbody>
        {products.map((product) => (
          <tr key={product.id}>
            <td>
              <button type="button" onClick={() => onSelect(product)}>
                {product.name}
              </button>
            </td>
            <td>{statusLabel(product.status)}</td>
            <td>{responsibleLabel(product, currentUser)}</td>
            <td>{formatDate(product.last_reviewed_at)}</td>
            <td>{product.version}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
