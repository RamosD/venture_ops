// Rótulos em português dos estados de decisão. Apenas apresentação.

import type { DecisionStatus } from "../../api/decisions";

export const DECISION_STATUS_LABELS: Record<DecisionStatus, string> = {
  active: "Activa",
  superseded: "Substituída",
};

export function decisionStatusLabel(status: string): string {
  return (DECISION_STATUS_LABELS as Record<string, string>)[status] ?? status;
}
