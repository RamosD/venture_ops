---
fase: F1
pipeline: F1-P02
prompt: F1-P02-PR07
modelo: claude-opus-4-8
inicio: 2026-07-12 23:50
fim: 2026-07-13 00:35
estado_execucao: Concluído
estado_revisao: Não revista
commit: não criado
---

# Resultado — Prompt 07 — Autenticação backend, sessão e CSRF

## 1. Resumo

Implementada a autenticação backend com Django Auth e sessão por cookie segura:
criação controlada da conta inicial (comando `createinitialuser`), endpoints de
CSRF, login, sessão e logout, com CSRF exigido nas operações mutáveis e auditoria
dos eventos relevantes. Cookies de sessão `HttpOnly`, `SameSite=Lax`, `Secure`
condicional a TLS (explícito por ambiente). Mensagens de erro genéricas (sem
enumeração de emails); sem registo público, sem recuperação, sem rate limiting,
sem MFA/SSO. 62 testes backend passam; fluxo verificado ao vivo. VAL-001 anotada
**Parcial**.

## 2. Endpoints (`/api/v1/auth/`)

| Método | Rota | Função |
|---|---|---|
| GET | `/api/v1/auth/csrf` | define o cookie `csrftoken` |
| POST | `/api/v1/auth/login` | autentica e cria sessão (CSRF exigido) |
| GET | `/api/v1/auth/session` | utilizador actual (ou anónimo) |
| POST | `/api/v1/auth/logout` | invalida a sessão (CSRF exigido) |

Criação de conta: `python manage.py createinitialuser --email <e> --password <p>`
(ou `INITIAL_USER_PASSWORD`). Sem registo público.

## 3. Cookies e sessão

- `SESSION_COOKIE_HTTPONLY=True`, `SESSION_COOKIE_SAMESITE="Lax"`,
  `SESSION_COOKIE_SECURE` = `DJANGO_SECURE_COOKIES` (false em dev; true com TLS).
- `CSRF_COOKIE_HTTPONLY=False` (o frontend lê o token → `X-CSRFToken`),
  `CSRF_COOKIE_SAMESITE="Lax"`, `CSRF_COOKIE_SECURE` condicional.
- Hashing: mecanismos padrão do Django (PBKDF2). Logout faz flush da sessão.
- Nota: o token CSRF **roda no login** (segurança) — o cliente relê o cookie
  após o login.

## 4. Eventos auditados

`auth.login` (sucesso, com actor), `auth.failed` (falha, sem actor),
`auth.logout` (com actor). Metadados vazios — sem palavra-passe/segredos.

## 5. Alterações

### Ficheiros criados

- `backend/apps/accounts/views.py`, `urls.py`
- `backend/apps/accounts/management/commands/createinitialuser.py` (+ `__init__` dos pacotes)
- `backend/apps/accounts/tests/test_auth.py`, `tests/test_createinitialuser.py`

### Ficheiros alterados

- `backend/config/settings.py` (sessions app; middleware sessão/CSRF/auth; DRF SessionAuthentication + IsAuthenticated por defeito; cookies/CSRF; `CORS_ALLOW_CREDENTIALS`)
- `backend/config/urls.py` (`/api/v1/auth/`)
- `backend/.env.example` (`DJANGO_SECURE_COOKIES`, `DJANGO_CSRF_TRUSTED_ORIGINS`)
- `backend/README.md` (secção de autenticação)
- `docs/gestao/04_matriz_validacao_global.md` (VAL-001 → Parcial)
- Registos globais no fecho.

## 6. Comandos e evidências

- `docker compose up -d --build backend`; `makemigrations --check` → "No changes detected".
- `manage.py test` → **62 testes OK**.
- Fluxo ao vivo (curl): `GET /csrf` (200, cookie); login **sem** token → **403**
  (CSRF); login **com** token → **200** (utilizador); `GET /session` → autenticado;
  `POST /logout` → **204**; `GET /session` → anónimo.

## 7. Validações (10/10)

| # | Verificação | Resultado | Evidência |
|---|---|---|---|
| 1 | Conta inicial pelo mecanismo controlado | Sucesso | `createinitialuser` (comando) |
| 2 | Login válido cria sessão | Sucesso | 200 + cookie `sessionid` |
| 3 | Login inválido rejeitado sem detalhe | Sucesso | 401 genérico; wrong-pw == unknown-email |
| 4 | Flags do cookie correctas | Sucesso | HttpOnly + SameSite=Lax (Secure condicional) |
| 5 | CSRF exigido em operações mutáveis | Sucesso | login sem token → 403 (live + teste) |
| 6 | Logout invalida a sessão | Sucesso | 204 + sessão anónima depois |
| 7 | Pedido autenticado devolve o utilizador | Sucesso | `/session` → user |
| 8 | Evento de autenticação auditado | Sucesso | `auth.login`/`auth.failed`/`auth.logout` |
| 9 | Sem segredos/palavra-passe em auditoria/logs | Sucesso | metadados vazios (teste) |
| 10 | Testes e CI passam | Sucesso | 62 testes OK |

## 8. Matriz de validação

- **VAL-001 → Parcial.** Falta recuperação + rate limiting (PR09) e ecrãs (PR08).

## 9. Problemas / limitações

- Sem registo público, recuperação, rate limiting, MFA/SSO/OIDC (por desenho).
- O token CSRF roda no login; o frontend (PR08) tem de reler o cookie após o login.

## 10. Decisões relevantes e vigência

- Sem desvio face a `docs/produto/00_decisoes_arranque.md` (Django Auth, sessão por
  cookie, CSRF por cabeçalho). Sem nova decisão global. Início da integração de
  emissores de auditoria (auth), conforme previsto.

## 11. Próximo passo

- Executar `F1-P02-PR08` (ecrãs de autenticação no frontend). Não avançar autonomamente.
