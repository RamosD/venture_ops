// Contratos da API de execuções assistidas (F1-P05-PR02), sobre o cliente HTTP
// central. Base `/api`; caminhos versionados `/v1/...`. Sessão por cookie + CSRF.
// A execução nasce sempre `prepared`; o cliente nunca escolhe estado, snapshots
// nem instruction_version. Sem PATCH/DELETE (contexto imutável).

import {
  apiGet,
  apiPost,
  apiPostBlob,
  apiPostFormWithStatus,
  apiPostWithStatus,
} from "./client";
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

// --- Tentativas de resultado (F1-P06) --------------------------------------
export type ResultSourceMode = "pasted" | "file";

export interface ResultAttempt {
  id: string;
  organisation: string;
  execution: string;
  attempt_number: number;
  source_mode: ResultSourceMode;
  source_tool: string;
  source_model: string;
  source_notes: string;
  imported_by: string;
  document: string;
  document_version: string;
  version_number: number;
  checksum: string;
  byte_size: number;
  created_at: string;
}

export interface ResultAttemptDetail extends ResultAttempt {
  content: string;
  execution_context: {
    status: ExecutionStatus;
    version: number;
    title: string;
    current_result_attempt: string | null;
  };
}

// Estado mínimo da execução devolvido pela importação (POST 201).
export interface ImportedExecutionState {
  status: ExecutionStatus;
  version: number;
  title: string;
  current_result_attempt: string | null;
}

export interface ImportResultInput {
  expected_version: number;
  source_tool: string;
  source_model?: string;
  source_notes?: string;
  // Exactamente uma das duas: `content` (texto colado) ou `file` (ficheiro).
  content?: string;
  file?: File;
}

// Desfecho tipado (a UI decide pelo estado do servidor, nunca localmente).
export type ImportOutcome =
  | { kind: "ok"; attempt: ResultAttempt; execution: ImportedExecutionState }
  | { kind: "conflict"; detail: string } // 409 (estado/versão)
  | { kind: "too_large" } // 413
  | { kind: "invalid"; detail: string } // 400
  | { kind: "error"; status?: number };

export const listResultAttempts = (
  executionId: string,
): Promise<{ results: ResultAttempt[] }> =>
  apiGet(`/v1/executions/${executionId}/result-attempts`);

export const getResultAttempt = (
  executionId: string,
  attemptNumber: number,
): Promise<ResultAttemptDetail> =>
  apiGet(`/v1/executions/${executionId}/result-attempts/${attemptNumber}`);

function toOutcome(status: number, data: any): ImportOutcome {
  if (status === 201) {
    const { execution, ...attempt } = data;
    return { kind: "ok", attempt, execution };
  }
  if (status === 409) {
    return { kind: "conflict", detail: data?.detail ?? "Conflito de estado." };
  }
  if (status === 413) return { kind: "too_large" };
  if (status === 400) {
    const detail =
      data?.detail ?? "Verifique os campos e a origem do resultado.";
    return { kind: "invalid", detail };
  }
  return { kind: "error", status };
}

export const importResult = async (
  executionId: string,
  input: ImportResultInput,
): Promise<ImportOutcome> => {
  const path = `/v1/executions/${executionId}/result-attempts`;
  if (input.file) {
    const form = new FormData();
    form.set("expected_version", String(input.expected_version));
    form.set("source_tool", input.source_tool);
    if (input.source_model) form.set("source_model", input.source_model);
    if (input.source_notes) form.set("source_notes", input.source_notes);
    form.set("file", input.file);
    const { status, data } = await apiPostFormWithStatus<any>(path, form);
    return toOutcome(status, data);
  }
  const { status, data } = await apiPostWithStatus<any>(path, {
    expected_version: input.expected_version,
    source_tool: input.source_tool,
    ...(input.source_model ? { source_model: input.source_model } : {}),
    ...(input.source_notes ? { source_notes: input.source_notes } : {}),
    content: input.content ?? "",
  });
  return toOutcome(status, data);
};

// --- Revisão humana de resultados (F1-P06-PR03, MVP-14) --------------------
export type ReviewDecision = "approved" | "rejected" | "correction_requested";

// Histórico mínimo de uma revisão (nunca o conteúdo do resultado). `observations`
// é o texto do próprio revisor.
export interface ResultReview {
  id: string;
  organisation: string;
  execution: string;
  result_attempt: string;
  attempt_number: number;
  reviewer: string;
  decision: ReviewDecision;
  observations: string;
  created_at: string;
}

// Comando de revisão: só `expected_version` (obrigatório) e `observations`. Nunca
// se envia `decision`/`reviewer`/`status` — cada operação tem o seu endpoint.
export type ReviewOperation = "approve" | "reject" | "request-correction";

