---
fase: F1
pipeline: F1-P03
prompt: F1-P03-PR02
modelo: claude-opus-4-8
inicio: 2026-07-13 13:00
fim: 2026-07-13 13:40
estado_execucao: Concluído
estado_revisao: Não revista
commit: não criado
---

# Resultado — Prompt 02 — API CRUD isolada e auditada do produto

## 1. Resumo

Implementada a **API inicial do portefólio** sobre o `Product` de PR01: criar
(informando apenas `name` e `purpose`), listar, consultar e editar produtos, com
**contexto empresarial derivado no servidor** (Membership activa), **concorrência
optimista** (409 em versão obsoleta, sem lost update) e **auditoria** de criação e
edição sem conteúdo sensível. Isolamento aplicado (RT-01): produtos de outra
empresa são **indistinguíveis** de um id inexistente (404) e as tentativas
cruzadas usam o evento de segurança já existente. **18 testes de API** novos + 19
de PR01 = **37 no módulo**; **153 testes backend verdes**; sem drift. Demonstração
**ao vivo** (contentor reconstruído) confirmou criação/listagem/edição/409/
isolamento e auditoria com apenas operação + nomes de campos. Sem DELETE, sem UI,
sem arquivo/filtros/paginação/revisão (PR03–PR06). **F1-P03 fica 2/6.**

## 2. Contratos (endpoints, sob `/api/v1/`)

| Método | Caminho | Efeito | Códigos |
|---|---|---|---|
| GET | `/products` | Lista produtos da empresa do contexto (`{"results": [...]}`) | 200, 403 |
| POST | `/products` | Cria produto (só `name`+`purpose` obrigatórios) | 201, 400, 403 |
| GET | `/products/{id}` | Detalhe (isolado por empresa) | 200, 403, 404 |
| PATCH | `/products/{id}` | Edição comum (exige `expected_version`) | 200, 400, 403, 404, 409 |

Sem `DELETE` (não há eliminação física). Resposta de leitura inclui sempre
`version`, `status`, `last_reviewed_at`, `organisation` e `responsible` (ids).

### Entrada de criação
- Obrigatórios: `name`, `purpose`. Opcionais aceites: `target_audience`, `phase`,
  `next_review_at`, `notes`, `responsible` (id).
- `organisation`, `status`, `version`, `last_reviewed_at` **não** são aceites do
  cliente — campos desconhecidos/proibidos → **400** (não são silenciosamente
  ignorados).

### Entrada de edição (PATCH comum)
- Exige `expected_version` (concorrência optimista).
- Editáveis: `name`, `purpose`, `target_audience`, `phase`, `next_review_at`,
  `notes`, `responsible`. **Não** aceita `status` nem `organisation` (→ 400).
- `status` (arquivo/reactivação) e "marcar como revisto" têm endpoints próprios em
  PR04; o PATCH comum nunca os altera.

## 3. Serviços (`apps/portfolio/service.py`)

- `create_product(actor, organisation, name, purpose, responsible_id=None, optionals)`
  — transaccional; `responsible` por defeito = utilizador autenticado; se
  `responsible_id` for indicado tem de ter Membership activa na mesma empresa;
  defaults do modelo aplicam `status=active`, `version=1`, `last_reviewed_at=agora`.
- `update_product(organisation, product_id, expected_version, changes, responsible_id=None)`
  — bloqueia a linha (`select_for_update`), valida a empresa e a versão, aplica só
  os campos editáveis, incrementa `version` **exactamente uma vez** e **nunca**
  toca `last_reviewed_at`. Erros de domínio: `ProductNotFound` (404),
  `ProductArchived`/`VersionConflict` (409), `ResponsibleNotInOrganisation` (400).

Sem repository pattern nem serviço genérico (RT-09); funções simples, como em F1-P02.

## 4. Isolamento (RT-01)

- Empresa derivada de `require_context` (Membership activa); sem contexto → **403**.
- Listagem/detalhe filtram pela empresa do contexto.
- Produto de outra empresa → **404 idêntico** ao de um id inexistente
  (`_resolve_or_not_found`: se o id existir noutra empresa, audita a tentativa
  cruzada e devolve o mesmo 404).
- O cliente nunca define `organisation`; não pode atribuir responsável de outra
  empresa.

## 5. Concorrência optimista

- `PATCH` exige `expected_version`; a linha é bloqueada e a versão validada dentro
  da transacção. Versão obsoleta → **409** sem escrita (sem lost update). Alteração
  válida incrementa `version` exactamente uma vez. Demonstrado ao vivo (v2→409 com
  `expected_version=1`; v2→v3 com a versão correcta).

## 6. Auditoria (RT-02)

- Eventos da **lista fechada** `AuditAction`: `product.created` e `product.updated`
  (já aprovados; nenhum evento novo criado).
- Metadados mínimos: `{"operation": "create"|"update", "fields": [nomes]}` +
  `entity_type="product"`, `entity_id`, `correlation_id`. **Nunca** `purpose`/
  `notes` integrais (verificado em teste e ao vivo).
- Tentativa cruzada → `security.cross_org_attempt` (evento de segurança existente),
  `entity_type=product`.

## 7. Tratamento de erros

400 (validação/campos proibidos) · 403 (sem contexto autorizado) · 404 (produto
inexistente ou de outra empresa, resposta idêntica) · 409 (versão obsoleta ou
produto arquivado). Sem stack trace nem detalhes internos (mensagens genéricas;
`full_clean` convertido em 400 limpo).

