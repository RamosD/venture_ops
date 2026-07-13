import { useEffect, useState, type FormEvent } from "react";

import { ApiError } from "../api/client";
import { getProfile, updateProfile } from "../api/profile";

export function ProfilePanel() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    let active = true;
    getProfile()
      .then((p) => {
        if (!active) return;
        setName(p.name);
        setEmail(p.email);
      })
      .catch(() => active && setError("Não foi possível carregar o perfil."));
    return () => {
      active = false;
    };
  }, []);

  async function handleSave(event: FormEvent) {
    event.preventDefault();
    if (busy) return;
    setBusy(true);
    setError(null);
    setMessage(null);
    try {
      const updated = await updateProfile({ name: name.trim(), email: email.trim() });
      setName(updated.name);
      setEmail(updated.email);
      setMessage("Perfil actualizado.");
    } catch (e: unknown) {
      setError(
        e instanceof ApiError && e.status === 400
          ? "Esse email já está em uso."
          : "Não foi possível actualizar o perfil.",
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <section aria-labelledby="profile-title">
      <h3 id="profile-title">Perfil</h3>
      {message && <p role="status">{message}</p>}
      {error && <p role="alert">{error}</p>}
      <form onSubmit={handleSave}>
        <label>
          Nome
          <input value={name} onChange={(e) => setName(e.target.value)} />
        </label>
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
          {busy ? "A guardar…" : "Guardar"}
        </button>
      </form>
    </section>
  );
}
