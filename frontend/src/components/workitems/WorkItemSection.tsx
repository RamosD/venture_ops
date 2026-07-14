import { useCallback, useEffect, useState } from "react";

import {
  getWorkItem,
  listWorkItems,
  WORK_TYPES,
  type WorkItem,
  type WorkStatus,
  type WorkType,
} from "../../api/workItems";
import { WorkItemDetail } from "./WorkItemDetail";
import { WorkItemForm } from "./WorkItemForm";
import { WorkItemList } from "./WorkItemList";
import { workTypeLabel } from "./labels";

interface Props {
  productId: string;
}

type View =
  | { kind: "list" }
  | { kind: "create" }
  | { kind: "detail"; item: WorkItem }
  | { kind: "edit"; item: WorkItem };

type LoadState = "loading" | "ready" | "error";
type StatusFilter = WorkStatus | "all";
type TypeFilter = WorkType | "all";

interface PageInfo {
  count: number;
  page: number;
  page_size: number;
  num_pages: number;
}

// Secção de Pendências na ficha do produto. Lista curta com filtros mínimos
// (estado, tipo, vencidas). Sem quadro kanban, sprint, backlog ou dependências.
export function WorkItemSection({ productId }: Props) {
  const [items, setItems] = useState<WorkItem[]>([]);
  const [loadState, setLoadState] = useState<LoadState>("loading");
  const [view, setView] = useState<View>({ kind: "list" });
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("all");
  const [typeFilter, setTypeFilter] = useState<TypeFilter>("all");
  const [onlyOverdue, setOnlyOverdue] = useState(false);
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
      const response = await listWorkItems({
        product: productId,
        status: statusFilter === "all" ? undefined : statusFilter,
        work_type: typeFilter === "all" ? undefined : typeFilter,
        overdue: onlyOverdue || undefined,
        page,
      });
      setItems(response.results);
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
  }, [productId, statusFilter, typeFilter, onlyOverdue, page]);

  useEffect(() => {
    void reload();
  }, [reload]);

  const openDetail = useCallback(async (id: string) => {
    const item = await getWorkItem(id);
    setView({ kind: "detail", item });
  }, []);

  function resetPage<T>(setter: (v: T) => void) {
    return (v: T) => {
      setter(v);
      setPage(1);
    };
  }

  return (
    <section aria-labelledby="workitems-title">
      <h4 id="workitems-title">Pendências</h4>

      {view.kind === "list" && (
        <>
          <button type="button" onClick={() => setView({ kind: "create" })}>
            Nova pendência
          </button>

          <div role="group" aria-label="Filtros de pendências">
            <label>
              Estado
              <select
                value={statusFilter}
                onChange={(e) =>
                  resetPage(setStatusFilter)(e.target.value as StatusFilter)
                }
              >
                <option value="all">Todos</option>
                <option value="open">Abertas</option>
                <option value="completed">Concluídas</option>
                <option value="cancelled">Canceladas</option>
              </select>
            </label>{" "}
            <label>
              Tipo
              <select
                value={typeFilter}
                onChange={(e) =>
                  resetPage(setTypeFilter)(e.target.value as TypeFilter)
                }
              >
                <option value="all">Todos os tipos</option>
                {WORK_TYPES.map((t) => (
                  <option key={t} value={t}>
                    {workTypeLabel(t)}
                  </option>
                ))}
              </select>
            </label>{" "}
            <label>
              <input
                type="checkbox"
                checked={onlyOverdue}
                onChange={(e) => resetPage(setOnlyOverdue)(e.target.checked)}
              />
              Apenas vencidas
            </label>
          </div>

          {loadState === "loading" && <p role="status">A carregar pendências…</p>}
          {loadState === "error" && (
            <p role="alert">
              Não foi possível carregar as pendências.{" "}
              <button type="button" onClick={() => void reload()}>
                Tentar novamente
              </button>
            </p>
          )}
          {loadState === "ready" && (
            <>
              <WorkItemList
                items={items}
                onSelect={(item) => void openDetail(item.id)}
              />
              <div role="group" aria-label="Paginação de pendências">
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
        <WorkItemForm
          productId={productId}
          onDone={(item) => {
            void reload();
            setView({ kind: "detail", item });
          }}
          onCancel={() => setView({ kind: "list" })}
        />
      )}

      {view.kind === "detail" && (
        <WorkItemDetail
          item={view.item}
          onEdit={(item) => setView({ kind: "edit", item })}
          onChanged={(item) => {
            void reload();
            setView({ kind: "detail", item });
          }}
          onBack={() => {
            void reload();
            setView({ kind: "list" });
          }}
        />
      )}

      {view.kind === "edit" && (
        <WorkItemForm
          productId={productId}
          item={view.item}
          onDone={(item) => {
            void reload();
            setView({ kind: "detail", item });
          }}
          onCancel={() => setView({ kind: "detail", item: view.item })}
        />
      )}
    </section>
  );
}