// Estado mínimo da execução devolvido pela revisão (POST 201).
export interface ReviewedExecutionState {
  status: ExecutionStatus;
  version: number;
  title: string;
  current_result_attempt: string | null;
}

// Desfecho tipado (a UI decide pelo estado do servidor, nunca localmente).
export type ReviewOutcome =
  | {
      kind: "ok";
      review: ResultReview;
      execution: ReviewedExecutionState;
      attempt: ResultAttempt;
    }
  | { kind: "conflict"; detail: string } // 409 (estado/versão/tentativa)
  | { kind: "forbidden"; detail: string } // 403 (não-Owner)
  | { kind: "invalid"; detail: string } // 400 (observações em falta, campos)
  | { kind: "not_found" } // 404 (execução/tentativa alheia ou inexistente)
  | { kind: "error"; status?: number };

export const listReviews = (
  executionId: string,
): Promise<{ results: ResultReview[] }> =>
  apiGet(`/v1/executions/${executionId}/reviews`);

function toReviewOutcome(status: number, data: any): ReviewOutcome {
  if (status === 201) {
    return {
      kind: "ok",
      review: data.review,
      execution: data.execution,
      attempt: data.attempt,
    };
  }
  if (status === 409) {
    return { kind: "conflict", detail: data?.detail ?? "Conflito de estado." };
  }
  if (status === 403) {
    return {
      kind: "forbidden",
      detail: data?.detail ?? "Sem permissão para rever.",
    };
  }
  if (status === 404) return { kind: "not_found" };
  if (status === 400) {
    const detail =
      data?.observations ?? data?.detail ?? "Verifique os campos da revisão.";
    return { kind: "invalid", detail };
  }
  return { kind: "error", status };
}

export const reviewResult = async (
  executionId: string,
  attemptNumber: number,
  operation: ReviewOperation,
  input: { expected_version: number; observations?: string },
): Promise<ReviewOutcome> => {
  const path = `/v1/executions/${executionId}/result-attempts/${attemptNumber}/${operation}`;
  const { status, data } = await apiPostWithStatus<any>(path, {
    expected_version: input.expected_version,
    ...(input.observations ? { observations: input.observations } : {}),
  });
  return toReviewOutcome(status, data);
};

// --- Aplicação controlada (F1-P06-PR04, MVP-15) ----------------------------
// Valores de confirmação exigidos pelo contrato (enviados explícitos).
export const DOCUMENT_APPLY_CONFIRMATION = "apply-document";
export const DECISION_APPLY_CONFIRMATION = "apply-decision";
export const WORK_ITEM_APPLY_CONFIRMATION = "apply-work-item";
export const NO_CHANGE_CONFIRMATION = "close-without-application";

export type ApplicationType = "document" | "decision" | "work_item" | "no_change";

// Metadados de uma aplicação (a ligação oficial execução↔versão criada; nunca o
// conteúdo aplicado).
export interface ResultApplication {
  id: string;
  organisation: string;
  execution: string;
  result_attempt: string;
  attempt_number: number;
  review: string;
  application_type: ApplicationType;
  applied_by: string;
  change_summary: string;
  rationale: string;
  target_document: string | null;
  base_document_version: string | null;
  created_document_version: string | null;
  target_decision: string | null;
  created_decision: string | null;
  target_work_item: string | null;
  base_version_number: number | null;
  created_version_number: number | null;
  created_version_checksum: string | null;
  created_at: string;
}

export interface AppliedExecutionState {
  status: ExecutionStatus;
  version: number;
  title: string;
  current_result_attempt: string | null;
}

export interface ApplyDocumentInput {
  target_document: string;
  expected_execution_version: number;
  expected_document_version: number;
  content: string;
  change_summary: string;
  attempt_number?: number;
  attempt_id?: string;
}

// Desfecho tipado (a UI decide pelo estado do servidor, nunca localmente).
export type ApplyOutcome =
  | {
      kind: "ok";
      application: ResultApplication;
      execution: AppliedExecutionState;
      created: boolean; // false numa repetição idempotente
    }
  | { kind: "conflict"; detail: string } // 409 (estado/versão/aplicação diferente)
  | { kind: "forbidden"; detail: string } // 403 (não-Owner)
  | { kind: "invalid"; detail: string } // 400 (conteúdo/confirmação/resumo)
  | { kind: "not_eligible"; detail: string } // 422 (documento alvo não elegível)
  | { kind: "not_found" } // 404 (execução/tentativa/documento alheio)
  | { kind: "too_large" } // 413
  | { kind: "error"; status?: number };

