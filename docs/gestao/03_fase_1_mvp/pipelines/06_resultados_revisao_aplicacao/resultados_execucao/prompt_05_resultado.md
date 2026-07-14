# F1-P06-PR05 — Aplicação a decisão, pendência e fecho sem alteração

- **Fase:** F1 — MVP · **Pipeline:** F1-P06 · **Prompt:** F1-P06-PR05
- **Item:** MVP-15 · **Capacidade:** MVP-15.C2 · **História:** MVP-15.H2
- **Tarefas:** MVP-15.T2, T3, T4, T5
- **Requisitos transversais:** RT-01, RT-02, RT-05, RT-09, RT-10
- **Validação principal:** VAL-010 (Parcial) · **Reforço:** VAL-004/005/006
- **Estado:** Concluído / Não revista · **F1-P06:** 5/6

## Veredicto

Uma execução `approved` conclui-se **exactamente uma vez** por **um** de quatro
caminhos: nova versão documental (PR04), **substituir decisão**, **concluir
pendência** ou **fechar sem alteração**. Uma execução produz **no máximo uma
`ResultApplication`** — a segunda tentativa (mesmo de outro tipo, mesmo por outro
endpoint) recebe 409. Decisões e pendências são actualizadas pelos **serviços
existentes** (`supersede_decision`, `complete_work_item`); o fecho `no_change` é
explícito e auditado, sem tocar em nenhuma fonte oficial. Provas negativas passam;
sem drift; suites verdes.

## Contratos (regra global: uma aplicação por execução)

- `POST /api/v1/executions/{id}/apply/decision` — `attempt_id`/`attempt_number`,
  `target_decision`, `expected_execution_version`, `expected_decision_version`,
  `title`, `context`, `decision_text`, `impact?`, `decided_at?`, `detail_document?`,
  `confirmation`.
- `POST /api/v1/executions/{id}/apply/work-item` — `target_work_item`,
  `expected_execution_version`, `expected_work_item_version`, `confirmation`.
- `POST /api/v1/executions/{id}/close-without-application` —
  `expected_execution_version`, `rationale`, `confirmation`.

Entrada estrita (rejeita `application_type`/`review`/versão criada/internos).
Confirmações do contrato: `apply-decision`, `apply-work-item`,
`close-without-application`. **201** criado / **200** idempotente.

## Serviço — refactor partilhado

`_prepare` (prefixo comum aos quatro caminhos): autoriza (só Owner activo), bloqueia
a execução, resolve a **idempotência antes do estado** (aplicação existente com
fingerprint igual → devolve-a; diferente → 409), exige `approved` +
`expected_execution_version`, tentativa **actual** com `ResultReview approved`.
`_complete_execution` transita `approved → completed` (+1 versão);
`_audit_apply` emite o evento 17 comum.

- **Decisão:** valida a decisão alvo **activa** do Product (empresarial/outro Product
  → 422; alheia → 404 auditada), chama `decisions.service.supersede_decision`
  (`AlreadySuperseded` → 422; `VersionConflict` → 409) — nova `active`, anterior
  `superseded`, cadeia preservada; `ResultApplication` guarda `target_decision`
  (anterior) e `created_decision` (nova).
- **Pendência:** valida o WorkItem `open` do Product, chama
  `work_items.service.complete_work_item` (`InvalidTransition` → 422;
  `VersionConflict` → 409) — não altera título/notas/tipo/prazo; guarda
  `target_work_item`.
- **Fecho:** `no_change` com `rationale` obrigatório; **sem** alvo nem mutação de
  fontes oficiais.

## Idempotência / concorrência / atomicidade

- `request_fingerprint` canónico por tipo (inclui `application_type`, alvo, versões
  esperadas e dados explícitos relevantes) — repetição idêntica → aplicação existente
  (200); diferente → 409.
- **Uma aplicação por execução** (OneToOne = defesa final): segundo caminho → 409;
  duas aplicações de tipos diferentes concorrentes → exactamente um vencedor.
- Bloqueia execução e alvo; mutação + criação da aplicação + transição na mesma
  transacção; falha não conclui a execução nem deixa entidade parcialmente alterada.
