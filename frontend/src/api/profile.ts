import { apiGet, apiPatch } from "./client";
import type { AuthUser } from "./auth";

export const getProfile = (): Promise<AuthUser> => apiGet("/v1/profile");

export const updateProfile = (changes: {
  name?: string;
  email?: string;
}): Promise<AuthUser> => apiPatch("/v1/profile", changes);