export const getApplication = (
  executionId: string,
): Promise<{ application: ResultApplication; execution: AppliedExecutionState }> =>
  apiGet(`/v1/executions/${executionId}/application`);

function toApplyOutcome(status: number, data: any): ApplyOutcome {
  if (status === 201 || status === 200) {
    return {
      kind: "ok",
      application: data.application,
      execution: data.execution,
      created: status === 201,
    };
  }
  if (status === 409)
    return { kind: "conflict", detail: data?.detail ?? "Conflito." };
  if (status === 403)
    return { kind: "forbidden", detail: data?.detail ?? "Sem permissão." };
  if (status === 422)
    return { kind: "not_eligible", detail: data?.detail ?? "Alvo não elegível." };
  if (status === 404) return { kind: "not_found" };
  if (status === 413) return { kind: "too_large" };
  if (status === 400) {
    const detail =
      data?.content ??
      data?.confirmation ??
      data?.change_summary ??
      data?.rationale ??
      data?.target_document ??
      data?.detail ??
      "Verifique os campos.";
    return { kind: "invalid", detail };
  }
  return { kind: "error", status };
}

export const applyDocument = async (
  executionId: string,
  input: ApplyDocumentInput,
): Promise<ApplyOutcome> => {
  const { status, data } = await apiPostWithStatus<any>(
    `/v1/executions/${executionId}/apply/document`,
    {
      target_document: input.target_document,
      expected_execution_version: input.expected_execution_version,
      expected_document_version: input.expected_document_version,
      content: input.content,
      change_summary: input.change_summary,
      confirmation: DOCUMENT_APPLY_CONFIRMATION,
      ...(input.attempt_id
        ? { attempt_id: input.attempt_id }
        : { attempt_number: input.attempt_number }),
    },
  );
  return toApplyOutcome(status, data);
};

export interface ApplyDecisionInput {
  target_decision: string;
  expected_execution_version: number;
  expected_decision_version: number;
  title: string;
  context: string;
  decision_text: string;
  impact?: string;
  decided_at?: string;
  detail_document?: string;
  attempt_number?: number;
  attempt_id?: string;
}

export const applyDecision = async (
  executionId: string,
  input: ApplyDecisionInput,
): Promise<ApplyOutcome> => {
  const { status, data } = await apiPostWithStatus<any>(
    `/v1/executions/${executionId}/apply/decision`,
    {
      target_decision: input.target_decision,
      expected_execution_version: input.expected_execution_version,
      expected_decision_version: input.expected_decision_version,
      title: input.title,
      context: input.context,
      decision_text: input.decision_text,
      ...(input.impact ? { impact: input.impact } : {}),
      ...(input.decided_at ? { decided_at: input.decided_at } : {}),
      ...(input.detail_document ? { detail_document: input.detail_document } : {}),
      confirmation: DECISION_APPLY_CONFIRMATION,
      ...(input.attempt_id
        ? { attempt_id: input.attempt_id }
        : { attempt_number: input.attempt_number }),
    },
  );
  return toApplyOutcome(status, data);
};

export interface ApplyWorkItemInput {
  target_work_item: string;
  expected_execution_version: number;
  expected_work_item_version: number;
  attempt_number?: number;
  attempt_id?: string;
}

export const applyWorkItem = async (
  executionId: string,
  input: ApplyWorkItemInput,
): Promise<ApplyOutcome> => {
  const { status, data } = await apiPostWithStatus<any>(
    `/v1/executions/${executionId}/apply/work-item`,
    {
      target_work_item: input.target_work_item,
      expected_execution_version: input.expected_execution_version,
      expected_work_item_version: input.expected_work_item_version,
      confirmation: WORK_ITEM_APPLY_CONFIRMATION,
      ...(input.attempt_id
        ? { attempt_id: input.attempt_id }
        : { attempt_number: input.attempt_number }),
    },
  );
  return toApplyOutcome(status, data);
};

export interface CloseWithoutApplicationInput {
  expected_execution_version: number;
  rationale: string;
  attempt_number?: number;
  attempt_id?: string;
}

export const closeWithoutApplication = async (
  executionId: string,
  input: CloseWithoutApplicationInput,
): Promise<ApplyOutcome> => {
  const { status, data } = await apiPostWithStatus<any>(
    `/v1/executions/${executionId}/close-without-application`,
    {
      expected_execution_version: input.expected_execution_version,
      rationale: input.rationale,
      confirmation: NO_CHANGE_CONFIRMATION,
      ...(input.attempt_id
        ? { attempt_id: input.attempt_id }
        : { attempt_number: input.attempt_number }),
    },
  );
  return toApplyOutcome(status, data);
};
