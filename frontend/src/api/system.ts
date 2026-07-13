import { apiGet } from "./client";

export interface SystemPingResponse {
  status: string;
}

// Smoke test técnico de integração frontend–backend (não substitui os health
// checks de PR05).
export function pingSystem(): Promise<SystemPingResponse> {
  return apiGet<SystemPingResponse>("/system/ping");
}
