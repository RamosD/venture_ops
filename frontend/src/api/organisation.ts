import { apiGet, apiPatch, apiPost } from "./client";

export interface Organisation {
  id: string;
  name: string;
  status: string;
}

export interface OrganisationState {
  organisation: Organisation | null;
  onboarding_required: boolean;
}

export const getOrganisation = (): Promise<OrganisationState> =>
  apiGet("/v1/organisation");

export const completeOnboarding = (name: string): Promise<Organisation> =>
  apiPost("/v1/onboarding", { name });

export const updateOrganisation = (name: string): Promise<Organisation> =>
  apiPatch("/v1/organisation", { name });
