# F1-P06-PR03 — Revisão humana dos resultados importados

- **Fase:** F1 — MVP
- **Pipeline:** F1-P06 — Resultados, revisão e aplicação controlada
- **Prompt:** F1-P06-PR03 · **Item:** MVP-14 · **Capacidade:** MVP-14.C1
- **Histórias:** MVP-14.H1, MVP-14.H2 · **Tarefas:** MVP-14.T1–T4
- **Requisitos transversais:** RT-01, RT-02, RT-05, RT-09, RT-10
- **Validação principal:** VAL-010 (Parcial) · **Validação reforçada:** VAL-009 (Parcial)
- **Estado:** Concluído / Não revista · **F1-P06:** 3/6

## Veredicto

Owner pode **rever** a tentativa actual de uma execução em
`result_pending_validation` e **aprovar**, **rejeitar** ou **pedir correcção**. Cada
operação é um comando explícito com o seu endpoint; a decisão vive num campo
fechado próprio (`ResultReview.decision`), nunca num campo genérico de estado. As
revisões são **imutáveis**, preservam-se com as tentativas, e **aprovar não aplica
nenhuma alteração oficial** (sem versão documental, sem tocar em
Product/Decision/WorkItem, sem aplicação, nunca `completed`). Autorização
(só Owner activo) e concorrência (uma revisão por tentativa; a 2.ª recebe 409)
estão demonstradas. Sem drift de migrações; suites backend e frontend verdes.

## Modelo — `ResultReview` (apps/executions/models.py)

| Campo | Tipo | Notas |
|---|---|---|
| `id` | UUID | pk |
| `organisation` | FK PROTECT | obrigatória, `editable=False` |
| `execution` | FK PROTECT → AIExecution | obrigatória |
| `result_attempt` | FK PROTECT → ResultAttempt | **única** (uma revisão por tentativa) |
| `reviewer` | FK PROTECT → User | deriva do utilizador autenticado |
| `decision` | CharField fechado | `approved` / `rejected` / `correction_requested` |
| `observations` | TextField | opcional na aprovação; obrigatória na rejeição/correcção |
| `created_at` | DateTime | `auto_now_add` |

**Regras estruturais:** append-only (save/delete/queryset bloqueados por
`ResultReviewImmutableError`); relações históricas em PROTECT; o conteúdo do
resultado **não** é copiado para a revisão (vive só na `DocumentVersion` da
tentativa). **Constraints de BD:** `uniq_resultreview_result_attempt` (defesa final
de concorrência), `executions_resultreview_decision_closed`,
`executions_resultreview_observations_required`
(`decision='approved' OR observations != ''`).

**Migração:** `executions/0003_resultreview.py` (aditiva; cria só a tabela nova).
`makemigrations --check` → sem drift.

## Transições (política central — transitions.py)

Todos os comandos consomem `validate_transition` (nenhuma matriz reimplementada) e
incrementam `AIExecution.version` **exactamente uma vez**:

- **Aprovar:** `result_pending_validation → approved`
- **Rejeitar:** `result_pending_validation → rejected` (terminal no MVP)
- **Pedir correcção:** `result_pending_validation → prepared` (preserva
  `current_result_attempt`, a tentativa e a revisão; permite nova importação com o
  número seguinte)

## Serviço — `review_service.py`

`approve_result` / `reject_result` / `request_correction` partilham
`_perform_review` (transacção atómica):

1. autoriza (só Owner activo — `membership.role == OWNER`) → `NotOwner` (403);
2. observações obrigatórias na rejeição/correcção → `ObservationsRequired` (400);
3. bloqueia a execução (`select_for_update`), valida `expected_version`
   (`VersionConflict` 409) e o estado (`ExecutionNotPendingValidation` 409);
4. resolve e bloqueia a tentativa, exigindo que seja `current_result_attempt`
   (`AttemptNotCurrent` 409; tentativa histórica já substituída não é revista de
   novo) — `AttemptNotFound` (404);
5. verifica ausência de revisão prévia (`AlreadyReviewed` 409; a constraint única é
   a defesa final — `IntegrityError` → `AlreadyReviewed`);
6. cria a revisão (`full_clean`), transita pela política central e incrementa a
   versão uma vez;
7. audita (evento real correspondente).

`ExecutionNotFound` é tratado na view como 404 indistinguível + auditoria
cross-org. `audit_review_denied` emite o evento `denied` **fora** da transacção
revertida (para persistir), no caso de dupla revisão.

## Endpoints (urls.py / views.py)

