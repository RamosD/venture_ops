import { useCallback, useEffect, useState } from "react";

import { ApiError } from "../../api/client";
import {
  ACTOR_TYPES,
  deactivateFunction,
  listFunctions,
  reactivateFunction,
  type ActorType,
  type FunctionProfile,
  type FunctionStatusFilter,
} from "../../api/functions";
import { FunctionForm } from "./FunctionForm";
import { actorTypeLabel, functionStatusLabel } from "./labels";

type View =
  | { kind: "list" }
  | { kind: "create" }
  | { kind: "detail"; fn: FunctionProfile }
  | { kind: "edit"; fn: FunctionProfile };

type LoadState = "loading" | "ready" | "error";

interface PageInfo {
  count: number;
  page: number;
  page_size: number;
  num_pages: number;
}

// Área empresarial de funções (catálogo reutilizável em execuções futuras).
// Sem router dedicado nem store global: um estado de vista local alterna entre
// lista, criação, detalhe e edição. Reutiliza o cliente HTTP central (sessão +
// CSRF). As funções não pertencem a um produto — são empresariais.
export function FunctionsWorkspace() {
  const [functions, setFunctions] = useState<FunctionProfile[]>([]);
  const [loadState, setLoadState] = useState<LoadState>("loading");
  const [view, setView] = useState<View>({ kind: "list" });

  const [statusFilter, setStatusFilter] = useState<FunctionStatusFilter>("active");
  const [actorFilter, setActorFilter] = useState<ActorType | "all">("all");
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
      const response = await listFunctions({
        status: statusFilter,
        actor_type: actorFilter === "all" ? undefined : actorFilter,
        page,
      });
      setFunctions(response.results);
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
  }, [statusFilter, actorFilter, page]);

  useEffect(() => {
    void reload();
  }, [reload]);

  const handleSaved = useCallback(
    (fn: FunctionProfile) => {
      void reload();
      setView({ kind: "detail", fn });
    },
    [reload],
  );

  function changeStatus(next: FunctionStatusFilter) {
    setStatusFilter(next);
    setPage(1);
  }
  function changeActor(next: ActorType | "all") {
    setActorFilter(next);
    setPage(1);
  }

  return (
    <section aria-labelledby="functions-title">
      <h2 id="functions-title">Funções</h2>

      {view.kind === "list" && (
        <>
          <button type="button" onClick={() => setView({ kind: "create" })}>
            Nova função
          </button>

          <div role="group" aria-label="Filtros das funções">
            <label>
              Estado
              <select
                value={statusFilter}
                onChange={(e) =>
                  changeStatus(e.target.value as FunctionStatusFilter)
                }
              >
                <option value="active">Activas</option>
                <option value="inactive">Inactivas</option>
                <option value="all">Todas</option>
              </select>
            </label>{" "}
            <label>
              Tipo
              <select
                value={actorFilter}
                onChange={(e) => changeActor(e.target.value as ActorType | "all")}
              >
                <option value="all">Todos</option>
                {ACTOR_TYPES.map((t) => (
                  <option key={t} value={t}>
                    {actorTypeLabel(t)}
                  </option>
                ))}
              </select>
            </label>
          </div>

          {loadState === "loading" && <p role="status">A carregar funções…</p>}
          {loadState === "error" && (
            <p role="alert">
              Não foi possível carregar as funções.{" "}
              <button type="button" onClick={() => void reload()}>
                Tentar novamente
              </button>
            </p>
          )}
          {loadState === "ready" && (
            <>
              {functions.length === 0 ? (
                <p>Ainda não há funções para este filtro.</p>
              ) : (
                <ul>
                  {functions.map((fn) => (
                    <li key={fn.id}>
                      <button
                        type="button"
                        onClick={() => setView({ kind: "detail", fn })}
                      >
                        {fn.name}
                      </button>{" "}
                      <span>{actorTypeLabel(fn.actor_type)}</span>
                      {fn.status === "inactive" && (
                        <span data-testid="inactive-badge"> (Inactiva)</span>
                      )}
                    </li>
                  ))}
                </ul>
              )}
              <div role="group" aria-label="Paginação">
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
        <FunctionForm
          onDone={handleSaved}
          onCancel={() => setView({ kind: "list" })}
        />
      )}

      {view.kind === "edit" && (
        <FunctionForm
          fn={view.fn}
          onDone={handleSaved}
          onCancel={() => setView({ kind: "detail", fn: view.fn })}
        />
      )}

      {view.kind === "detail" && (
        <FunctionDetail
          fn={view.fn}
          onEdit={(fn) => setView({ kind: "edit", fn })}
          onBack={() => {
            void reload();
            setView({ kind: "list" });
          }}
          onChanged={(fn) => setView({ kind: "detail", fn })}
        />
      )}
    </section>
  );
}

function FunctionDetail({
  fn,
  onEdit,
  onBack,
  onChanged,
}: {
  fn: FunctionProfile;
  onEdit: (fn: FunctionProfile) => void;
  onBack: () => void;
  onChanged: (fn: FunctionProfile) => void;
}) {
  const [confirmingDeactivate, setConfirmingDeactivate] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const isActive = fn.status === "active";

  async function runDeactivate() {
    if (busy) return;
    setBusy(true);
    setError(null);
    try {
      const updated = await deactivateFunction(fn.id, fn.version);
      setConfirmingDeactivate(false);
      onChanged(updated);
    } catch (e: unknown) {
      setError(
        e instanceof ApiError && e.status === 409
          ? "A função foi alterada entretanto; recarregue."
          : "Não foi possível inactivar a função.",
      );
    } finally {
      setBusy(false);
    }
  }

  async function runReactivate() {
    if (busy) return;
    setBusy(true);
    setError(null);
    try {
      const updated = await reactivateFunction(fn.id, fn.version);
      onChanged(updated);
    } catch (e: unknown) {
      setError(
        e instanceof ApiError && e.status === 409
          ? "A função foi alterada entretanto; recarregue."
          : "Não foi possível reactivar a função.",
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <section aria-labelledby="function-detail-title">
      <h3 id="function-detail-title">{fn.name}</h3>
      {fn.status === "inactive" && (
        <p data-testid="inactive-badge">
          <strong>Função inactiva</strong> — não seleccionável em novas execuções.
        </p>
      )}
      {error && <p role="alert">{error}</p>}
      <dl>
        <dt>Tipo</dt>
        <dd>{actorTypeLabel(fn.actor_type)}</dd>
        <dt>Estado</dt>
        <dd>{functionStatusLabel(fn.status)}</dd>
        <dt>Propósito</dt>
        <dd>{fn.purpose}</dd>
        <dt>Responsabilidades</dt>
        <dd>{fn.responsibilities}</dd>
        <dt>Limites</dt>
        <dd>{fn.constraints || "—"}</dd>
        <dt>Requer aprovação humana</dt>
        <dd>{fn.requires_approval ? "Sim" : "Não"}</dd>
        <dt>Documento de instruções</dt>
        <dd>{fn.instruction_document ? "Associado" : "—"}</dd>
      </dl>

      <p>
        <button type="button" onClick={() => onEdit(fn)} disabled={busy}>
          Editar
        </button>{" "}
        {isActive ? (
          confirmingDeactivate ? (
            <>
              <button type="button" onClick={runDeactivate} disabled={busy}>
                Confirmar inactivação
              </button>{" "}
              <button
                type="button"
                onClick={() => setConfirmingDeactivate(false)}
                disabled={busy}
              >
                Cancelar
              </button>
            </>
          ) : (
            <button
              type="button"
              onClick={() => setConfirmingDeactivate(true)}
              disabled={busy}
            >
              Inactivar
            </button>
          )
        ) : (
          <button type="button" onClick={runReactivate} disabled={busy}>
            Reactivar
          </button>
        )}{" "}
        <button type="button" onClick={onBack} disabled={busy}>
          Voltar
        </button>
      </p>
    </section>
  );
}
