// Rótulos em português dos tipos documentais e políticas de exportação.
// Apenas apresentação — a enumeração fechada é definida no backend/api.

import type { DocumentType, ExportPolicy } from "../../api/documents";

export const DOCUMENT_TYPE_LABELS: Record<DocumentType, string> = {
  contexto_da_empresa: "Contexto da empresa",
  visao_de_produto: "Visão de produto",
  instrucoes: "Instruções",
  decisao_detalhada: "Decisão detalhada",
  resultado: "Resultado",
};

export const EXPORT_POLICY_LABELS: Record<ExportPolicy, string> = {
  allowed: "Exportação permitida",
  confirm: "Exportação com confirmação",
  denied: "Exportação recusada",
};

export function documentTypeLabel(type: string): string {
  return (DOCUMENT_TYPE_LABELS as Record<string, string>)[type] ?? type;
}

export function exportPolicyLabel(policy: string): string {
  return (EXPORT_POLICY_LABELS as Record<string, string>)[policy] ?? policy;
}
