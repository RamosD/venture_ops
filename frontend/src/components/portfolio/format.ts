// Utilitários de apresentação do portefólio (sem lógica de negócio).

import type { Product } from "../../api/products";

// Data legível e determinística (AAAA-MM-DD) a partir do ISO do servidor.
export function formatDate(iso: string | null): string {
  if (!iso) return "—";
  return iso.slice(0, 10);
}

// Estado administrativo em português (apenas leitura; sem inventar estados).
export function statusLabel(status: string): string {
  if (status === "active") return "Activo";
  if (status === "archived") return "Arquivado";
  return status;
}

// Responsável: no MVP individual é o próprio utilizador; mostramos o email quando
// corresponde, senão o identificador (não inventamos nomes de outros).
export function responsibleLabel(
  product: Product,
  currentUser: { id: string; email: string } | null,
): string {
  if (currentUser && product.responsible === currentUser.id) {
    return currentUser.email;
  }
  return product.responsible;
}
