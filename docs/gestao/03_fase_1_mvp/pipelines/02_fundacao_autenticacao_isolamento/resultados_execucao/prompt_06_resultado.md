---
fase: F1
pipeline: F1-P02
prompt: F1-P02-PR06
modelo: claude-opus-4-8
inicio: 2026-07-12 23:00
fim: 2026-07-12 23:35
estado_execucao: Concluído
estado_revisao: Não revista
commit: não criado
---

# Resultado — Prompt 06 — Auditoria mínima append-only

## 1. Resumo

Criada a entidade `AuditEvent` e o serviço público `record_event`, com auditoria
append-only ao nível aplicacional. `actor` e `organisation` são opcionais
(`SET_NULL`, nunca `CASCADE`), com snapshots dos identificadores para preservação
histórica. A acção é validada contra a **lista fechada** dos 21 eventos do MVP;
`correlation_id` é preservado; os metadados são protegidos contra conteúdo
proibido (segredos e conteúdo integral). Update/delete normais estão bloqueados
(instância e queryset). Migração aplica e reverte. 48 testes backend passam
(14 novos de auditoria). Integração dos emissores nos módulos **não** foi feita
nesta etapa (começa em PR07, consolida em F1-P07). VAL-012 anotada **Parcial**.

## 2. Modelo `AuditEvent`

- `id` (UUIDv4), `action` (lista fechada `AuditAction`), `result`
  (`success`/`failure`/`denied`);
- `actor` FK→User `null=True SET_NULL related_name="+"`;
  `organisation` FK→Organisation `null=True SET_NULL`;
- `actor_id_snapshot`, `organisation_id_snapshot` (identificadores preservados);
- `entity_type`, `entity_id`; `correlation_id` (indexado); `metadata` (JSON filtrado);
- `created_at` (indexado). Sem `CASCADE`; sem cópia integral de utilizador/empresa.
- Append-only: `save()` bloqueia updates, `delete()` bloqueia, e o
  `AuditEventQuerySet` bloqueia `update()`/`delete()` em massa.

## 3. Migração

- `apps/audit/migrations/0001_initial.py` — cria `AuditEvent`.
- Aplica e **reverte** (`migrate audit zero` → OK; `migrate audit` → OK).

## 4. Serviço de emissão (`apps/audit/service.py`)

`record_event(action, actor=None, organisation=None, entity_type, entity_id,
result, correlation_id, metadata)`:
- valida a acção contra `AuditAction.values` (senão `InvalidAuditActionError`);
- `reject_prohibited_content(metadata)` (senão `ProhibitedContentError`);
- grava snapshots dos ids; gera `correlation_id` se não fornecido.

## 5. Conteúdo proibido (`apps/audit/metadata.py`)

- Chaves proibidas (exactas e por sufixo `_password`/`_token`/`_secret`/`_cookie`/`_key`):
  palavras-passe, tokens, cookies, segredos, `prompt`, `content`, `payload`, etc.
- Valores string acima de 1000 caracteres rejeitados (evita documentos/resultados integrais).
- Profundidade máxima de metadados limitada.

## 6. Eventos testados

`auth.login`, `auth.failed`, `organisation.created`, `organisation.updated`,
`product.created`, `result.imported`; acção inválida rejeitada. Lista fechada
completa dos 21 eventos definida em `AuditAction`.

## 7. Comandos executados

- `makemigrations audit` → `0001_initial`
- `docker compose up -d --build backend` → backend saudável; `showmigrations audit` → `[X]`
- `docker compose exec backend python manage.py test` → **48 testes OK**
- Reversibilidade: `migrate audit zero` (OK) + `migrate audit` (OK)

## 8. Validações (11/11)

| # | Verificação | Resultado | Evidência |
|---|---|---|---|
| 1 | Emissão com actor e organização | Sucesso | `test_emit_with_actor_and_organisation` |
| 2 | Emissão sem actor | Sucesso | `test_emit_without_actor` |
| 3 | Emissão sem organização | Sucesso | `test_emit_without_organisation` |
| 4 | `correlation_id` preservado | Sucesso | `test_correlation_id_is_preserved` |
| 5 | Evento não pode ser actualizado | Sucesso | `save()`/queryset `update()` → `AppendOnlyViolation` |
| 6 | Evento não pode ser apagado | Sucesso | `delete()`/queryset `delete()` → `AppendOnlyViolation` |
| 7 | Remover actor não elimina evento | Sucesso | `test_deleting_actor_keeps_event` (SET_NULL + snapshot) |
| 8 | Remover empresa não elimina eventos | Sucesso | `test_deleting_organisation_keeps_event` |
| 9 | Conteúdo proibido rejeitado | Sucesso | chaves sensíveis + valor integral → `ProhibitedContentError` |
| 10 | Migração aplica e reverte | Sucesso | apply/unapply/apply |
| 11 | Testes e CI passam | Sucesso | 48 testes OK; workflow CI inalterado válido |

## 9. Matriz de validação

- **VAL-012 → Parcial.** Evidência: modelo + serviço de auditoria append-only com
  preservação e protecção de conteúdo. Integração dos emissores pendente (PR07+/F1-P07).

## 10. Problemas / limitações

- Emissores ainda não integrados nos módulos (por desenho). Consulta/linha
  temporal de auditoria (MVP-17.C2) fica para F1-P07.
- Sem alteração ao CI; a suite cresceu para 48 testes.

## 11. Decisões relevantes e vigência

- Sem desvio face a `docs/produto/00_decisoes_arranque.md`. `SET_NULL` + snapshots
  seguem a orientação da pipeline (PR06) e de DEC-20260712-06. Sem nova decisão global.

## 12. Próximo passo

- Executar `F1-P02-PR07` (autenticação backend, sessão e CSRF). Não avançar
  autonomamente.
