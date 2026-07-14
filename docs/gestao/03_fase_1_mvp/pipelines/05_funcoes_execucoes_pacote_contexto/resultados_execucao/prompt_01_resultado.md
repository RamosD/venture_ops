---
fase: F1
pipeline: F1-P05
prompt: F1-P05-PR01
modelo: claude-opus-4-8
inicio: 2026-07-13 22:40
fim: 2026-07-13 23:40
estado_execucao: Concluído
estado_revisao: Não revista
commit: não criado
---

# Resultado — Prompt 01 — Catálogo de funções organizacionais

## 1. Veredicto

**Concluído.** O modelo `FunctionProfile` existe com `actor_type` fechado
(`human`/`ai`/`hybrid`), ciclo `active↔inactive`, `requires_approval` com política
SEC-HUM, documento de instruções empresarial opcional validado, concorrência
optimista por `version`, isolamento por empresa e auditoria (evento 10). API
mínima (GET/POST lista, GET/PATCH detalhe, `deactivate`, `reactivate`) e área
empresarial **Funções** na UI (lista, filtros, criação, edição, inactivação com
confirmação, reactivação). Sem DELETE. Migração aplica, reverte em base
controlada e **sem drift**.

**Condição de entrada confirmada:** F1-P04 **Concluída (6/6)** (ver
`04_.../resultados_execucao/prompt_06_resultado.md`); árvore de trabalho limpa no
arranque (sem alterações não relacionadas); nenhum defeito estrutural pendente de
F1-P04. **Nenhum módulo anterior foi alterado** (só se acrescentou uma linha de
routing em `config/urls.py` para montar `apps.functions.urls`).

**Fronteiras respeitadas:** não se implementou execução, snapshot, pacote de
contexto, chamada a modelos, resultados, aprovação, templates de função nem
permissões por função. **VAL-007 permanece Parcial** até uma função ser
efectivamente usada numa execução (F1-P05-PR02).

**Regressão verde:** backend **324 testes OK** (293 anteriores + 31 novos);
frontend **57 testes OK** (49 anteriores + 8 novos); `npm run build` OK;
`makemigrations --check` sem drift.

## 2. Modelo e contratos

**`FunctionProfile`** (`functions_functionprofile`), estende
`OrganisationScopedModel` (UUIDv4, `created_at`/`updated_at`, `organisation`
obrigatória `PROTECT` `editable=False`):

| Campo | Tipo | Regra |
|---|---|---|
| `name` | CharField(255) | obrigatório, não vazio/só espaços |
| `actor_type` | TextChoices | `human`/`ai`/`hybrid` (fechado) |
| `purpose` | TextField | obrigatório, não vazio/só espaços |
| `responsibilities` | TextField | obrigatório, não vazio/só espaços |
| `constraints` | TextField | opcional |
| `instruction_document` | FK→`documents.Document` `PROTECT` | opcional; validado (ver §4) |
| `requires_approval` | BooleanField | política SEC-HUM (ver §5) |
| `status` | TextChoices | `active`/`inactive`, nasce `active` |
| `version` | PositiveIntegerField | concorrência optimista, ≥1 |

**Defesa em profundidade (CheckConstraints):** `name`/`purpose`/`responsibilities`
não vazios; `actor_type` e `status` fechados; `version ≥ 1`; e
`~(actor_type in ai,hybrid) OR requires_approval=True` (invariante SEC-HUM ao
nível da BD). Normalização de espaços exteriores em `save`/`clean`.

**Contratos de entrada (estritos, padrão do backend):** o cliente nunca envia
`organisation`, `status`, `version` nem timestamps (campos rejeitados com 400). O
`status` só muda por operações dedicadas.

## 3. API

Montada sob `/api/v1/` (`config/urls.py`):

- `GET   /api/v1/functions` — lista da empresa; filtros `status`
  (`active` por defeito, `inactive`, `all`) e `actor_type`; paginação
  (`page`/`page_size`, máx. 100); ordenação determinística `-created_at, id`.
