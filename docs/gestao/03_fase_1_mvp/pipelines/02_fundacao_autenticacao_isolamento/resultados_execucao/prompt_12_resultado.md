---
fase: F1
pipeline: F1-P02
prompt: F1-P02-PR12
modelo: claude-opus-4-8
inicio: 2026-07-13 10:00
fim: 2026-07-13 11:20
estado_execucao: Concluído
estado_revisao: Revista
commit: não criado
---

# Resultado — Prompt 12 — Hardening de identidade e concorrência

## 1. Resumo

Iteração de hardening pós-pipeline sobre F1-P02 que resolve quatro reservas
técnicas: (A) unicidade case-insensitive do email com normalização única e
constraint funcional na BD; (B) `createinitialuser` deixa de aceitar a
palavra-passe por argumento CLI (entrada oculta com confirmação, ou
`--noinput` por variável de ambiente, com validadores do Django); (C) retenção
configurável dos registos de rate limiting + comando de limpeza `purge_rate_limit_attempts`;
(D) rate limiting tornado atómico por advisory lock do PostgreSQL, com testes
concorrentes reais; (E) garantia de BD de uma Membership activa por utilizador
(constraint condicional) + tratamento de `IntegrityError` no onboarding, com teste
concorrente real. 116 testes backend + 12 frontend; concorrência estável em 3
rondas; migrações aplicam/revertem em base vazia e existente. Sem regressões.
**F1-P02 permanece Concluída (12/12).**

## 2. Política de normalização do email

- `apps/accounts/normalization.py::normalize_email` = **strip + lower de todo o
  endereço** (parte local **e** domínio → identidade case-insensitive). Fonte
  única usada em criação, autenticação (`get_by_natural_key` iexact), recuperação
  e edição de perfil. Documentada em `docs/produto/00_decisoes_arranque.md §3`.

## 3. Constraint adoptada (email)

- `UniqueConstraint(Lower("email"), name="uniq_customuser_email_ci")` em `CustomUser`.
- Migração `accounts/0003` normaliza os emails existentes e **detecta colisões
  case-insensitive** (falha clara; **não funde nem apaga** contas) antes de impor
  a constraint.

## 4. Alterações ao `createinitialuser`

- **Removida** a opção `--password`. Interactivo: `getpass` + confirmação.
  `--noinput`: lê `INITIAL_USER_PASSWORD` (falha claro se ausente). Validadores do
  Django aplicados (`AUTH_PASSWORD_VALIDATORS` adicionados). Palavra-passe nunca
  impressa/registada. Idempotente: conta existente não é alterada.

## 5. Política de retenção (rate limiting)

- `RATE_LIMIT_RETENTION_SECONDS` (default **86400s** = 24h), obrigatoriamente
  **superior à maior janela activa** (900s). Índice `created_at` adicionado.

## 6. Comando de limpeza

- `python manage.py purge_rate_limit_attempts [--dry-run]`: remove registos
  anteriores à retenção; preserva janelas activas (retenção > maior janela);
  idempotente; mostra apenas contagens/datas (sem chaves/hashes); **sem scheduler**
  (execução periódica configurada no ambiente do piloto). Erro claro se a retenção
  for inferior à maior janela.

## 7. Estratégia de concorrência — rate limiting

- `rate_limit.allow(key, limit, window)`: `transaction.atomic` + `pg_advisory_xact_lock(hashtext(key))`
  serializa por chave, tornando verificação+registo atómicos. O login/recuperação
  usam `allow` (o gate conta a tentativa; sucesso limpa). Teste concorrente (20
  threads, ligações independentes, barrier) prova que exactamente `limit` passam.

## 8. Estratégia de concorrência — onboarding

- `select_for_update` (já existente) serializa por utilizador; acrescentada a
  **constraint condicional** `UniqueConstraint(fields=["user"], condition=Q(is_active=True))`
  como garantia final de BD; `complete_onboarding` captura `IntegrityError` (num
  savepoint) e devolve `AlreadyHasOrganisationError`, revertendo tudo (sem
  Organisation órfã). Teste concorrente (2 threads) → 1 empresa, 1 Membership
  activa, uma criada e uma bloqueada.

## 9. Migrações

- `accounts/0003` — índice `created_at`; RunPython (normalização + verificação de
  colisão); constraint `Lower(email)` única.
- `organisations/0002` — constraint condicional de Membership activa por utilizador.
- Aplicam em base vazia (test DB) e na base existente; **revertem e reaplicam** com
  dados intactos.

## 10. Testes executados / total

- `manage.py test` → **116 testes OK** (backend); `npm run test` → **12 OK**;
  `npm run build` OK.
- Concorrência isolada **3 rondas** (rate limit + onboarding) — estável.
- Drift: "No changes detected". Migrações: empty base + base existente +
  reverter/reaplicar. Health `/live` e `/ready` 200. Smokes: login com email em
  maiúsculas → 200; recuperação; onboarding; isolamento (via suite); purge dry-run;
  bootstrap `--noinput` idempotente.

## 11. Problemas encontrados e correcções

- Sem `AUTH_PASSWORD_VALIDATORS` os validadores não actuavam → adicionados.
- Rate limiting count-then-insert tinha janela de corrida → substituído por gate
  atómico com advisory lock.
- Onboarding concorrente dependia só de `select_for_update` → reforçado com
  constraint de BD + tratamento de `IntegrityError` (sem órfãs).

## 12. Ficheiros alterados

- Criados: `apps/accounts/normalization.py`, `management/commands/purge_rate_limit_attempts.py`,
  `apps/accounts/migrations/0003_*.py`, `apps/organisations/migrations/0002_*.py`,
  `apps/accounts/tests/test_email_normalization.py`, `test_rate_limit_retention.py`,
  `test_concurrency.py`, `apps/organisations/tests/test_concurrency.py`.
- Alterados: `apps/accounts/managers.py`, `models.py`, `rate_limit.py`, `views.py`,
  `management/commands/createinitialuser.py`, `apps/accounts/tests/test_createinitialuser.py`,
  `apps/organisations/models.py`, `service.py`, `config/settings.py`,
  `backend/.env.example`, `backend/README.md`, `docs/produto/00_decisoes_arranque.md`,
  registos de governação e matriz.

## 13. Estado final da pipeline

- **F1-P02 Concluída (12/12)** — hardening incorporado; sem regressões.

## 14. Pendências / reservas

- Execução periódica do `purge_rate_limit_attempts` será configurada no ambiente
  do piloto (cron/agendador de ambiente), fora do âmbito desta fase.
- Suite completa de segurança (MVP-18) e consulta de auditoria em F1-P07.

## 15. Próximo passo recomendado

- Efectuar **commit** do hardening e **gerar a pipeline F1-P03** (portefólio e
  ficha do produto) just-in-time. Não iniciada nesta iteração.
