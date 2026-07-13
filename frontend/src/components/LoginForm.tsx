import { useState, type FormEvent } from "react";

import { useAuth } from "../auth/AuthContext";

export function LoginForm() {
  const { signIn } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (submitting) return; // prevenção de submissão duplicada
    setSubmitting(true);
    setError(null);
    const result = await signIn(email.trim(), password);
    if (!result.ok) {
      setError(result.error ?? "Não foi possível iniciar sessão.");
      setPassword("");
    }
    setSubmitting(false);
  }

  return (
    <form onSubmit={handleSubmit} aria-labelledby="login-title">
      <h2 id="login-title">Iniciar sessão</h2>
      <label>
        Email
        <input
          type="email"
          name="email"
          autoComplete="username"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
      </label>
      <label>
        Palavra-passe
        <input
          type="password"
          name="password"
          autoComplete="current-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
      </label>
      {error && <p role="alert">{error}</p>}
      <button type="submit" disabled={submitting}>
        {submitting ? "A entrar…" : "Entrar"}
      </button>
    </form>
  );
}
