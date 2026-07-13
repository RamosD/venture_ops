import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { AuthProvider } from "../auth/AuthContext";
import { OrganisationGate } from "./OrganisationGate";

function json(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

// Respostas de autenticação/portefólio comuns: com empresa pronta, o
// OrganisationGate passa a montar também a área de portefólio (que usa o
// AuthContext e lista produtos). Estes handlers mantêm o teste focado na empresa.
function authAndPortfolio(url: string): Response | null {
  if (url.endsWith("/v1/auth/csrf")) return json({ detail: "ok" });
  if (url.endsWith("/v1/auth/session"))
    return json({
      authenticated: true,
      user: { id: "u1", email: "owner@x.pt", name: "Owner" },
    });
  if (url.includes("/v1/products"))
    return json({ results: [], count: 0, page: 1, page_size: 20, num_pages: 1 });
  return null;
}

function renderGate() {
  return render(
    <AuthProvider>
      <OrganisationGate />
    </AuthProvider>,
  );
}

describe("OrganisationGate", () => {
  afterEach(() => {
    vi.restoreAllMocks();
    document.cookie = "csrftoken=t";
  });

  it("mostra onboarding sem empresa e conclui a criação", async () => {
    let hasOrg = false;
    vi.stubGlobal(
      "fetch",
      vi.fn(async (url: string, init: RequestInit = {}) => {
        if (url.endsWith("/v1/organisation") && (init.method ?? "GET") === "GET") {
          return hasOrg
            ? json({
                organisation: { id: "o1", name: "Minha Empresa", status: "active" },
                onboarding_required: false,
              })
            : json({ organisation: null, onboarding_required: true });
        }
        if (url.endsWith("/v1/onboarding") && init.method === "POST") {
          hasOrg = true;
          return json({ id: "o1", name: "Minha Empresa", status: "active" }, 201);
        }
        return authAndPortfolio(url) ?? json({ detail: "nf" }, 404);
      }),
    );

    renderGate();
    fireEvent.change(await screen.findByLabelText("Nome da empresa"), {
      target: { value: "Minha Empresa" },
    });
    fireEvent.click(screen.getByRole("button", { name: /criar empresa/i }));

    // Após o onboarding, passa a mostrar o painel da empresa.
    expect(await screen.findByRole("heading", { name: "Empresa" })).toBeInTheDocument();
    expect(screen.getByText("active")).toBeInTheDocument();
  });

  it("mostra o painel quando já existe empresa", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (url: string) => {
        if (url.endsWith("/v1/organisation")) {
          return json({
            organisation: { id: "o1", name: "Empresa X", status: "active" },
            onboarding_required: false,
          });
        }
        return authAndPortfolio(url) ?? json({ detail: "nf" }, 404);
      }),
    );
    renderGate();
    const nameInput = (await screen.findByLabelText(
      "Nome da empresa",
    )) as HTMLInputElement;
    expect(nameInput.value).toBe("Empresa X");
  });
});
