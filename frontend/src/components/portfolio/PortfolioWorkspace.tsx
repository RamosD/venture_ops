import { useCallback, useEffect, useState } from "react";

import {
  listProducts,
  type Product,
  type ProductStatusFilter,
} from "../../api/products";
import { useAuth } from "../../auth/AuthContext";
import { ProductCreateForm } from "./ProductCreateForm";
import { ProductDetail } from "./ProductDetail";
import { ProductEditForm } from "./ProductEditForm";
import { ProductList } from "./ProductList";

type View =
  | { kind: "list" }
  | { kind: "create" }
  | { kind: "detail"; product: Product }
  | { kind: "edit"; product: Product };

type LoadState = "loading" | "ready" | "error";

interface PageInfo {
  count: number;
  page: number;
  page_size: number;
  num_pages: number;
}

// Área de portefólio (aparece depois do onboarding empresarial). Container simples
// e explícito, sem store global nem router dedicado: um estado de vista local
// alterna entre lista, criação, ficha e edição. Os filtros/página vivem no estado
// do componente e são preservados durante a sessão da interface.
export function PortfolioWorkspace() {
  const { user } = useAuth();
  const [products, setProducts] = useState<Product[]>([]);
  const [loadState, setLoadState] = useState<LoadState>("loading");
  const [view, setView] = useState<View>({ kind: "list" });

  const [statusFilter, setStatusFilter] = useState<ProductStatusFilter>("active");
  const [onlyMine, setOnlyMine] = useState(false);
  const [page, setPage] = useState(1);
  const [pageInfo, setPageInfo] = useState<PageInfo>({
    count: 0,
    page: 1,
    page_size: 20,
    num_pages: 1,
  });

  const reload = useCallback(async () => {
    // Só mostra "a carregar" enquanto não há dados; refrescos em segundo plano
    // (mudança de filtro, resolução da sessão) mantêm a lista visível sem piscar.
    setLoadState((prev) => (prev === "ready" ? prev : "loading"));
    try {
      const response = await listProducts({
        status: statusFilter,
        responsible: onlyMine && user ? user.id : undefined,
        page,
      });
      setProducts(response.results);
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
  }, [statusFilter, onlyMine, user, page]);

  useEffect(() => {
    void reload();
  }, [reload]);

  const openDetail = useCallback((product: Product) => {
    setView({ kind: "detail", product });
  }, []);

  const handleCreated = useCallback(
    (product: Product) => {
      // Actualiza a lista e abre a ficha criada (mostra os defaults do servidor).
      void reload();
      setView({ kind: "detail", product });
    },
    [reload],
  );

  const handleSaved = useCallback(
    (product: Product) => {
      void reload();
      setView({ kind: "detail", product });
    },
    [reload],
  );

  // Mudar de filtro repõe a primeira página (paginação determinística).
  function changeStatus(next: ProductStatusFilter) {
    setStatusFilter(next);
    setPage(1);
  }
  function changeOnlyMine(next: boolean) {
    setOnlyMine(next);
    setPage(1);
  }

  return (
    <section aria-labelledby="portfolio-title">
      <h2 id="portfolio-title">Portefólio</h2>

      {view.kind === "list" && (
        <>
          <button type="button" onClick={() => setView({ kind: "create" })}>
            Novo produto
          </button>

          <div role="group" aria-label="Filtros do portefólio">
            <label>
              Estado
              <select
                value={statusFilter}
                onChange={(e) =>
                  changeStatus(e.target.value as ProductStatusFilter)
                }
              >
                <option value="active">Activos</option>
                <option value="archived">Arquivados</option>
                <option value="all">Todos</option>
              </select>
            </label>{" "}
            <label>
              <input
                type="checkbox"
                checked={onlyMine}
                onChange={(e) => changeOnlyMine(e.target.checked)}
              />
              Apenas os meus
            </label>
          </div>

          {loadState === "loading" && <p role="status">A carregar produtos…</p>}
          {loadState === "error" && (
            <p role="alert">
              Não foi possível carregar o portefólio.{" "}
              <button type="button" onClick={() => void reload()}>
                Tentar novamente
              </button>
            </p>
          )}
          {loadState === "ready" && (
            <>
              <ProductList
                products={products}
                currentUser={user}
                onSelect={openDetail}
              />
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
        <ProductCreateForm
          onCreated={handleCreated}
          onCancel={() => setView({ kind: "list" })}
        />
      )}

      {view.kind === "detail" && (
        <ProductDetail
          product={view.product}
          currentUser={user}
          onEdit={(product) => setView({ kind: "edit", product })}
          onBack={() => setView({ kind: "list" })}
          onChanged={() => void reload()}
        />
      )}

      {view.kind === "edit" && (
        <ProductEditForm
          product={view.product}
          onSaved={handleSaved}
          onCancel={() => setView({ kind: "detail", product: view.product })}
        />
      )}
    </section>
  );
}
