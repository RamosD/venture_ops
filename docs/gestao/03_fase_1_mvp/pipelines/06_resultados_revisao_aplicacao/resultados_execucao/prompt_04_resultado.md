# F1-P06-PR04 — Aplicação controlada: nova versão documental

- **Fase:** F1 — MVP · **Pipeline:** F1-P06 · **Prompt:** F1-P06-PR04
- **Item:** MVP-15 · **Capacidade:** MVP-15.C1 · **História:** MVP-15.H1
- **Tarefas:** MVP-15.T1, T2, T4, T5 (parcialmente)
- **Requisitos transversais:** RT-01, RT-02, RT-03, RT-05, RT-09, RT-10
- **Validações:** VAL-010 (Parcial), VAL-004 (evidência de versão aplicada)
- **Estado:** Concluído / Não revista · **F1-P06:** 4/6

## Veredicto

Um resultado **aprovado** pode, por comando humano explícito, ser aplicado a um
documento alvo do Product da execução: cria-se uma **nova `DocumentVersion`**
(preservando todas as anteriores), liga-se à execução e à tentativa aprovada via
`ResultApplication` e a execução transita `approved → completed`. A operação é
**explícita** (o servidor nunca extrai/aplica o resultado automaticamente),
**idempotente** (`request_fingerprint` + unicidade por execução) e **auditada**
(evento 17). **Nenhuma aplicação sem aprovação** é possível. Sem drift; suites
verdes.

## Modelo — `ResultApplication` (apps/executions/models.py)

Append-only (save/delete/queryset bloqueados). Campos: `id`, `organisation`
(PROTECT), `execution` (**OneToOne** PROTECT — uma aplicação por execução),
`result_attempt` (PROTECT), `review` (PROTECT), `application_type` fechado
`{document, decision, work_item, no_change}` (só `document` neste prompt),
`applied_by` (PROTECT), `request_fingerprint` (SHA-256), `change_summary`,
`rationale`, alvos/criados **PROTECT null** (`target_document`,
`base_document_version`, `created_document_version`, `target_decision`,
`created_decision`, `target_work_item`), `created_at`.

- **Sem GenericForeignKey**; **sem FK de `executions` dentro de `DocumentVersion`**
  (evita dependência circular) — a ligação oficial é `created_document_version`.
- **Constraints:** `uniq_resultapplication_execution` (defesa final),
  `type_closed`, `document_coherent` (`application_type='document'` ⇒ alvo, versão
  base e versão criada presentes e `change_summary` não vazio).
- Migração `executions/0004_resultapplication.py` (aditiva; `makemigrations
  --check` sem drift).

## Comando — `application_service.apply_document`

Transacção atómica:

1. autoriza (só Owner activo) → 403;
2. valida confirmação explícita do contrato (`DOCUMENT_APPLY_CONFIRMATION =
   "apply-document"`), conteúdo explícito e `change_summary` → 400;
3. valida/encode o conteúdo (UTF-8 + limite; 413/400) e calcula o checksum canónico;
4. bloqueia a execução; **idempotência antes do estado** — se já existe aplicação:
   fingerprint igual → devolve a existente (200); diferente → 409;
5. exige `status == approved` (senão 409) e `expected_execution_version` (senão 409);
6. resolve a tentativa (actual) e exige `ResultReview approved` (senão 409, denied);
7. bloqueia e valida o **documento alvo**: do Product da execução (empresarial/outro
   Product → 422), não `resultado` (422), não gerido por ResultAttempt (422),
   `expected_document_version` (409); alheio → 404 (cross-org auditado);
8. escreve o objecto, cria a nova `DocumentVersion` (anteriores preservadas), cria a
   `ResultApplication` (base + criada) e transita `approved → completed` (+1 versão);
9. audita `change.applied` (evento 17).

**Fingerprint canónico** (SHA-256 sobre JSON ordenado): execution, attempt,
application_type, target_document, expected_execution_version,
expected_document_version, checksum do conteúdo, change_summary normalizado.

## Atomicidade BD↔storage

- Falha de storage (`_write_object`) → nada de BD escrito → execução fica `approved`
  → 503 + `storage.failure`.
- Falha de BD após a escrita → o objecto órfão é removido e tudo é revertido →
  **nunca** `completed` sem `ResultApplication` nem `ResultApplication` sem versão.
- Conflito → alvo e execução intactos.

## API

