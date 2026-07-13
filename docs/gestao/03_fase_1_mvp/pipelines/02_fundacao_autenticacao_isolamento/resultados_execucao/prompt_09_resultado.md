---
fase: F1
pipeline: F1-P02
prompt: F1-P02-PR09
modelo: claude-opus-4-8
inicio: 2026-07-13 01:55
fim: 2026-07-13 03:05
estado_execucao: Concluído
estado_revisao: Não revista
commit: não criado
---

# Resultado — Prompt 09 — Recuperação, rate limiting e perfil mínimo

## 1. Resumo

Completadas as capacidades de acesso do MVP: recuperação de palavra-passe por
token temporário de utilização única (com expiração, invalidação de sessões e
email de dev por consola, configurável para SMTP), rate limiting **persistente
em PostgreSQL** (sem Redis, multiprocesso) para login e recuperação com auditoria
de falhas repetidas, e perfil mínimo (consulta/edição do próprio). Interface
mínima de recuperação e de perfil. 78 testes backend + 10 frontend passam; fluxos
validados também ao vivo (rate limit → 429; recuperação por token de consola;
perfil no browser). VAL-001 passa a **Validado** para o escopo do MVP.

## 2. Mecanismo adoptado

- **Rate limiting:** modelo `RateLimitAttempt` (PostgreSQL) com janela deslizante
  por chave com hash (`sha256`); partilhado por todos os processos (BD comum),
  **sem Redis** e **sem dependências novas**. É um **controlo de segurança**
  (não throttling de conveniência): login conta falhas e bloqueia no limiar;
  recuperação conta pedidos. Sucesso de login limpa as falhas.
- **Recuperação:** modelo `PasswordResetToken` (só guarda o hash do token);
  token `secrets.token_urlsafe`, expira (`PASSWORD_RESET_TTL_SECONDS`), uso único
  (`used_at`); `set_password` invalida sessões anteriores (muda o hash de sessão).
- **Email:** `EMAIL_BACKEND` configurável (consola em dev; SMTP por env no piloto).

## 3. Endpoints

- `POST /api/v1/auth/password/reset-request` (genérico; rate limited);
- `POST /api/v1/auth/password/reset-confirm` (token + nova palavra-passe);
- `GET`/`PATCH /api/v1/profile` (próprio; autorização no backend);
- `POST /api/v1/auth/login` passa a ter rate limiting + auditoria.

## 4. Eventos auditados

`auth.failed` com `result=denied` e `metadata={"reason":"rate_limited","scope":...}`
para falhas repetidas (login/recuperação). Sem palavras-passe/payloads.

## 5. Alterações

### Ficheiros criados
- `backend/apps/accounts/rate_limit.py`, `passwords.py`
- `backend/apps/accounts/migrations/0002_passwordresettoken_ratelimitattempt.py`
- `backend/apps/accounts/tests/test_recovery.py`, `test_rate_limit.py`, `test_profile.py`
- `frontend/src/api/profile.ts`
- `frontend/src/components/RecoveryPanel.tsx`, `ProfilePanel.tsx`, `recovery-profile.test.tsx`

### Ficheiros alterados
- `backend/apps/accounts/models.py` (PasswordResetToken, RateLimitAttempt)
- `backend/apps/accounts/views.py` (rate limiting no login; recuperação; perfil)
- `backend/apps/accounts/urls.py`, `backend/config/urls.py` (`/api/v1/profile`)
- `backend/config/settings.py` (email configurável; `RATE_LIMIT_*`; `PASSWORD_RESET_TTL_SECONDS`)
- `backend/.env.example`, `backend/README.md`
- `frontend/src/api/client.ts` (`apiPatch`), `api/auth.ts` (recuperação), `App.tsx`
- `docs/gestao/04_matriz_validacao_global.md` (VAL-001 → Validado)
- Registos globais no fecho.

## 6. Comandos e evidências

- `makemigrations accounts` → `0002_...`; `makemigrations --check` → "No changes detected".
- `docker compose ... --build backend` (force-recreate) → **78 testes OK**.
- `npm run build` OK; `npm run test` → **10 testes OK**.
- **Rate limit ao vivo:** 6 logins inválidos → `401,401,401,401,401,429`;
  `RateLimitAttempt` com 5 linhas na BD (persistente/multiprocesso).
- **Recuperação ao vivo:** reset-request (200 genérico) → token lido da **consola
  (email dev)** → reset-confirm (200) → login senha antiga **401** / senha nova **200**.
- **Perfil no browser:** login → painel "Perfil" (Nome/Email/Guardar) carregado.

## 7. Validações (13/13)

| # | Verificação | Resultado | Evidência |
|---|---|---|---|
| 1 | Pedido de recuperação não revela existência | Sucesso | respostas idênticas (teste + live) |
| 2 | Token válido funciona | Sucesso | reset-confirm 200 (live + teste) |
| 3 | Token expirado rejeitado | Sucesso | `test_expired_token_is_rejected` |
| 4 | Token reutilizado rejeitado | Sucesso | `test_reused_token_is_rejected` |
| 5 | Redefinição invalida sessões antigas | Sucesso | `test_reset_invalidates_previous_sessions` |
| 6 | Rate limit bloqueia no limiar | Sucesso | 6.ª tentativa → 429 (live + teste) |
| 7 | Janela expira | Sucesso | `test_window_expires_and_access_recovers` |
| 8 | Acesso recupera após a janela | Sucesso | idem |
| 9 | Persistente entre processos | Sucesso | linhas em PostgreSQL (BD partilhada) |
| 10 | Falhas repetidas auditadas | Sucesso | evento `auth.failed`/`denied`/`rate_limited` |
| 11 | Perfil só edita o próprio | Sucesso | `ProfileView` usa `request.user`; `test_can_only_edit_self` |
| 12 | Testes backend/frontend/CI passam | Sucesso | 78 + 10; CI inalterado válido |
| 13 | VAL-001 com evidência completa (MVP) | Sucesso | matriz → Validado |

## 8. Dependências

- Nenhuma nova (rate limiting em PostgreSQL; recuperação com `secrets`/`hashlib`;
  email `console`). Sem Redis.

## 9. Matriz de validação

- **VAL-001 → Validado** (escopo MVP de autenticação completo).

## 10. Problemas / limitações

- Recuperação/redefinição não estão na lista fechada de 21 eventos, pelo que não
  emitem evento próprio (apenas as falhas repetidas são auditadas); coerente com
  a lista fechada.
- Sem MFA/SSO/OIDC (fora do MVP). Email real depende de configuração no piloto.

## 11. Decisões relevantes e vigência

- Sem desvio face a `docs/produto/00_decisoes_arranque.md`. Rate limiting em
  PostgreSQL é a concretização prevista (persistente, sem Redis). Sem nova
  decisão global.

## 12. Próximo passo

- Executar `F1-P02-PR10` (empresa, membership e onboarding). Não avançar
  autonomamente.
