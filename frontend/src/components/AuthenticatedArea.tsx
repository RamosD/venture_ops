import { useState } from "react";

import { useAuth } from "../auth/AuthContext";

export function AuthenticatedArea() {
  const { user, signOut, refresh } = useAuth();
  const [busy, setBusy] = useState(false);

  async function handleSignOut() {
    if (busy) return;
    setBusy(true);
    await signOut();
    setBusy(false);
  }

  return (
    <section aria-labelledby="area-title">
      <h2 id="area-title">Área autenticada</h2>
      <p>
        Sessão iniciada como <strong>{user?.email}</strong>.
      </p>
      <button type="button" onClick={() => void refresh()}>
        Verificar sessão
      </button>{" "}
      <button type="button" onClick={handleSignOut} disabled={busy}>
        {busy ? "A terminar…" : "Terminar sessão"}
      </button>
    </section>
  );
}
