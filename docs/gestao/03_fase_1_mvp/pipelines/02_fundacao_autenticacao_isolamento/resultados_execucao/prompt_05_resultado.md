---
fase: F1
pipeline: F1-P02
prompt: F1-P02-PR05
modelo: claude-opus-4-8
inicio: 2026-07-12 22:10
fim: 2026-07-12 22:45
estado_execucao: Concluído
estado_revisao: Não revista
commit: não criado
---

# Resultado — Prompt 05 — Health checks, testes base e CI mínimo

## 1. Resumo

Implementados os health checks técnicos `GET /health/live` (processo activo, sem
dependências) e `GET /health/ready` (verifica PostgreSQL e armazenamento; 503
controlado quando uma dependência falha), com respostas mínimas sem informação
sensível. Consolidada a estrutura de testes (unitários e de integração, por
módulo) e adicionados testes de health e de configuração obrigatória. Criado o CI
mínimo (`.github/workflows/ci.yml`): instalação, `check`, verificação de drift,
migrações numa base limpa, testes backend e build/testes frontend — **sem deploy
automático**. 34 testes backend passam; a demonstração ao vivo confirmou o 503
controlado. VAL-016 anotada como **Parcial** (só fundação; deploy/rollback não
validados).

## 2. Distinção dos endpoints técnicos

| Endpoint | Verifica | Resposta |
|---|---|---|
| `GET /api/system/ping` | nada (smoke da aplicação) | `{"status":"ok"}` |
| `GET /health/live` | processo activo | `{"status":"live"}` |
| `GET /health/ready` | PostgreSQL + armazenamento | `ready` (200) / `not_ready` (503) |

## 3. Alterações

### Ficheiros criados

- `backend/apps/common/health.py` (views + `_check_database`/`_check_storage`)
- `backend/apps/common/tests/test_health.py`, `backend/apps/common/tests/test_config.py`
- `.github/workflows/ci.yml`

### Ficheiros alterados

- `backend/config/urls.py` (rotas `/health/live`, `/health/ready`)
- `backend/README.md` (tabela dos três endpoints técnicos)
- `docs/gestao/04_matriz_validacao_global.md` (VAL-016 → Parcial)
- Registos globais no fecho (status, painel, diário).

### Ficheiros removidos

- Nenhum.

## 4. Configuração de CI (`.github/workflows/ci.yml`)

- **Job backend:** serviço `postgres:16` (base limpa); `pip install`;
  `manage.py check`; `makemigrations --check --dry-run` (sem drift);
  `migrate --noinput` (base limpa); `manage.py test`. Config por env
  (`DJANGO_SECRET_KEY`, `POSTGRES_*`, `STORAGE_ROOT`).
- **Job frontend:** `setup-node@22` com cache npm; `npm ci`; `npm run build`;
  `npm run test`.
- **Sem passos de deploy/rollback** (comentário explícito no workflow).

## 5. Comandos executados (evidência local)

- Rebuild backend no compose; `GET /health/live` → 200 `{"status":"live"}`;
  `GET /health/ready` → 200 `{"status":"ready","checks":{"database":"ok","storage":"ok"}}`.
- **Demo de falha controlada:** `docker compose stop db` → `/health/ready` → **503**
  `{"status":"not_ready","checks":{"database":"error","storage":"ok"}}`;
  `/health/live` mantém 200; `docker compose start db` → `/health/ready` volta a 200.
- `docker compose exec backend python manage.py test` → **34 testes OK**.
- Reprodução dos passos CI backend contra base limpa (`ci_clean`): `check` OK,
  `makemigrations --check` = "No changes detected", `migrate` aplica.
- Frontend: `npm run build` OK e `npm run test` (2) OK (sem alterações no frontend nesta etapa).

## 6. Validações (10/10)

| # | Verificação | Resultado | Evidência |
|---|---|---|---|
| 1 | `/health/live` responde | Sucesso | 200 `{"status":"live"}` |
| 2 | `/health/ready` saudável com BD+armazenamento | Sucesso | 200 `checks` ambos `ok` |
| 3 | `/health/ready` falha controlada | Sucesso | db parada → 503 `database: error` |
| 4 | Respostas sem segredos | Sucesso | apenas `status`/`checks` (teste) |
| 5 | Testes backend passam | Sucesso | 34 testes OK |
| 6 | Build frontend passa | Sucesso | `vite build` OK |
| 7 | CI numa base limpa | Sucesso | migrate/check reproduzidos em `ci_clean`; serviço postgres no workflow |
| 8 | Config em falta → mensagem clara | Sucesso | `ImproperlyConfigured` + `test_config` |
| 9 | CI sem deploy | Sucesso | workflow sem passos de deploy |
| 10 | Docker Compose funcional | Sucesso | stack saudável após a demo |

## 7. Matriz de validação

- **VAL-016 → Parcial.** Evidência: health checks + CI build/testes. **Deploy e
  rollback NÃO validados** (transferidos para MVP-20/F1-P08). Nenhuma outra VAL
  alterada.

## 8. Problemas / limitações

- O CI real (GitHub Actions) não foi executado neste ambiente; os seus passos
  foram reproduzidos localmente (backend contra base limpa; frontend build/test).
- Sem observabilidade, métricas, alertas, deploy, rollback ou plataforma de
  produção (por desenho).

## 9. Decisões relevantes e vigência

- Sem desvio face a `docs/produto/00_decisoes_arranque.md`. Sem nova decisão global.

## 10. Próximo passo

- Executar `F1-P02-PR06` (auditoria mínima append-only). Não avançar autonomamente.
