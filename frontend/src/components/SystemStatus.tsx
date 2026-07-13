import { useEffect, useState } from "react";

import { pingSystem } from "../api/system";

type PingState =
  | { kind: "loading" }
  | { kind: "available"; status: string }
  | { kind: "error"; message: string };

// Indicador técnico do backend (smoke). Distinto da autenticação.
export function SystemStatus() {
  const [state, setState] = useState<PingState>({ kind: "loading" });

  useEffect(() => {
    let active = true;
    pingSystem()
      .then((r) => active && setState({ kind: "available", status: r.status }))
      .catch(
        (e: unknown) =>
          active &&
          setState({
            kind: "error",
            message: e instanceof Error ? e.message : "Erro desconhecido.",
          }),
      );
    return () => {
      active = false;
    };
  }, []);

  return (
    <footer aria-live="polite">
      {state.kind === "loading" && <small role="status">Backend: a verificar…</small>}
      {state.kind === "available" && (
        <small role="status">Backend: {state.status}</small>
      )}
      {state.kind === "error" && (
        <small role="alert">Backend indisponível: {state.message}</small>
      )}
    </footer>
  );
}