- `POST  /api/v1/functions` — cria (`active`); aplica a política `requires_approval`.
- `GET   /api/v1/functions/{id}` — detalhe (alheio → 404 auditado).
- `PATCH /api/v1/functions/{id}` — edição; exige `expected_version`; **não** altera
  `status`; incrementa `version` uma vez.
- `POST  /api/v1/functions/{id}/deactivate` — `active → inactive` (explícita).
- `POST  /api/v1/functions/{id}/reactivate` — `inactive → active` (explícita).

**Sem DELETE** (nem no recurso nem na colecção → 405). Erros:
400 (validação/campo não permitido/documento inválido/política), 403 (sem
Membership), 404 (inexistente ou alheio — indistinguível), 409 (versão obsoleta
ou transição inválida).

## 4. Regras de negócio

- Função **não é papel de autorização** (artefacto 02 §6.3): é conteúdo/
  configuração reutilizável em execuções; independente dos papéis de acesso.
- Nasce `active`; **sem eliminação física**.
- **Documento de instruções** (quando indicado): da MESMA empresa; do tipo exacto
  `instrucoes` (`DocumentType.INSTRUCTIONS`); **empresarial** (`product` nulo,
  porque a função é reutilizável entre produtos); com `current_version` válida.
  Qualquer violação → 400 (documento alheio não vaza existência).
- Função `inactive` **não é seleccionável** em novas execuções (default da lista é
  `active`); execuções passadas preservarão referência e snapshot (MVP-11) — a
  inactivação **não** elimina relações históricas.
- `status` **não** é alterável por PATCH; inactivar/reactivar são operações
  explícitas e dedicadas.
- **Política de edição de função `inactive` (explícita):** uma função `inactive`
  **pode ser editada** (conteúdo) **sem ser reactivada** — separação deliberada
  entre conteúdo e estado (recomendação do prompt); reactivar continua a ser um
  acto distinto.
- Todas as mutações usam `expected_version` (`select_for_update` +
  incremento único); versão obsoleta → 409.

## 5. Política `requires_approval` (SEC-HUM)

Documentada no resultado, **sem** criar um mecanismo genérico de políticas —
apenas esta invariante mínima:

- `actor_type` **`ai`/`hybrid` → `requires_approval` obrigatoriamente `True`** no
  MVP. Um `False` explícito é rejeitado (400); se omitido, aplica-se `True` por
  defeito.
- `actor_type` **`human`** → valor por defeito `False`; aceita `True` ou `False`.
- Na **edição**, a política é reaplicada sobre o `actor_type` resultante: mudar o
  tipo para `ai`/`hybrid` **força** `requires_approval=True` mesmo que o campo não
  seja enviado; um `False` explícito nesse caso é rejeitado. Assim o campo **nunca
  enfraquece** a validação humana obrigatória de resultados de IA.

## 6. Isolamento, concorrência e auditoria

- **Isolamento (RT-01):** empresa derivada da Membership (`require_context`);
  função de outra empresa → 404 indistinguível + `security.cross_org_attempt`
  auditado com `entity_type="function"` e `entity_id` alvo (sem payload). Aplica-se
  a detalhe, edição e transições.
- **Concorrência:** teste real em PostgreSQL — duas mutações concorrentes na mesma
  versão (editar vs inactivar): exactamente uma vence, a outra recebe conflito;
  `version` avança **uma** vez (sem lost update nem dupla transição).
- **Auditoria (RT-02):** evento 10 (`function.created`/`function.updated`) da lista
  fechada; inactivação/reactivação usam `function.updated` com
  `operation`+`transition`. Metadados incluem `operation`, `actor_type`,
  `transition` e `fields` (nomes) — **nunca** `purpose`, `responsibilities`,
  `constraints` nem instruções integrais (provado por teste com tokens únicos que
  não aparecem em nenhum metadado).

