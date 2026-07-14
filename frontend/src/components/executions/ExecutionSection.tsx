import { useCallback, useEffect, useState } from "react";

import {
  getExecution,
  listExecutions,
  type ExecutionDetail as Execution,
  type ExecutionSummary,
} from "../../api/executions";
import { listFunctions } from "../../api/functions";
import { ExecutionCreateForm } from "./ExecutionCreateForm";
import { ExecutionDetail } from "./ExecutionDetail";
import { ExecutionList } from "./ExecutionList";

interface Props {
  productId: string;
}

type View =
  | { kind: "list" }
  | { kind: "create" }
  | { kind: "detail"; execution: Execution };

type LoadState = "loading" | "ready" | "error";

interface PageInfo {
  count: number;
  page: number;
  page_size: number;
  num_pages: number;
}

// Área de execuções da ficha do produto. Container local (sem store/router). A
// listagem filtra sempre pelo produto actual. Não há edição, eliminação nem
// transições de estado — apenas preparar, listar e consultar o contexto congelado.
export function ExecutionSection({ productId }: Props) {
  const [executions, setExecutions] = useState<ExecutionSummary[]>([]);
  const [functionNames, setFunctionNames] = useState<Record<string, string>>({});
  const [loadState, setLoadState] = useState<LoadState>("loading");
  const [view, setView] = useState<View>({ kind: "list" });
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
      const response = await listExecutions({ product: productId, page });
      setExecutions(response.results);
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
  }, [productId, page]);

  // Nomes das funções (inclui inactivas: execuções passadas podem referenciá-las).
  const loadFunctionNames = useCallback(async () => {
    try {
      const res = await listFunctions({ status: "all", page_size: 100 });
      const map: Record<string, string> = {};
      for (const f of res.results) map[f.id] = f.name;
      setFunctionNames(map);
    } catch {
      /* nomes ausentes: a lista mostra um rótulo genérico */
    }
  }, []);

  useEffect(() => {
    void reload();
  }, [reload]);
  useEffect(() => {
    void loadFunctionNames();
  }, [loadFunctionNames]);

  const openDetail = useCallback(async (summary: ExecutionSummary) => {
    // Só aqui se carrega o detalhe completo (snapshots + contexto).
    const detail = await getExecution(summary.id);
    setView({ kind: "detail", execution: detail });
  }, []);

  return (
    <section aria-labelledby="executions-title">
      <h4 id="executions-title">Execuções</h4>

      {view.kind === "list" && (
        <>
          <button type="button" onClick={() => setView({ kind: "create" })}>
            Preparar execução
          </button>

          {loadState === "loading" && <p role="status">A carregar execuções…</p>}
          {loadState === "error" && (
            <p role="alert">
              Não foi possível carregar as execuções.{" "}
              <button type="button" onClick={() => void reload()}>
                Tentar novamente
              </button>
            </p>
          )}
          {loadState === "ready" && (
            <>
              <ExecutionList
                executions={executions}
                functionNames={functionNames}
                onSelect={(execution) => void openDetail(execution)}
              />
              <div role="group" aria-label="Paginação de execuções">
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
        <ExecutionCreateForm
          productId={productId}
          onCreated={(execution) => {
            void reload();
            void loadFunctionNames();
            setView({ kind: "detail", execution });
          }}
          onCancel={() => setView({ kind: "list" })}
        />
      )}

      {view.kind === "detail" && (
        <ExecutionDetail
          execution={view.execution}
          onBack={() => {
            void reload();
            setView({ kind: "list" });
          }}
        />
      )}
    </section>
  );
}