Nota (401 vs 403): a stack usa `SessionAuthentication`, pelo que um pedido **não
autenticado** recebe **403** (o DRF só devolve 401 quando um autenticador fornece
`WWW-Authenticate`). Comportamento herdado de F1-P02, coerente em todo o backend.

## 8. Testes (18 de API; 37 no módulo)

`apps/portfolio/tests/test_product_api.py`:

| # | Verificação obrigatória | Teste | Resultado |
|---|---|---|---|
| 1 | Owner cria só com name+purpose | `test_owner_creates_product_with_name_and_purpose_only` | OK |
| 2 | defaults no servidor | `test_defaults_applied_on_server` | OK |
| 3 | organisation não escolhível | `test_client_cannot_choose_organisation` | OK |
| 4 | listagem só da empresa actual | `test_list_only_contains_current_company_products` | OK |
| 5 | detalhe próprio funciona | `test_own_detail_works` | OK |
| 6 | produto alheio → 404 | `test_foreign_product_returns_404` | OK |
| 7 | tentativa cruzada auditada | `test_cross_attempt_is_audited` | OK |
| 8 | edição válida incrementa version | `test_valid_edit_increments_version` | OK |
| 9 | versão obsoleta → 409 | `test_edit_with_stale_version_returns_409` | OK |
| 10 | edição comum não altera last_reviewed_at | `test_common_edit_does_not_change_last_reviewed_at` | OK |
| 11 | archived não editável | `test_archived_product_cannot_be_edited` | OK |
| 12 | responsável alheio rejeitado | `test_foreign_responsible_is_rejected` | OK |
| 13 | criação e edição auditadas | `test_create_and_edit_are_audited` | OK |
| 14 | conteúdo integral fora da auditoria | `test_full_content_not_in_audit` | OK |
| 15 | regressão auth/onboarding/isolamento verde | suite completa (153) | OK |

Extra: sem Membership → 403 (lista e criação); edição de produto alheio → 404;
`status`/`version` não patcháveis (400); nome em branco rejeitado.

## 9. Demonstração ao vivo (contentor reconstruído)

`docker compose up -d --build backend`; base de desenvolvimento (porta 5434):
CSRF → login → onboarding → **criar** produto só com `name`+`purpose` (201,
defaults aplicados: `status=active`, `version=1`, `responsible`=utilizador,
`last_reviewed_at` definido, opcionais vazios) → **listar** (só o próprio) →
**editar** com versão correcta (200, `version` 2→3, `last_reviewed_at`
**inalterado**) → **conflito** com versão obsoleta (409) → enviar `organisation`
(400). Eventos `product.created`/`product.updated` com apenas operação + nomes de
campos. Dados de smoke removidos no fim (base repõe users=2, products=0).

## 10. Ficheiros

### Criados
- `backend/apps/portfolio/serializers.py`
- `backend/apps/portfolio/service.py`
- `backend/apps/portfolio/views.py`
- `backend/apps/portfolio/urls.py`
- `backend/apps/portfolio/tests/test_product_api.py`
- `docs/gestao/03_fase_1_mvp/pipelines/03_portefolio_ficha_produto/resultados_execucao/prompt_02_resultado.md`

### Alterados
- `backend/config/urls.py` (monta `apps.portfolio.urls` sob `/api/v1/`)
- `docs/gestao/01_status_pipelines.md`, `00_painel_execucao_global.md`,
  `05_diario_execucao_ia.md`, `04_matriz_validacao_global.md` (VAL-002/003/012)

### Migrações
- **Nenhuma nova** (apenas comportamento/serialização; `makemigrations --check` →
  No changes detected).

## 11. Comandos e evidências

- `manage.py test apps.portfolio.tests.test_product_api` → **18 OK**.
- `manage.py test` → **153 OK** (135 anteriores + 18).
- `makemigrations --check --dry-run` → **No changes detected**; `check` → sem issues.
- Live: `GET /api/v1/products` sem sessão → **403**; fluxo completo ao vivo (§9).

## 12. Problemas encontrados

- Smoke inicial: caracteres acentuados enviados pelo shell em latin-1 → a API
  rejeitou com **400 limpo** (JSON inválido). Não é defeito da API (comportamento
  correcto); o smoke foi repetido com ASCII e passou. Sem alterações de código.

## 13. Decisões

Sem decisão global (nenhum desvio estrutural). Decisões locais: (a) campos
desconhecidos/proibidos na entrada → **400** (rejeição explícita, não ignorados);
(b) `responsible` opcional na API, validado contra Membership activa da empresa
(suporta o caso individual sem criar selector/convites); (c) `PATCH` comum não
altera `status` (arquivo/reactivação separados em PR04).

## 14. Pendências / reservas

- Arquivo/reactivação, filtros, paginação, ordenação e "marcar como revisto" →
  **PR04**; UI → **PR03/PR05**.
- Teste de concorrência **real com duas ligações** (duas escritas simultâneas) →
  **PR04** (aqui a concorrência optimista é coberta por 409 em versão obsoleta e
  por `select_for_update`).
- VAL-003 **Parcial**; VAL-002 e VAL-012 mantêm-se **Parciais** com evidência
  acrescentada do módulo `Product`.

## 15. Estado da pipeline e próximo passo

- **F1-P03 Em execução (2/6).**
- Próximo: **F1-P03-PR03** — interface inicial do portefólio (React/TS) sobre os
  contratos desta API. Não iniciado.
