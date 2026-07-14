import { useCallback, useEffect, useState } from "react";

import {
  getDecision,
  listDecisions,
  type Decision,
  type DecisionStatus,
} from "../../api/decisions";
import { DecisionDetail } from "./DecisionDetail";
import { DecisionForm } from "./DecisionForm";
import { DecisionList } from "./DecisionList";

interface Props {
  productId: string;
}

type View =
  | { kind: "list" }
  | { kind: "create" }
  | { kind: "detail"; decision: Decision }
  | { kind: "supersede"; decision: Decision };

type LoadState = "loading" | "ready" | "error";
type StatusFilter = DecisionStatus | "all";

interface PageInfo {
  count: number;
  page: number;
  page_size: number;
  num_pages: number;
}

// Secção de Decisões na ficha do produto. Container local (sem store/router),
// alternando entre lista, criação, detalhe e substituição. A lista filtra pelo
// produto actual e por estado; o histórico (substituídas) permanece visível.
export function DecisionSection({ productId }: Props) {
  const [decisions, setDecisions] = useState<Decision[]>([]);
  const [loadState, setLoadState] = useState<LoadState>("loading");
  const [view, setView] = useState<View>({ kind: "list" });
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("all");
  const [page, setPage] = useState(1);
  const [pageInfo, setPageInfo] = useState<PageInfo>({
    count: 0,
    page: 1,
    page_size: 20,
    num_pages: 1,
  });

  const reload = useCallback(async () => {
    setLoadState((prev) => (prev === "ready" ? prev : "loading"));
    try {
      const response = await listDecisions({
        product: productId,
        status: statusFilter === "all" ? undefined : statusFilter,
        page,
      });
      setDecisions(response.results);
      setPageInfo({
        count: response.count ?? response.results.length,
        page: response.page ?? 1,
        page_size: response.page_size ?? response.results.length,
        num_pages: response.num_pages ?? 1,
      });
      setLoadState("ready");
    } catch {
      setLoadState("error");
    }
  }, [productId, statusFilter, page]);

  useEffect(() => {
    void reload();
  }, [reload]);

  const openDetail = useCallback(async (id: string) => {
    const decision = await getDecision(id);
    setView({ kind: "detail", decision });
  }, []);

  function changeStatus(next: StatusFilter) {
    setStatusFilter(next);
    setPage(1);
  }

  return (
    <section aria-labelledby="decisions-title">
      <h4 id="decisions-title">Decisões</h4>

      {view.kind === "list" && (
        <>
          <button type="button" onClick={() => setView({ kind: "create" })}>
            Nova decisão
          </button>

          <div role="group" aria-label="Filtros de decisões">
            <label>
              Estado
              <select
                value={statusFilter}
                onChange={(e) => changeStatus(e.target.value as StatusFilter)}
              >
                <option value="all">Todas</option>
                <option value="active">Activas</option>
                <option value="superseded">Substituídas</option>
              </select>
            </label>
          </div>

          {loadState === "loading" && <p role="status">A carregar decisões…</p>}
          {loadState === "error" && (
            <p role="alert">
              Não foi possível carregar as decisões.{" "}
              <button type="button" onClick={() => void reload()}>
                Tentar novamente
              </button>
            </p>
          )}
          {loadState === "ready" && (
            <>
              <DecisionList
                decisions={decisions}
                onSelect={(d) => void openDetail(d.id)}
              />
              <div role="group" aria-label="Paginação de decisões">
                <button
                  type="button"
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={pageInfo.page <= 1}
                >
                  Anterior
                </button>{" "}
                <span>
                  Página {pageInfo.page} de {pageInfo.num_pages}
                </span>{" "}
                <button
                  type="button"
                  onClick={() => setPage((p) => p + 1)}
                  disabled={pageInfo.page >= pageInfo.num_pages}
                >
                  Seguinte
                </button>
              </div>
            </>
          )}
        </>
      )}

      {view.kind === "create" && (
        <DecisionForm
          productId={productId}
          onDone={(decision) => {
            void reload();
            setView({ kind: "detail", decision });
          }}
          onCancel={() => setView({ kind: "list" })}
        />
      )}

      {view.kind === "detail" && (
        <DecisionDetail
          decision={view.decision}
          onSupersede={(decision) => setView({ kind: "supersede", decision })}
          onOpenChain={(id) => void openDetail(id)}
          onBack={() => {
            void reload();
            setView({ kind: "list" });
          }}
        />
      )}

      {view.kind === "supersede" && (
        <DecisionForm
          productId={productId}
          supersedes={view.decision}
          onDone={(decision) => {
            void reload();
            setView({ kind: "detail", decision });
          }}
          onCancel={() => setView({ kind: "detail", decision: view.decision })}
        />
      )}
    </section>
  );
}
