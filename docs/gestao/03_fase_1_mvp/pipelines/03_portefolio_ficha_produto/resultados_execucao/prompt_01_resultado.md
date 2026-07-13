---
fase: F1
pipeline: F1-P03
prompt: F1-P03-PR01
modelo: claude-opus-4-8
inicio: 2026-07-13 12:00
fim: 2026-07-13 12:35
estado_execucao: Concluído
estado_revisao: Não revista
commit: não criado
---

# Resultado — Prompt 01 — Criar o modelo de produto e a migração

## 1. Resumo

Criada a fundação persistente do portefólio: a entidade **`Product`** (ficha
administrativa mínima), a **primeira migração** do módulo `portfolio` e os
**testes estruturais** do modelo. `Product` estende `OrganisationScopedModel`
(isolamento estrutural obrigatório por `Organisation`, UUIDv4 + carimbos), com os
5 campos obrigatórios da ficha (artefacto 04 §2.1), os opcionais (§2.2), estados
mínimos **Activo/Arquivado** (artefacto 03 §2.1) e `version` para concorrência
optimista. `last_reviewed_at` é **inicializada na criação** (`default`) e **não**
está ligada a qualquer edição (sem `auto_now`) — a operação explícita de revisão
chega em PR04. **19 testes** do módulo + **116** anteriores = **135 testes
backend verdes**; sem drift; migração aplica/reverte/reaplica em base vazia e na
base de desenvolvimento existente, preservando dados fora do módulo. Nenhuma API,
serializer, serviço CRUD ou UI foi antecipada. **F1-P03 fica Em execução (1/6).**

## 2. Modelo `Product` (campos finais)

| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUIDField (PK) | UUIDv4, via `UUIDPrimaryKeyModel` |
| `created_at` / `updated_at` | DateTimeField | `auto_now_add` / `auto_now` (herdados) |
| `organisation` | FK → `Organisation` | obrigatória, `PROTECT`, `editable=False` (derivada do contexto no servidor; RT-01) |
| `name` | CharField(255) | obrigatório; não vazio nem só espaços |
| `purpose` | TextField | obrigatório; não vazio nem só espaços |
| `status` | CharField(16) choices | `active`/`archived`; default `active` |
| `responsible` | FK → `CustomUser` | obrigatória, `PROTECT`; Membership activa na mesma empresa |
| `last_reviewed_at` | DateTimeField | obrigatória; `default=timezone.now`; **nunca** `auto_now` |
| `target_audience` | CharField(255) | opcional (`blank`) |
| `phase` | CharField(64) | opcional (`blank`); atributo livre, sem taxonomia imposta |
| `next_review_at` | DateTimeField | opcional (`null`, `blank`) |
| `notes` | TextField | opcional (`blank`) |
| `version` | PositiveIntegerField | default 1; concorrência optimista |

`db_table = "portfolio_product"` (convenção do módulo).

## 3. Regras e decisões de implementação

- **Isolamento (RT-01):** `Product` deriva de `OrganisationScopedModel` — a
  empresa é real, não nula, `PROTECT` e `editable=False`; nunca aceite do cliente.
- **`last_reviewed_at`:** `default=timezone.now` inicializa na criação; sem
  `auto_now`, as edições comuns não a alteram (MVP-05.R1). A operação "marcar como
  revisto" (PR04) será a única fonte de actualização.
- **`attention_level` não persistido** (MVP-05.R3): não existe qualquer campo;
  teste estrutural confirma-o.
- **Validação de domínio em `clean()`** (ponto de entrada do serviço/API em PR02):
  `name`/`purpose` não vazios; `responsible` com `Membership` **activa** na mesma
  `Organisation`. `objects.create` (que não chama `full_clean`) não é o caminho de
  domínio — o serviço chamará `full_clean`, como no resto do backend.
- **Normalização:** só espaços exteriores (`strip`) em `name`/`purpose`, sempre
  aplicada no `save()` (mesmo sem `full_clean`); o conteúdo interior é preservado.
- **Defesa em profundidade (BD):** `CheckConstraint` para `name <> ''`,
  `purpose <> ''` e `version >= 1` (padrão de constraints de F1-P02).
- **`responsible` com `PROTECT`** e sem eliminação física do produto (arquivar é
  uma transição de estado, não `delete`).
- **Política de opcionais:** texto usa `""` (`blank`), não `NULL`; o opcional
  temporal (`next_review_at`) usa `NULL`. Decisão local documentada aqui (não é
  desvio estrutural; sem decisão global).

## 4. Não implementado (fora do âmbito deste prompt)

Endpoints, serializers, serviços CRUD, UI, arquivo/reactivação, filtros,
paginação, operação "marcar como revisto", agregados (documentos/decisões/
pendências/execuções) e regras de atenção. Nenhum estado adicional, fase/gate de
projecto ou indicador de portefólio foi criado.

## 5. Migração

- `apps/portfolio/migrations/0001_initial.py` — `CreateModel Product`
  (dependências: `organisations.0002`, `AUTH_USER_MODEL`).
