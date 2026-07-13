import { apiGet, apiPost } from "./client";

export interface AuthUser {
  id: string;
  email: string;
  name: string;
}

export interface SessionState {
  authenticated: boolean;
  user?: AuthUser;
}

// Contratos reais de PR07 (montados sob /api/v1/auth/).
export const fetchCsrf = (): Promise<{ detail: string }> =>
  apiGet("/v1/auth/csrf");

export const fetchSession = (): Promise<SessionState> =>
  apiGet("/v1/auth/session");

export const login = (email: string, password: string): Promise<AuthUser> =>
  apiPost("/v1/auth/login", { email, password });

export const logout = (): Promise<void> => apiPost("/v1/auth/logout");

export const requestPasswordReset = (
  email: string,
): Promise<{ detail: string }> =>
  apiPost("/v1/auth/password/reset-request", { email });

export const confirmPasswordReset = (
  token: string,
  newPassword: string,
): Promise<{ detail: string }> =>
  apiPost("/v1/auth/password/reset-confirm", {
    token,
    new_password: newPassword,
  });
