---
fase: F1
pipeline: F1-P06
prompt: F1-P06-PR01
modelo: claude-opus-4-8
inicio: 2026-07-14 08:20
fim: 2026-07-14 09:20
estado_execucao: Concluído
estado_revisao: Não revista
commit: não criado
---

# Resultado — Prompt 01 — Registo manual e imutável de resultados

## 1. Veredicto

**Concluído.** É possível importar manualmente um resultado produzido fora da
aplicação (texto colado ou ficheiro UTF-8), materializá-lo como `Document` do tipo
`resultado` com conteúdo **só no armazenamento privado**, criar uma **tentativa
imutável e numerada** (`ResultAttempt`) e transitar a execução de `prepared` para
`result_pending_validation` pela política central de estados. **Importar ≠ aprovar
≠ aplicar** (DEC-F0-FINAL-05): nenhuma aprovação ou aplicação automática ocorre.

**Condição de entrada confirmada:** F1-P05 Concluída (6/6) e **commitada**
(`405bc10 feat(f1-p05): implementar funções, execuções e pacote de contexto`);
árvore de trabalho com apenas o trabalho (não commitado) de F1-P06-PR01;
`AIExecution`, `Document`, `DocumentVersion`, armazenamento e auditoria funcionais;
nenhum defeito estrutural pendente. Nenhuma correcção silenciosa de módulos
anteriores — as alterações ao módulo documental são **requisitos explícitos** deste
prompt (ver §7).

**Regressão:** suite total **424 testes** (396 + 28 novos). Verde verificado de
forma limpa: **28 testes novos** (`test_result_attempt` + concorrência + migração)
e o módulo **documental (54)** — cobrem todo o código novo de PR01 e as restrições
à API genérica; `makemigrations --check` **sem drift** no estado de PR01; frontend
inalterado (**91 OK** — este prompt é só backend). **Nota (posterior a PR01):** a
árvore de trabalho recebeu depois código externo de **F1-P06-PR03 (revisão)** —
`ResultReview`/`review_service`/vistas de aprovação — **sem migração**, o que
introduz *drift* e faria a suite completa falhar o teste de *drift*; isto é externo
ao âmbito de PR01/PR02 e não foi alterado por mim.

## 2. Modelo e contratos

**`ResultAttempt`** (`executions_resultattempt`) — append-only, imutável:

| Campo | Regra |
|---|---|
| `id` UUID | pk |
| `organisation` FK PROTECT | obrigatória, `editable=False` |
| `execution` FK→AIExecution PROTECT | `related_name="result_attempts"` |
| `attempt_number` | ≥1, **atribuído no servidor** |
| `result_document_version` FK→DocumentVersion PROTECT | versão exacta do resultado |
| `imported_by` FK→User PROTECT | — |
| `source_mode` | `pasted`/`file` (derivado no servidor) |
| `source_tool` | obrigatório, não vazio |
| `source_model` / `source_notes` | opcionais (notas ≤ 500) |
| `created_at` | — |

Constraints: `unique(execution, attempt_number)`, `attempt_number ≥ 1`,
`source_mode` fechado, `source_tool` não vazio. **Imutabilidade:** `save` bloqueia
após criação; `delete` e queryset `update`/`delete` levantam
`ResultAttemptImmutableError`. Conteúdo **nunca** é guardado aqui nem em
`AIExecution`.

**`AIExecution.current_result_attempt`** (novo) — FK→ResultAttempt, nullable,
PROTECT, `editable=False`, gerado no servidor; aponta só para uma tentativa da
própria execução; preserva-se após aprovação/rejeição/conclusão (F1-P06+). Migração
`executions/0002` **aditiva** (nullable) — segura para execuções `prepared`
existentes.

**API** (montada sob `/api/v1/`):
- `POST /executions/{id}/result-attempts` — JSON (`content`) ou multipart (`file`).
- `GET  /executions/{id}/result-attempts` — lista (crescente por `attempt_number`,
  sem conteúdo).
- `GET  /executions/{id}/result-attempts/{attempt_number}` — detalhe com o
  conteúdo da **versão exacta**.

## 3. Importação e transição

Disponível **apenas** com `execution.status=prepared`; exige `expected_version`.
Aceita **exactamente uma** de `content`/`file` (ambos ou nenhum → 400);
`source_tool` obrigatório; `source_mode` derivado no servidor. Aplica o limite
documental (`DOCUMENT_MAX_BYTES` → 413); ficheiro binário/UTF-8 inválido → 400. O
nome do ficheiro **não** é usado como `storage_key` (gerada no servidor); não se
guarda caminho local, cookie, token nem metadados sensíveis; o resultado é
**conteúdo não confiável**.

Operação atómica (`import_result`): bloqueia a execução (`select_for_update`),
valida `expected_version` e o estado, determina `attempt_number`, cria o
`Document` `resultado` (associado ao Product da execução, título determinístico
`Resultado (tentativa N) — <execução>`) + `DocumentVersion` inicial via o
**serviço documental público** (`create_document`, que coordena BD↔storage), cria
a `ResultAttempt`, define `current_result_attempt`, aplica `prepared →
result_pending_validation` pela política central, incrementa `version` **uma vez**
e audita. Segunda importação enquanto `result_pending_validation` → **409**; versão
obsoleta → **409**.

