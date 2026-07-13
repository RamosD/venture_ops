---
fase: F1
pipeline: F1-P02
prompt: F1-P02-PR08
modelo: claude-opus-4-8
inicio: 2026-07-13 00:50
fim: 2026-07-13 01:40
estado_execucao: Concluído
estado_revisao: Não revista
commit: não criado
---

# Resultado — Prompt 08 — Ecrãs de autenticação no frontend

## 1. Resumo

Criada a interface mínima de autenticação: formulário de login, área autenticada
mínima e logout, integrados com a sessão por cookie do backend (PR07). O cliente
HTTP central passou a enviar o cookie de sessão (`credentials: same-origin`) e o
token CSRF (`X-CSRFToken`), a tratar 401/403 como sessão expirada e a devolver
mensagens sem detalhe sensível. Estado de sessão gerido por um `AuthContext`
(sem store global complexa e sem persistir credenciais). Build e 8 testes
(Vitest) passam; e2e login→área→logout validado também no **browser real**.
Corrigido o proxy de desenvolvimento (`changeOrigin: false`) para o CSRF do
Django funcionar via proxy. VAL-001 permanece **Parcial**.

## 2. Componentes e rotas

- `AuthProvider` / `useAuth` (`src/auth/AuthContext.tsx`) — estado
  `loading|anon|authed`, `signIn`/`signOut`/`refresh`, aviso de sessão expirada.
- `LoginForm` — email/palavra-passe, estado de submissão, erro genérico,
  prevenção de submissão duplicada (botão desactivado + de-dup no cliente).
- `AuthenticatedArea` — mostra o utilizador, "Verificar sessão" e "Terminar sessão".
- `SystemStatus` — indicador técnico do backend (ping), movido de `App`.
- **Área autenticada por estado** (sem router): `anon` → login; `authed` → área.
  A área só é acessível com sessão válida.

## 3. Contratos utilizados (PR07)

- `GET /api/v1/auth/csrf` (define o cookie CSRF);
- `GET /api/v1/auth/session` (estado da sessão);
- `POST /api/v1/auth/login`, `POST /api/v1/auth/logout` (CSRF exigido);
- `GET /api/system/ping` (indicador de sistema).

## 4. Alterações

### Ficheiros criados

- `frontend/src/auth/AuthContext.tsx`, `frontend/src/auth/auth-flow.test.tsx`
- `frontend/src/api/auth.ts`
- `frontend/src/components/LoginForm.tsx`, `AuthenticatedArea.tsx`, `SystemStatus.tsx`, `SystemStatus.test.tsx`

### Ficheiros alterados

- `frontend/src/api/client.ts` (POST + CSRF + credenciais + handler de 401/403; de-dup só em GET)
- `frontend/src/App.tsx` (AuthProvider + área por estado + SystemStatus)
- `frontend/vite.config.ts` (`changeOrigin: false` — CSRF via proxy)
- `docs/gestao/04_matriz_validacao_global.md` (VAL-001, evidência UI)
- Registos globais no fecho.

### Ficheiros removidos

- `frontend/src/App.test.tsx` (substituído por `SystemStatus.test.tsx` + `auth-flow.test.tsx`)

## 5. Comandos e evidências

- `npm run build` (tsc + vite) OK; `npm run test` → **8 testes OK**
  (2 SystemStatus + 6 auth e2e).
- `docker compose up -d --build frontend`; browser real em `http://localhost:5180`:
  login (`owner@x.pt`) → **"Área autenticada — Sessão iniciada como owner@x.pt"** →
  "Terminar sessão" → volta ao login.
- Diagnóstico: primeiro login no browser deu **403 CSRF** (proxy com
  `changeOrigin: true` alterava o `Host`, falhando a verificação de Origin do
  Django); corrigido para `changeOrigin: false` → login **200**.

## 6. Validações (9/9)

| # | Verificação | Resultado | Evidência |
|---|---|---|---|
| 1 | Entrar pela UI | Sucesso | browser: área autenticada; teste e2e |
| 2 | Área autenticada só com sessão | Sucesso | render por estado (anon→login) |
| 3 | Logout termina a sessão | Sucesso | browser + teste (volta ao login) |
| 4 | Sessão expirada tratada | Sucesso | `test trata a sessão expirada` (aviso + login) |
| 5 | CSRF funciona | Sucesso | header `X-CSRFToken` (teste) + login 200 no browser |
| 6 | Erro de login sem dados sensíveis | Sucesso | "Credenciais inválidas." genérico |
| 7 | Credenciais não persistidas | Sucesso | `localStorage`/`sessionStorage` vazios (teste) |
| 8 | e2e login→área→logout | Sucesso | teste e2e + browser real |
| 9 | Build e testes passam | Sucesso | build OK; 8 testes OK |

## 7. Matriz de validação

- **VAL-001 → Parcial** (backend PR07 + UI PR08). Falta recuperação + rate
  limiting (PR09).

## 8. Problemas / limitações

- Correcção do proxy (`changeOrigin: false`) necessária para o CSRF via proxy;
  registada. Sem router (área por estado — suficiente no MVP).
- Sem recuperação de palavra-passe, perfil, onboarding nem ecrãs de domínio
  (por desenho).

## 9. Decisões relevantes e vigência

- Sem desvio face a `docs/produto/00_decisoes_arranque.md`. O ajuste do proxy é
  coerente com a estratégia de mesma origem (§10). Sem nova decisão global.

## 10. Próximo passo

- Executar `F1-P02-PR09` (recuperação de acesso, rate limiting e perfil mínimo).
  Não avançar autonomamente.
