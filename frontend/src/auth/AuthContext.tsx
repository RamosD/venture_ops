import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";

import { ApiError, setUnauthorizedHandler } from "../api/client";
import {
  fetchCsrf,
  fetchSession,
  login as apiLogin,
  logout as apiLogout,
  type AuthUser,
} from "../api/auth";

type Status = "loading" | "anon" | "authed";

interface SignInResult {
  ok: boolean;
  error?: string;
}

interface AuthContextValue {
  status: Status;
  user: AuthUser | null;
  notice: string | null;
  signIn: (email: string, password: string) => Promise<SignInResult>;
  signOut: () => Promise<void>;
  refresh: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

const SESSION_EXPIRED = "A sua sessão expirou. Inicie sessão novamente.";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<Status>("loading");
  const [user, setUser] = useState<AuthUser | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const statusRef = useRef<Status>(status);
  statusRef.current = status;

  const goAnon = useCallback((message: string | null) => {
    setUser(null);
    setStatus("anon");
    setNotice(message);
  }, []);

  const goAuthed = useCallback((nextUser: AuthUser) => {
    setUser(nextUser);
    setStatus("authed");
    setNotice(null);
  }, []);

  // Sessão expirada: só relevante quando julgávamos estar autenticados.
  useEffect(() => {
    setUnauthorizedHandler(() => {
      if (statusRef.current === "authed") goAnon(SESSION_EXPIRED);
    });
    return () => setUnauthorizedHandler(null);
  }, [goAnon]);

  const refresh = useCallback(async () => {
    try {
      const session = await fetchSession();
      if (session.authenticated && session.user) {
        goAuthed(session.user);
      } else if (statusRef.current === "authed") {
        goAnon(SESSION_EXPIRED);
      } else {
        goAnon(null);
      }
    } catch {
      goAnon(null);
    }
  }, [goAnon, goAuthed]);

  // Arranque: prepara o cookie CSRF e determina a sessão actual.
  useEffect(() => {
    let active = true;
    (async () => {
      try {
        await fetchCsrf();
      } catch {
        /* segue mesmo sem CSRF pré-carregado */
      }
      if (!active) return;
      await refresh();
    })();
    return () => {
      active = false;
    };
  }, [refresh]);

  const signIn = useCallback(
    async (email: string, password: string): Promise<SignInResult> => {
      try {
        await fetchCsrf(); // garante token actualizado
        const signedIn = await apiLogin(email, password);
        goAuthed(signedIn);
        return { ok: true };
      } catch (error: unknown) {
        if (error instanceof ApiError && error.status === 401) {
          return { ok: false, error: "Credenciais inválidas." };
        }
        return { ok: false, error: "Não foi possível iniciar sessão." };
      }
    },
    [goAuthed],
  );

  const signOut = useCallback(async () => {
    try {
      await apiLogout();
    } catch {
      /* mesmo que falhe, terminamos a sessão localmente */
    }
    goAnon(null);
  }, [goAnon]);

  return (
    <AuthContext.Provider
      value={{ status, user, notice, signIn, signOut, refresh }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth tem de ser usado dentro de AuthProvider.");
  return ctx;
}
