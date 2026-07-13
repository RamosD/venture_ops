---
fase: F1
pipeline: F1-P02
prompt: F1-P02-PR03
modelo: claude-opus-4-8
inicio: 2026-07-12 19:05
fim: 2026-07-12 19:45
estado_execucao: Concluído
estado_revisao: Não revista
commit: não criado
---

# Resultado — Prompt 03 — Fundação React/TypeScript e cliente HTTP central

## 1. Resumo

Criada a fundação mínima do frontend React + TypeScript (Vite) com um cliente HTTP
central que comunica com `GET /api/system/ping`. A página inicial apresenta três
estados — **a carregar**, **backend disponível** e **backend indisponível** — a
partir da resposta real do backend. O cliente central trata erros de forma
uniforme (`ApiError`), previne submissões duplicadas (de-duplicação de pedidos
idênticos em curso) e usa a base da API por ambiente (`VITE_API_BASE_URL`, por
defeito `/api` via proxy de desenvolvimento — mesma origem, sem CORS). Build
(`tsc` + `vite`) e testes (Vitest, 2 casos) passam. Sem autenticação, sem store
global, sem UI de domínio, sem credenciais no browser.

## 2. Alterações

### Ficheiros criados

- `frontend/package.json`, `frontend/tsconfig.json`, `frontend/vite.config.ts`, `frontend/index.html`, `frontend/.env.example`
- `frontend/src/main.tsx`, `frontend/src/App.tsx`, `frontend/src/App.test.tsx`
- `frontend/src/setupTests.ts`, `frontend/src/vite-env.d.ts`
- `frontend/src/api/client.ts` (cliente HTTP central), `frontend/src/api/system.ts` (chamada ao ping)

### Ficheiros alterados

- `frontend/README.md` (frontend inicializado; comandos e estratégia de proxy)
- Registos globais no fecho (status, painel, diário).

### Ficheiros removidos

- `frontend/.gitkeep` (a pasta deixou de ser apenas reserva).

## 3. Dependências adicionadas

- Produção: `react` ^18.3.1, `react-dom` ^18.3.1.
- Desenvolvimento: `vite` ^5.4, `@vitejs/plugin-react` ^4.3, `typescript` ^5.6,
  `vitest` ^2.1, `jsdom` ^25, `@testing-library/react` ^16,
  `@testing-library/jest-dom` ^6, `@types/react` ^18.3, `@types/react-dom` ^18.3.
- Gestor: `npm` (Node 22.14.0). Sem Redux nem biblioteca de UI (não necessárias).

## 4. Comandos executados

- `npm install` (176 pacotes)
- `npm run build` → `tsc --noEmit && vite build` → build de produção OK (`dist/`)
- `npm run test` → Vitest, **2 testes OK**
- Verificação do backend em porta limpa: `runserver` + `GET /api/system/ping` → **200 `{"status":"ok"}`** (backend e migrações continuam funcionais)

## 5. Validações (9/9)

| # | Verificação | Resultado | Evidência |
|---|---|---|---|
| 1 | Frontend arranca | Sucesso | `vite` dev + `dist/` de build |
| 2 | Build passa | Sucesso | `tsc --noEmit && vite build` (32 módulos, `dist/index.html`) |
| 3 | Cliente HTTP central existe | Sucesso | `src/api/client.ts` (`apiGet`, `ApiError`, de-duplicação) |
| 4 | `/api/system/ping` é chamado | Sucesso | teste assere `fetch("/api/system/ping", {method:"GET"})` |
| 5 | Sucesso é apresentado | Sucesso | teste: "Backend disponível: ok" |
| 6 | Falha de comunicação tratada | Sucesso | teste: estado "Backend indisponível" (`role="alert"`) |
| 7 | Sem credenciais persistidas | Sucesso | sem `localStorage`/`document.cookie`/tokens no código |
| 8 | Backend e migrações funcionais | Sucesso | ping 200 em porta limpa |
| 9 | Sem ecrã de autenticação | Sucesso | só página de estado do sistema |

## 6. Problemas e excepções / limitações

- Na máquina actual a porta 8000 está ocupada por um serviço pré-existente (não
  pertencente a este projecto), pelo que a demonstração ao vivo do salto
  frontend→proxy→backend na porta convencional 8000 não foi possível; o backend
  foi validado numa porta limpa (200) e a chamada a `/api/system/ping` está
  coberta por teste automatizado. O alvo do proxy (`http://localhost:8000`) é a
  porta Django convencional; basta o backend correr em 8000 para o proxy operar.
- Processos de servidor de verificação (runserver/vite) foram terminados; nenhum
  ficou a correr por engano.

## 7. Decisões relevantes e vigência

- Sem desvio face a `docs/produto/00_decisoes_arranque.md`. Toolchain (npm/Vite),
  prefixo/base `/api`, estratégia de mesma origem via proxy e CORS restritivo
  seguem PR01. Sem nova decisão global.

## 8. Pendências materiais / riscos

- Ecrãs de autenticação e cliente autenticado: PR08 (após auth backend PR07).
- Docker Compose que integra frontend+backend+BD+armazenamento: PR04.
- Risco: nenhum estrutural.

## 9. Próximo passo

- Executar `F1-P02-PR04` (adaptador de armazenamento filesystem + Docker Compose
  local). Não avançar autonomamente.
