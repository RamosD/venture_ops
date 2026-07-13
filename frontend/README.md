# Frontend — VentureOps AI

Fundação mínima React + TypeScript (Vite). Estado: **F1-P02-PR03** — cliente HTTP
central e página inicial que demonstra a comunicação com `GET /api/system/ping`.
Sem autenticação e sem UI de domínio (produtos/empresa/etc.).

## Requisitos

- Node.js 22 LTS (validado em 22.14.0), npm 10

## Instalação e comandos

```bash
cd frontend
npm install
npm run dev      # servidor de desenvolvimento (proxy /api -> http://localhost:8000)
npm run build    # typecheck (tsc) + build de produção (vite)
npm run test     # testes (vitest)
```

## Comunicação com o backend

- O cliente HTTP central ([`src/api/client.ts`](src/api/client.ts)) usa a base
  `VITE_API_BASE_URL` (por defeito `/api`, mesma origem).
- Em desenvolvimento, o Vite encaminha `/api` para `http://localhost:8000`
  (ver `vite.config.ts`), evitando CORS — estratégia de mesma origem/proxy
  decidida em `docs/produto/00_decisoes_arranque.md` §10.
- A página inicial chama `/api/system/ping` e apresenta um de três estados:
  **a carregar**, **backend disponível**, **backend indisponível**.

## Estrutura

```text
frontend/
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── .env.example
└── src/
    ├── main.tsx
    ├── App.tsx
    ├── App.test.tsx
    ├── setupTests.ts
    ├── vite-env.d.ts
    └── api/
        ├── client.ts     # cliente HTTP central (erros + de-duplicação)
        └── system.ts     # chamada a /api/system/ping
```

Sem credenciais persistidas no browser. A sessão por cookie e o CSRF são
introduzidos em PR07/PR08.
