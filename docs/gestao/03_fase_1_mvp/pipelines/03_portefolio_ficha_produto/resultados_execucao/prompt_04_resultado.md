---
fase: F1
pipeline: F1-P03
prompt: F1-P03-PR04
modelo: claude-opus-4-8
inicio: 2026-07-13 15:00
fim: 2026-07-13 15:50
estado_execucao: Concluído
estado_revisao: Não revista
commit: não criado
---

# Resultado — Prompt 04 — Ciclo de vida, revisão explícita, filtros e paginação

## 1. Resumo

Completado o comportamento backend do portefólio: **arquivo/reactivação**
(transições `active↔archived`, sem eliminação física), operação explícita
**"marcar como revisto"** (única fonte de actualização de `last_reviewed_at` —
CLR-02) e **filtros/paginação/ordenação** na listagem, tudo preservando
**concorrência optimista** (`expected_version`, incremento único, 409 em versão
obsoleta), **isolamento** por empresa e **auditoria**. Acrescentado um **teste real
de concorrência** em PostgreSQL (duas escritas com a mesma versão → exactamente uma
vence, a outra recebe conflito, sem lost update). **24 testes novos** (23
funcionais + 1 concorrência) → **61 no módulo**; **177 testes backend verdes**;
sem drift; smoke ao vivo dos novos endpoints. Nenhuma regra de atenção, pesquisa,
notificação ou eliminação física foi criada. **F1-P03 fica 4/6.**

## 2. Endpoints acrescentados (sob /api/v1/)

| Método | Caminho | Efeito | Códigos |
|---|---|---|---|
| POST | `/products/{id}/archive` | active → archived | 200, 400, 403, 404, 409 |
| POST | `/products/{id}/reactivate` | archived → active | 200, 400, 403, 404, 409 |
| POST | `/products/{id}/mark-reviewed` | actualiza `last_reviewed_at` (só active) | 200, 400, 403, 404, 409 |

`GET /products` passa a suportar filtros e paginação (ver §5). Todas as operações
de ciclo de vida exigem `expected_version` (corpo) e **rejeitam** qualquer outro
campo, incluindo `organisation` (→ 400).

## 3. Regras das transições (artefacto 03 §2.1)

Todas as operações mutáveis: exigem `expected_version`; são **atómicas**
(`@transaction.atomic` + `select_for_update`); validam a empresa; incrementam
`version` **exactamente uma vez**; devolvem **409** em versão obsoleta; são
auditadas; não aceitam `organisation` do cliente.

- **Arquivo:** só `active`; produto já `archived` → 409; não elimina dados; não
  toca `last_reviewed_at`; `archived` não é editável nem revisível.
- **Reactivação:** só `archived`; preserva todos os dados; não cria nova entidade;
  não toca `last_reviewed_at`.
- **Marcar como revisto (CLR-02):** só `active`; actualiza `last_reviewed_at` para
  o instante da operação; incrementa `version`; acção **separada** da edição; não
  altera `purpose`, `notes` nem outros campos; edições comuns continuam **sem**
  actualizar `last_reviewed_at`.

## 4. Concorrência optimista

`_load_locked` bloqueia a linha (`select_for_update`) e valida `version` antes de
qualquer transição. Sob READ COMMITTED, a transacção que espera relê a linha já
actualizada e vê a nova versão → a segunda operação com a versão original recebe
`VersionConflict` (409). Demonstrado por teste real (2 threads, ligações
independentes, barrier): exactamente uma vence, `version` final = 2, o nome final é
o da vencedora (sem lost update).

## 5. Filtros, ordenação e paginação

- `status`: `active` (por defeito), `archived` ou `all`; valor inválido → 400.
- `responsible`: identificador de utilizador; inválido → 400.
- Ordenação estável: `updated_at` desc, `id` como desempate (total, determinística).
- Paginação: `page` (>=1, defeito 1) e `page_size` (defeito **20**, máximo **100**,
  limitado); resposta inclui `results`, `count`, `page`, `page_size`, `num_pages`.
- Os filtros **nunca** atravessam empresas (partem sempre da empresa do contexto).
- Sem pesquisa textual nesta fase.

Nota de compatibilidade: a resposta continua a incluir `results`; os campos de
paginação são aditivos (o frontend de PR03 ignora-os). O **defeito passou a
`active`** (antes devolvia todos), conforme a especificação.

## 6. Auditoria (RT-02, lista fechada)

- **Arquivo:** `product.archived`, `metadata={"operation":"archive","transition":"active->archived"}`.
- **Reactivação:** `product.updated` (acção agregada), `metadata={"operation":"reactivate","transition":"archived->active"}`.
- **Marcar como revisto:** `product.updated`, `metadata={"operation":"mark_reviewed","fields":["last_reviewed_at"]}`.

Nenhum evento novo criado (a lista fechada não tem `product.reactivated` nem
`product.reviewed`; usa-se `product.updated` com a operação nos metadados). Nunca
se regista `purpose`/`notes` integrais (verificado em teste).