## 7. Frontend

Área empresarial **Funções** (`FunctionsWorkspace`) montada em `OrganisationGate`
(a seguir ao portefólio), **sem novo router** e sem store global — estado de vista
local (lista/criação/detalhe/edição). Reutiliza o cliente HTTP central (sessão +
CSRF). Inclui: lista com filtros por estado e tipo, paginação determinística;
criação e edição (`FunctionForm`) com selecção **opcional** de documento de
instruções (só oferece documentos empresariais `instrucoes` com versão válida; o
servidor revalida); inactivação **com confirmação explícita**; reactivação
explícita; função `inactive` claramente identificada (aviso e badge). A regra
SEC-HUM reflecte-se na UI (para `ai`/`hybrid` a caixa "requer aprovação" fica
marcada e desactivada). Não foram criados modelos de funções, políticas avançadas
nem gestão de permissões.

## 8. Testes e demonstração

- **Backend (31 novos):** `test_function_api.py` (criação dos 3 tipos; tipo
  inválido; defaults; `ai`/`hybrid` rejeitam `requires_approval=false`; `human`
  aceita ambos; documento `instrucoes` da mesma empresa aceite; tipo errado,
  empresa alheia, ligado a produto e sem `current_version` rejeitados; listagem
  isolada; detalhe alheio 404 auditado; edição incrementa `version`; versão
  obsoleta 409; inactivar; `inactive` fora da lista `active`; reactivar; transição
  repetida 409; ausência de DELETE; auditoria sem texto integral; edição de
  `inactive` sem reactivar; PATCH não altera `status`; edição para `ai` força
  aprovação e rejeita `false` explícito; filtro por `actor_type`; nome em branco
  rejeitado; inactivação alheia 404; anónimo rejeitado). `test_function_concurrency.py`
  (vencedor único). `test_migration.py` (aplica/reverte; sem drift).
- **Frontend (8 novos):** estado vazio; criar; força aprovação IA na UI; editar;
  inactivar com confirmação; reactivar; `inactive` fora da lista `active` por
  defeito; filtro por tipo.
- **Regressão:** backend **324 OK**; frontend **57 OK**; `npm run build` OK.
- **Migração:** `makemigrations --check` → sem drift; aplica em base de testes e
  reverte em base controlada (teste dedicado). **Nota honesta:** reverter a
  migração `functions.0001` **remove** a tabela `functions_functionprofile` (não
  preserva dados do módulo); as restantes apps ficam intactas.

## 9. Eventos de auditoria utilizados

Apenas da lista fechada `AuditAction`: `function.created` (10),
`function.updated` (10) e `security.cross_org_attempt` (20). Nenhuma acção nova
foi introduzida.

## 10. Migrações

`functions/0001_initial.py` (depende de `documents.0001_initial` e
`organisations.0002_...`). Cria a tabela e as 7 CheckConstraints. Sem drift.

## 11. VAL e pendências

- **VAL-007 → Parcial** (função criada, seleccionável logicamente e com ciclo de
  vida/histórico demonstrados; a validação completa exige o uso numa execução —
  F1-P05-PR02).
- **VAL-002 / VAL-012** permanecem **Parciais** (isolamento e auditoria reforçados
  com o novo módulo; suites transversais e consolidação em F1-P07).
- **Reservas/integrações adiadas:** snapshot das instruções na execução (MVP-11);
  bloqueio de selecção de funções `inactive` na criação de execução (PR02);
  atenção/consolidação (F1-P07). Sem desvio estrutural real → **nenhuma decisão
  global criada**.

## 12. Estado final e próximo passo

- **F1-P05 Em execução (1/6).** Estado de revisão: **Não revista** — a execução
  técnica não substitui a revisão humana (guia §10).
- **Próximo prompt recomendado: F1-P05-PR02** (execuções com contexto e snapshots
  imutáveis). **Não iniciado nesta iteração.**
