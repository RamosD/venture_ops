---
fase: F1
pipeline: F1-P05
prompt: F1-P05-PR02
modelo: claude-opus-4-8
inicio: 2026-07-14 00:00
fim: 2026-07-14 00:55
estado_execucao: Concluído
estado_revisao: Não revista
commit: não criado
---

# Resultado — Prompt 02 — Fundação de execução assistida (AIExecution + contexto)

## 1. Veredicto

**Concluído.** `AIExecution` e `ExecutionContextDocument` existem: criação em
estado `prepared`, snapshots imutáveis de função e produto gerados no servidor,
`instruction_version` como versão exacta das instruções, contexto ligado a
**versões documentais exactas** (ordenado, isolado, imutável), política central de
estados disponível para F1-P06 (sem antecipar comandos funcionais), API
list/create/detail, isolamento por empresa e auditoria (evento 11) sem conteúdo
integral. Sem PATCH nem DELETE. Migração aplica, reverte em base controlada e
**sem drift**.

**Fronteiras respeitadas:** não se implementou execução automática, pacote de
contexto, chamada a IA, resultados, revisão, aplicação de alterações nem as
transições funcionais de F1-P06 (apenas a matriz declarada e testada). Sem UI.

**Regressão verde:** backend **365 testes OK** (324 anteriores + 41 novos);
frontend inalterado (**57 OK**); `makemigrations --check` sem drift.

## 2. Modelos

### `AIExecution` (`executions_aiexecution`, estende `OrganisationScopedModel`)

| Campo | Tipo | Regra |
|---|---|---|
| `product` | FK→Product `PROTECT` | obrigatório, mesma empresa, `active` na criação |
| `function_profile` | FK→FunctionProfile `PROTECT` | obrigatório, mesma empresa, `active` na criação |
| `requested_by` | FK→User `PROTECT` | deriva de `request.user` |
| `title` | CharField(255) | obrigatório, não vazio |
| `objective` | TextField | obrigatório, não vazio |
| `request_instructions` | TextField | obrigatório, não vazio |
| `constraints` | TextField | opcional |
| `expected_output_format` | TextField | obrigatório, não vazio |
| `execution_mode` | TextChoices | `manual_local`/`manual_external` |
| `status` | TextChoices `editable=False` | enum oficial completa; nasce `prepared` |
| `function_snapshot` | JSONField `editable=False` | gerado no servidor |
| `product_snapshot` | JSONField `editable=False` | gerado no servidor |
| `instruction_version` | FK→DocumentVersion `PROTECT` `editable=False` | versão exacta ou `null` |
| `version` | PositiveIntegerField | concorrência (≥1) |

CheckConstraints: 4 campos de texto não vazios; `execution_mode` e `status`
fechados; `version ≥ 1`.

### `ExecutionContextDocument` (`executions_executioncontextdocument`)

`id` UUID; `execution` FK `PROTECT` `editable=False`; `document_version` FK
`PROTECT` `editable=False`; `order` PositiveInteger; `purpose` CharField(255)
opcional curto; `created_at`. **Imutável** (save bloqueia update, delete bloqueado,
queryset bloqueia update/delete). Constraints: **unique(execution, order)**,
**unique(execution, document_version)**, `order ≥ 1`.

## 3. Snapshots (gerados exclusivamente no servidor)

- **`function_snapshot`**: `id`, `name`, `actor_type`, `purpose`,
  `responsibilities`, `constraints`, `requires_approval` — só os campos aprovados
  da função no instante da criação. Nunca fornecido/alterado pelo cliente;
  alterações posteriores à função (ou a sua inactivação) **não** o mudam nem
  invalidam a execução.
- **`product_snapshot`**: `id`, `name`, `purpose`, `status`, e `phase`/
  `target_audience` **só quando existirem**. Sem credenciais, email nem dados
  pessoais (o responsável **não** entra no snapshot). Alterações posteriores ao
  produto não o mudam.
- **`instruction_version`**: `null` se a função não tiver documento de instruções;
  caso contrário aponta para a `current_version` exacta no instante da criação
  (documento tem de continuar `instrucoes` e da mesma empresa). Se o documento
  estiver `denied` no momento da criação → execução **rejeitada** (400); se
  `confirm`, a execução é criada (a política é reavaliada na geração do pacote —
  F1-P05-PR04). Alterações posteriores ao documento/função não mudam a versão.

## 4. Política de estados (para F1-P06)

Módulo central [`transitions.py`](../../../../../backend/apps/executions/transitions.py):
estados oficiais `prepared`/`result_pending_validation`/`approved`/`rejected`/
`completed`; matriz válida = `prepared→result_pending_validation`,
`result_pending_validation→approved|rejected|prepared` (correcção),
`approved→completed`; todas as restantes inválidas; `rejected`/`completed`
terminais. `can_transition`/`validate_transition` são o **ponto único** a consumir
por F1-P06. Nesta pipeline nenhuma transição funcional é exposta — a criação impõe
`prepared` e não existe endpoint genérico de mudança de estado.

