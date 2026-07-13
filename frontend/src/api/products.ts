// Contratos do portefólio de produtos (F1-P03-PR02/PR04), sobre o cliente HTTP
// central. A base da API é `/api` (client.ts); os caminhos versionados usam
// `/v1/...`, como em organisation.ts. Sessão por cookie + CSRF no cliente.

import { apiGet, apiPatch, apiPost } from "./client";

export interface Product {
  id: string;
  organisation: string;
  name: string;
  purpose: string;
  status: string;
  responsible: string;
  last_reviewed_at: string;
  target_audience: string;
  phase: string;
  next_review_at: string | null;
  notes: string;
  version: number;
  created_at: string;
  updated_at: string;
}

export type ProductStatusFilter = "active" | "archived" | "all";

export interface ProductListParams {
  status?: ProductStatusFilter;
  responsible?: string;
  page?: number;
  page_size?: number;
}

export interface ProductListResponse {
  results: Product[];
  count: number;
  page: number;
  page_size: number;
  num_pages: number;
}

// Criação: só `name` e `purpose` são obrigatórios; opcionais quando preenchidos.
export interface ProductCreateInput {
  name: string;
  purpose: string;
  target_audience?: string;
  phase?: string;
  next_review_at?: string | null;
  notes?: string;
}

// Edição comum: exige `expected_version` (concorrência optimista). Não altera
// estado (arquivo/reactivação/revisão têm operações próprias).
export interface ProductUpdateInput {
  expected_version: number;
  name?: string;
  purpose?: string;
  target_audience?: string;
  phase?: string;
  next_review_at?: string | null;
  notes?: string;
}

export const listProducts = (
  params: ProductListParams = {},
): Promise<ProductListResponse> => {
  const query = new URLSearchParams();
  if (params.status) query.set("status", params.status);
  if (params.responsible) query.set("responsible", params.responsible);
  if (params.page) query.set("page", String(params.page));
  if (params.page_size) query.set("page_size", String(params.page_size));
  const qs = query.toString();
  return apiGet(`/v1/products${qs ? `?${qs}` : ""}`);
};

export const getProduct = (id: string): Promise<Product> =>
  apiGet(`/v1/products/${id}`);

export const createProduct = (input: ProductCreateInput): Promise<Product> =>
  apiPost("/v1/products", input);

export const updateProduct = (
  id: string,
  input: ProductUpdateInput,
): Promise<Product> => apiPatch(`/v1/products/${id}`, input);

// Operações de ciclo de vida e revisão (exigem a `version` actual).
export const archiveProduct = (
  id: string,
  expectedVersion: number,
): Promise<Product> =>
  apiPost(`/v1/products/${id}/archive`, { expected_version: expectedVersion });

export const reactivateProduct = (
  id: string,
  expectedVersion: number,
): Promise<Product> =>
  apiPost(`/v1/products/${id}/reactivate`, {
    expected_version: expectedVersion,
  });

export const markReviewed = (
  id: string,
  expectedVersion: number,
): Promise<Product> =>
  apiPost(`/v1/products/${id}/mark-reviewed`, {
    expected_version: expectedVersion,
  });
