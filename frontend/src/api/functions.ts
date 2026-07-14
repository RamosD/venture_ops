// Contratos da API de funções organizacionais (F1-P05-PR01), sobre o cliente
// HTTP central. A base da API é `/api`; caminhos versionados usam `/v1/...`.
// Sessão por cookie + CSRF. Sem DELETE. A função organizacional é conteúdo/
// configuração (que perfil executa o trabalho), não um papel de autorização.

import { apiGet, apiPatch, apiPost } from "./client";

// Enumeração fechada de tipos de actor (espelha o backend; novos tipos exigem
// alteração formal).
export const ACTOR_TYPES = ["human", "ai", "hybrid"] as const;
export type ActorType = (typeof ACTOR_TYPES)[number];

export const FUNCTION_STATUSES = ["active", "inactive"] as const;
export type FunctionStatus = (typeof FUNCTION_STATUSES)[number];

// Filtro de estado da listagem (por defeito só `active`).
export type FunctionStatusFilter = FunctionStatus | "all";

export interface FunctionProfile {
  id: string;
  organisation: string;
  name: string;
  actor_type: ActorType;
  purpose: string;
  responsibilities: string;
  constraints: string;
  instruction_document: string | null;
  requires_approval: boolean;
  status: FunctionStatus;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface FunctionListResponse {
  results: FunctionProfile[];
  count: number;
  page: number;
  page_size: number;
  num_pages: number;
}

export interface FunctionListParams {
  status?: FunctionStatusFilter;
  actor_type?: ActorType;
  page?: number;
  page_size?: number;
}

// Criação: name, actor_type, purpose e responsibilities obrigatórios. Para
// actor_type ai/hybrid, requires_approval é sempre forçado a true no servidor.
export interface FunctionCreateInput {
  name: string;
  actor_type: ActorType;
  purpose: string;
  responsibilities: string;
  constraints?: string;
  instruction_document?: string | null;
  requires_approval?: boolean;
}

// Edição: exige `expected_version` (concorrência optimista). Nunca altera o
// estado (inactivar/reactivar são operações dedicadas).
export interface FunctionUpdateInput {
  expected_version: number;
  name?: string;
  actor_type?: ActorType;
  purpose?: string;
  responsibilities?: string;
  constraints?: string;
  instruction_document?: string | null;
  requires_approval?: boolean;
}

export const listFunctions = (
  params: FunctionListParams = {},
): Promise<FunctionListResponse> => {
  const query = new URLSearchParams();
  if (params.status) query.set("status", params.status);
  if (params.actor_type) query.set("actor_type", params.actor_type);
  if (params.page) query.set("page", String(params.page));
  if (params.page_size) query.set("page_size", String(params.page_size));
  const qs = query.toString();
  return apiGet(`/v1/functions${qs ? `?${qs}` : ""}`);
};

export const getFunction = (id: string): Promise<FunctionProfile> =>
  apiGet(`/v1/functions/${id}`);

export const createFunction = (
  input: FunctionCreateInput,
): Promise<FunctionProfile> => apiPost("/v1/functions", input);

export const updateFunction = (
  id: string,
  input: FunctionUpdateInput,
): Promise<FunctionProfile> => apiPatch(`/v1/functions/${id}`, input);

export const deactivateFunction = (
  id: string,
  expectedVersion: number,
): Promise<FunctionProfile> =>
  apiPost(`/v1/functions/${id}/deactivate`, { expected_version: expectedVersion });

export const reactivateFunction = (
  id: string,
  expectedVersion: number,
): Promise<FunctionProfile> =>
  apiPost(`/v1/functions/${id}/reactivate`, { expected_version: expectedVersion });
