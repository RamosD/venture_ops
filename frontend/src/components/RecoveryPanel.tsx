import { useState, type FormEvent } from "react";

import { ApiError } from "../api/client";
import { confirmPasswordReset, requestPasswordReset } from "../api/auth";

export function RecoveryPanel({ onBack }: { onBack: () => void }) {
  const [step, setStep] = useState<"request" | "confirm">("request");
  const [email, setEmail] = useState("");
  const [token, setToken] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function handleRequest(event: FormEvent) {
    event.preventDefault();
    if (busy) return;
    setBusy(true);
    setError(null);
    try {
      const res = await requestPasswordReset(email.trim());
      setMessage(res.detail);
      setStep("confirm");
    } catch {
      // Resposta genérica mesmo em erro; segue para o passo de confirmação.
      setMessage(
        "Se existir uma conta com esse email, enviámos instruções de recuperação.",
      );
      setStep("confirm");
    } finally {
      setBusy(false);
    }
  }

  async function handleConfirm(event: FormEvent) {
    event.preventDefault();
    if (busy) return;
    setBusy(true);
    setError(null);
    try {
      const res = await confirmPasswordReset(token.trim(), newPassword);
      setMessage(res.detail + " Já pode iniciar sessão.");
      setNewPassword("");
    } catch (e: unknown) {
      setError(
        e instanceof ApiError && e.status === 400
          ? "Token inválido, expirado ou já utilizado."
          : "Não foi possível redefinir a palavra-passe.",
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <section aria-labelledby="recovery-title">
      <h2 id="recovery-title">Recuperar acesso</h2>
      {message && <p role="status">{message}</p>}
      {error && <p role="alert">{error}</p>}

      {step === "request" ? (
        <form onSubmit={handleRequest}>
          <label>
            Email
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </label>
          <button type="submit" disabled={busy}>
            {busy ? "A enviar…" : "Enviar instruções"}
          </button>
        </form>
      ) : (
        <form onSubmit={handleConfirm}>
          <label>
            Token de recuperação
            <input
              type="text"
              value={token}
              onChange={(e) => setToken(e.target.value)}
              required
            />
          </label>
          <label>
            Nova palavra-passe
            <input
              type="password"
              autoComplete="new-password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              required
            />
          </label>
          <button type="submit" disabled={busy}>
            {busy ? "A redefinir…" : "Redefinir palavra-passe"}
          </button>
        </form>
      )}

      <button type="button" onClick={onBack}>
        Voltar ao login
      </button>
    </section>
  );
}