- `POST /api/v1/executions/{id}/result-attempts/{n}/approve`
- `POST /api/v1/executions/{id}/result-attempts/{n}/reject`
- `POST /api/v1/executions/{id}/result-attempts/{n}/request-correction`
- `GET  /api/v1/executions/{id}/reviews`

**Entrada** (estrita): `expected_version` (obrigatório, inteiro) e `observations`;
rejeita `status`/`reviewer`/`decision`/internos (400). Não há acção genérica de
revisão com decisão arbitrária (base `_ReviewCommandView` fixa a decisão por
subclasse). **Resposta 201:** `{review, execution (contexto mínimo), attempt}`.
`GET /reviews` devolve histórico mínimo (sem conteúdo do resultado).

## Auditoria (eventos 14–16)

`result.approved` / `result.rejected` / `result.correction_requested`
(entity = `result_review`), metadados `operation`, `attempt_number`, `review_id`,
`transition`, `execution_version` — **sem** resultado nem observações integrais
(provado com tokens). Dupla revisão negada → `denied` (mesma acção). Acesso cruzado
→ `security.cross_org_attempt` + 404.

## Frontend — `ValidationPanel`

No `ExecutionDetail`, em `result_pending_validation` o `ValidationPanel` assume
(nos restantes estados fica o `ResultAttemptsPanel`). Apresenta: tentativa actual
(origem, conteúdo original, pré-visualização segura via `ResultAttemptView`),
histórico de tentativas (abrível) e de revisões (só leitura), e três acções
separadas. A **aprovação** exige confirmação com o texto obrigatório (aprovar
valida o resultado / não aplica alterações / aplicação será operação posterior);
**rejeição e correcção** exigem observações. Botões desactivados durante a
submissão; 409 recarrega o estado sem repetir; depois de correcção volta ao
formulário de importação; **nenhuma acção de aplicação** (nota explícita). Snapshots
e versões documentais de contexto continuam no detalhe (acima). Contratos tipados
em `api/executions.ts` (`listReviews`, `reviewResult`).

## Testes

**Backend (24):** `test_result_review.py` (Owner aprova; não-Owner 403; aprovação
só→approved e uma transição; sem versão documental; não altera
Product/Decision/WorkItem; sem aplicação; rejeição exige observações e →rejected
terminal; correcção exige observações e →prepared preservando tentativa/revisão;
nova importação cria tentativa seguinte; tentativa histórica não re-revista; dupla
revisão→409 e caminho `AlreadyReviewed` auditado `denied`; versão obsoleta→409;
revisão alheia→404 auditada; imutabilidade; eventos 14–16 emitidos; auditoria sem
conteúdo; entrada estrita; listagem mínima) + `test_result_review_concurrency.py`
(duas revisões concorrentes → exactamente uma). **Frontend (7):**
`result-review.test.tsx` (contexto completo; aprovar com confirmação; rejeitar com
observações; pedir correcção → Preparada; histórico de tentativas e revisões; sem
aplicação; 409 recarrega) + 3 testes de PR02 ajustados ao novo estado pending.

**Resultados:** 123 testes `apps.executions` backend OK; 112 frontend OK; `tsc` +
`vite build` OK; `makemigrations --check` sem drift.

## Problemas encontrados

- Falso positivo de deadlock/`connection is closed` em corridas locais: causado por
  pipes `| head` que fecham o stdout e enviam SIGPIPE ao processo de testes,
  deixando bloqueios na base de testes. **Resolução:** correr as suites redirigindo
  para ficheiro (sem pipe de fecho antecipado). Não é defeito de código.
- Ajuste ao teste "dupla revisão": em sequência, a 2.ª revisão falha por
  `VersionConflict`/estado (a 1.ª já transitou); o caminho da constraint única
  (`AlreadyReviewed` → `denied`) é reproduzido num teste dedicado que recoloca o
  estado por validar.

## Pendências / reservas

- **VAL-010** permanece **Parcial** até a aplicação controlada (F1-P06-PR04+) e a
  validação integrada (PR06). **VAL-009** permanece **Parcial** (reforçada).
- **M1** (fluxo vertical ponta a ponta) **não** declarado nesta etapa.
- Não implementado (fora de âmbito): aplicação, alteração automática de documentos,
  aplicação parcial, diffs, notificações, aprovação automática, excepções à revisão
  humana, chamadas a IA.

## Próximo passo recomendado

**F1-P06-PR04** — Aplicar resultado aprovado a um documento (primeira aplicação
oficial controlada). Não avançar antes de revisão.
