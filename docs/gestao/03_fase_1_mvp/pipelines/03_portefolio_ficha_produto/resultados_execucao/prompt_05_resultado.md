---
fase: F1
pipeline: F1-P03
prompt: F1-P03-PR05
modelo: claude-opus-4-8
inicio: 2026-07-13 16:10
fim: 2026-07-13 17:05
estado_execucao: Concluído
estado_revisao: Não revista
commit: não criado
---

# Resultado — Prompt 05 — Experiência completa do portefólio e da ficha

## 1. Resumo

Completada a interface do portefólio sobre os contratos de PR04: **filtros** por
estado (Activos/Arquivados/Todos) e por responsável ("Apenas os meus"),
**paginação** (Anterior/Seguinte com indicador de página), e as acções de ciclo de
vida na ficha — **editar**, **arquivar** (confirmação explícita), **reactivar**,
**marcar como revisto** (confirmação que explica ser uma revisão real) e
**recarregar após conflito 409**. A ficha mostra todos os campos (estado e última
revisão só de leitura) e reserva uma área de contexto relacionado com aviso claro
de ausência — **sem** dados nem contagens simuladas. **16 testes de componente**
(28 no frontend) verdes e estáveis (3 rondas); `npm run build` OK. **Demonstração
ao vivo** no browser cobriu o ciclo completo (criar 2, marcar revisto, arquivar,
filtrar arquivados, reactivar), com os estados confirmados no backend. **F1-P03
fica 5/6.**

## 2. Componentes e contratos

- `api/products.ts` — acrescentados: `listProducts(params)` com `status`,
  `responsible`, `page`; tipos `ProductStatusFilter`/`ProductListResponse`
  (com `count/page/page_size/num_pages`); e `archiveProduct`,
  `reactivateProduct`, `markReviewed` (POST com `expected_version`).
- `PortfolioWorkspace` — filtros + paginação (estado local preservado na sessão),
  refrescos em segundo plano **sem piscar** a lista, e ligação das acções da ficha.
- `ProductDetail` — passou a **stateful**: acções com confirmação inline
  (sem modais), tratamento de 409 (aviso + recarregar) e placeholder de vistas
  agregadas.
- `ProductList`/`ProductCreateForm`/`ProductEditForm` — reutilizados de PR03.

Endpoints consumidos: `GET /v1/products?status=&responsible=&page=`,
`POST /v1/products/{id}/archive|reactivate|mark-reviewed`, além dos de PR02/PR03.

## 3. Regras de UX aplicadas

- **Arquivar** exige confirmação explícita (botão → "Confirmar arquivo").
- **Marcar como revisto** exige confirmação com texto que explica ser uma revisão
  real da ficha (distinta de guardar uma edição).
- **Reactivar** é acção explícita (botão), só visível em produtos arquivados.
- `last_reviewed_at` só muda visualmente após "marcar como revisto"; a edição
  comum não a altera nem se apresenta como revisão.
- Produto **arquivado**: banner claro + edição/revisão indisponíveis; só reactivar.
- **Conflito 409** nunca sobrescreve o servidor — mostra aviso e oferece
  **Recarregar dados** (versão actual).
- Confirmações **inline** simples, sem modais nem abstracções complexas.

## 4. Vistas agregadas progressivas

A ficha reserva a secção "Contexto relacionado" com o aviso «Documentos, decisões,
pendências e execuções ainda não estão disponíveis nesta versão». **Sem** dados
falsos, **sem** contagens simuladas e **sem** APIs para módulos inexistentes.
`attention_level` não é apresentado (persistido ou calculado).

## 5. Integração

Reutiliza o cliente HTTP central (sessão por cookie + CSRF); sem novo cliente, sem
store global, sem biblioteca de UI adicional e sem router dedicado. A experiência
de perfil e empresa mantém-se intacta.

## 6. Testes (16 de componente; 28 no frontend)

`src/components/portfolio/portfolio.test.tsx`:

