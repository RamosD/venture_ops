import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { ProfilePanel } from "./ProfilePanel";
import { RecoveryPanel } from "./RecoveryPanel";

function json(data: unknown, status = 200): Response {
  return new Response(status === 204 ? null : JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

describe("RecoveryPanel", () => {
  afterEach(() => vi.restoreAllMocks());

  it("mostra mensagem genérica ao pedir recuperação", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (url: string) => {
        if (url.endsWith("/password/reset-request")) {
          return json({
            detail:
              "Se existir uma conta com esse email, enviámos instruções de recuperação.",
          });
        }
        return json({ detail: "nf" }, 404);
      }),
    );
    render(<RecoveryPanel onBack={() => {}} />);
    fireEvent.change(screen.getByLabelText("Email"), {
      target: { value: "owner@x.pt" },
    });
    fireEvent.click(screen.getByRole("button", { name: /enviar instruções/i }));
    expect(await screen.findByRole("status")).toHaveTextContent(
      "enviámos instruções",
    );
    // Avança para o passo de confirmação (token + nova palavra-passe).
    expect(
      await screen.findByLabelText("Token de recuperação"),
    ).toBeInTheDocument();
  });
});

describe("ProfilePanel", () => {
  afterEach(() => vi.restoreAllMocks());

  it("carrega e edita o próprio perfil", async () => {
    let name = "Dono";
    vi.stubGlobal(
      "fetch",
      vi.fn(async (url: string, init: RequestInit = {}) => {
        if (url.endsWith("/v1/profile") && (init.method ?? "GET") === "GET") {
          return json({ id: "u1", email: "owner@x.pt", name });
        }
        if (url.endsWith("/v1/profile") && init.method === "PATCH") {
          name = JSON.parse(init.body as string).name;
          return json({ id: "u1", email: "owner@x.pt", name });
        }
        return json({ detail: "nf" }, 404);
      }),
    );
    render(<ProfilePanel />);
    const nameInput = (await screen.findByLabelText("Nome")) as HTMLInputElement;
    expect(nameInput.value).toBe("Dono");
    fireEvent.change(nameInput, { target: { value: "Novo Nome" } });
    fireEvent.click(screen.getByRole("button", { name: /guardar/i }));
    expect(await screen.findByRole("status")).toHaveTextContent(
      "Perfil actualizado.",
    );
  });
});
