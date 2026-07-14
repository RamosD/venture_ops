// Rótulos em português dos modos e estados de execução assistida.

import type { ExecutionMode, ExecutionStatus } from "../../api/executions";

export const EXECUTION_MODE_LABELS: Record<ExecutionMode, string> = {
  manual_local: "Manual local",
  manual_external: "Manual externa",
};

export const EXECUTION_STATUS_LABELS: Record<ExecutionStatus, string> = {
  prepared: "Preparada",
  result_pending_validation: "Resultado por validar",
  approved: "Aprovada",
  rejected: "Rejeitada",
  completed: "Concluída",
};

export const EXPORT_POLICY_LABELS: Record<string, string> = {
  allowed: "Permitida",
  confirm: "Com confirmação",
  denied: "Recusada",
};

export const exportPolicyLabel = (p: string): string =>
  EXPORT_POLICY_LABELS[p] ?? p;

export const SOURCE_MODE_LABELS: Record<string, string> = {
  pasted: "Colado",
  file: "Ficheiro",
};

export const sourceModeLabel = (m: string): string =>
  SOURCE_MODE_LABELS[m] ?? m;

// Rótulos das decisões de revisão humana (MVP-14).
export const REVIEW_DECISION_LABELS: Record<string, string> = {
  approved: "Aprovado",
  rejected: "Rejeitado",
  correction_requested: "Correcção pedida",
};

export const reviewDecisionLabel = (d: string): string =>
  REVIEW_DECISION_LABELS[d] ?? d;

export const executionModeLabel = (m: string): string =>
  (EXECUTION_MODE_LABELS as Record<string, string>)[m] ?? m;
export const executionStatusLabel = (s: string): string =>
  (EXECUTION_STATUS_LABELS as Record<string, string>)[s] ?? s;

// Checksum abreviado para apresentação (nunca o conteúdo).
export const abbrevChecksum = (checksum: string): string =>
  checksum ? checksum.slice(0, 12) : "—";
