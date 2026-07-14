// Contratos da API documental (F1-P04-PR02), sobre o cliente HTTP central.
// A base da API é `/api` (client.ts); os caminhos versionados usam `/v1/...`.
// Sessão por cookie + CSRF no cliente. O conteúdo Markdown vive em armazenamento
// privado no backend; a listagem nunca devolve conteúdo integral.

import { apiGet, apiPatch, apiPost } from "./client";

// Enumeração fechada de tipos documentais (espelha o backend; novos tipos
// exigem alteração formal — MVP-07.R1).
export const DOCUMENT_TYPES = [
  "contexto_da_empresa",
  "visao_de_produto",
  "instrucoes",
  "decisao_detalhada",
  "resultado",
] as const;
export type DocumentType = (typeof DOCUMENT_TYPES)[number];

// Política de exportação (DEC-F0-FINAL-08). `denied` é apenas um marcador: não
// oculta nem elimina o documento na aplicação; o bloqueio de selecção/geração
// de pacote é aplicado em F1-P05 (CLR-03).
export const EXPORT_POLICIES = ["allowed", "confirm", "denied"] as const;
export type ExportPolicy = (typeof EXPORT_POLICIES)[number];

// Metadados de listagem/leitura (sem conteúdo integral).
export interface DocumentSummary {
  id: string;
  organisation: string;
  product: string | null;
  title: string;
  document_type: DocumentType;
  is_outdated: boolean;
  export_policy: ExportPolicy;
  current_version_number: number | null;
  version: number;
  created_at: string;
  updated_at: string;
}

// Detalhe: metadados + conteúdo da versão actual (lido do armazenamento).
export interface DocumentDetail extends DocumentSummary {
  content: string;
  checksum: string;
}

// Metadados imutáveis de uma versão (histórico; sem conteúdo).
export interface DocumentVersionSummary {
  id: string; // UUID exacto da versão (referenciável, ex.: contexto de execução)
  version_number: number;
  checksum: string;
  byte_size: number;
  author: string;
  change_summary: string;
  created_at: string;
}

export interface DocumentVersionDetail extends DocumentVersionSummary {
  content: string;
}

export interface DocumentListResponse {
  results: DocumentSummary[];
  count: number;
  page: number;
  page_size: number;
  num_pages: number;
}

export interface DocumentVersionListResponse {
  results: DocumentVersionSummary[];
  count: number;
}

export interface DocumentListParams {
  product?: string;
  // Documentos empresariais (sem produto) — usado pela selecção de contexto de
  // execução. `true` devolve só documentos ao nível da empresa (product null).
  empresarial?: boolean;
  document_type?: DocumentType;
  is_outdated?: boolean;
  export_policy?: ExportPolicy;
  page?: number;
  page_size?: number;
}

// Criação: title, document_type e content obrigatórios; product e marcadores
// opcionais. `organisation`/`storage_key`/`checksum` nunca são enviados.
export interface DocumentCreateInput {
  title: string;
  document_type: DocumentType;
  content: string;
  product?: string | null;
  is_outdated?: boolean;
  export_policy?: ExportPolicy;
}

// Edição: exige `expected_version` (concorrência optimista). Conteúdo, resumo de
// alteração e/ou metadados, conforme contrato explícito.
export interface DocumentUpdateInput {
  expected_version: number;
  content?: string;
  change_summary?: string;
  title?: string;
  document_type?: DocumentType;
  product?: string | null;
  is_outdated?: boolean;
  export_policy?: ExportPolicy;
}

export const listDocuments = (
  params: DocumentListParams = {},
): Promise<DocumentListResponse> => {
  const query = new URLSearchParams();
  if (params.product) query.set("product", params.product);
  if (params.empresarial !== undefined)
    query.set("empresarial", String(params.empresarial));
  if (params.document_type) query.set("document_type", params.document_type);
  if (params.is_outdated !== undefined)
    query.set("is_outdated", String(params.is_outdated));
  if (params.export_policy) query.set("export_policy", params.export_policy);
  if (params.page) query.set("page", String(params.page));
  if (params.page_size) query.set("page_size", String(params.page_size));
  const qs = query.toString();
  return apiGet(`/v1/documents${qs ? `?${qs}` : ""}`);
};

export const getDocument = (id: string): Promise<DocumentDetail> =>
  apiGet(`/v1/documents/${id}`);

export const createDocument = (
  input: DocumentCreateInput,
): Promise<DocumentDetail> => apiPost("/v1/documents", input);

export const updateDocument = (
  id: string,
  input: DocumentUpdateInput,
): Promise<DocumentDetail> => apiPatch(`/v1/documents/${id}`, input);

export const listVersions = (
  id: string,
): Promise<DocumentVersionListResponse> =>
  apiGet(`/v1/documents/${id}/versions`);

export const getVersion = (
  id: string,
  versionNumber: number,
): Promise<DocumentVersionDetail> =>
  apiGet(`/v1/documents/${id}/versions/${versionNumber}`);

export const restoreVersion = (
  id: string,
  versionNumber: number,
  expectedVersion: number,
  changeSummary?: string,
): Promise<DocumentDetail> =>
  apiPost(`/v1/documents/${id}/restore`, {
    version_number: versionNumber,
    expected_version: expectedVersion,
    ...(changeSummary ? { change_summary: changeSummary } : {}),
  });

// Preview seguro: renderização sanitizada no backend. Devolve apenas HTML já
// sanitizado; o conteúdo não é guardado.
export const previewMarkdown = (content: string): Promise<{ html: string }> =>
  apiPost("/v1/documents/preview", { content });
