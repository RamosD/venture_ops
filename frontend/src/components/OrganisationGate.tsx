import { useCallback, useEffect, useState, type FormEvent } from "react";

import { ApiError } from "../api/client";
import {
  completeOnboarding,
  getOrganisation,
  updateOrganisation,
  type Organisation,
} from "../api/organisation";
import { PortfolioWorkspace } from "./portfolio/PortfolioWorkspace";

type GateState =
  | { kind: "loading" }
  | { kind: "onboarding" }
  | { kind: "ready"; organisation: Organisation };

// Decide entre onboarding (sem empresa) e painel da empresa (com empresa).
export function OrganisationGate() {
  const [state, setState] = useState<GateState>({ kind: "loading" });
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const result = await getOrganisation();
      if (result.organisation) {
        setState({ kind: "ready", organisation: result.organisation });
      } else {
        setState({ kind: "onboarding" });
      }
    } catch {
      setError("Não foi possível carregar a empresa.");
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  if (error) return <p role="alert">{error}</p>;
  if (state.kind === "loading") return <p role="status">A carregar empresa…</p>;
  if (state.kind === "onboarding") return <OnboardingForm onDone={load} />;
  // Com empresa: painel da empresa + área de portefólio (depois do onboarding).
  return (
    <>
      <OrganisationPanel organisation={state.organisation} onUpdated={load} />
      <PortfolioWorkspace />
    </>
  );
}

function OnboardingForm({ onDone }: { onDone: () => void }) {
  const [name, setName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (busy) return;
    setBusy(true);
    setError(null);
    try {
      await completeOnboarding(name.trim());
      onDone();
    } catch (e: unknown) {
      setError(
        e instanceof ApiError && e.status === 409
          ? "Já existe uma empresa associada a esta conta."
          : "Não foi possível criar a empresa.",
      );
      setBusy(false);
    }
  }

  return (
    <section aria-labelledby="onboarding-title">
      <h2 id="onboarding-title">Criar a sua empresa</h2>
      <p>Para começar, dê um nome à sua empresa.</p>
      {error && <p role="alert">{error}</p>}
      <form onSubmit={handleSubmit}>
        <label>
          Nome da empresa
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </label>
        <button type="submit" disabled={busy}>
          {busy ? "A criar…" : "Criar empresa"}
        </button>
      </form>
    </section>
  );
}

function OrganisationPanel({
  organisation,
  onUpdated,
}: {
  organisation: Organisation;
  onUpdated: () => void;
}) {
  const [name, setName] = useState(organisation.name);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function handleSave(event: FormEvent) {
    event.preventDefault();
    if (busy) return;
    setBusy(true);
    setError(null);
    setMessage(null);
    try {
      await updateOrganisation(name.trim());
      setMessage("Empresa actualizada.");
      onUpdated();
    } catch (e: unknown) {
      setError(
        e instanceof ApiError && e.status === 403
          ? "Apenas o Owner pode editar a empresa."
          : "Não foi possível actualizar a empresa.",
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <section aria-labelledby="org-title">
      <h2 id="org-title">Empresa</h2>
      <p>
        Estado: <strong>{organisation.status}</strong>
      </p>
      {message && <p role="status">{message}</p>}
      {error && <p role="alert">{error}</p>}
      <form onSubmit={handleSave}>
        <label>
          Nome da empresa
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </label>
        <button type="submit" disabled={busy}>
          {busy ? "A guardar…" : "Guardar"}
        </button>
      </form>
    </section>
  );
}