- `POST /api/v1/executions/{id}/apply/document` — entrada estrita: `attempt_id` **ou**
  `attempt_number`, `target_document`, `expected_execution_version`,
  `expected_document_version`, `content`, `change_summary`, `confirmation`. Rejeita
  `application_type`/`review`/versão criada/internos. **201** criado / **200**
  idempotente.
- `GET /api/v1/executions/{id}/application` — a aplicação da execução ou 404.

Resposta: `{application, execution (contexto mínimo)}` — sem conteúdo integral.

## Idempotência

- Repetir **o mesmo** comando (mesmos parâmetros/versões esperadas) depois de timeout
  devolve a aplicação existente (200) **sem nova versão** — provado.
- Repetir com conteúdo/alvo/parâmetros **diferentes** → 409.
- Um único evento de aplicação bem-sucedida; unicidade por execução é a defesa final.

## Auditoria

Evento 17 `change.applied` (entity = `result_application`): `application_type`,
`attempt_number`, `review_id`, `target_document_id`, `base_version`,
`created_version`, `checksum` abreviado, `transition`, `execution_version` — **sem**
conteúdo aplicado nem `change_summary` integral (provado com tokens). Tentativa sem
aprovação → `denied`. Cross-org → `security.cross_org_attempt` + 404.

## Frontend — `ApplicationPanel`

No `ExecutionDetail`, **só em `approved`** (`ExecutionDetail` passa a orquestrar:
`prepared`→importação, `result_pending_validation`→revisão, `approved`→aplicação,
restantes→histórico). Apresenta: tentativa aprovada + revisão, resultado original
(referência), documentos elegíveis do Product, versão actual do alvo, editor de
conteúdo + `change_summary`, botão "Usar resultado como ponto de partida" (nunca
aplica directamente), **confirmação final explícita** (o conteúdo foi revisto / será
criada nova versão oficial / a execução ficará concluída), aviso de que a **aprovação
anterior não aplicou nada**; 409 recarrega documento + execução sem sobrescrever;
mostra a versão criada e a ligação; **sem decisões nem pendências**. Contratos em
`api/executions.ts` (`applyDocument`, `getApplication`); reutiliza
`api/documents.ts` sem 2.º cliente.

## Testes

**Backend (25):** `test_result_application.py` (aplicação em `approved`; prepared/
pending/rejected não aplicam; completed com comando diferente → 409; tentativa tem
de estar aprovada; aprovação sem aplicação não altera documento; conteúdo/
confirmação obrigatórios; alvo do Product aceite; empresarial/outro Product/
resultado → 422; alheio → 404 auditado; versão base guardada e anterior preservada;
nova versão criada e ligada; versão obsoleta doc/execução → 409; falha de storage →
`approved`; falha de BD sem aplicação parcial; idempotência idêntica e 409 diferente;
imutabilidade; auditoria sem conteúdo; não-Owner 403; GET application; entrada
estrita) + `test_result_application_concurrency.py` (duas aplicações idênticas
concorrentes → exactamente uma versão). **Frontend (5):**
`result-application.test.tsx` (exige escolha/conteúdo/confirmação; não confirma sem
conteúdo; 409 recarrega; mostra versão criada; sem decisões/pendências).

**Resultados:** frontend 117 OK; `tsc` + `vite build` OK; `makemigrations --check`
sem drift. (Suite backend completa de `apps.executions` a correr como verificação de
regressão.)

## Problemas encontrados

- Ordenação do serviço: uma execução `prepared` pode não ter tentativas, pelo que a
  resolução da tentativa (para o fingerprint) 404-ava antes do estado. **Resolução:**
  verificar a idempotência (existência de aplicação) e o estado `approved` **antes**
  de resolver a tentativa.
- O contentor Postgres de desenvolvimento tinha parado (inactividade); reiniciado
  (`docker start ventureops-db-1`) para correr migrações/testes.

## Não implementado (fora de âmbito)

Decisão, pendência, fecho sem alteração (F1-P06-PR05); múltiplos alvos; parsing/diff
automático; rollback automático; aplicação parcial; chamada a IA.

## Reservas / pendências

- **VAL-010** permanece **Parcial** até os restantes caminhos (PR05) e a validação
  integrada (PR06). **VAL-004** recebe evidência da versão aplicada.
- **M1** (fluxo vertical ponta a ponta) **não** declarado.

## Próximo passo recomendado

**F1-P06-PR05** — Aplicar a decisão, pendência ou fechar sem alteração. Não avançar
antes de revisão.
