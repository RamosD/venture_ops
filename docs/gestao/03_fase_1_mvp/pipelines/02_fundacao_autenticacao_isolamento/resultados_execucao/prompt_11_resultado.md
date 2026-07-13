---
fase: F1
pipeline: F1-P02
prompt: F1-P02-PR11
modelo: claude-opus-4-8
inicio: 2026-07-13 08:30
fim: 2026-07-13 09:10
estado_execucao: Concluído
estado_revisao: Não revista
commit: não criado
---

# Resultado — Prompt 11 — Contexto de empresa e testes de isolamento

## 1. Resumo

Concluída a pipeline F1-P02. O contexto de empresa passa a ser **derivado
exclusivamente da Membership activa** no servidor (helper simples e explícito, sem
middleware genérico): pedidos autenticados sem Membership são rejeitados (403), o
acesso por identificador valida a pertença à empresa do contexto (id alheio → 404
consistente e auditado), e o cliente não pode trocar de empresa por parâmetro.
Criada a primeira bateria de isolamento com **duas empresas** (8 testes) sobre os
endpoints existentes, com auditoria de acessos cruzados. 96 testes backend + 12
frontend passam; comportamento validado ao vivo. VAL-002 e VAL-012 permanecem
**parciais**. **F1-P02 fica Concluída (11/11).**

## 2. Comportamento implementado

- `apps/organisations/context.py`:
  - `require_context(request)` → `(membership, organisation)` da Membership activa;
    **403** se não existir contexto de empresa.
  - `deny_cross_org(request, organisation, target_id, entity_type)` → audita o
    acesso cruzado e devolve **404** consistente (não revela existência).
- `OrganisationDetailView` (`GET /api/v1/organisations/<uuid:pk>`): valida a
  pertença; id do contexto → 200; outro id → 404 auditado.
- `OrganisationView.patch`: sem Membership → **403** (era 404).
- Convenção documentada: **403** = sem contexto de empresa; **404** = recurso de
  outra empresa (consistente com id inexistente).

## 3. Regras de isolamento (SEC-ISO-01..03; IS-01..04)

- Contexto derivado da Membership; o cliente nunca escolhe `organisation_id`.
- Operações por id validam a pertença à empresa do contexto.
- Queries empresariais filtram-se pela empresa do contexto (padrão estabelecido
  para os módulos de domínio futuros).
- Aplicado **apenas** aos endpoints actualmente existentes (empresa); sem
  produtos nem módulos de pipelines posteriores.

## 4. Auditoria

- `security.cross_org_attempt` (evento 20) em tentativas cruzadas: actor, empresa
  do **contexto**, `entity_id` do alvo, `result=denied`, `metadata={"reason":"cross_org"}`,
  `correlation_id` presente; sem payloads.

## 5. Testes de isolamento (duas empresas)

Utilizadores/empresas criados por factory nos testes (cenário técnico com vários
utilizadores/empresas, apesar da regra de uma empresa por conta na experiência):
contexto derivado; troca por id bloqueada; leitura cruzada (não revela existência);
alteração cruzada impossível; sem Membership → 403; Membership inactiva sem
contexto; tentativa cruzada auditada; acesso legítimo funcional.

## 6. Alterações

### Ficheiros criados
- `backend/apps/organisations/context.py`
- `backend/apps/organisations/tests/test_isolation.py`

### Ficheiros alterados
- `backend/apps/organisations/views.py` (`OrganisationDetailView`; PATCH sem Membership → 403)
- `backend/apps/organisations/urls.py` (`organisations/<uuid:pk>`)
- `backend/apps/organisations/tests/test_onboarding.py` (edição sem Membership → 403)
- `docs/gestao/04_matriz_validacao_global.md` (VAL-002/VAL-012, evidência)
- Registos globais no fecho.

### Migrações
- **Nenhuma nova** (apenas comportamento nas vistas).

## 7. Comandos e evidências

- `makemigrations --check` → "No changes detected".
- `manage.py test apps.organisations.tests.test_isolation` → **8 testes OK**.
- `manage.py test` → **96 testes OK**; `npm run test` → **12 testes OK**.
- **Ao vivo:** own org por id → 200; id aleatório/alheio → 404 "Não encontrado.";
  evento `security.cross_org_attempt` com `reason=cross_org`, `correlation_id`,
  `entity_id` do alvo.

## 8. Validações (11/11)

| # | Verificação | Resultado | Evidência |
|---|---|---|---|
| 1 | Contexto derivado da Membership | Sucesso | `test_context_is_derived_from_membership` |
| 2 | Cliente não troca empresa por parâmetro | Sucesso | id alheio → 404 (live + teste) |
| 3 | Pedido sem Membership rejeitado | Sucesso | 403 (teste) |
| 4 | Leitura cruzada falha | Sucesso | 404; não revela existência |
| 5 | Alteração cruzada falha | Sucesso | `test_cross_alteration_is_impossible` |
| 6 | Tentativa por id alheio falha | Sucesso | 404 (live + teste) |
| 7 | Tentativas cruzadas auditadas | Sucesso | `security.cross_org_attempt` (live + teste) |
| 8 | Acesso legítimo funcional | Sucesso | `test_legitimate_access_within_own_company` |
| 9 | 100% dos testes de isolamento passam | Sucesso | 8/8 |
| 10 | Testes backend/frontend/CI passam | Sucesso | 96 + 12; CI inalterado válido |
| 11 | VAL-002/VAL-012 parciais com evidência | Sucesso | matriz actualizada |

## 9. Matriz de validação

- **VAL-002 → Parcial** (isolamento nos endpoints existentes; módulos de domínio
  ainda não existem). **VAL-012 → Parcial** (emissores integrados; consolidação em
  F1-P07).

## 10. Problemas / limitações / riscos

- Isolamento aplicado apenas ao módulo de empresa (único com endpoints); os
  módulos de domínio (produtos, documentos…) reutilizarão este padrão nas
  pipelines seguintes.
- Suite completa de segurança (MVP-18) e consulta de auditoria ficam para F1-P07.
- Sem bloqueios reais.

## 11. Estado da pipeline

- **F1-P02 Concluída (11/11).** Percurso vertical técnico fechado: arranque → BD →
  frontend↔backend → armazenamento → testes/health/CI → auditoria → autenticação →
  ecrãs → recuperação/rate limiting/perfil → onboarding → contexto/isolamento.

## 12. Próximo passo

- Analisar o estado real do repositório e **gerar a pipeline F1-P03** (portefólio
  e ficha do produto), just-in-time. Não criada automaticamente nesta iteração.
