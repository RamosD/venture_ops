# Painel de execução global

Resumo executivo do estado da execução assistida por IA. Não reproduz detalhes
dos resultados; aponta para os documentos especializados.

- Estado global: **Implementação iniciada** (Fase 0 concluída com reservas; governação não bloqueante — DEC-20260712-01)
- Fase actual: **F1 — MVP**
- Pipeline actual: F1-P06 — Resultados, revisão e aplicação controlada (**Concluída — 6/6**); próxima: F1-P07 (não iniciada)
- Marco **M1 — ATINGIDO** (fluxo vertical ponta a ponta): preparar → gerar pacote → importar → rever → pedir correcção → importar → aprovar → aplicar → concluir, demonstrado por E2E automatizado na imagem reconstruída (10 testes `test_pipeline_e2e`) + stack Docker saudável (health live/ready 200; endpoints de revisão/aplicação roteados; migrações 0001–0005 aplicadas na base existente). Demo visual no browser ficou bloqueada por indisponibilidade temporária da ferramenta de browser — flow validado pelos endpoints reais e pelos 124 testes de componente das UIs.
- Último prompt: F1-P06-PR06 — Concluído / Não revista (validação de fecho de F1-P06: cenário principal E1–E6 + cenários A–E + provas negativas importar≠aprovar≠aplicar + isolamento + autorização + concorrência num teste E2E dedicado; 2 defeitos de expectativa de teste corrigidos — `test_approval_creates_no_application` passou a verificar ausência de instância `ResultApplication` (o modelo existe desde PR04) e a prova negativa E2E passou a contar as versões do documento **alvo** e não o total global; hasher rápido só-em-testes acrescentado a settings (sem impacto em produção); regressão backend completa **502 testes OK**, frontend **124 OK** + build, `makemigrations --check` sem drift, reversibilidade estrutural verificada (forward em base vazia; reverter executions→0001 remove tentativas/revisões/aplicações; forward de novo; outras apps preservadas), migrações aplicadas na base existente do contentor; VAL-009 e VAL-010 **Validadas**, VAL-004/005/006 com evidência de aplicação, VAL-002/012/014 mantêm-se Parciais, VAL-011 inalterada; nenhuma IA chamada; sem desvio estrutural)
- Último prompt anterior: F1-P06-PR05 — Concluído / Não revista (completa a aplicação controlada com os caminhos de decisão, pendência e fecho sem alteração — MVP-15.C2: regra global **uma execução produz no máximo uma `ResultApplication`** (unicidade por execução + fingerprint idempotente, não contornável por endpoints distintos); `application_service` refactorizado com um prefixo comum `_prepare` (autoriza só-Owner, bloqueia execução, verifica idempotência antes do estado, exige `approved`+`expected_execution_version`, tentativa actual com `ResultReview approved`) partilhado pelos quatro caminhos; **decisão** (`apply/decision`) — decisão alvo activa do Product da execução, campos da nova decisão fornecidos explicitamente, usa o serviço `supersede_decision` existente (nova `active`, anterior `superseded`, cadeia preservada), `ResultApplication` guarda `target_decision`+`created_decision`; **pendência** (`apply/work-item`) — WorkItem `open` do Product, usa `complete_work_item` (não altera título/notas/tipo/prazo), guarda `target_work_item`; **fecho** (`close-without-application`) — `no_change` com rationale obrigatório + confirmação explícita, sem alterar nenhuma fonte oficial; todos exigem aprovação + confirmação do contrato, transitam `approved→completed` (versão +1) e emitem o evento 17 `change.applied` distinguindo o tipo, sem resultado/decision_text/notes/rationale integral; segundo caminho após aplicação → 409 (uma aplicação por execução), idempotência (repetição idêntica → existente; diferente → 409), concorrência entre dois tipos deixa exactamente um vencedor; alvo de outro Product/superseded/não-open → 422, alheio → 404 auditado; constraints de coerência por tipo (decision/work_item/no_change) na migração `executions/0005`; UI `ApplicationPanel` completo com **quatro opções** (nova versão documental / substituir decisão / concluir pendência / fechar sem alteração), apresenta só alvos elegíveis (decisões activas, pendências abertas), formulários explícitos sem parsing do resultado, resumo exacto da mutação antes de confirmar, aviso de aplicação única, 409 recarrega, apresenta a aplicação final e impede segunda aplicação; provas negativas (importar/aprovar não alteram Document/Decision/WorkItem; só apply/close leva a completed); +19 testes backend (caminhos + concorrência) e +7 frontend; regressão 124 frontend + build; makemigrations --check sem drift; VAL-010 Parcial até PR06, VAL-004/005/006 com evidência de aplicação; M1 não declarado)
- Último prompt anterior: F1-P06-PR04 — Concluído / Não revista (primeira aplicação oficial de um resultado aprovado — nova versão documental: modelo `ResultApplication` append-only — `id`, `organisation`, `execution` **OneToOne** (uma aplicação por execução, defesa final), `result_attempt`, `review`, `application_type` fechado {document,decision,work_item,no_change} (só `document` implementado), `applied_by`, `request_fingerprint` SHA-256 (idempotência), `change_summary`/`rationale`, alvos/criados PROTECT (`target_document`/`base_document_version`/`created_document_version`/`target_decision`/`created_decision`/`target_work_item`), `created_at`; sem GenericForeignKey, sem FK de executions dentro de DocumentVersion (a ligação oficial é `created_document_version`); constraints unicidade por execução + tipo fechado + coerência de `document` (alvo/base/criada presentes e resumo não vazio); migração `executions/0004` aditiva sem drift; `application_service.apply_document` numa transacção que autoriza (só Owner activo), valida confirmação explícita do contrato + conteúdo explícito + resumo, valida/encode conteúdo, bloqueia execução, verifica idempotência (fingerprint) antes do estado, exige `approved`+`expected_execution_version`, tentativa actual com `ResultReview approved`, bloqueia e valida o documento alvo (do Product da execução; empresarial/outro Product/`resultado`/gerido por ResultAttempt rejeitados; `expected_document_version`), escreve o objecto e cria a nova `DocumentVersion` (versões anteriores preservadas), cria a `ResultApplication` (base+created) e transita `approved→completed` incrementando `version` uma vez; idempotência — repetir o mesmo comando devolve a aplicação existente (200) sem nova versão, comando diferente → 409, unicidade por execução é defesa final; atomicidade BD↔storage — falha de storage deixa `approved` (503+storage.failure), falha de BD remove o objecto órfão e não deixa aplicação parcial, nunca há `completed` sem aplicação nem aplicação sem versão; endpoints `POST /executions/{id}/apply/document` (entrada estrita: rejeita application_type/review/versão criada/internos) e `GET /executions/{id}/application`; auditoria evento 17 `change.applied` com application_type/attempt_number/review_id/target_document_id/base_version/created_version/checksum/transition/execution_version (sem conteúdo aplicado nem change_summary integral), tentativa sem aprovação auditada `denied`, cross-org `security.cross_org_attempt`→404; UI `ApplicationPanel` no detalhe (só em `approved`) com tentativa aprovada/revisão/resultado original de referência, lista de documentos elegíveis do Product, versão actual do alvo, editor de conteúdo + resumo, botão "Usar resultado como ponto de partida" (nunca aplica directamente), confirmação final explícita (conteúdo revisto/nova versão oficial/execução concluída), aviso de que a aprovação anterior não aplicou nada, 409 recarrega documento+execução sem sobrescrever, mostra a versão criada e a ligação, sem decisões/pendências; +25 testes backend (aplicação + concorrência) e +5 frontend; regressão frontend 117 + build; makemigrations --check sem drift; VAL-010 Parcial, VAL-004 com evidência de versão aplicada; M1 não declarado)
- Último prompt anterior: F1-P06-PR03 — Concluído / Não revista (revisão humana dos resultados importados: modelo `ResultReview` append-only — `id`/`organisation`/`execution`/`result_attempt`/`reviewer`/`decision` fechada {approved,rejected,correction_requested}/`observations`/`created_at`; unicidade sobre `result_attempt` (uma revisão por tentativa, defesa final de concorrência) + constraint de observações obrigatórias na rejeição/correcção + decisão fechada; `review_service` com três comandos explícitos (aprovar/rejeitar/pedir correcção) sob bloqueio de execução+tentativa, `expected_version`, política central de transições e autorização só-Owner activo; endpoints `POST /executions/{id}/result-attempts/{n}/approve|reject|request-correction` + `GET /executions/{id}/reviews`; aprovar `result_pending_validation→approved` (sem versão documental, sem tocar em Product/Decision/WorkItem, sem aplicação, nunca `completed`); rejeitar `→rejected` (terminal); pedir correcção `→prepared` preservando `current_result_attempt`, tentativa e revisão, permitindo nova importação (nº seguinte); versão da execução incrementada uma vez por transição; auditoria eventos 14–16 com `operation`/`attempt_number`/`review_id`/`transition`/`execution_version` (sem resultado nem observações integrais), dupla revisão auditada `denied`, cross-org `security.cross_org_attempt`→404; UI `ValidationPanel` no detalhe (só em `result_pending_validation`) com tentativa actual/conteúdo/pré-visualização segura, histórico de tentativas e revisões, três acções separadas, confirmação de aprovação que explica aprovar valida≠aplica (aplicação posterior), observações obrigatórias em rejeição/correcção, botões desactivados na submissão, 409 recarrega, sem qualquer acção de aplicação; +24 testes backend (revisão + concorrência) e +7 frontend; regressão 123 executions backend + 112 frontend + build; makemigrations --check sem drift; VAL-010 Parcial, VAL-009 Parcial)
- Próximo passo: **efectuar commit de F1-P06** e gerar **F1-P07** just-in-time (não iniciado)
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
- **Pipeline F1-P06 (resultados, revisão, aplicação) — CONCLUÍDA (6/6); M1 atingido.
  F1-P06-PR01:** `ResultAttempt` append-only + `current_result_attempt`
  (migração aditiva), serviço `import_result` + API `/executions/{id}/
  result-attempts`, restrições à API documental genérica (`resultado` não criável;
  documento ligado a tentativa não editável/recuperável); +28 testes backend;
  sem drift; VAL-009 Parcial. **F1-P06-PR02:** UI de importação/histórico
  (`ResultAttemptsPanel`/`ResultImportForm`/`ResultAttemptView` no `ExecutionDetail`;
  importar por texto/ficheiro com confirmação, tentativa actual, histórico,
  pré-visualização segura via backend; sem aprovar/aplicar); auxiliar multipart
  `apiPostFormWithStatus`; +14 testes frontend; regressão 105 frontend + build.
  **F1-P06-PR03:** revisão humana — `ResultReview` append-only (uma revisão por
  tentativa; decisão fechada; observações obrigatórias na rejeição/correcção),
  `review_service` (aprovar/rejeitar/pedir correcção) com bloqueio+`expected_version`+
  política central+autorização só-Owner, endpoints explícitos + `GET /reviews`,
  auditoria eventos 14–16 sem conteúdo (dupla revisão `denied`); UI `ValidationPanel`
  (tentativa actual, histórico de tentativas e revisões, confirmação aprovar≠aplicar,
  observações obrigatórias, 409 recarrega, sem aplicação); +24 testes backend +
  concorrência, +7 frontend; regressão 123 executions backend + 112 frontend + build;
  sem drift; VAL-009/VAL-010 Parciais.
  **F1-P06-PR04:** aplicação documental controlada — `ResultApplication` append-only
  (uma por execução; fingerprint SHA-256 idempotente; ligação oficial via
  `created_document_version`, sem FK circular nem GenericFK), `application_service`
  (Owner, confirmação/conteúdo/resumo explícitos, locks execução+documento,
  `approved`+versões, alvo elegível do Product, nova `DocumentVersion` preservando
  as anteriores, `approved→completed`), idempotência (repetição → existente; comando
  diferente → 409), atomicidade BD↔storage (falha de storage deixa `approved`; sem
  aplicação parcial); endpoints `POST /apply/document` + `GET /application`;
  auditoria evento 17 `change.applied` sem conteúdo; UI `ApplicationPanel` (só em
  `approved`, editor + confirmação, aprovar não aplicou nada, 409 recarrega, mostra
  versão criada); +25 testes backend + concorrência, +5 frontend; regressão 117
  frontend + build; sem drift; VAL-010 Parcial, VAL-004 com evidência.
  **F1-P06-PR05:** caminhos decisão/pendência/fecho — `_prepare` partilhado
  (Owner+idempotência+approved+tentativa/revisão), `apply_decision` (usa
  `supersede_decision`: nova activa/anterior superseded, cadeia+ligação),
  `apply_work_item` (usa `complete_work_item`, preserva campos), `close_without_application`
  (no_change, rationale+confirmação, sem tocar em fontes oficiais); **uma aplicação
  por execução** (segundo caminho→409; concorrência entre tipos → 1 vencedor);
  constraints de coerência por tipo (migração 0005); endpoints `apply/decision`,
  `apply/work-item`, `close-without-application`; auditoria 17 distingue o tipo, sem
  conteúdo; UI `ApplicationPanel` com 4 opções (só alvos elegíveis, resumo da
  mutação, impede 2.ª aplicação); provas negativas; +19 testes backend + concorrência,
  +7 frontend; regressão 124 frontend + build; sem drift; VAL-010 Parcial,
  VAL-004/005/006 com evidência.
  **F1-P06-PR06 (fecho):** validação E2E (E1–E6 + A–E + provas negativas + isolamento
  + autorização) num teste dedicado, corrigidos 2 defeitos de expectativa de teste;
  regressão backend **502** + frontend **124** + build; drift zero; reversibilidade
  estrutural verificada; migrações aplicadas na base existente; stack Docker saudável
  (health live/ready 200; endpoints roteados). **VAL-009 e VAL-010 Validadas; M1
  atingido.** Próximo: commit de F1-P06 e gerar F1-P07.
- Última actualização: 2026-07-14 17:30
