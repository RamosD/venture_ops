// Contratos da API de pendências (F1-P04-PR05), sobre o cliente HTTP central.
// A base da API é `/api`; caminhos versionados usam `/v1/...`. Sessão por cookie
// + CSRF. Um único ciclo de vida: open → completed | cancelled (finais). Sem
// DELETE. `is_overdue` é calculado no servidor (nunca persistido).

import { apiGet, apiPatch, apiPost } from "./client";

export const WORK_TYPES = [
  "action",
  "review",
  "validation",
  "obligation",
  "decision_follow_up",
] as const;
export type WorkType = (typeof WORK_TYPES)[number];

export const PRIORITIES = ["low", "medium", "high"] as const;
export type Priority = (typeof PRIORITIES)[number];

export const WORK_STATUSES = ["open", "completed", "cancelled"] as const;
export type WorkStatus = (typeof WORK_STATUSES)[number];

export interface WorkItem {
  id: string;
  organisation: string;
  product: string;
  decision: string | null;
  title: string;
  work_type: WorkType;
  responsible: string;
  priority: Priority;
  due_at: string | null;
  notes: string;
  status: WorkStatus;
  is_overdue: boolean;
  completed_at: string | null;
  cancelled_at: string | null;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface WorkItemListResponse {
  results: WorkItem[];
  count: number;
  page: number;
  page_size: number;
  num_pages: number;
}

export interface WorkItemListParams {
  product?: string;
  status?: WorkStatus;
  work_type?: WorkType;
  responsible?: string;
  overdue?: boolean;
  page?: number;
  page_size?: number;
}

export interface WorkItemCreateInput {
  product: string;
  title: string;
  work_type: WorkType;
  responsible?: string;
  priority?: Priority;
  due_at?: string | null;
  notes?: string;
  decision?: string | null;
}

export interface WorkItemUpdateInput {
  expected_version: number;
  title?: string;
  work_type?: WorkType;
  priority?: Priority;
  due_at?: string | null;
  notes?: string;
  decision?: string | null;
}

export const listWorkItems = (
  params: WorkItemListParams = {},
): Promise<WorkItemListResponse> => {
  const query = new URLSearchParams();
  if (params.product) query.set("product", params.product);
  if (params.status) query.set("status", params.status);
  if (params.work_type) query.set("work_type", params.work_type);
  if (params.responsible) query.set("responsible", params.responsible);
  if (params.overdue) query.set("overdue", "true");
  if (params.page) query.set("page", String(params.page));
  if (params.page_size) query.set("page_size", String(params.page_size));
  const qs = query.toString();
  return apiGet(`/v1/work-items${qs ? `?${qs}` : ""}`);
};

export const getWorkItem = (id: string): Promise<WorkItem> =>
  apiGet(`/v1/work-items/${id}`);

export const createWorkItem = (input: WorkItemCreateInput): Promise<WorkItem> =>
  apiPost("/v1/work-items", input);

export const updateWorkItem = (
  id: string,
  input: WorkItemUpdateInput,
): Promise<WorkItem> => apiPatch(`/v1/work-items/${id}`, input);

export const completeWorkItem = (
  id: string,
  expectedVersion: number,
): Promise<WorkItem> =>
  apiPost(`/v1/work-items/${id}/complete`, { expected_version: expectedVersion });

export const cancelWorkItem = (
  id: string,
  expectedVersion: number,
): Promise<WorkItem> =>
  apiPost(`/v1/work-items/${id}/cancel`, { expected_version: expectedVersion });
