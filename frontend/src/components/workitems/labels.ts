// Rótulos em português dos tipos, prioridades e estados de pendência.

import type { Priority, WorkStatus, WorkType } from "../../api/workItems";

export const WORK_TYPE_LABELS: Record<WorkType, string> = {
  action: "Acção",
  review: "Revisão",
  validation: "Validação",
  obligation: "Obrigação",
  decision_follow_up: "Seguimento de decisão",
};

export const PRIORITY_LABELS: Record<Priority, string> = {
  low: "Baixa",
  medium: "Média",
  high: "Alta",
};

export const WORK_STATUS_LABELS: Record<WorkStatus, string> = {
  open: "Aberta",
  completed: "Concluída",
  cancelled: "Cancelada",
};

export const workTypeLabel = (t: string): string =>
  (WORK_TYPE_LABELS as Record<string, string>)[t] ?? t;
export const priorityLabel = (p: string): string =>
  (PRIORITY_LABELS as Record<string, string>)[p] ?? p;
export const workStatusLabel = (s: string): string =>
  (WORK_STATUS_LABELS as Record<string, string>)[s] ?? s;
