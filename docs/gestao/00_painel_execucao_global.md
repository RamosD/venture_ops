# Painel de execução global

Resumo executivo do estado da execução assistida por IA. Não reproduz detalhes
dos resultados; aponta para os documentos especializados.

- Estado global: **Implementação iniciada** (Fase 0 concluída com reservas; governação não bloqueante — DEC-20260712-01)
- Fase actual: **F1 — MVP**
- Pipeline actual: F1-P05 — Funções, execuções e pacote de contexto (**Concluída — 6/6**)
- Último prompt: F1-P05-PR06 — Concluído / Não revista (validação integrada e fecho: E2E ao vivo do cenário — função IA com instruções `confirm`, execução `prepared` com A/B, C `denied` não seleccionável, snapshots congelados perante edições, versões v1 preservadas após v2, bloqueio→confirmação, Markdown/ZIP determinísticos com 7 secções/manifesto/checksum, hostil em DADOS, política superveniente `denied`→409→`allowed`; concorrência real — gerações simultâneas idênticas e alteração de política concorrente coerente sem pacote parcial; isolamento com 2 empresas; auditoria com correlation_id sem conteúdo; migrações sem drift aplicadas em base vazia e na base de dev existente; regressão 396 backend + 91 frontend + build; health live/ready 200; Docker healthy; nenhum defeito — nenhuma correcção de código; nenhuma IA chamada, nenhum resultado criado, execuções permanecem `prepared`; **VAL-007 e VAL-008 Validadas**; VAL-002/VAL-012/VAL-014 Parciais; VAL-009 não validável sem resultados)
- Próximo passo: **commit de F1-P05** e depois **gerar a pipeline F1-P06** (resultados, revisão e aplicação controlada), just-in-time
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
- **Pipeline F1-P05 (funções, execuções, pacote de contexto) — em execução (1/6).
  F1-P05-PR01:** módulo `functions` novo (`FunctionProfile`, serviço, API,
  serializers estritos, migração `0001`), área empresarial **Funções** na UI
  (lista/filtros/criação/edição/inactivação com confirmação/reactivação), sem
  novo router; nenhum módulo anterior alterado (só routing acrescentado); 31 novos
  testes backend + 8 frontend; regressão 324 backend + 57 frontend verde.
- **F1-P05-PR02:** módulo `executions` (`AIExecution` + `ExecutionContextDocument`,
  `transitions.py`, serviço, API, serializers estritos, migração `0001`);
  execuções `prepared` criáveis com snapshots imutáveis e versões documentais
  exactas; sem UI (F1-P05-PR03); nenhum módulo anterior alterado (só routing
  acrescentado); 41 novos testes backend; regressão 365 backend + 57 frontend.
- **F1-P05-PR03:** UI de execuções (`ExecutionSection`/`ExecutionList`/
  `ExecutionCreateForm`/`ContextDocumentSelector`/`FunctionSnapshotView`/
  `ExecutionDetail`) integrada na ficha do produto (substitui o aviso de
  indisponibilidade; mantém documentos/decisões/pendências); duas adições de
  leitura aditivas ao módulo documental (filtro `empresarial`, `id` de versão);
  16 novos testes frontend; regressão 365 backend + 73 frontend + build.
- **F1-P05-PR04:** serviço `context_package.py` + endpoints
  `context-package/preview` e `context-package/download` (geração determinística,
  `export_policy` no servidor, `single_markdown`/ZIP, checksum SHA-256, evento 12);
  definição `CONTEXT_PACKAGE_MAX_BYTES`; nenhum módulo anterior alterado; 27 novos
  testes backend; regressão 392 backend + 73 frontend; sem drift.
- **F1-P05-PR05:** UI do pacote (`ContextPackagePanel` no `ExecutionDetail`;
  análise de política, confirmação, preview de texto não executável, cópia via
  Clipboard, descarga `.md`/`.zip` com revogação de URL); auxiliares
  `apiPostWithStatus`/`apiPostBlob` no cliente central; handoff manual simulado
  nos testes (sem IA, execuções ficam `prepared`); 18 novos testes; regressão
  392 backend + 91 frontend + build.
- **F1-P05-PR06 (fecho):** validação integrada ponta a ponta + concorrência da
  geração (2 gerações simultâneas idênticas; alteração de política concorrente
  coerente); +4 testes backend (integração + concorrência); regressão 396 backend
  + 91 frontend + build; migrações aplicadas na base de dev existente sem drift;
  nenhum defeito — nenhuma correcção de código. **F1-P05 Concluída (6/6);
  VAL-007/VAL-008 Validadas.**
- Última actualização: 2026-07-14 08:00
