// Contratos da API de execuções assistidas (F1-P05-PR02), sobre o cliente HTTP
// central. Base `/api`; caminhos versionados `/v1/...`. Sessão por cookie + CSRF.
// A execução nasce sempre `prepared`; o cliente nunca escolhe estado, snapshots
// nem instruction_version. Sem PATCH/DELETE (contexto imutável).

import { apiGet, apiPost, apiPostBlob, apiPostWithStatus } from "./client";
import type { ActorType } from "./functions";

export const EXECUTION_MODES = ["manual_local", "manual_external"] as const;
export type ExecutionMode = (typeof EXECUTION_MODES)[number];

export const EXECUTION_STATUSES = [
  "prepared",
  "result_pending_validation",
  "approved",
  "rejected",
  "completed",
] as const;
export type ExecutionStatus = (typeof EXECUTION_STATUSES)[number];

// Snapshot imutável da função (só campos aprovados no instante da criação).
export interface FunctionSnapshot {
  id: string;
  name: string;
  actor_type: ActorType;
  purpose: string;
  responsibilities: string;
  constraints: string;
  requires_approval: boolean;
}

// Snapshot imutável do produto (dados mínimos; sem dados pessoais).
export interface ProductSnapshot {
  id: string;
  name: string;
  purpose: string;
  status: string;
  phase?: string;
  target_audience?: string;
}

// Documento de contexto: versão exacta + marcadores ACTUAIS (aviso).
export interface ContextDocument {
  document: string;
  document_version: string;
  order: number;
  purpose: string;
  title: string;
  document_type: string;
  version_number: number;
  checksum: string;
  export_policy: string;
  is_outdated: boolean;
}

// Metadados de lista (sem conteúdo integral).
export interface ExecutionSummary {
  id: string;
  organisation: string;
  product: string;
  function_profile: string;
  requested_by: string;
  title: string;
  execution_mode: ExecutionMode;
  status: ExecutionStatus;
  document_count: number;
  version: number;
  created_at: string;
  updated_at: string;
}

// Detalhe: metadados + snapshots + instruction_version + contexto ordenado.
export interface ExecutionDetail extends ExecutionSummary {
  objective: string;
  request_instructions: string;
  constraints: string;
  expected_output_format: string;
  function_snapshot: FunctionSnapshot;
  product_snapshot: ProductSnapshot;
  instruction_version: string | null;
  context_documents: ContextDocument[];
}

export interface ExecutionListResponse {
  results: ExecutionSummary[];
  count: number;
  page: number;
  page_size: number;
  num_pages: number;
}

export interface ExecutionListParams {
  product?: string;
  status?: ExecutionStatus;
  function_profile?: string;
  execution_mode?: ExecutionMode;
  page?: number;
  page_size?: number;
}

// Item de contexto: versão documental exacta + papel opcional. A `order` é
// determinada pela posição na lista (o cliente não a escolhe directamente).
export interface ContextItemInput {
  document_version: string;
  purpose?: string;
}

export interface ExecutionCreateInput {
  product: string;
  function_profile: string;
  title: string;
  objective: string;
  request_instructions: string;
  constraints?: string;
  expected_output_format: string;
  execution_mode: ExecutionMode;
  context: ContextItemInput[];
}

export const listExecutions = (
  params: ExecutionListParams = {},
): Promise<ExecutionListResponse> => {
  const query = new URLSearchParams();
  if (params.product) query.set("product", params.product);
  if (params.status) query.set("status", params.status);
  if (params.function_profile)
    query.set("function_profile", params.function_profile);
  if (params.execution_mode) query.set("execution_mode", params.execution_mode);
  if (params.page) query.set("page", String(params.page));
  if (params.page_size) query.set("page_size", String(params.page_size));
  const qs = query.toString();
  return apiGet(`/v1/executions${qs ? `?${qs}` : ""}`);
};

export const getExecution = (id: string): Promise<ExecutionDetail> =>
  apiGet(`/v1/executions/${id}`);

export const createExecution = (
  input: ExecutionCreateInput,
): Promise<ExecutionDetail> => apiPost("/v1/executions", input);

// --- Pacote de contexto (F1-P05-PR04/PR05) ---------------------------------
export type ContextPackageFormat = "single_markdown" | "separate_files";

export interface ContextPackageManifestDoc {
  order: number;
  document: string;
  document_version: string;
  title: string;
  document_type: string;
  version_number: number;
  checksum: string;
  is_outdated: boolean;
  export_policy: string;
}

export interface ContextPackageManifest {
  execution_id: string;
  format: ContextPackageFormat;
  sections: string[];
  instruction_version: {
    document: string;
    document_version: string;
    version_number: number;
    checksum: string;
  } | null;
  documents: ContextPackageManifestDoc[];
}

// Resposta 200 do preview (conteúdo em single_markdown; lista de ficheiros em ZIP).
export interface ContextPackagePreview {
  format: ContextPackageFormat;
  checksum: string;
  warnings: string[];
  manifest: ContextPackageManifest;
  content?: string;
  files?: string[];
}

// Corpo 409: análise de política (sem conteúdo). É a fonte de verdade do backend.
export interface ContextPackageBlocked {
  detail: string;
  reason: "denied" | "confirmation_required";
  denied_document_ids: string[];
  confirmation_required_document_ids: string[];
}

export interface ContextPackageRequest {
  format?: ContextPackageFormat;
  confirmed_document_ids?: string[];
  operation?: "preview" | "copy";
  destination_label?: string;
}

// Resultado do preview: distingue os três desfechos possíveis pelo estado do
// servidor (a UI nunca decide localmente se algo é permitido).
export type PreviewOutcome =
  | { kind: "ok"; preview: ContextPackagePreview }
  | { kind: "blocked"; blocked: ContextPackageBlocked }
  | { kind: "too_large" }
  | { kind: "error"; status?: number };

export const previewContextPackage = async (
  executionId: string,
  request: ContextPackageRequest,
): Promise<PreviewOutcome> => {
  const { status, data } = await apiPostWithStatus<unknown>(
    `/v1/executions/${executionId}/context-package/preview`,
    request,
  );
  if (status === 200) {
    return { kind: "ok", preview: data as ContextPackagePreview };
  }
  if (status === 409) {
    return { kind: "blocked", blocked: data as ContextPackageBlocked };
  }
  if (status === 413) {
    return { kind: "too_large" };
  }
  return { kind: "error", status };
};

export const downloadContextPackage = (
  executionId: string,
  request: ContextPackageRequest,
): Promise<{ blob: Blob; filename: string; checksum: string }> =>
  apiPostBlob(`/v1/executions/${executionId}/context-package/download`, request);
