---
fase: F1
pipeline: F1-P02
prompt: F1-P02-PR10
modelo: claude-opus-4-8
inicio: 2026-07-13 03:20
fim: 2026-07-13 04:15
estado_execucao: Concluído
estado_revisao: Não revista
commit: não criado
---

# Resultado — Prompt 10 — Onboarding e comportamento da empresa

## 1. Resumo

Implementado o onboarding empresarial sobre as entidades `Organisation` e
`Membership` já existentes desde PR02 (**não recriadas**, **sem novas migrações**).
Um utilizador autenticado sem Membership activa é conduzido ao onboarding, que
cria transaccionalmente uma Organisation activa e uma Membership Owner; pedidos
concorrentes são serializados (`select_for_update`) e a criação de uma segunda
empresa é bloqueada. Consulta e edição mínima da empresa com autorização Owner no
servidor; criação e alteração auditadas. Interface mínima de onboarding e de
dados da empresa. 88 testes backend + 12 frontend passam; fluxo validado ao vivo
(onboarding no browser; bloqueio da 2.ª empresa; auditoria). VAL-002 → **Parcial**.

## 2. Endpoints e serviços

- `POST /api/v1/onboarding` — cria Organisation + Membership Owner (transaccional).
- `GET /api/v1/organisation` — empresa actual (ou `onboarding_required`).
- `PATCH /api/v1/organisation` — edição mínima (nome), só Owner.
- Serviço `apps/organisations/service.py`: `get_active_membership`,
  `complete_onboarding` (`@transaction.atomic` + `select_for_update`),
  `edit_organisation`.

## 3. Regras aplicadas

- O papel **Owner é atribuído pelo serviço**; o cliente não o define.
- O cliente **não escolhe `organisation_id`**: derivado sempre da Membership no servidor.
- Edição só afecta a empresa do próprio utilizador (autorização no backend).
- Sem selector de empresa, convites, gestão de membros nem papéis diferenciados; sem produtos.

## 4. Componentes (frontend)

- `OrganisationGate` — decide entre onboarding (sem empresa) e painel da empresa.
- `OnboardingForm` — nome mínimo → cria empresa.
- `OrganisationPanel` — estado + edição do nome.

## 5. Eventos auditados

`organisation.created` (evento 3) e `organisation.updated`, com actor e empresa.

## 6. Migrações

- **Nenhuma nova.** A concorrência é resolvida por `select_for_update` sobre a
  linha do utilizador (comportamento, não esquema), pelo que não foi preciso
  alterar o modelo de PR02.

## 7. Alterações

### Ficheiros criados
- `backend/apps/organisations/service.py`, `views.py`, `urls.py`
- `backend/apps/organisations/tests/test_onboarding.py`
- `frontend/src/api/organisation.ts`
- `frontend/src/components/OrganisationGate.tsx`, `organisation-gate.test.tsx`

### Ficheiros alterados
- `backend/config/urls.py` (`/api/v1/` onboarding + organisation)
- `backend/apps/organisations/tests/test_identity_foundation.py` (teste PR02 obsoleto actualizado: onboarding passa a existir)
- `frontend/src/App.tsx` (OrganisationGate na área autenticada)
- `frontend/src/auth/auth-flow.test.tsx` (mock de `/v1/organisation`)
- `docs/gestao/04_matriz_validacao_global.md` (VAL-002 → Parcial)
- Registos globais no fecho.

## 8. Comandos e evidências

- `makemigrations --check` → "No changes detected" (sem novas migrações).
- `manage.py test` → **88 testes OK**; `npm run build`/`test` → **12 testes OK**.
- **Ao vivo (browser):** login `owner@x.pt` (sem empresa) → onboarding → criar
  "Acme Lda" → painel "Empresa" (Estado: active).
- **Ao vivo (backend):** Membership Owner activa; `organisation.created` auditado;
  2.ª empresa → `AlreadyHasOrganisationError`; 1 organisation / 1 membership.

## 9. Validações (11/11)

| # | Verificação | Resultado | Evidência |
|---|---|---|---|
| 1 | 1.ª entrada sem empresa → onboarding | Sucesso | `onboarding_required` (browser + teste) |
| 2 | Onboarding cria Organisation + Membership Owner | Sucesso | live + `test_onboarding_creates_org_and_owner_membership` |
| 3 | Operação transaccional | Sucesso | `@transaction.atomic` |
| 4 | Pedidos duplicados não criam duas empresas | Sucesso | `select_for_update`; teste sequencial |
| 5 | 2.ª empresa bloqueada | Sucesso | 409 (live + `test_second_organisation_is_blocked`) |
| 6 | Não autorizado não edita empresa alheia | Sucesso | `test_other_user_cannot_edit_someone_elses_org` (404) |
| 7 | Edição válida persistida | Sucesso | `test_owner_edits_organisation` |
| 8 | Criação e alteração auditadas | Sucesso | `organisation.created`/`updated` (live + teste) |
| 9 | Frontend completa o onboarding | Sucesso | browser real |
| 10 | Testes negativos passam | Sucesso | bloqueio/autorização/validação |
| 11 | Auth e recuperação continuam funcionais | Sucesso | 88 testes (auth/recuperação incluídos) |

## 10. Matriz de validação

- **VAL-002 → Parcial.** Fundação de isolamento (empresa/membership/contexto no
  servidor). Suite de isolamento com duas empresas em PR11.

## 11. Problemas / limitações

- Concurrency testada de forma sequencial (o mecanismo real é `select_for_update`);
  a prova de concorrência verdadeira exigiria carga paralela.
- Sem selector/convites/membros/papéis diferenciados/produtos (por desenho).

## 12. Próximo passo

- Executar `F1-P02-PR11` (contexto de empresa no servidor e testes de isolamento).
  Não avançar autonomamente.
