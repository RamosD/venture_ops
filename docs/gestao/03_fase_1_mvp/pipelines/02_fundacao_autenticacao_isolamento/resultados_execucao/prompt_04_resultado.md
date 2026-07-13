---
fase: F1
pipeline: F1-P02
prompt: F1-P02-PR04
modelo: claude-opus-4-8
inicio: 2026-07-12 20:40
fim: 2026-07-12 21:55
estado_execucao: Concluído
estado_revisao: Não revista
commit: não criado
---

# Resultado — Prompt 04 — Armazenamento filesystem e Docker Compose local

## 1. Resumo

Implementado o contrato mínimo de armazenamento (`StorageAdapter`: `save`,
`open`, `exists`, `checksum`, `delete`) e a implementação filesystem privada
(chaves geradas no servidor, prevenção de path traversal, checksum SHA-256,
escrita atómica, raiz fora de directórios públicos, ponto de extensão para S3 sem
implementar S3). Criado o Docker Compose local que integra PostgreSQL, backend,
frontend e um **volume privado** de armazenamento, com health checks/dependências
suficientes e variáveis por ficheiro de exemplo (sem segredos reais no
repositório). `docker compose up` sobe os quatro elementos; o frontend comunica
com `/api/system/ping` via proxy; migrações aplicam numa base vazia dentro do
ambiente; 25 testes backend passam; build frontend passa.

## 2. Alterações

### Ficheiros criados

- `backend/apps/storage/exceptions.py`, `base.py`, `filesystem.py`
- `backend/apps/storage/tests/__init__.py`, `tests/test_filesystem.py`
- `backend/Dockerfile`, `backend/.dockerignore`
- `frontend/Dockerfile`, `frontend/.dockerignore`
- `compose.yaml`, `.env.example` (raiz), `README.md` (raiz)

### Ficheiros alterados

- `backend/apps/storage/__init__.py` (`get_storage()` + interface pública)
- `backend/config/settings.py` (`STORAGE_ROOT`, `STORAGE_MAX_BYTES`)
- `frontend/vite.config.ts` (alvo do proxy por `VITE_BACKEND_ORIGIN`; `host: true`)
- `frontend/tsconfig.json` (deixa de typechecar `vite.config.ts`)
- `.gitignore` (`backend/var/`)
- Registos globais no fecho (status, painel, diário).

### Ficheiros removidos

- Nenhum.

## 3. Volumes e serviços

- `pgdata` — dados do PostgreSQL.
- `storage_data` — **volume privado** montado em `/var/storage` no backend; **não
  publicado no host** e **sem rota** que sirva objectos → objectos privados.
- Serviços: `db` (postgres:16, healthcheck `pg_isready`), `backend` (build local,
  healthcheck `/api/system/ping`, depende de `db` saudável), `frontend`
  (Vite, depende de `backend` saudável, proxy `/api` → `http://backend:8000`).
- Portas host configuráveis por `.env` (defaults 8000/5173/5433).

## 4. Dependências

- Sem novas dependências de aplicação (Python/Node). Imagens base: `postgres:16`,
  `python:3.13-slim`, `node:22-alpine`. Sem S3, Redis, Celery, Kafka, Kubernetes.

## 5. Comandos executados

- `docker compose up -d --build` → db/backend saudáveis, frontend a correr
- `curl :8010/api/system/ping` → 200 `{"status":"ok"}`
- `curl :5180/` → 200 (index) e `curl :5180/api/system/ping` → 200 (via proxy)
- `docker compose exec backend python manage.py showmigrations` → `accounts`/`organisations` `[X]`
- `docker compose exec backend python manage.py test` → **25 testes OK** (inclui storage)
- Demo (Django shell no backend): `save/open/checksum/delete` no volume; traversal rejeitado

## 6. Validações (12/12)

| # | Verificação | Resultado | Evidência |
|---|---|---|---|
| 1 | `compose up` inicia os serviços | Sucesso | `compose ps`: 3 serviços a correr |
| 2 | PostgreSQL disponível | Sucesso | `db` healthy (`pg_isready`) |
| 3 | Backend responde | Sucesso | ping 200 (host 8010) |
| 4 | Frontend responde | Sucesso | index 200 (host 5180) |
| 5 | Frontend comunica com `/api/system/ping` | Sucesso | proxy → 200 `{"status":"ok"}` |
| 6 | Escrita/leitura filesystem | Sucesso | `read_ok=True` no volume |
| 7 | Checksum estável | Sucesso | `checksum_stable=True` (SHA-256) |
| 8 | Path traversal rejeitado | Sucesso | `InvalidKeyError` + teste dedicado |
| 9 | Objectos não públicos | Sucesso | volume não publicado; sem rota (teste `Resolver404`) |
| 10 | Migrações em base vazia no ambiente | Sucesso | migrate no arranque; test DB criado de raiz |
| 11 | Testes backend passam | Sucesso | 25 testes OK |
| 12 | Build frontend passa | Sucesso | `vite build` OK (`dist/`) |

## 7. Problemas e excepções

- Na máquina actual as portas 8000/5432 estão ocupadas por serviços pré-existentes;
  a verificação usou portas host 8010/5180/5434 via `.env` local (ignorado pelo
  git). Os defaults do compose mantêm-se convencionais (8000/5173/5433).
- Sem S3, URLs temporárias, observabilidade, deploy ou rollback (por desenho).

## 8. Decisões relevantes e vigência

- Sem desvio face a `docs/produto/00_decisoes_arranque.md` (contrato de storage §14;
  toolchain; fronteira HTTP). Sem nova decisão global.

## 9. Pendências materiais / riscos

- Health checks técnicos (`/health/live`, `/health/ready`) e CI: PR05.
- Risco: nenhum estrutural. Backup/recuperação completos ficam para F1-P08/MVP-20.

## 10. Próximo passo

- Executar `F1-P02-PR05` (health checks, testes base consolidados e CI mínimo).
  Não avançar autonomamente.
