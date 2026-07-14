// Rótulos em português dos tipos de actor e estados de função organizacional.

import type { ActorType, FunctionStatus } from "../../api/functions";

export const ACTOR_TYPE_LABELS: Record<ActorType, string> = {
  human: "Humana",
  ai: "IA",
  hybrid: "Híbrida",
};

export const FUNCTION_STATUS_LABELS: Record<FunctionStatus, string> = {
  active: "Activa",
  inactive: "Inactiva",
};

export const actorTypeLabel = (t: string): string =>
  (ACTOR_TYPE_LABELS as Record<string, string>)[t] ?? t;
export const functionStatusLabel = (s: string): string =>
  (FUNCTION_STATUS_LABELS as Record<string, string>)[s] ?? s;