- Constraints de coerência por tipo (decision/work_item/no_change) — migração
  `executions/0005` (aditiva; `makemigrations --check` sem drift).

## Auditoria

Evento 17 `change.applied` distingue `document`/`decision`/`work_item`/`no_change`,
regista o alvo e a entidade criada quando existir e a `transition`
`approved→completed` — **sem** resultado, observações, `decision_text`, `notes` nem
`rationale` integral (provado com tokens). Tentativa sem aprovação → `denied`.
Acesso cruzado → `security.cross_org_attempt` + 404.

## Frontend — `ApplicationPanel` (quatro opções)

Só em `approved`. Quatro opções mutuamente exclusivas (nova versão documental /
substituir decisão / concluir pendência / fechar sem alteração); apresenta **apenas
alvos elegíveis** (decisões `active`, pendências `open`, documentos não-`resultado`
do Product); formulários explícitos (nova decisão; confirmação de conclusão;
rationale) — nenhum preenchido por parsing do resultado (consultável como
referência); **resumo exacto da mutação** antes da confirmação; aviso de que a
aprovação não aplicou nada e de que só é possível **uma** aplicação; 409 recarrega
sem sobrescrever; apresenta a aplicação final com ligação ao alvo e **impede segunda
aplicação**. Contratos em `api/executions.ts`; reutiliza `api/decisions.ts` e
`api/workItems.ts` (sem 2.º cliente).

## Provas negativas (verificadas)

- Importar / aprovar / rejeitar / pedir correcção **não** alteram
  Document/Decision/WorkItem.
- Só `apply/*` ou `close-without-application` leva a `completed`.
- Nenhum estado não-`approved` (prepared/pending/rejected) permite aplicar (409).
- Nenhum endpoint contorna a `ResultApplication` única (segundo caminho → 409).

## Testes

**Backend (19):** `test_result_application_paths.py` (substituição de decisão;
superseded/outro Product/alheia rejeitadas; nova activa/anterior superseded/cadeia/
ligação; conclusão de pendência preservando campos; final/outro Product/alheia
rejeitadas; `no_change` exige rationale, não altera entidades, conclui; todos exigem
aprovação e confirmação; uma aplicação por execução; doc→decisão e decisão→pendência
rejeitadas; idempotência e 409; auditoria única sem conteúdo; provas negativas) +
`test_result_application_paths_concurrency.py` (dois tipos concorrentes → um
vencedor). O caminho documental (PR04, 25 testes) foi reverificado verde após o
refactor. **Frontend (7):** `result-application-paths.test.tsx` (quatro opções; só
alvos elegíveis; substituir decisão com confirmação; concluir pendência; fecho com
rationale; impede segunda aplicação; 409 recarrega).

**Resultados:** 44 testes backend (PR04 documento + PR05 paths + concorrência) OK;
124 frontend OK; `tsc` + `vite build` OK; `makemigrations --check` sem drift.
(Regressão completa de `apps.executions` a correr como verificação final.)

## Problemas encontrados

- Refactor do serviço partilhado: garantir que o estado `approved` é validado **antes**
  de resolver a tentativa (uma execução `prepared` pode não ter tentativas) — mantido
  do PR04 no `_prepare` comum.
- Teste de componente com corrida de carregamento: as opções renderizam após
  `loadState==='ready'`; os testes passaram a aguardar (`findByTestId`) a primeira
  opção antes de interagir.

## Não implementado (fora de âmbito)

Múltiplas aplicações; aplicação parcial; criação automática de pendências; decisão
gerada automaticamente; parsing/diff; rollback; agentes; chamadas a IA.

## Reservas / pendências

- **VAL-010** permanece **Parcial** até a validação integrada ponta a ponta (E1–E6)
  em F1-P06-PR06. **VAL-004/005/006** recebem evidência de aplicação.
- **M1** (fluxo vertical ponta a ponta) **não** declarado.

## Próximo passo recomendado

**F1-P06-PR06** — Validar o fluxo vertical e encerrar F1-P06 (E2E, concorrência,
provas negativas, regressão, marco M1). Não avançar antes de revisão.