## 7. Testes (24 novos; 61 no módulo)

`tests/test_product_lifecycle.py` (23) e `tests/test_product_concurrency.py` (1):

| # | Verificação obrigatória | Resultado |
|---|---|---|
| 1 | active pode ser archived | OK |
| 2 | archived não pode ser arquivado novamente | OK |
| 3 | archived pode ser reactivado | OK |
| 4 | active não pode ser reactivado | OK |
| 5 | versão obsoleta falha em cada comando | OK |
| 6 | arquivo não apaga o produto | OK |
| 7 | arquivo não altera last_reviewed_at | OK |
| 8 | reactivação não altera last_reviewed_at | OK |
| 9 | edição comum não altera last_reviewed_at | OK |
| 10 | mark-reviewed altera last_reviewed_at | OK |
| 11 | mark-reviewed incrementa version | OK |
| 12 | archived não pode ser marcado como revisto | OK |
| 13 | filtro active funciona | OK |
| 14 | filtro archived funciona | OK |
| 15 | filtro por responsável funciona | OK |
| 16 | paginação é estável | OK |
| 17 | filtro não expõe produtos de outra empresa | OK |
| 18 | operações de ciclo de vida são auditadas | OK |
| 19 | conteúdo integral não entra na auditoria | OK |
| 20 | migrações não apresentam drift | OK (`makemigrations --check`) |
| 21 | suite anterior permanece verde | OK (177 backend) |
| — | concorrência real (2 escritas, mesma versão) | OK |

Extra: ciclo de vida rejeita campos desconhecidos (400); operação sobre produto
alheio → 404; campos opcionais editáveis; data opcional inválida → 400; filtro de
estado inválido → 400.

## 8. Demonstração ao vivo (contentor reconstruído)

Base de desenvolvimento (porta 5434): criar → **mark-reviewed** (v1→v2,
`last_reviewed_at` avança de 12:48:30 para 12:48:32) → **archive** (v2, 200) →
**re-archive** (409) → **editar arquivado** (409) → **reactivate** (v3, 200) →
filtros (`active` count=1, `archived` count=0) → paginação
(`count=1,page=1,page_size=1,num_pages=1`). Dados de smoke removidos (base repõe
users=2, products=0).

## 9. Ficheiros

### Criados
- `backend/apps/portfolio/tests/test_product_lifecycle.py`
- `backend/apps/portfolio/tests/test_product_concurrency.py`
- `docs/gestao/03_fase_1_mvp/pipelines/03_portefolio_ficha_produto/resultados_execucao/prompt_04_resultado.md`

### Alterados
- `backend/apps/portfolio/service.py` (`InvalidTransition`, `_load_locked`, `archive_product`, `reactivate_product`, `mark_reviewed`)
- `backend/apps/portfolio/views.py` (filtros/paginação na listagem; `_run_lifecycle` + 3 vistas)
- `backend/apps/portfolio/serializers.py` (`ExpectedVersionSerializer`)
- `backend/apps/portfolio/urls.py` (rotas archive/reactivate/mark-reviewed)
- `docs/gestao/01_status_pipelines.md`, `00_painel_execucao_global.md`,
  `05_diario_execucao_ia.md`, `04_matriz_validacao_global.md` (VAL-002/003/012)

### Migrações
- **Nenhuma nova** (apenas comportamento; `makemigrations --check` → No changes detected).

## 10. Comandos e evidências

- `manage.py test apps.portfolio` → **61 OK**.
- `manage.py test` → **177 OK** (153 anteriores + 24).
- `makemigrations --check --dry-run` → No changes detected; `check` → sem issues.
- Live: fluxo completo dos novos endpoints + filtros/paginação (§8).

## 11. Decisões

Sem decisão global. Locais: (a) reactivação e revisão usam `product.updated` da
lista fechada com a operação nos metadados (não há acção dedicada); (b) `page_size`
por defeito 20, máximo 100; (c) todas as operações de ciclo de vida incrementam
`version` (concorrência coerente); (d) resposta de listagem aditiva (mantém
`results`; defeito passa a `active`).

## 12. Pendências / reservas

- UI de arquivar/reactivar, filtros, paginação e botão "marcar como revisto" →
  **PR05**.
- Regras de atenção (R-AT-01 usa `last_reviewed_at`) → fora desta pipeline
  (F1-P07/MVP-16); aqui apenas se garante a semântica da data.
- VAL-003 permanece **Parcial** (UI completa e validação integrada em PR05/PR06);
  VAL-002 e VAL-012 mantêm-se **Parciais** com evidência acrescentada do módulo.

## 13. Estado da pipeline e próximo passo

- **F1-P03 Em execução (4/6).**
- Próximo: **F1-P03-PR05** — completar a experiência de UI (filtros, paginação,
  arquivar/reactivar, campos opcionais e "marcar como revisto"). Não iniciado.
