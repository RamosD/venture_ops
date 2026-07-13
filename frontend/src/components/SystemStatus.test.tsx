import { render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { SystemStatus } from "./SystemStatus";

describe("SystemStatus — /api/system/ping", () => {
  afterEach(() => vi.restoreAllMocks());

  it("apresenta o estado do backend quando o ping responde ok", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(
        async () =>
          new Response(JSON.stringify({ status: "ok" }), {
            status: 200,
            headers: { "Content-Type": "application/json" },
          }),
      ),
    );
    render(<SystemStatus />);
    await waitFor(() =>
      expect(screen.getByRole("status")).toHaveTextContent("Backend: ok"),
    );
    expect(fetch).toHaveBeenCalledWith(
      "/api/system/ping",
      expect.objectContaining({ method: "GET" }),
    );
  });

  it("trata a falha de comunicação", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => {
        throw new Error("network down");
      }),
    );
    render(<SystemStatus />);
    await waitFor(() =>
      expect(screen.getByRole("alert")).toHaveTextContent("Backend indisponível"),
    );
  });
});