## 4. Coordenação BD↔storage

`create_document` escreve o objecto **antes** da BD e limpa o órfão se a sua
própria transacção falhar. Como a tentativa/transição ocorrem **depois**, se um
passo posterior falhar o serviço remove o objecto órfão escrito (e regista
`storage.failure` se a remoção falhar) — a execução **nunca** muda de estado numa
importação falhada. **Sem** declarar transacção distribuída inexistente.

## 5. Storage do conteúdo

O conteúdo do resultado vive **exclusivamente** no armazenamento privado (chave
gerada no servidor); `ResultAttempt.result_document_version` aponta para a versão
exacta. O checksum SHA-256 da versão **coincide** com o conteúdo importado (testado).

## 6. Listagem e detalhe

- **Listagem:** ordem crescente por `attempt_number`; inclui `source_tool`,
  `source_model`, `source_mode`, `checksum`, `byte_size`, versão documental e data;
  **sem conteúdo integral** nem chaves de storage.
- **Detalhe:** metadados + conteúdo da **versão exacta** da tentativa (nunca
  `Document.current_version`) + contexto mínimo da execução (estado, versão,
  título, tentativa actual) — **não** o pacote integral de contexto, sem segredos
  nem auditoria interna.

## 7. Restrições da API documental genérica (requisito do prompt)

- `POST /documents` **rejeita** `document_type=resultado` (400) — resultados são
  materializados só pela importação.
- `PATCH /documents/{id}` e `POST /documents/{id}/restore` **rejeitam** (409)
  documentos ligados a uma `ResultAttempt` (geridos pela execução); a **leitura**
  continua permitida. A verificação usa a relação inversa `result_attempts` sem
  importar o módulo `executions` (evita ciclo de dependências).
- **Compatibilidade:** documentos `resultado` porventura existentes de antes desta
  implementação **não** são apagados nem convertidos; apenas a criação genérica
  passa a ser bloqueada e a edição/recuperação bloqueada quando há tentativa ligada.
  Sem migração de dados. Dois testes documentais que criavam `resultado` pela API
  genérica foram adaptados (intenção preservada: UTF-8/filtro), pois o contrato
  mudou por requisito explícito.

## 8. Auditoria

Evento 13 (`result.imported`), `entity_type="result_attempt"`,
`entity_id=<attempt>`. Metadados mínimos: `operation`, `execution_id`,
`attempt_number`, `source_mode`, `document_id`, `document_version_id`, `checksum`
abreviado, `execution_version`. **Não** inclui o resultado, `source_notes`,
`source_tool`/`source_model`, prompt, pacote nem conteúdo (provado por testes com
tokens). Acesso cruzado → `security.cross_org_attempt` + 404 indistinguível.

## 9. Testes (novos) e demonstração

`test_result_attempt.py` cobre os 29 requisitos: content→tentativa 1; file→
tentativa; ambos/nenhum rejeitados; limite→413; UTF-8 inválido→400; `source_tool`
obrigatório; nasce `prepared`; transita para `result_pending_validation`; não
aprova; não altera Product/documentos/decisões/pendências; referencia a versão
exacta (`resultado` do Product); conteúdo fora da BD; checksum coincide; tentativa
imutável; `attempt_number` no servidor (cliente rejeitado); segunda importação→409;
versão obsoleta→409; **falha de storage não altera a execução**; **falha de BD
limpa o órfão**; `resultado` bloqueado na API genérica; documento ligado não
editável/recuperável (leitura ok); listagem sem conteúdo; detalhe com versão
exacta; execução alheia→404 auditada; auditoria sem conteúdo; entrada estrita.
`test_result_import_concurrency.py`: **duas importações concorrentes → exactamente
uma tentativa** e uma transição (`version=2`). `test_migration.py` (executions)
actualizado: aplica/reverte as **três** tabelas, sem drift. **Regressão:** backend
**424 OK**; documentos **54 OK**; frontend **91 OK**.

## 10. VAL e reservas

- **VAL-009 → Parcial** (resultado externo importável como tentativa imutável
  associada à execução correcta; UI de importação/histórico e validação integrada
  em F1-P06-PR02+).
- **VAL-010 não validada** (revisão/aprovação — F1-P06 posteriores).
- **VAL-002/VAL-012/VAL-014** permanecem Parciais.
- Reservas: UI de importação e histórico de tentativas; sanitização na
  renderização do resultado importado (F1-P06-PR-seguinte / F1-P07); revisão,
  aprovação, rejeição, correcção e aplicação (F1-P06). Sem desvio estrutural →
  **nenhuma decisão global criada**.

## 11. Estado final e próximo passo

- **F1-P06 Em execução (1/6).** Estado de revisão: **Não revista**.
- **Próximo prompt recomendado: F1-P06-PR02.** **Não iniciado nesta iteração.**
