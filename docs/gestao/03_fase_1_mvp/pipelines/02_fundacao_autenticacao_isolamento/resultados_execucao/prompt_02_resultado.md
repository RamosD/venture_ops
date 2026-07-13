---
fase: F1
pipeline: F1-P02
prompt: F1-P02-PR02
modelo: claude-opus-4-8
inicio: 2026-07-12 18:10
fim: 2026-07-12 18:55
estado_execucao: Concluído
estado_revisao: Não revista
commit: não criado
---

# Resultado — Prompt 02 — PostgreSQL, fundação de identidade/empresa e isolamento

## 1. Resumo

Configurado PostgreSQL por variáveis de ambiente e criada, de forma atómica, a
fundação mínima de identidade e empresa: `CustomUser` (email único, UUIDv4,
`AUTH_USER_MODEL` activo), `Organisation` (estado Activa/Arquivada) e `Membership`
(utilizador–empresa, papel Owner, unicidade por utilizador+empresa). Adicionada a
convenção reutilizável `OrganisationScopedModel` (relação real e obrigatória com
`Organisation`, `PROTECT`, não editável pelo cliente) para entidades empresariais
futuras, sem tabela fictícia. Gerada e aplicada a primeira migração do projecto
(`accounts.0001`, `organisations.0001`) numa base PostgreSQL vazia; reversão e
reaplicação verificadas. 16 testes verdes. Sem login/onboarding/edição. Sem
SQLite. `/api/system/ping` continua funcional.

## 2. Alterações

### Ficheiros criados

- `backend/apps/common/models.py` (`UUIDPrimaryKeyModel` abstracto)
- `backend/apps/accounts/managers.py` (`CustomUserManager`)
- `backend/apps/accounts/models.py` (`CustomUser`)
- `backend/apps/accounts/migrations/0001_initial.py`
- `backend/apps/accounts/tests/__init__.py`, `backend/apps/accounts/tests/test_custom_user.py`
- `backend/apps/organisations/models.py` (`Organisation`, `Membership`, `OrganisationScopedModel`)
- `backend/apps/organisations/migrations/0001_initial.py`
- `backend/apps/organisations/tests/__init__.py`, `backend/apps/organisations/tests/test_identity_foundation.py`

### Ficheiros alterados

- `backend/config/settings.py` (`django.contrib.contenttypes`+`auth`; `AUTH_USER_MODEL="accounts.CustomUser"`; `DATABASES` PostgreSQL por env)
- `backend/requirements.txt` (`psycopg[binary]==3.2.13`)
- `backend/.env.example` (`POSTGRES_*`)
- `backend/README.md` (base de dados de desenvolvimento; comando migrate)
- Registos globais no fecho (status, painel, diário).

### Ficheiros removidos

- Nenhum.

## 3. Migrações

- `accounts.0001_initial` — cria `CustomUser` (com dependência swappable de `AUTH_USER_MODEL`).
- `organisations.0001_initial` — cria `Organisation` e `Membership` (FK a `AUTH_USER_MODEL` e a `Organisation`; `UniqueConstraint(user, organisation)`).
- `makemigrations --check --dry-run`: "No changes detected" (sem drift entre modelos e migrações).
- Migrações de framework aplicadas: `contenttypes`, `auth` (dependências normais do PermissionsMixin).

## 4. Comandos executados

- `pip install "psycopg[binary]>=3.2,<3.3"`
- `docker run -d --name ventureops-pg-dev ... -p 5433:5432 postgres:16` (PostgreSQL descartável de desenvolvimento)
- `python manage.py check` → 0 issues
- `python manage.py makemigrations accounts organisations` → 2 migrações
- `python manage.py migrate` (base vazia) → OK
- Reversão controlada: `migrate organisations zero`, `migrate auth zero`, `migrate accounts zero` → OK; `migrate` (reaplicar) → OK
- `python manage.py test` → 16 testes OK
- `runserver` + `GET /api/system/ping` → 200 `{"status":"ok"}`

## 5. Testes (10/10 obrigatórios)

| # | Verificação | Resultado | Evidência |
|---|---|---|---|
| 1 | Migrações aplicam em PostgreSQL vazio | Sucesso | `migrate` OK; base de testes criada de raiz |
| 2 | Migrações revertíveis de forma controlada | Sucesso | `...zero` OK + reaplicação OK |
| 3 | `AUTH_USER_MODEL` → `CustomUser` | Sucesso | teste + settings |
| 4 | Email único garantido | Sucesso | `IntegrityError` no duplicado |
| 5 | `Membership` liga utilizador e empresa | Sucesso | teste de associação |
| 6 | Papel Owner aceite (e default) | Sucesso | teste de papel |
| 7 | Restrições de `Membership` aplicadas | Sucesso | `UniqueConstraint(user, organisation)` |
| 8 | Convenção empresarial exige `Organisation` | Sucesso | introspecção (null=False, PROTECT), sem tabela fictícia |
| 9 | Sem endpoint/serviço de onboarding | Sucesso | `Resolver404` nas rotas de onboarding/empresa |
| 10 | `/api/system/ping` funcional | Sucesso | 200 `{"status":"ok"}` |

Total: **16 testes**, todos OK.

## 6. Problemas e excepções

- Problemas encontrados: Nenhum.
- Ambiente: o PostgreSQL local nativo (serviço `postgresql-x64-18`, porta 5432) não
  tem credenciais conhecidas; usou-se um PostgreSQL **descartável em contentor**
  (`ventureops-pg-dev`, porta 5433) para verificação. A aplicação é agnóstica —
  aponta-se para qualquer PostgreSQL via `POSTGRES_*`. Compose canónico em PR04.
- Trabalho não executado (por desenho): login/logout, recuperação, onboarding,
  edição da empresa, selector, convites, papéis avançados, restantes entidades.

## 7. Decisões relevantes e vigência

- Sem desvio estrutural face a `docs/produto/00_decisoes_arranque.md`; não foi
  criada nova decisão global. `CustomUser`, UUIDv4, `AUTH_USER_MODEL` e PostgreSQL
  seguem as decisões de PR01. Driver: `psycopg[binary]` 3.2 (implementação dentro
  da stack; registado em `requirements.txt`).

## 8. Pendências materiais / riscos

- Pendência: o contentor `ventureops-pg-dev` é de desenvolvimento; PR04 formaliza
  o ambiente local (Docker Compose). Risco: nenhum estrutural.
- Autenticação e onboarding continuam pendentes (PR07–PR10), por desenho.

## 9. Próximo passo

- Executar `F1-P02-PR03` (frontend React/TS + cliente HTTP central consumindo
  `/api/system/ping`). Não avançar autonomamente.