| # | Verificação obrigatória | Resultado |
|---|---|---|
| 1 | filtro de activos | OK |
| 2 | filtro de arquivados | OK |
| 3 | filtro de todos | OK |
| 4 | paginação | OK |
| 5 | arquivo com confirmação | OK |
| 6 | produto arquivado deixa de ser editável | OK |
| 7 | reactivação | OK |
| 8 | marcação explícita como revisto | OK |
| 9 | edição comum não muda a data de revisão | OK |
| 10 | conflito 409 permite recarregar | OK |
| 11 | campos opcionais são editáveis | OK |
| 12 | estado e responsável apresentados correctamente | OK |
| 13 | nenhum agregado futuro é simulado | OK |
| 14 | autenticação/perfil/empresa continuam funcionais | OK (suites existentes) |
| 15 | build e suite frontend passam | OK (`npm run build`, `vitest`) |

Extra: estado vazio; criação com defaults; submissão duplicada evitada; erro da
API tratado; filtro por responsável ("apenas os meus").

## 7. Demonstração ao vivo (browser, contentores reconstruídos)

Conta `p5@x.pt` / "Empresa P5": criar **Produto Um** e **Produto Dois** (só Nome +
Propósito) → em Produto Um, **marcar como revisto** (confirmação → versão 1→2) →
**arquivar** (confirmação → versão 3, banner "Produto arquivado", edição
indisponível) → lista **Activos** oculta-o e mostra Produto Dois → filtro
**Arquivados** mostra Produto Um → **reactivar** (versão 4, estado Activo, acções
repostas). Estados confirmados no backend (Produto Um active v4; Produto Dois
active v1). Dados de demo removidos (base repõe users=2, products=0).

## 8. Ficheiros

### Criados
- `docs/gestao/03_fase_1_mvp/pipelines/03_portefolio_ficha_produto/resultados_execucao/prompt_05_resultado.md`

### Alterados
- `frontend/src/api/products.ts` (params de listagem + acções de ciclo de vida)
- `frontend/src/components/portfolio/PortfolioWorkspace.tsx` (filtros/paginação; refresco sem piscar; acções)
- `frontend/src/components/portfolio/ProductDetail.tsx` (stateful: acções, confirmações, 409, placeholder agregado)
- `frontend/src/components/portfolio/portfolio.test.tsx` (16 testes da experiência completa)
- `frontend/src/components/organisation-gate.test.tsx` (mock de listagem com forma paginada)
- `docs/gestao/01_status_pipelines.md`, `00_painel_execucao_global.md`,
  `05_diario_execucao_ia.md`, `04_matriz_validacao_global.md` (VAL-003, UI)

## 9. Comandos e evidências

- `npm run test` → **28 testes OK** (12 anteriores + 16); portfolio estável em 3 rondas.
- `npm run build` → tsc `--noEmit` + `vite build` OK (49 módulos).
- Live: ciclo completo no browser (§7) + verificação de estados no backend.

## 10. Problemas encontrados

- Piscar da lista em refrescos (mudança de filtro / resolução de sessão) causava
  uma corrida no estado vazio: a listagem voltava a "a carregar" e removia o
  elemento entre o `findByText` e a asserção. Corrigido no `PortfolioWorkspace`
  mantendo a lista visível durante refrescos em segundo plano (só mostra "a
  carregar" enquanto não há dados) — melhora também a UX. Suite estável depois.

## 11. Decisões

Sem decisão global. Locais: (a) filtro por responsável exposto como "Apenas os
meus" (usa o id do utilizador actual), sem criar selector de membros; (b)
confirmações inline em vez de modais; (c) refresco em segundo plano não repõe o
estado "a carregar" (evita piscar); (d) área agregada apenas informativa.

## 12. Pendências / reservas

- Validação integrada de fecho (ponta a ponta, isolamento, concorrência,
  auditoria e regressão) → **PR06**.
- Vistas agregadas reais (documentos/decisões/pendências/execuções) e nível de
  atenção → F1-P04+ / F1-P07.

## 13. Estado da pipeline e próximo passo

- **F1-P03 Em execução (5/6).**
- Próximo: **F1-P03-PR06** — validação integrada e fecho da pipeline. Não iniciado.