## 5. Regras de contexto (selecção de versões)

- Combinação `execution+order` e `execution+document_version` **únicas**;
- associação **imutável** após a criação;
- cada versão pertence à mesma empresa; documento pode ser **empresarial**
  (`product` null) ou tem de pertencer ao **produto da execução** — versão de
  documento ligado a outro produto → 400; de outra empresa → 400;
- a **versão de instruções da função não é repetida** como documento de dados → 400;
- **pelo menos uma** versão de contexto é obrigatória → 400 se vazia;
- `export_policy=denied` → **rejeitada** na selecção (400); `confirm` aceite
  (sujeita a confirmação na geração); `is_outdated` **não bloqueia** (apresentado
  como aviso no detalhe);
- a ordem deriva da **posição na lista** (o cliente não escolhe `order`); nunca se
  lê a versão *actual* do documento — usa-se a versão exacta indicada.

## 6. API

- `GET /api/v1/executions` — lista da empresa; filtros `product`, `status`,
  `function_profile`, `execution_mode`; paginação; ordenação determinística
  (`-created_at, id`); **sem conteúdo integral** (metadados + `document_count`).
- `POST /api/v1/executions` — recebe `product`, `function_profile`, `title`,
  `objective`, `request_instructions`, `constraints?`, `expected_output_format`,
  `execution_mode` e `context` (lista ordenada de `{document_version, purpose?}`);
  **rejeita** `organisation`, `status`, snapshots, `instruction_version` e campos
  internos (400); cria execução+snapshots+contexto numa transacção; audita.
- `GET /api/v1/executions/{id}` — metadados, snapshots, `instruction_version` e
  lista ordenada de documentos (título, tipo, `version_number`, checksum,
  `export_policy` **actual**, `is_outdated`); **sem conteúdo integral** (o conteúdo
  será montado só pelo serviço de pacote — F1-P05-PR04).

**Sem PATCH nem DELETE** (405): o contexto é imutável e não há edição da execução
nesta pipeline.

## 7. Isolamento, integridade e auditoria

- **Isolamento (RT-01):** empresa derivada da Membership; execução alheia → 404
  indistinguível + `security.cross_org_attempt` (`entity_type="execution"`).
  Entradas alheias (produto/função/versão) → 400 (não vazam existência).
- **Integridade:** relações históricas com `PROTECT`; snapshots e versões exactas
  nunca alteráveis pelo cliente; duas criações independentes permitidas.
- **Auditoria (RT-02):** evento 11 (`execution.created`) com `operation`,
  `product_id`, `function_profile_id`, `execution_mode`, `document_count`,
  `document_version_ids` e `instruction_version_id` — **sem** `objective`,
  `request_instructions`, `constraints`, snapshots nem conteúdo documental (provado
  por teste com tokens únicos).

## 8. Testes (41 novos)

`test_execution_api.py` cobre os 28 requisitos: criação com função `active`;
função `inactive` rejeitada; produto `archived` rejeitado; contexto por versão
exacta; documento empresarial/mesmo produto aceites; outro produto/outra empresa
rejeitados; `denied` rejeitado; `confirm` aceite; `instruction_version` exacta
preservada (+ `denied` rejeita, instrução não repetível como dados); alterações
posteriores a instruções/função/produto/versão **não** alteram a execução; ordem
preservada; ordem duplicada (BD) e versão duplicada (API) rejeitadas; nasce
`prepared`; cliente não escolhe status/snapshots; listagem isolada e sem conteúdo;
detalhe alheio 404 auditado; auditoria sem conteúdo; sem PATCH/DELETE; duas
criações; filtros. `test_transitions.py` (matriz completa válida/inválida +
alinhamento com `Status`). `test_immutability.py` (contexto imutável). 
`test_migration.py` (aplica/reverte; sem drift). **Regressão:** backend 365 OK;
frontend 57 OK. **Nota honesta:** reverter a migração `executions.0001` remove as
tabelas do módulo (não preserva execuções); outras apps ficam intactas.

## 9. VAL e reservas

- **VAL-007 → Parcial** (função agora **usada** numa execução com snapshot; falta
  o ciclo completo com resultados — F1-P06).
- **VAL-008 → Parcial** (versões exactas preservadas e contexto congelado
  demonstrados; a **geração** fiel do pacote e a `export_policy` efectiva chegam em
  F1-P05-PR04).
- **VAL-009 → não validável** aqui (exige resultados — F1-P06).
- **VAL-002/VAL-012** reforçadas (Parciais).
- Reservas: geração do pacote e reavaliação de `export_policy`/`confirm`
  (F1-P05-PR04); comandos funcionais e matriz aplicada (F1-P06). Sem desvio
  estrutural → **nenhuma decisão global criada**.

## 10. Estado final e próximo passo

- **F1-P05 Em execução (2/6).** Estado de revisão: **Não revista**.
- **Próximo prompt recomendado: F1-P05-PR03** (interface de preparação da
  execução). **Não iniciado nesta iteração.**
