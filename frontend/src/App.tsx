import { useState } from "react";

import { AuthProvider, useAuth } from "./auth/AuthContext";
import { AuthenticatedArea } from "./components/AuthenticatedArea";
import { LoginForm } from "./components/LoginForm";
import { OrganisationGate } from "./components/OrganisationGate";
import { ProfilePanel } from "./components/ProfilePanel";
import { RecoveryPanel } from "./components/RecoveryPanel";
import { SystemStatus } from "./components/SystemStatus";

function UnauthenticatedView() {
  const [view, setView] = useState<"login" | "recovery">("login");
  if (view === "recovery") {
    return <RecoveryPanel onBack={() => setView("login")} />;
  }
  return (
    <>
      <LoginForm />
      <button type="button" onClick={() => setView("recovery")}>
        Recuperar acesso
      </button>
    </>
  );
}

function Shell() {
  const { status, notice } = useAuth();

  return (
    <main>
      <h1>VentureOps AI</h1>
      {notice && <p role="status">{notice}</p>}
      {status === "loading" && <p role="status">A carregar…</p>}
      {status === "anon" && <UnauthenticatedView />}
      {status === "authed" && (
        <>
          <AuthenticatedArea />
          <OrganisationGate />
          <ProfilePanel />
        </>
      )}
      <SystemStatus />
    </main>
  );
}

export function App() {
  return (
    <AuthProvider>
      <Shell />
    </AuthProvider>
  );
}