- **Reversível**: reverter para `zero` remove `portfolio_product`; reaplicar
  recria-a. Não altera migrações históricas.
- Aplica em **base vazia** (base de testes) e na **base de desenvolvimento
  existente** (aplicar → reverter → reaplicar), com dados fora do módulo intactos
  (orgs=1, users=2 preservados).

## 6. Testes (19 no módulo)

`apps/portfolio/tests/test_product_model.py` (17) e `test_migration.py` (2).

| # | Verificação (obrigatória) | Teste | Resultado |
|---|---|---|---|
| 1 | Product exige Organisation | `test_organisation_is_required` | OK |
| 2 | Product exige name | `test_name_is_required` | OK |
| 3 | Product exige purpose | `test_purpose_is_required` | OK |
| 4 | status inicial é active | `test_initial_status_is_active` | OK |
| 5 | version inicial é 1 | `test_initial_version_is_one` | OK |
| 6 | last_reviewed_at inicializado na criação | `test_last_reviewed_at_is_initialised_on_creation` | OK |
| 7 | opcionais realmente opcionais | `test_optional_fields_are_optional` | OK |
| 8 | responsible da mesma empresa aceite | `test_responsible_same_company_is_accepted` | OK |
| 9 | responsible de outra empresa rejeitado | `test_responsible_other_company_is_rejected` | OK |
| 10 | status inválido rejeitado | `test_invalid_status_is_rejected` | OK |
| 11 | attention_level não persistido | `test_attention_level_is_not_persisted` | OK |
| 12 | migração aplica e reverte | `test_migration_applies_and_reverts` | OK |
| 13 | suite anterior verde | `manage.py test` (135) | OK |

Testes adicionais: edição comum não toca `last_reviewed_at`; Membership inactiva
rejeitada; normalização preserva espaços interiores; `organisation` não editável;
arquivar é transição (não delete); `version < 1` rejeitada pela BD; PK é UUID.

## 7. Comandos e evidências

Executados com a base PostgreSQL de desenvolvimento (contentor `ventureops-db-1`,
`127.0.0.1:5434`):

- `makemigrations portfolio` → `0001_initial` criada.
- `makemigrations --check --dry-run` → **No changes detected** (sem drift).
- `manage.py test apps.portfolio` → **19 testes OK**.
- `manage.py test` → **135 testes OK** (116 anteriores + 19).
- Base existente: `migrate portfolio` (OK) → `migrate portfolio zero` (OK) →
  `migrate portfolio` (OK); dados fora do módulo preservados.

## 8. Ficheiros

### Criados
- `backend/apps/portfolio/models.py`
- `backend/apps/portfolio/migrations/0001_initial.py`
- `backend/apps/portfolio/tests/__init__.py`
- `backend/apps/portfolio/tests/test_product_model.py`
- `backend/apps/portfolio/tests/test_migration.py`
- `docs/gestao/03_fase_1_mvp/pipelines/03_portefolio_ficha_produto/resultados_execucao/prompt_01_resultado.md`

### Alterados (governação)
- `docs/gestao/01_status_pipelines.md` (linha F1-P03)
- `docs/gestao/00_painel_execucao_global.md` (pipeline/prompt actual, próximo passo)
- `docs/gestao/05_diario_execucao_ia.md` (linha do diário)

### Migrações
- **Nova:** `portfolio/0001_initial`. Nenhuma migração histórica alterada.

## 9. Decisões

Sem decisão global (nenhum desvio estrutural). Decisões locais registadas na
secção 3 (política de opcionais texto/`NULL`; `PROTECT` em `responsible`;
`CheckConstraint` de defesa em profundidade; `default=timezone.now` em vez de
`auto_now` para `last_reviewed_at`).

## 10. Problemas / limitações / pendências

- O contentor `ventureops-backend-1` tem o código do módulo **antes** desta
  alteração (imagem construída sem bind mount do código); não conhece
  `portfolio.0001`. Sem impacto (não há endpoints); será refletido no próximo
  build/deploy (a acompanhar em PR02, ao introduzir a API).
- Validação de domínio (`clean`/`full_clean`) é o ponto de entrada; a aplicação
  efectiva no fluxo de criação (responsável por defeito = utilizador autenticado,
  transacção) pertence ao serviço/API em **PR02**.
- Concorrência optimista: o campo `version` existe; o incremento condicional
  (evitar lost update) é implementado em **PR02/PR04**.
- VAL-002/VAL-003 permanecem **preparadas** (não demonstradas nesta etapa; sem
  API/UI ainda).

## 11. Estado da pipeline

- **F1-P03 Em execução (1/6).** Fundação do modelo e migração concluídas.

## 12. Próximo passo recomendado

- **F1-P03-PR02** — Implementar a API CRUD isolada e auditada sobre `Product`
  (criação com apenas `name`+`purpose`, contexto derivado no servidor,
  concorrência optimista com 409, auditoria). Não iniciado nesta iteração.
