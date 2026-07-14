# Painel de execução global

Resumo executivo do estado da execução assistida por IA. Não reproduz detalhes
dos resultados; aponta para os documentos especializados.

- Estado global: **Implementação iniciada** (Fase 0 concluída com reservas; governação não bloqueante — DEC-20260712-01)
- Fase actual: **F1 — MVP**
- Pipeline actual: F1-P04 — Documentos, tipos, decisões e pendências (**Concluída — 6/6**)
- Último prompt: F1-P04-PR06 — Concluído / Não revista (validação integrada e fecho: E2E ao vivo dos três módulos na ficha, preview XSS neutralizada, cadeia de decisão, 5 pendências/transições; regressão 293 backend + 49 frontend + build; concorrência estável 3×; checksums coincidentes e `current_version` sem órfãos; auditoria com `correlation_id` e 0 fugas de conteúdo; drift zero; sem defeitos — nenhuma correcção de código; VAL-004/005/006 Validadas)
- Próximo passo: **commit de F1-P04** e depois **gerar a pipeline F1-P05** (funções, execuções e pacote de contexto), just-in-time
- Mapa das pipelines criado: `03_fase_1_mvp/02_mapa_pipelines.md` (F1-P02 detalhada; F1-P03..P08 mapeadas, just-in-time)
- Bloqueios críticos: Nenhum
- Decisões críticas recentes: DEC-20260712-04 (Fase 0 concluída com reservas); DEC-20260712-05 (4 clarificações de decomposição da Fase 1); DEC-20260712-06 (correcção de dependências técnicas de F1-P02: CustomUser desde a 1.ª migração, fundação User/Org/Membership em PR02, `/api/system/ping` antes dos health checks)
- Reservas vigentes:
  - selecção da plataforma concreta de deploy antes de `MVP-20` (tarefa MVP-20.T1);
  - execução efectiva do piloto (MVP-22; participante mínimo: Aldino Ramos);
  - implementação e validação dos controlos de segurança (MVP-18/MVP-21).
- Progresso resumido: backlog da Fase 1 decomposto (MVP-01..23; 39 capacidades,
  41 histórias, 85 requisitos, 112 tarefas após clarificações). Mapa das
  pipelines F1-P02..P08 criado; F1-P02 detalhada com 11 prompts (fundação,
  autenticação, empresa/isolamento, auditoria mínima), pronta para execução.
  Correcção de pré-execução (F1-P01-PR03) aplicada: `CustomUser` obrigatório
  desde a primeira migração, fundação User/Organisation/Membership deslocada para
  F1-P02-PR02, endpoint `/api/system/ping` em PR01 consumido por PR03; F1-P02
  mantém 11 prompts e resultado global inalterado. **Implementação iniciada
  (F1-P02-PR01):** esqueleto Django+DRF (11 módulos vazios), configuração por
  ambiente validada, endpoint `/api/system/ping` (200 `{"status":"ok"}`), 14
  decisões de arranque documentadas. **F1-P02-PR02:** PostgreSQL por env,
  `CustomUser`/`Organisation`/`Membership` e 1.ª migração (aplica/reverte em base
  vazia), convenção de entidade empresarial, 16 testes verdes; sem
  autenticação/onboarding. **F1-P02-PR03:** frontend React/TS (Vite) com cliente
  HTTP central que consome `/api/system/ping` (estados a carregar/disponível/erro);
  build e 2 testes verdes; sem autenticação, store global nem UI de domínio.
  **F1-P02-PR04:** adaptador de armazenamento filesystem privado (chaves no
  servidor, anti-traversal, checksum) e Docker Compose local (PostgreSQL+backend+
  frontend+volume privado); `compose up` integrado, 25 testes backend verdes.
  **F1-P02-PR05:** health checks `/health/live` (processo) e `/health/ready`
  (BD+armazenamento, 503 controlado), CI mínimo build/testes sem deploy
  (`.github/workflows/ci.yml`), 34 testes backend verdes; VAL-016 Parcial (sem
  deploy/rollback). **F1-P02-PR06:** auditoria append-only (`AuditEvent` +
  serviço `record_event`, actor/empresa opcionais `SET_NULL`, snapshots,
  correlação, conteúdo proibido rejeitado); 48 testes backend verdes; VAL-012
  Parcial (emissores por integrar). **F1-P02-PR07:** autenticação backend
  (login/sessão/logout por cookie HttpOnly/SameSite/Secure-condicional, CSRF
  exigido, conta inicial por comando controlado, eventos auditados); 62 testes
  verdes; VAL-001 Parcial. **F1-P02-PR08:** ecrãs de autenticação (login/área
  autenticada/logout) integrados com sessão por cookie e CSRF; cliente HTTP
  central com CSRF+credenciais+sessão expirada; e2e validado em testes e browser
  real (proxy corrigido `changeOrigin:false`); 8 testes frontend. **F1-P02-PR09:**
  recuperação por token único/expirável (invalida sessões, email dev por consola),
  rate limiting persistente em PostgreSQL (sem Redis, auditado) e perfil mínimo;
  78 testes backend + 10 frontend; demos ao vivo (429, recuperação, perfil);
  **VAL-001 Validado** (escopo MVP). **F1-P02-PR10:** onboarding empresarial
  (Organisation activa + Membership Owner, transaccional com `select_for_update`,
  2.ª empresa bloqueada), edição mínima autorizada no servidor, auditoria;
  88 testes backend + 12 frontend; onboarding validado no browser; VAL-002
  Parcial. **F1-P02-PR11:** contexto de empresa derivado da Membership no servidor
  (sem Membership → 403; acesso por id alheio → 404 auditado), bateria de
  isolamento com 2 empresas (8 testes); 96 testes backend + 12 frontend; VAL-002
  e VAL-012 parciais. **F1-P02-PR12 (hardening):** email case-insensitive
  (constraint `Lower(email)`), `createinitialuser` sem palavra-passe em CLI,
  rate limiting atómico (advisory lock) + retenção/limpeza, garantia de BD de uma
  Membership activa por utilizador; concorrência testada (rate limit + onboarding,
  estável); 116 testes backend + 12 frontend. **Pipeline F1-P02 concluída
  (12/12)**. A validação humana de resultados de IA no produto permanece obrigatória.
- Última actualização: 2026-07-14 10:35
