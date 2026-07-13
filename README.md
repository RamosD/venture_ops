# VentureOps AI

Monólito modular (Django + DRF) com frontend React/TypeScript, PostgreSQL e
armazenamento documental privado. Estado: **Fase 1 / MVP — F1-P02** (fundação).

## Ambiente local integrado (Docker Compose)

Sobe PostgreSQL, backend, frontend e o volume privado de armazenamento com um
comando:

```bash
cp .env.example .env      # ajuste segredos/portas locais (não commitar .env)
docker compose up --build
```

Serviços (portas configuráveis em `.env`):

| Serviço  | Host (por defeito)        | Notas |
|----------|---------------------------|-------|
| frontend | http://localhost:5173     | Vite; proxy `/api` → backend |
| backend  | http://localhost:8000     | `GET /api/system/ping` |
| db       | localhost:5433            | PostgreSQL 16 |

O backend aplica migrações no arranque. Comandos úteis:

```bash
docker compose exec backend python manage.py migrate       # migrações
docker compose exec backend python manage.py test          # testes backend
docker compose exec frontend npm run build                 # build frontend
docker compose down            # parar   (adicionar -v para apagar volumes)
```

Componentes:

- Backend: [`backend/README.md`](backend/README.md)
- Frontend: [`frontend/README.md`](frontend/README.md)
- Decisões técnicas de arranque: [`docs/produto/00_decisoes_arranque.md`](docs/produto/00_decisoes_arranque.md)

Sem S3, URLs temporárias, Redis/Celery/Kafka/Kubernetes nem plataforma de deploy
nesta etapa. O armazenamento usa um adaptador filesystem privado com ponto de
extensão para S3 (não implementado).
