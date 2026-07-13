# Backend — VentureOps AI

Esqueleto executável do backend (Django + Django REST Framework) do monólito
modular. Estado: **F1-P02-PR01** — arranque mínimo, sem base de dados, sem
autenticação e sem modelos de domínio. PR02 introduz PostgreSQL, `CustomUser`
(via `AUTH_USER_MODEL`) e a primeira migração.

## Requisitos

- Python 3.13 (validado em 3.13.2)
- pip + venv (gestor de dependências Python)

## Instalação

```bash
cd backend
python -m venv .venv
# Windows (PowerShell): .venv\Scripts\Activate.ps1
# Linux/macOS:          source .venv/bin/activate
pip install -r requirements.txt
```

## Configuração

A configuração é feita por variáveis de ambiente (ver `.env.example`). São
**obrigatórias** `DJANGO_SECRET_KEY`, `POSTGRES_DB`, `POSTGRES_USER` e
`POSTGRES_PASSWORD`; em falta, o arranque falha com uma mensagem clara. Exporte-as
no ambiente antes de arrancar, por exemplo (PowerShell):

```powershell
$env:DJANGO_SECRET_KEY = "dev-key-nao-usar-em-producao"
$env:POSTGRES_DB = "ventureops"; $env:POSTGRES_USER = "ventureops"; $env:POSTGRES_PASSWORD = "ventureops_dev"
$env:POSTGRES_HOST = "127.0.0.1"; $env:POSTGRES_PORT = "5433"
```

## Base de dados (desenvolvimento)

PostgreSQL é obrigatório (sem SQLite como persistência). O Docker Compose local
canónico chega em PR04. Enquanto isso, um PostgreSQL descartável em contentor
(porta **5433**, para não colidir com instalações locais na 5432):

```bash
docker run -d --name ventureops-pg-dev \
  -e POSTGRES_DB=ventureops -e POSTGRES_USER=ventureops -e POSTGRES_PASSWORD=ventureops_dev \
  -p 5433:5432 postgres:16
python manage.py migrate          # aplica a migração inicial
# remover quando não for necessário: docker rm -f ventureops-pg-dev
```

Qualquer PostgreSQL serve — basta apontar as variáveis `POSTGRES_*` para ele.

## Comandos oficiais

Executar a partir de `backend/` com o ambiente virtual activo:

| Objectivo   | Comando |
|-------------|---------|
| Verificação | `python manage.py check` |
| Migrações   | `python manage.py migrate` (requer PostgreSQL) |
| Arranque    | `python manage.py runserver` |
| Testes      | `python manage.py test` (requer PostgreSQL para a base de testes) |
| Build       | Backend sem passo de build dedicado nesta etapa (aplicação Python); a imagem/artefacto é produzida em PR04/MVP-20. |

## Endpoints técnicos

Três endpoints técnicos distintos (nenhum expõe informação sensível):

| Endpoint | Verifica | Resposta |
|---|---|---|
| `GET /api/system/ping` | nada (smoke da aplicação) | `{"status":"ok"}` |
| `GET /health/live` | processo activo | `{"status":"live"}` |
| `GET /health/ready` | PostgreSQL + armazenamento | `{"status":"ready","checks":{...}}` (200) ou `not_ready` (503) |

`/api/system/ping` não consulta a BD nem o armazenamento e não exige
autenticação. `/health/ready` devolve **503** de forma controlada quando uma
dependência falha.

## Autenticação

Sessão por cookie (Django Auth), sem registo público. Conta inicial criada por
comando controlado:

```bash
python manage.py createinitialuser --email owner@x.pt --password "<senha>"
```

Endpoints (`/api/v1/auth/`): `GET csrf`, `POST login`, `GET session`,
`POST logout`, `POST password/reset-request`, `POST password/reset-confirm`.
Perfil próprio: `GET`/`PATCH /api/v1/profile`. Operações mutáveis exigem o
cabeçalho `X-CSRFToken` (valor do cookie `csrftoken`). **O token CSRF roda no
login** — reler o cookie a seguir ao login antes de novos pedidos mutáveis.

Recuperação: token temporário de utilização única enviado por email (consola em
dev; SMTP configurável). Rate limiting de login e recuperação é **persistente em
PostgreSQL** (sem Redis), configurável por `RATE_LIMIT_*`.

## Estrutura

```text
backend/
├── manage.py
├── requirements.txt
├── .env.example
├── config/            # projecto Django (settings, urls, wsgi/asgi, env)
└── apps/              # módulos de domínio do monólito modular (vazios nesta etapa)
    ├── accounts/      # utilizadores/auth (CustomUser criado em PR02)
    ├── organisations/
    ├── portfolio/
    ├── documents/
    ├── decisions/
    ├── work_items/
    ├── functions/
    ├── executions/
    ├── audit/
    ├── storage/
    └── common/        # utilitários partilhados + endpoints técnicos de sistema
```

As decisões técnicas de arranque estão em
`docs/produto/00_decisoes_arranque.md`.
