// Contratos da API de decisões (F1-P04-PR04), sobre o cliente HTTP central.
// A base da API é `/api`; caminhos versionados usam `/v1/...`. Sessão por cookie
// + CSRF no cliente. Sem DELETE nem PATCH: a decisão histórica não é reescrita —
// altera-se por substituição (cria nova, marca anterior superseded).

import { apiGet, apiPost } from "./client";

export const DECISION_STATUSES = ["active", "superseded"] as const;
export type DecisionStatus = (typeof DECISION_STATUSES)[number];

export interface Decision {
  id: string;
  organisation: string;
  title: string;
  context: string;
  decision_text: string;
  responsible: string;
  decided_at: string;
  impact: string;
  status: DecisionStatus;
  product: string | null;
  detail_document: string | null;
  supersedes: string | null;
  replaced_by: string | null;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface DecisionListResponse {
  results: Decision[];
  count: number;
  page: number;
  page_size: number;
  num_pages: number;
}

export interface DecisionListParams {
  product?: string;
  status?: DecisionStatus;
  page?: number;
  page_size?: number;
}

// Criação: title/context/decision_text obrigatórios; associações opcionais.
export interface DecisionCreateInput {
  title: string;
  context: string;
  decision_text: string;
  responsible?: string;
  product?: string | null;
  detail_document?: string | null;
  impact?: string;
  decided_at?: string;
}

// Substituição: dados da nova decisão + versão esperada da anterior.
export interface DecisionSupersedeInput extends DecisionCreateInput {
  expected_version?: number;
}

export const listDecisions = (
  params: DecisionListParams = {},
): Promise<DecisionListResponse> => {
  const query = new URLSearchParams();
  if (params.product) query.set("product", params.product);
  if (params.status) query.set("status", params.status);
  if (params.page) query.set("page", String(params.page));
  if (params.page_size) query.set("page_size", String(params.page_size));
  const qs = query.toString();
  return apiGet(`/v1/decisions${qs ? `?${qs}` : ""}`);
};

export const getDecision = (id: string): Promise<Decision> =>
  apiGet(`/v1/decisions/${id}`);

export const createDecision = (input: DecisionCreateInput): Promise<Decision> =>
  apiPost("/v1/decisions", input);

export const supersedeDecision = (
  id: string,
  input: DecisionSupersedeInput,
): Promise<Decision> => apiPost(`/v1/decisions/${id}/supersede`, input);
