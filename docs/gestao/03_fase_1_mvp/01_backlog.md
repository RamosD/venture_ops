# Backlog detalhado — Fase 1: MVP do VentureOps AI

## 1. Identificação e objectivo da Fase 1

**Fase:** F1 — MVP
**Baseline de referência:** `docs/gestao/01_baseline/05_backlog_macro.md` (itens MVP-01 a MVP-23; RT-01 a RT-10)
**Escopo congelado:** `docs/gestao/02_fase_0_preparacao/artefactos/12_decisao_saida_fase_0.md`, §11 (DB-14, Confirmada)
**Autorização:** DEC-20260712-04 (Fase 0 concluída com reservas; decomposição controlada autorizada)
**Estado da fase:** Em preparação (decomposição concluída; implementação não iniciada)

**Objectivo:** entregar uma aplicação pequena e utilizável que permita a um
fundador gerir administrativamente vários produtos, preservar contexto e
completar um ciclo de execução assistida por IA com validação humana — validando
a tese do MVP num piloto real. Este backlog decompõe os 23 itens macro em
capacidades, histórias/requisitos técnicos e tarefas de implementação,
convertíveis em prompts de execução (não gerados nesta iteração).

**Hierarquia obrigatória:** Fase → Item macro → Capacidade/épico → História
funcional ou requisito técnico → Tarefa de implementação.

**Convenção de identificadores:** `MVP-XX.Cn` capacidade; `MVP-XX.Hn` história;
`MVP-XX.Rn` requisito técnico; `MVP-XX.Tn` tarefa.

## 2. Fontes e decisões vigentes

* Baseline: visão §15.1 (tese), arquitectura (monólito modular, React/TS, Django/DRF, PostgreSQL, Markdown em ficheiros), roadmap §4 (Fase 1), backlog macro (MVP-01..23, RT-01..10, OUT-*).
* Artefactos F0 confirmados (DB-01 a DB-14, DEC-20260712-04): segmento e caso de uso (01); fluxo C1–C4/E1–E6/T1–T2 e modelo de 8 entidades (02); estados e transições (03); ficha de 5 campos, testada com VentureOps AI (04); fronteira BD/Markdown com `is_outdated`/`export_policy` (05); 5 regras de atenção (06); pacote de contexto de 7 secções (07); uma empresa/individual/Owner com acumulação controlada de papéis (08); stack greenfield, Django Auth, filesystem/S3 (09); checklist de segurança SEC-* e 21 eventos auditáveis (10); plano do piloto com participante mínimo Aldino Ramos (11); escopo congelado (12).
* Decisões de fecho incorporadas: DEC-F0-FINAL-02 (plataforma → MVP-20), -03 (participante), -05 (papéis), -06 (função prévia + snapshot), -07 (tipos de pendência), -08 (marcadores documentais).
* Governação: revisão não bloqueante (DEC-20260712-01); a validação humana de resultados de IA no produto é regra funcional obrigatória (RT-05, SEC-HUM-01..06).

## 3. Escopo incluído

Conforme escopo congelado (artefacto 12, §11.1): uma empresa; utilizador
individual (Owner); vários produtos; ficha administrativa (5 campos); documentos
Markdown versionados com `is_outdated`/`export_policy`; decisões; pendências
mínimas (5 tipos); funções organizacionais; execuções assistidas manuais; pacote
de contexto; registo e validação humana de resultados; visão de atenção (5
regras); auditoria (21 eventos); exportação; isolamento por empresa; segurança
mínima (checklist F0-B12); operação mínima (logs, health checks, backups,
migrações, deploy, rollback); testes críticos; piloto; avaliação.

Opcional (só se não comprometer prazo/segurança/foco — artefacto 12, §11.3): IA
local manual limitada; importação inicial de Markdown; referência externa por URL.

## 4. Escopo excluído

Adiado (V1+): multiutilizador e convites; permissões avançadas; ligação
automática a IA; sincronização Git; pesquisa; notificações; templates; revisões
periódicas; histórico consolidado/comparação de versões; classificação avançada
de documentos; API controlada; indicadores de portefólio. Descartado do núcleo:
gestão completa de projectos; ERP; CRM; agentes autónomos/multiagente;
marketplace; alojamento de modelos; construtor de workflows; chat genérico;
avatares; app móvel; automações sem aprovação. Infra-estrutura excluída:
microserviços, filas, Redis, Celery, Kafka, Kubernetes dedicado, pesquisa
vectorial. Qualquer entrada exige controlo formal de alteração (artefacto 12, §12).

## 5. Princípios de implementação

1. Monólito modular com fronteiras por módulo de domínio (arquitectura §5).
2. `organisation_id` em todas as entidades e autorização no backend desde a primeira migração (SEC-ISO-01/02; nunca confiar no cliente).
3. Fonte oficial única: valores operacionais na BD; conteúdo em Markdown versionado imutável (RT-04; artefacto 05).
4. Resultados de IA nunca se tornam oficiais sem acção humana explícita; importar ≠ aprovar ≠ aplicar (RT-05; DEC-F0-FINAL-05).
5. Conteúdo não confiável: sanitizar Markdown/HTML, nunca executar (RT-07; SEC-DOC-02).
6. Auditoria append-only das operações da lista fechada (RT-02; artefacto 10 §8).
7. Simplicidade: sem frameworks genéricos, motores de regras ou infra-estrutura especulativa (RT-09).
8. Cada tarefa produz resultado verificável com teste ou demonstração (RT-10).
9. Alterações pequenas, incrementais e reversíveis; fluxo vertical antes da largura horizontal.

## 6. Estratégia incremental

**Incremento V — fluxo vertical mínimo (prioridade absoluta):** autenticar →
criar/aceder à empresa → criar produto → preencher ficha → criar documento →
registar decisão ou pendência → configurar função → criar execução → exportar
pacote → importar resultado → rever → aprovar/rejeitar → aplicar alteração
controlada → consultar atenção → verificar auditoria → exportar dados.

O fluxo vertical atravessa MVP-01→02→03→04/05→06→08/09→10→11→12→13→14→15→16→17→19,
usando a versão mínima de cada capacidade (marcada [V] nas tarefas). Só depois
de o fluxo vertical funcionar ponta a ponta se completa a largura (filtros,
arquivo, tipos documentais completos, casos de erro secundários, exportação
completa) e a operação (MVP-20), os testes consolidados (MVP-21) e o piloto
(MVP-22/23). Evitar construir módulos horizontais completos antes do primeiro
fluxo ponta a ponta.

---

## 7. Itens macro do MVP

### MVP-01 — Fundação operacional do produto

**Identificação** — Objectivo: disponibilizar a base executável e testável do MVP. Problema: repositório greenfield, sem estrutura, persistência ou pipeline. Valor: qualquer capacidade posterior torna-se implementável e verificável. Artefactos F0: 09 (stack), 10 (segurança), 05 (armazenamento).

**Escopo** — Incluído: estrutura do monólito modular (backend Django/DRF + frontend React/TS), configuração por ambiente, PostgreSQL, adaptador de armazenamento documental (filesystem dev; interface preparada para S3), Docker Compose local, testes base, CI mínimo (build+testes). Excluído: deploy em produção (MVP-20), Redis/Celery/filas, Kubernetes. Dependências: nenhuma (primeiro item). Pressupostos: stack confirmada (DB-11). Decisões vigentes: DB-11; DEC-F0-FINAL-02 (plataforma só em MVP-20). Reservas: nenhuma própria.

**Capacidades**
- MVP-01.C1 — Esqueleto executável do monólito (backend, frontend, BD, ambientes, compose).
- MVP-01.C2 — Fundação de qualidade (testes base, CI mínimo, validação de configuração no arranque).

**Histórias**
- **MVP-01.H1** — Como operador técnico, pretendo arrancar a aplicação localmente com um comando, para desenvolver e verificar qualquer capacidade.
  Pré-condições: Docker e código clonado. | Fluxo: arrancar compose → backend, frontend e BD sobem → health check responde. | Resultado: ambiente local funcional. | Regras: configuração validada no arranque; segredos fora do código (SEC-SEC-01). | Erros: configuração em falta → arranque falha com mensagem clara. | Aceitação: `docker compose up` deixa a aplicação acessível e o health check devolve OK. | Evidência: demonstração + saída do health check.

**Requisitos técnicos**
- MVP-01.R1 — Estrutura modular do backend por domínios (accounts, organisations, portfolio, documents, decisions, work_items, functions, executions, audit, storage, common), sem acoplamento entre módulos (arquitectura §5.1).
- MVP-01.R2 — Migrações versionadas desde o início; **todas** as entidades empresariais criadas já com `organisation_id` (SEC-ISO-01).
- MVP-01.R3 — Adaptador de armazenamento documental com interface única (filesystem em dev; S3-compatível como implementação futura sem alterar chamadores).
- MVP-01.R4 — Configuração por variáveis de ambiente com validação no arranque; sem segredos no repositório.
- MVP-01.R5 — CI mínimo: build + execução de testes em cada alteração; sem deploy automático nesta fase.

**Tarefas**
| ID | Tarefa | Resultado verificável | Dependências | Testes |
|---|---|---|---|---|
| MVP-01.T1 [V] | Criar estrutura do repositório (backend/frontend/docs preservado) e projecto Django modular | Projecto arranca vazio | — | smoke |
| MVP-01.T2 [V] | Configurar PostgreSQL + migração inicial com convenção `organisation_id` | Migração aplica e reverte | T1 | migração |
| MVP-01.T3 [V] | Criar frontend React/TS mínimo com cliente HTTP central | Página base carrega e chama API | T1 | smoke |
| MVP-01.T4 [V] | Docker Compose local (backend, frontend, BD, storage local) | `compose up` funcional | T1–T3 | manual |
| MVP-01.T5 | Adaptador de armazenamento (interface + filesystem) com chaves geradas no servidor e checksum | Escrita/leitura/checksum testadas | T2 | unitários |
| MVP-01.T6 | CI mínimo (build + testes) e validação de configuração no arranque | Pipeline verde; arranque falha sem config | T1–T5 | CI |

**Conclusão** — Implementado quando o ambiente local sobe com um comando, migrações e adaptador testados, CI verde; auditável (estrutura preparada para audit); documentado (README técnico mínimo); valida pré-condições de VAL-016 (parcial).

### MVP-02 — Autenticação e acesso inicial

**Identificação** — Objectivo: garantir acesso controlado à aplicação. Problema: sem identidade não há isolamento nem auditoria com actor. Valor: o fundador entra em segurança no seu contexto. Artefactos F0: 08 (Owner individual), 09 (Django Auth + cookie), 10 (SEC-AUTH-01/02).

**Escopo** — Incluído: registo/entrada/saída, sessão por cookie segura, recuperação de palavra-passe, perfil mínimo, rate limiting de login/recuperação. Excluído: SSO, OIDC, MFA, convites, multiutilizador. Dependências: MVP-01. Pressupostos: TLS nos ambientes partilhados (Secure condicional). Decisões vigentes: DB-10/DB-11; DEC-F0-FINAL-05 (papéis acumulados, operações distintas). Reservas: nenhuma.

**Capacidades**
- MVP-02.C1 — Identidade e sessão (registo, login, logout, sessão cookie, CSRF).
- MVP-02.C2 — Recuperação de acesso e perfil mínimo.

**Histórias**
- **MVP-02.H1** — Como fundador, pretendo autenticar-me com sessão segura, para aceder apenas ao meu contexto autorizado.
  Pré-condições: conta criada. | Fluxo: login → sessão emitida em cookie HttpOnly/SameSite (+Secure com TLS) → acesso às áreas autorizadas → logout invalida a sessão. | Resultado: sessão activa e revogável. | Regras: CSRF activo; nenhuma credencial no frontend; hashing robusto. | Erros: credenciais erradas → 401 sem detalhe; tentativas repetidas → rate limit + evento de auditoria. | Aceitação: login/logout funcionam; cookie com flags correctas; rate limit dispara. | Evidência: testes de sessão/CSRF/rate-limit.
- **MVP-02.H2** — Como fundador, pretendo recuperar a palavra-passe com token temporário, para não perder o acesso à minha empresa.
  Pré-condições: conta com email. | Fluxo: pedido → token temporário → redefinição → sessões antigas invalidadas. | Resultado: acesso recuperado. | Regras: token expira; invalidação de sessões após mudança crítica. | Erros: token expirado/reutilizado → rejeição. | Aceitação: ciclo completo testado, incluindo expiração. | Evidência: teste de integração.

**Requisitos técnicos**
- MVP-02.R1 — Django Auth com sessão por cookie (`HttpOnly`, `SameSite`, `Secure` com TLS) e protecção CSRF (SEC-AUTH-01).
- MVP-02.R2 — Rate limiting em login e recuperação (SEC-AUTH-02), com evento de auditoria para falhas repetidas.
- MVP-02.R3 — Perfil mínimo do utilizador (nome, email) sem campos especulativos.
- MVP-02.R4 — Logins/logouts relevantes e falhas repetidas auditados (eventos 1–2 da lista fechada).

**Tarefas**
| ID | Tarefa | Resultado verificável | Dependências | Testes |
|---|---|---|---|---|
| MVP-02.T1 [V] | Registo e login/logout com sessão cookie + CSRF | Ciclo entra/sai testado | MVP-01 | integração |
| MVP-02.T2 [V] | Ecrãs de entrada no frontend com cliente autenticado | Login funcional na UI | T1 | e2e mínimo |
| MVP-02.T3 | Recuperação de palavra-passe com token temporário e invalidação de sessões | Ciclo completo testado | T1 | integração |
| MVP-02.T4 | Rate limiting login/recuperação + auditoria de falhas repetidas | Limite dispara; evento gerado | T1 | segurança |
| MVP-02.T5 | Perfil mínimo (consulta/edição do próprio) | CRUD do próprio perfil | T1 | integração |

**Conclusão** — Utilizador autenticado acede apenas ao seu contexto; flags de cookie e CSRF verificadas; rate limiting activo; eventos auditados; valida VAL-001.

### MVP-03 — Gestão da empresa

**Identificação** — Objectivo: representar a entidade empresarial principal, contexto obrigatório de tudo. Problema: sem empresa não há isolamento nem portefólio. Valor: o fundador tem o seu espaço isolado. Artefactos F0: 08 (uma empresa activa, membership única Owner), 02 (C1).

**Escopo** — Incluído: criação inicial da empresa no onboarding, consulta/edição de dados básicos, configuração mínima, membership única (fundador=Owner). Excluído: multiempresa na experiência, selector de empresa, convites, gestão de membros. Dependências: MVP-02. Pressupostos: estrutura preparada para multiempresa sem a expor (artefacto 08 §3). Decisões vigentes: DB-10 (D-08-01/02/03), DEC-F0-FINAL-05. Reservas: nenhuma.

**Capacidades**
- MVP-03.C1 — Ciclo de vida da empresa (criação no onboarding, consulta, edição, estados Activa/Arquivada).
- MVP-03.C2 — Membership única Owner com contexto de empresa derivado no servidor.

**Histórias**
- **MVP-03.H1** — Como fundador autenticado pela primeira vez, pretendo criar a minha empresa, para ter o contexto onde tudo o resto vive.
  Pré-condições: sessão activa, sem empresa. | Fluxo: formulário mínimo (nome) → empresa Activa criada → membership Owner criada → redirecção para o portefólio. | Resultado: empresa e membership únicas. | Regras: uma empresa activa por conta (D-08-01); slug/identificador gerado no servidor. | Erros: tentativa de segunda empresa → rejeitada no MVP. | Aceitação: onboarding cria empresa+membership; segunda criação bloqueada. | Evidência: teste de integração + auditoria (evento 3).
- **MVP-03.H2** — Como Owner, pretendo consultar e editar os dados básicos da empresa, para manter a informação correcta.
  Pré-condições: empresa criada. | Fluxo: consulta → edição → gravação. | Resultado: dados actualizados e auditados. | Regras: só o Owner (membership validada no servidor). | Erros: acesso sem membership → 403/404. | Aceitação: edição funciona; acesso alheio rejeitado. | Evidência: testes de autorização.

**Requisitos técnicos**
- MVP-03.R1 — O `organisation_id` operacional deriva sempre da membership do utilizador autenticado; nunca é aceite do cliente sem validação (SEC-ISO-01/02).
- MVP-03.R2 — Modelo conceptual de membership (utilizador–empresa–papel) desde já, com uma associação única no MVP (preparação V1 sem exposição).
- MVP-03.R3 — Criação/alteração de empresa auditada (evento 3).

**Tarefas**
| ID | Tarefa | Resultado verificável | Dependências | Testes |
|---|---|---|---|---|
| MVP-03.T1 [V] | Entidades Organisation + Membership com migração | Migração aplicada | MVP-02 | migração |
| MVP-03.T2 [V] | Onboarding: criação da empresa + membership Owner | H1 completa | T1 | integração |
| MVP-03.T3 | Consulta/edição da empresa com autorização no servidor | H2 completa | T2 | autorização |
| MVP-03.T4 | Middleware/contexto de empresa derivado da membership em todos os pedidos | Pedidos sem membership rejeitados | T2 | isolamento |

**Conclusão** — Empresa criada e usada como contexto obrigatório; membership validada no servidor; eventos auditados; contribui para VAL-002.

### MVP-04 — Gestão do portefólio de produtos

**Identificação** — Objectivo: gerir vários produtos numa visão consolidada. Problema: a multiplicidade de produtos é o núcleo da dor do segmento. Valor: visão de portefólio única. Artefactos F0: 02 (C2), 03 (estados de produto), 04 (ficha), 01 (segmento 2+ produtos).

**Escopo** — Incluído: criar, editar, consultar, listar com filtros, arquivar e reactivar produtos. Excluído: indicadores de portefólio, revisões periódicas (V1), fases/gates. Dependências: MVP-03; MVP-05 (ficha) intimamente ligado. Pressupostos: estados Activo/Arquivado (F0-B05). Decisões vigentes: DB-04/05/07. Reservas: nenhuma.

**Capacidades**
- MVP-04.C1 — CRUD e ciclo de vida do produto (Activo/Arquivado/reactivação).
- MVP-04.C2 — Lista de portefólio com filtros mínimos (estado, responsável).

**Histórias**
- **MVP-04.H1** — Como operador, pretendo criar e manter vários produtos, para gerir o meu portefólio num único sítio.
  Pré-condições: empresa activa. | Fluxo: criar produto (ficha mínima) → listar → editar → arquivar/reactivar. | Resultado: portefólio actualizado. | Regras: estados e transições de F0-B05 §2.1; produto pertence à empresa do contexto. | Erros: transição inválida → rejeitada; produto de outra empresa → 404. | Aceitação: ciclo criar→editar→arquivar→reactivar testado; acesso cruzado impossível. | Evidência: integração + isolamento.
- **MVP-04.H2** — Como fundador, pretendo ver a lista dos meus produtos com estado e responsável, para perceber o portefólio de relance.
  Pré-condições: produtos criados. | Fluxo: abrir portefólio → lista com nome, estado, responsável, última revisão → filtrar. | Resultado: visão consolidada. | Regras: apenas produtos da empresa; paginação simples. | Erros: — | Aceitação: lista correcta e filtrável. | Evidência: teste de API + UI.

**Requisitos técnicos**
- MVP-04.R1 — Entidade Product com campos da ficha (F0-B07) e `organisation_id`; controlo de concorrência optimista na edição (versão).
- MVP-04.R2 — Transições de estado validadas no servidor (F0-B05); arquivo em vez de eliminação física (RT-08/integridade).
- MVP-04.R3 — Operações de produto auditadas (evento 4).

**Tarefas**
| ID | Tarefa | Resultado verificável | Dependências | Testes |
|---|---|---|---|---|
| MVP-04.T1 [V] | Entidade Product + migração + API CRUD com autorização | CRUD testado | MVP-03 | integração |
| MVP-04.T2 [V] | UI: lista de portefólio + criação/edição | H2 na UI | T1 | e2e mínimo |
| MVP-04.T3 | Arquivar/reactivar com validação de transições | Transições válidas/ inválidas testadas | T1 | unitários |
| MVP-04.T4 | Filtros (estado, responsável) e paginação | Filtros correctos | T1 | API |
| MVP-04.T5 | Auditoria de criação/edição/arquivo | Eventos gerados | T1, MVP-17.T1 | auditoria |

**Conclusão** — Vários produtos reais geríveis e consultáveis; transições validadas; auditado; valida VAL-003 (com MVP-05).

### MVP-05 — Ficha administrativa do produto

**Identificação** — Objectivo: concentrar o contexto essencial de cada produto. Problema: sem ficha coerente não há visão fiável. Valor: compreender um produto em segundos. Artefactos F0: 04 (5 campos testados com VentureOps AI), 06 (campos que alimentam a atenção).

**Escopo** — Incluído: 5 campos obrigatórios (Nome, Propósito, Estado, Responsável, Data da última revisão) com defaults; opcionais (público-alvo, fase, próxima revisão, notas); vistas agregadas (documentos, decisões, pendências, execuções). Excluído: campos adiados (sensibilidade do produto, equipa, indicadores). Dependências: MVP-04 (entidade), MVP-06/08/09/11 (agregadas — progressivas). Pressupostos: defaults reduzem escrita a Nome+Propósito. Decisões vigentes: DB-07 (Confirmada, teste real). Reservas: nenhuma.

**Capacidades**
- MVP-05.C1 — Ficha com campos obrigatórios/opcionais, defaults e vistas agregadas progressivas.

**Histórias**
- **MVP-05.H1** — Como operador, pretendo preencher a ficha mínima ao criar um produto, para o identificar sem esforço.
  Pré-condições: empresa activa. | Fluxo: criar → só Nome e Propósito exigem escrita → Estado=Activo, Responsável=operador, Última revisão=agora por defeito. | Resultado: ficha completa com esforço curto. | Regras: defaults do artefacto 04 §4. | Erros: nome vazio → validação. | Aceitação: criação exige apenas 2 campos escritos. | Evidência: teste + demonstração (piloto reconfirma).
- **MVP-05.H2** — Como fundador, pretendo abrir a ficha e ver o contexto agregado do produto, para decidir sem procurar noutros sítios.
  Pré-condições: produto com entidades associadas. | Fluxo: abrir ficha → separadores visão geral/documentos/decisões/pendências/execuções. | Resultado: contexto agregado. | Regras: agregadas por associação, não campos de entrada (artefacto 04 §2.3). | Erros: — | Aceitação: agregadas correctas por produto. | Evidência: teste de API + UI.

**Requisitos técnicos**
- MVP-05.R1 — Campos obrigatórios/opcionais conforme artefacto 04 §2; "Data da última revisão" actualizada automaticamente na criação/edição relevante.
- MVP-05.R2 — Vistas agregadas via associações (sem duplicação de dados; RT-04).
- MVP-05.R3 — Nível de atenção calculado, nunca persistido (artefacto 02 §6.5).

**Tarefas**
| ID | Tarefa | Resultado verificável | Dependências | Testes |
|---|---|---|---|---|
| MVP-05.T1 [V] | Formulário de ficha com defaults e validações | H1 completa | MVP-04.T1 | integração |
| MVP-05.T2 [V] | Página de ficha com separador visão geral | Ficha consultável | T1 | e2e mínimo |
| MVP-05.T3 | Separadores agregados (documentos/decisões/pendências/execuções) — progressivo | Agregadas correctas | MVP-06/08/09/11 | API |
| MVP-05.T4 | Actualização automática da data de última revisão | Campo actualiza | T1 | unitários |

**Conclusão** — Ficha coerente e suficiente para compreender o produto (critério do macro); esforço de preenchimento curto confirmado; contribui para VAL-003 e alimenta VAL-011.

### MVP-06 — Gestão documental em Markdown

**Identificação** — Objectivo: manter conhecimento e contexto de forma portável e versionada. Problema: o contexto narrativo precisa de fonte única, versões e segurança. Valor: memória empresarial recuperável. Artefactos F0: 05 (fronteira/versões/marcadores), 10 (SEC-DOC-*), 02 (C3/E6).

**Escopo** — Incluído: criar/editar/visualizar documentos; conteúdo Markdown em ficheiro via adaptador; metadados na BD; versões imutáveis; recuperação de versão (nova versão a partir de anterior); associação a produto (opcional ao nível da empresa); campos `is_outdated` e `export_policy`; sanitização na renderização; controlo de concorrência. Excluído: comparação de versões, pesquisa, classificação avançada, colaboração em tempo real. Dependências: MVP-03; MVP-01.T5 (adaptador). Pressupostos: granularidade "versão por alteração submetida" (artefacto 05, V-01). Decisões vigentes: DB-06; DEC-F0-FINAL-08. Reservas: nenhuma.

**Capacidades**
- MVP-06.C1 — CRUD documental com conteúdo em ficheiro e metadados na BD.
- MVP-06.C2 — Versionamento imutável com histórico e recuperação.
- MVP-06.C3 — Segurança documental (sanitização, marcadores, concorrência).

**Histórias**
- **MVP-06.H1** — Como operador, pretendo criar e editar documentos Markdown associados a um produto, para preservar o contexto.
  Pré-condições: empresa/produto. | Fluxo: criar (título, tipo, produto opcional, conteúdo) → v1 criada → editar → nova versão. | Resultado: documento versionado. | Regras: cada alteração submetida cria versão (V-01); conteúdo só via backend (SEC-DOC-01). | Erros: conteúdo acima do limite → 413; UTF-8 inválido → rejeitado. | Aceitação: criar/editar geram versões; limites aplicados. | Evidência: integração + versões.
- **MVP-06.H2** — Como operador, pretendo consultar o histórico e recuperar uma versão anterior, para nunca perder conteúdo.
  Pré-condições: documento com 2+ versões. | Fluxo: histórico → escolher versão → recuperar → nova versão criada a partir da anterior. | Resultado: conteúdo restaurado com histórico completo. | Regras: versões imutáveis (V-02/V-03); recuperação auditada (evento 7). | Erros: versão inexistente → 404. | Aceitação: recuperação preserva todas as versões. | Evidência: teste de recuperação.
- **MVP-06.H3** — Como operador, pretendo marcar um documento como desactualizado ou restringir a sua exportação, para controlar qualidade e sensibilidade.
  Pré-condições: documento activo. | Fluxo: alternar `is_outdated`; definir `export_policy`. | Resultado: marcadores actualizados na BD. | Regras: fonte oficial BD; `is_outdated` alimenta R-AT-05; `export_policy` aplicada pelo backend (DEC-F0-FINAL-08). | Erros: valor de política inválido → validação. | Aceitação: marcadores persistem e produzem efeito (atenção/exportação). | Evidência: testes das regras.

**Requisitos técnicos**
- MVP-06.R1 — Entidades Document + DocumentVersion (imutável, com checksum, autor, resumo de alteração); `current_version_id` consistente (arquitectura §6.2).
- MVP-06.R2 — Escrita coordenada BD↔ficheiro pelo backend (SEC-STO-01); objectos privados; chaves geradas no servidor.
- MVP-06.R3 — Sanitização na renderização: HTML/scripts bloqueados, URLs perigosas, sem execução de código (SEC-DOC-02); nomes de ficheiro sanitizados (SEC-DOC-04).
- MVP-06.R4 — Controlo de concorrência por versão base; conflito → 409 sem sobrescrita silenciosa (artefacto 05, U-03).
- MVP-06.R5 — Campos `is_outdated` (default false) e `export_policy` (default confirm) na BD, sem valor concorrente no Markdown.
- MVP-06.R6 — Eventos 5–7 auditados (criação/alteração, versão, recuperação).

**Tarefas**
| ID | Tarefa | Resultado verificável | Dependências | Testes |
|---|---|---|---|---|
| MVP-06.T1 [V] | Entidades Document/DocumentVersion + migração | Migração aplicada | MVP-03, MVP-01.T5 | migração |
| MVP-06.T2 [V] | API criar/consultar/editar com versão por submissão | H1 completa | T1 | integração |
| MVP-06.T3 [V] | Editor + pré-visualização sanitizada no frontend | XSS neutralizado na preview | T2 | segurança |
| MVP-06.T4 | Histórico e recuperação de versão | H2 completa | T2 | recuperação |
| MVP-06.T5 | Marcadores `is_outdated`/`export_policy` (modelo+API+UI) | H3 completa | T2 | unitários |
| MVP-06.T6 | Controlo de concorrência (versão base; 409) | Conflito detectado | T2 | integração |
| MVP-06.T7 | Auditoria documental (eventos 5–7) | Eventos gerados | T2, MVP-17.T1 | auditoria |

**Conclusão** — Documento criado, alterado e recuperável por versão (critério macro); sanitização comprovada; marcadores funcionais; valida VAL-004 e VAL-014.

### MVP-07 — Tipos documentais mínimos

**Identificação** — Objectivo: organizar documentos sem criar um sistema documental genérico. Problema: sem tipos mínimos, o contexto não é navegável. Valor: documentos com finalidade clara. Artefactos F0: 02 (glossário), 07 (documentos de instruções e de resultado).

**Escopo** — Incluído: tipos `contexto_da_empresa`, `visao_de_produto`, `instrucoes` (de função), `decisao_detalhada`, `resultado` (de execução). Excluído: tipos configuráveis, templates (V1). Dependências: MVP-06. Pressupostos: enumeração fixa no MVP. Decisões vigentes: DB-04/06. Reservas: nenhuma.

**Capacidades**
- MVP-07.C1 — Enumeração fixa de tipos com uso funcional (filtragem e ligação a função/decisão/execução).

**Histórias**
- **MVP-07.H1** — Como operador, pretendo classificar cada documento com um tipo mínimo, para o encontrar e usar no fluxo certo.
  Pré-condições: documento em criação. | Fluxo: escolher tipo na criação → listar/filtrar por tipo. | Resultado: documentos organizados. | Regras: enumeração fechada; tipo `instrucoes` usável em funções; `resultado` gerado no fluxo de execução. | Erros: tipo inválido → validação. | Aceitação: tipos disponíveis e filtráveis; usados por MVP-10/13. | Evidência: testes de API.

**Requisitos técnicos**
- MVP-07.R1 — Enumeração fechada validada no servidor; novos tipos exigem alteração formal.
- MVP-07.R2 — Tipos integrados nas associações (instruções→função; resultado→execução).

**Tarefas**
| ID | Tarefa | Resultado verificável | Dependências | Testes |
|---|---|---|---|---|
| MVP-07.T1 [V] | Campo tipo + enumeração + validação | Tipos aplicados | MVP-06.T2 | unitários |
| MVP-07.T2 | Filtro por tipo na listagem documental | Filtro correcto | T1 | API |
| MVP-07.T3 | Integração de tipos com função/execução | Associações validadas | T1, MVP-10/13 | integração |

**Conclusão** — Tipos mínimos disponíveis e utilizados no piloto (critério macro); sem sistema genérico.

### MVP-08 — Gestão de decisões

**Identificação** — Objectivo: preservar decisões e a respectiva justificação. Problema: decisões não registadas perdem-se e repetem-se. Valor: memória de decisão auditável. Artefactos F0: 03 (estados Activa/Substituída), 02 (E1).

**Escopo** — Incluído: registo (título, resumo/contexto, responsável, data, produto opcional, documento de detalhe opcional), consulta, substituição. Excluído: workflows de aprovação de decisão, tipos de decisão configuráveis. Dependências: MVP-04, MVP-06 (detalhe opcional). Pressupostos: estados mínimos de F0-B05 §2.3. Decisões vigentes: DB-04/05. Reservas: nenhuma.

**Capacidades**
- MVP-08.C1 — Registo e ciclo de vida da decisão (Activa→Substituída) com associações.

**Histórias**
- **MVP-08.H1** — Como fundador, pretendo registar uma decisão com contexto e responsável, para preservar porque foi tomada.
  Pré-condições: empresa/produto. | Fluxo: registar → Activa → associar produto e documento de detalhe (opcional). | Resultado: decisão consultável. | Regras: entidades da mesma empresa; data e responsável obrigatórios. | Erros: associação cruzada de empresa → rejeitada. | Aceitação: registo e consulta com associações válidas. | Evidência: integração + auditoria (evento 8).
- **MVP-08.H2** — Como fundador, pretendo substituir uma decisão por outra, para manter o histórico sem editar o passado.
  Pré-condições: decisão Activa. | Fluxo: registar nova → marcar anterior Substituída com ligação. | Resultado: cadeia de decisões rastreável. | Regras: substituição não apaga; transição F0-B05. | Erros: substituir já Substituída → rejeitado. | Aceitação: cadeia navegável. | Evidência: testes de transição.

**Requisitos técnicos**
- MVP-08.R1 — Entidade Decision (arquitectura §6.2) com `organisation_id` e transições validadas.
- MVP-08.R2 — Ligação opcional a documento de detalhe (tipo `decisao_detalhada`).
- MVP-08.R3 — Eventos 8 auditados.

**Tarefas**
| ID | Tarefa | Resultado verificável | Dependências | Testes |
|---|---|---|---|---|
| MVP-08.T1 [V] | Entidade + API de registo/consulta | H1 completa | MVP-04.T1 | integração |
| MVP-08.T2 [V] | UI de decisões no produto | Registo na UI | T1 | e2e mínimo |
| MVP-08.T3 | Substituição com cadeia | H2 completa | T1 | unitários |
| MVP-08.T4 | Auditoria de decisões | Eventos gerados | T1, MVP-17.T1 | auditoria |

**Conclusão** — Decisão registada, consultada e relacionada com produto (critério macro); valida VAL-005.

### MVP-09 — Gestão mínima de pendências

**Identificação** — Objectivo: controlar assuntos administrativos sem criar um gestor de projectos. Problema: obrigações e seguimentos perdem-se. Valor: lista curta accionável. Artefactos F0: 03 (estados+tipos), 06 (R-AT-02/03), DEC-F0-FINAL-07.

**Escopo** — Incluído: criar/editar pendências com os 5 tipos (`action`, `review`, `validation`, `obligation`, `decision_follow_up`), responsável, prioridade, prazo, produto, ligação opcional a decisão; estados Aberta/Concluída/Cancelada. Excluído: sprints, bugs, histórias técnicas, quadros kanban, dependências entre pendências. Dependências: MVP-04; MVP-08 (ligação opcional). Pressupostos: tipo é atributo, não estado. Decisões vigentes: DEC-F0-FINAL-07. Reservas: nenhuma.

**Capacidades**
- MVP-09.C1 — Ciclo de vida da pendência com tipos mínimos e associações.

**Histórias**
- **MVP-09.H1** — Como operador, pretendo registar uma pendência tipificada com prazo e responsável, para não perder obrigações administrativas.
  Pré-condições: empresa/produto. | Fluxo: criar (título, tipo, prazo, responsável) → Aberta. | Resultado: pendência acompanhável. | Regras: tipo da enumeração fechada; prazo alimenta R-AT-03. | Erros: tipo fora da enumeração → validação. | Aceitação: criação com os 5 tipos; vencimento derivado do prazo. | Evidência: integração.
- **MVP-09.H2** — Como operador, pretendo concluir ou cancelar pendências, para manter a lista fiável.
  Pré-condições: pendência Aberta. | Fluxo: concluir (E6 ou directamente) / cancelar. | Resultado: estado final. | Regras: transições F0-B05 §2.4. | Erros: transição de estado final → rejeitada. | Aceitação: transições testadas. | Evidência: unitários + auditoria (evento 9).

**Requisitos técnicos**
- MVP-09.R1 — Entidade WorkItem com tipo (enumeração DEC-F0-FINAL-07), prazo, prioridade, `organisation_id`.
- MVP-09.R2 — Sem estados por tipo (um único ciclo de vida); sem conceitos de gestão de projectos.
- MVP-09.R3 — Eventos 9 auditados.

**Tarefas**
| ID | Tarefa | Resultado verificável | Dependências | Testes |
|---|---|---|---|---|
| MVP-09.T1 [V] | Entidade + API com tipos e transições | H1/H2 completas | MVP-04.T1 | integração |
| MVP-09.T2 [V] | UI de pendências no produto | Criação/conclusão na UI | T1 | e2e mínimo |
| MVP-09.T3 | Ligação opcional a decisão | Associação validada | T1, MVP-08.T1 | API |
| MVP-09.T4 | Auditoria de pendências | Eventos gerados | T1, MVP-17.T1 | auditoria |

**Conclusão** — Pendências reais acompanháveis até conclusão/cancelamento (critério macro); valida VAL-006.

### MVP-10 — Gestão de funções organizacionais

**Identificação** — Objectivo: representar responsabilidades humanas, de IA e híbridas. Problema: sem funções, as execuções não têm perfil nem limites. Valor: governação humano–IA explícita. Artefactos F0: 02 (C4, §6.3), 03 (§2.5), DEC-F0-FINAL-06.

**Escopo** — Incluído: criar/editar funções (nome, tipo humana/IA/híbrida, propósito, responsabilidades, limites, `requires_approval`, documento de instruções), estados Activa/Inactiva. Excluído: modelos de funções (V1), políticas por função. Dependências: MVP-06 (documento de instruções). Pressupostos: função é configuração prévia, não passo do ciclo (DEC-F0-FINAL-06). Decisões vigentes: DB-04; DEC-F0-FINAL-06. Reservas: nenhuma.

**Capacidades**
- MVP-10.C1 — Configuração e ciclo de vida da função organizacional, com instruções versionadas.

**Histórias**
- **MVP-10.H1** — Como Owner, pretendo configurar previamente uma função (por exemplo "Analista de produto — IA"), para a reutilizar em execuções.
  Pré-condições: empresa; documento de instruções (opcional). | Fluxo: criar função → Activa → disponível para selecção em E2. | Resultado: função reutilizável. | Regras: distinção função (conteúdo) vs papel de acesso (F0-B10); `requires_approval` por defeito para funções IA. | Erros: tipo inválido → validação. | Aceitação: função criada e seleccionável; inactiva não seleccionável em novas execuções. | Evidência: integração.
- **MVP-10.H2** — Como Owner, pretendo inactivar/reactivar funções, para gerir o catálogo sem perder histórico.
  Pré-condições: função Activa. | Fluxo: inactivar → deixa de aparecer em novas execuções; execuções passadas mantêm referência+snapshot. | Resultado: catálogo limpo com histórico íntegro. | Regras: F0-B05 §2.5. | Erros: — | Aceitação: inactivação não afecta execuções passadas. | Evidência: testes.

**Requisitos técnicos**
- MVP-10.R1 — Entidade FunctionProfile (arquitectura §6.2) com `actor_type`, `requires_approval`, `instruction_document_id` opcional.
- MVP-10.R2 — Só funções Activas seleccionáveis em novas execuções; snapshot garantido em MVP-11.
- MVP-10.R3 — Eventos 10 auditados.

**Tarefas**
| ID | Tarefa | Resultado verificável | Dependências | Testes |
|---|---|---|---|---|
| MVP-10.T1 [V] | Entidade + API CRUD de funções | H1 completa | MVP-06.T2 | integração |
| MVP-10.T2 [V] | UI de funções | Criação na UI | T1 | e2e mínimo |
| MVP-10.T3 | Inactivação/reactivação com preservação de histórico | H2 completa | T1 | unitários |
| MVP-10.T4 | Auditoria de funções | Eventos gerados | T1, MVP-17.T1 | auditoria |

**Conclusão** — Função criada e seleccionável numa execução (critério macro); valida VAL-007.

### MVP-11 — Criação de execução assistida

**Identificação** — Objectivo: registar uma necessidade a executar com apoio de IA, com contexto rastreável. Problema: sem registo estruturado, as execuções de IA não têm rastreabilidade. Valor: cada trabalho de IA tem origem, contexto e estado. Artefactos F0: 02 (E2), 03 (§2.6), 07, DEC-F0-FINAL-06.

**Escopo** — Incluído: criar execução (produto, função activa, objectivo, modo manual, selecção de versões documentais), snapshot das instruções da função, estados de F0-B05 §2.6. Excluído: execução automática, polling, API de agentes. Dependências: MVP-04, MVP-06, MVP-10. Pressupostos: modo `manual_local`/`manual_external`. Decisões vigentes: DB-04/05; DEC-F0-FINAL-06. Reservas: nenhuma.

**Capacidades**
- MVP-11.C1 — Criação da execução com selecção de contexto por versões exactas.
- MVP-11.C2 — Snapshot de instruções e ciclo de estados da execução.

**Histórias**
- **MVP-11.H1** — Como operador, pretendo criar uma execução escolhendo produto, função e documentos com versões exactas, para preparar trabalho de IA rastreável.
  Pré-condições: produto, função Activa, documentos. | Fluxo: criar → seleccionar versões → snapshot das instruções → Preparada. | Resultado: execução com contexto congelado. | Regras: função tem de estar Activa; versões exactas preservadas (VAL-008); tudo da mesma empresa. | Erros: função inactiva → rejeitada; documento de outra empresa → rejeitado. | Aceitação: execução criada referencia versões e snapshot imutáveis. | Evidência: integração + verificação do snapshot.
- **MVP-11.H2** — Como operador, pretendo consultar as execuções de um produto com o seu estado, para acompanhar o trabalho de IA.
  Pré-condições: execuções criadas. | Fluxo: listar por produto → detalhe com contexto/estado. | Resultado: acompanhamento claro. | Regras: estados F0-B05 §2.6. | Erros: — | Aceitação: lista e detalhe correctos. | Evidência: API + UI.

**Requisitos técnicos**
- MVP-11.R1 — Entidades AIExecution + ExecutionContextDocument (versões exactas, ordem) — arquitectura §6.2.
- MVP-11.R2 — Snapshot imutável das instruções da função no momento da criação (DEC-F0-FINAL-06); referência à versão do documento de instruções.
- MVP-11.R3 — Máquina de estados no servidor (Preparada → Resultado por validar → Aprovada/Rejeitada → Concluída; correcção → Preparada).
- MVP-11.R4 — Eventos 11 auditados.

**Tarefas**
| ID | Tarefa | Resultado verificável | Dependências | Testes |
|---|---|---|---|---|
| MVP-11.T1 [V] | Entidades de execução + contexto + migração | Migração aplicada | MVP-10.T1, MVP-06.T1 | migração |
| MVP-11.T2 [V] | API criar execução com versões + snapshot | H1 completa | T1 | integração |
| MVP-11.T3 [V] | UI de criação e detalhe de execução | Criação na UI | T2 | e2e mínimo |
| MVP-11.T4 | Transições de estado no servidor | Transições válidas/inválidas | T2 | unitários |
| MVP-11.T5 | Auditoria de execuções | Eventos gerados | T2, MVP-17.T1 | auditoria |

**Conclusão** — Execução criada com contexto rastreável (critério macro); snapshot verificado; contribui para VAL-008/009.

### MVP-12 — Geração do pacote de contexto

**Identificação** — Objectivo: preparar informação coerente para execução manual externa ou local. Problema: preparar contexto à mão é a maior fricção e risco de fuga. Valor: pacote pronto, seguro e fiel às versões. Artefactos F0: 07 (estrutura de 7 secções, formatos, anti-injecção), 10 (§10 política IA externa), DEC-F0-FINAL-08.

**Escopo** — Incluído: gerar pacote com as 7 secções (objectivo, função, instruções do pedido, produto, restrições, formato esperado, documentos-DADOS com versões e fontes), exportação texto único (defeito) ou ficheiros separados, aplicação de `export_policy` (denied bloqueia; confirm exige confirmação), aviso ao utilizador. Excluído: envio automático a IA, templates de prompt por modelo. Dependências: MVP-11. Pressupostos: formatos neutros. Decisões vigentes: DB-09; DEC-F0-FINAL-08. Reservas: confirmação com modelo externo (recomendação, transferida para a validação — ver §14).

**Capacidades**
- MVP-12.C1 — Geração do pacote fiel às versões, com separação instruções/dados.
- MVP-12.C2 — Controlo de exportação (`export_policy`, confirmação, aviso, auditoria).

**Histórias**
- **MVP-12.H1** — Como operador, pretendo gerar e copiar/exportar o pacote de contexto de uma execução, para o usar manualmente numa IA externa ou local.
  Pré-condições: execução Preparada. | Fluxo: gerar → pré-visualizar → copiar ou descarregar. | Resultado: pacote com as 7 secções e fontes identificadas. | Regras: conteúdo gerado a partir das versões exactas (PC-03); declaração anti-injecção presente (R-PC-01..03). | Erros: execução em estado inválido → 409. | Aceitação: pacote corresponde às versões seleccionadas; estrutura completa. | Evidência: teste de geração + comparação de conteúdo.
- **MVP-12.H2** — Como operador, pretendo que documentos restritos sejam bloqueados ou exijam confirmação, para não expor conteúdo sensível a IA externa.
  Pré-condições: documentos com `export_policy` variada. | Fluxo: `denied` → excluído com aviso; `confirm` → confirmação explícita; `allowed` → incluído. | Resultado: exportação controlada. | Regras: aplicado no backend (R-PC-05); geração auditada (evento 12). | Erros: tentativa de contornar via API → bloqueada. | Aceitação: os três comportamentos testados no servidor. | Evidência: testes de segurança.

**Requisitos técnicos**
- MVP-12.R1 — Serviço de geração a partir das versões referenciadas (nunca da versão actual), com marcadores de início/fim e fontes.
- MVP-12.R2 — Formatos: texto/Markdown único (defeito) e ficheiros separados; sem optimização por fornecedor.
- MVP-12.R3 — `export_policy` aplicada no servidor; aviso ao utilizador antes de exportar; registo do destino/modo.
- MVP-12.R4 — Eventos 12 auditados; sem segredos no pacote.

**Tarefas**
| ID | Tarefa | Resultado verificável | Dependências | Testes |
|---|---|---|---|---|
| MVP-12.T1 [V] | Serviço de geração (7 secções, versões exactas) | Pacote fiel testado | MVP-11.T2 | integração |
| MVP-12.T2 [V] | UI de pré-visualização/cópia/descarga | H1 completa | T1 | e2e mínimo |
| MVP-12.T3 | Aplicação de `export_policy` + confirmação + aviso | H2 completa | T1, MVP-06.T5 | segurança |
| MVP-12.T4 | Exportação em ficheiros separados | Formato alternativo testado | T1 | API |
| MVP-12.T5 | Auditoria de geração/exportação de pacote | Eventos gerados | T1, MVP-17.T1 | auditoria |

**Conclusão** — Pacote corresponde às versões seleccionadas e pode ser exportado/copiado (critério macro); política de exportação comprovada; valida VAL-008 e alimenta VAL-013.

### MVP-13 — Registo do resultado da IA

**Identificação** — Objectivo: preservar o resultado produzido fora da aplicação, associado à execução correcta. Problema: resultados soltos em chats perdem rastreabilidade. Valor: cada resultado tem origem e estado. Artefactos F0: 02 (E4), 07 (importação), 03 (§2.7), DEC-F0-FINAL-05 (importar ≠ aprovar).

**Escopo** — Incluído: registar resultado (texto/Markdown colado ou ficheiro) numa execução Preparada, origem (ferramenta/modelo, modo) e notas; documento de resultado (tipo `resultado`); estado passa a Resultado por validar. Excluído: importação automática, parsing estruturado de respostas. Dependências: MVP-11, MVP-06/07. Pressupostos: conteúdo importado é não confiável (sanitizado na renderização). Decisões vigentes: DB-09; DEC-F0-FINAL-05. Reservas: nenhuma.

**Capacidades**
- MVP-13.C1 — Importação manual do resultado com origem, materializado como documento de resultado.

**Histórias**
- **MVP-13.H1** — Como operador, pretendo colar ou anexar o resultado produzido pela IA na execução correspondente, para o manter rastreável.
  Pré-condições: execução Preparada; resultado obtido externamente. | Fluxo: colar/anexar → origem+notas → documento de resultado criado → execução Resultado por validar. | Resultado: resultado associado à execução correcta. | Regras: importar **não** valida nem aplica (SEC-HUM); conteúdo tratado como não confiável (RT-07). | Erros: execução noutro estado → 409; tamanho excedido → 413. | Aceitação: resultado registado com origem; estado correcto; sem efeitos oficiais. | Evidência: integração + auditoria (evento 13).
- **MVP-13.H2** — Como operador, pretendo consultar o resultado registado com o contexto que o originou, para o rever com base completa.
  Pré-condições: resultado registado. | Fluxo: abrir execução → resultado + contexto (versões, snapshot). | Resultado: base de revisão completa. | Regras: renderização sanitizada. | Erros: — | Aceitação: detalhe completo. | Evidência: UI + testes.

**Requisitos técnicos**
- MVP-13.R1 — Resultado como documento (tipo `resultado`) referenciado pela execução; origem e modo na BD.
- MVP-13.R2 — Registo não altera nenhum estado oficial além do estado da execução (importar ≠ aprovar).
- MVP-13.R3 — Eventos 13 auditados.

**Tarefas**
| ID | Tarefa | Resultado verificável | Dependências | Testes |
|---|---|---|---|---|
| MVP-13.T1 [V] | API de registo do resultado (texto/ficheiro, origem) | H1 completa | MVP-11.T2, MVP-06.T2 | integração |
| MVP-13.T2 [V] | UI de importação e detalhe do resultado | H2 completa | T1 | e2e mínimo |
| MVP-13.T3 | Sanitização do resultado importado na renderização | XSS neutralizado | T1 | segurança |
| MVP-13.T4 | Auditoria de importação | Eventos gerados | T1, MVP-17.T1 | auditoria |

**Conclusão** — Resultado registado e associado à execução correcta (critério macro); valida VAL-009.

### MVP-14 — Revisão e aprovação de resultados

**Identificação** — Objectivo: manter controlo humano sobre os resultados de IA. Problema: resultados aplicados sem revisão corrompem a fonte de verdade. Valor: confiança na informação oficial. Artefactos F0: 03 (§2.7), 10 (SEC-HUM-01..06), DEC-F0-FINAL-05.

**Escopo** — Incluído: aprovar, rejeitar, pedir correcção (volta a Preparada), observações; acção explícita de utilizador autorizado; auditoria completa. Excluído: aprovação automática, aprovação por excepção, notificações. Dependências: MVP-13. Pressupostos: no MVP individual, o Owner exerce o papel de revisor (operações distintas). Decisões vigentes: DEC-F0-FINAL-05; RT-05. Reservas: nenhuma.

**Capacidades**
- MVP-14.C1 — Ciclo de validação humana do resultado (aprovar/rejeitar/correcção) com auditoria.

**Histórias**
- **MVP-14.H1** — Como revisor, pretendo aprovar ou rejeitar um resultado com observações, para decidir explicitamente o que se torna oficial.
  Pré-condições: execução Resultado por validar. | Fluxo: rever conteúdo+contexto → aprovar/rejeitar com observações → estado actualizado. | Resultado: decisão de validação registada. | Regras: acção explícita; aprovar **não** aplica (SEC-HUM-02); revisor autorizado (Owner no MVP). | Erros: dupla revisão → 409; estado inválido → rejeitado. | Aceitação: nenhum estado oficial muda sem esta acção; auditoria com actor/data/decisão (eventos 14–15). | Evidência: testes de fluxo + auditoria.
- **MVP-14.H2** — Como revisor, pretendo pedir correcção, para dar nova oportunidade sem rejeitar definitivamente.
  Pré-condições: Resultado por validar. | Fluxo: pedir correcção com observações → execução volta a Preparada. | Resultado: novo ciclo possível no mesmo registo. | Regras: transição F0-B05 §2.6/2.7; histórico preservado. | Erros: — | Aceitação: retorno a Preparada testado; evento 16 auditado. | Evidência: testes de transição.

**Requisitos técnicos**
- MVP-14.R1 — Campos de revisão na execução (revisor, data, decisão, observações) — folded conforme modelo funcional.
- MVP-14.R2 — Autorização da operação de revisão validada no servidor (operações críticas exigem Owner — SEC-AUT-02).
- MVP-14.R3 — Eventos 14–16 auditados.

**Tarefas**
| ID | Tarefa | Resultado verificável | Dependências | Testes |
|---|---|---|---|---|
| MVP-14.T1 [V] | API de revisão (aprovar/rejeitar/correcção) | H1/H2 completas | MVP-13.T1 | integração |
| MVP-14.T2 [V] | UI de caixa de validação | Revisão na UI | T1 | e2e mínimo |
| MVP-14.T3 | Garantia "aprovar ≠ aplicar" (nenhuma mutação documental na aprovação) | Prova negativa testada | T1 | segurança |
| MVP-14.T4 | Auditoria de revisão | Eventos gerados | T1, MVP-17.T1 | auditoria |

**Conclusão** — Resultado não altera estado oficial sem revisão explícita (critério macro); valida VAL-010.

### MVP-15 — Actualização controlada após aprovação

**Identificação** — Objectivo: reflectir resultados aprovados sem automação perigosa. Problema: aplicar mudanças é o momento de maior risco de corrupção. Valor: mudanças oficiais deliberadas, ligadas à execução e auditáveis. Artefactos F0: 02 (E6), 05 (U-02), DEC-F0-FINAL-05 (aplicar é operação explícita).

**Escopo** — Incluído: operação explícita "aplicar" que, a partir de um resultado Aprovado, cria nova versão documental / actualiza decisão / conclui pendência, com ligação à execução; execução passa a Concluída. Excluído: aplicação automática, aplicação parcial assistida por IA, diffs automáticos. Dependências: MVP-14, MVP-06, MVP-08, MVP-09. Pressupostos: aplicação manual/orientada no MVP. Decisões vigentes: DEC-F0-FINAL-05; RT-05. Reservas: nenhuma.

**Capacidades**
- MVP-15.C1 — Aplicação controlada a documentos (nova versão ligada à execução).
- MVP-15.C2 — Aplicação controlada a decisões/pendências e fecho da execução.

**Histórias**
- **MVP-15.H1** — Como operador, pretendo aplicar um resultado aprovado a um documento criando nova versão, para oficializar a mudança com rastreabilidade.
  Pré-condições: execução Aprovada; documento alvo. | Fluxo: escolher alvo → confirmar aplicação → nova versão criada com referência à execução → execução Concluída. | Resultado: mudança oficial rastreável. | Regras: só após aprovação (SEC-HUM-03); versão criada segue V-01/V-02; operação auditada (evento 17). | Erros: execução não aprovada → 409; conflito de versão base → 409. | Aceitação: nova versão referencia execução; estados finais correctos. | Evidência: integração + auditoria.
- **MVP-15.H2** — Como operador, pretendo concluir pendências ou actualizar decisões a partir de um resultado aprovado, para fechar o ciclo administrativo.
  Pré-condições: execução Aprovada. | Fluxo: aplicar a pendência (Concluída) ou decisão (actualização/substituição) → ligação à execução. | Resultado: estado administrativo actualizado. | Regras: transições válidas; SEC-HUM-04. | Erros: transição inválida → rejeitada. | Aceitação: efeitos correctos e auditados. | Evidência: testes de fluxo.

**Requisitos técnicos**
- MVP-15.R1 — Operação de aplicação como comando explícito, idempotente por execução, ligado à execução na entidade alvo.
- MVP-15.R2 — Nenhum caminho de código permite mutação documental directa a partir de resultado não aprovado (prova por teste).
- MVP-15.R3 — Execução → Concluída apenas após aplicação (ou fecho explícito).
- MVP-15.R4 — Eventos 17 auditados.

**Tarefas**
| ID | Tarefa | Resultado verificável | Dependências | Testes |
|---|---|---|---|---|
| MVP-15.T1 [V] | Comando de aplicação a documento (nova versão + ligação) | H1 completa | MVP-14.T1, MVP-06.T2 | integração |
| MVP-15.T2 [V] | UI de aplicação orientada | Aplicação na UI | T1 | e2e mínimo |
| MVP-15.T3 | Aplicação a decisão/pendência | H2 completa | T1, MVP-08/09 | integração |
| MVP-15.T4 | Prova negativa: sem aplicação sem aprovação | Teste negativo passa | T1 | segurança |
| MVP-15.T5 | Auditoria de aplicação | Eventos gerados | T1, MVP-17.T1 | auditoria |

**Conclusão** — Alterações aprovadas relacionadas com a execução e auditáveis (critério macro); reforça VAL-010 e VAL-004.

### MVP-16 — Visão de atenção

**Identificação** — Objectivo: mostrar produtos e assuntos que exigem intervenção, com motivos compreensíveis. Problema: sem sinalização, produtos são negligenciados. Valor: ponto de entrada diário do fundador. Artefactos F0: 06 (R-AT-01..05, parâmetros), 02 (T2).

**Escopo** — Incluído: painel com as 5 regras determinísticas calculadas por consulta; motivo apresentável por item; parâmetro prazo de revisão (30 dias, configurável ao nível da empresa); navegação para a entidade sinalizada. Excluído: pontuações, ranking, notificações, indicadores persistidos. Dependências: MVP-04/05 (R-AT-01), MVP-09 (R-AT-02/03), MVP-11/13/14 (R-AT-04), MVP-06 (R-AT-05). Pressupostos: cálculo por consulta simples (arquitectura §15.7). Decisões vigentes: DB-08; DEC-F0-FINAL-07/08. Reservas: calibração do prazo no piloto.

**Capacidades**
- MVP-16.C1 — Painel de atenção com as 5 regras e motivos explicáveis.

**Histórias**
- **MVP-16.H1** — Como fundador, pretendo abrir o painel de atenção e ver o que exige intervenção com o motivo, para agir sem investigar.
  Pré-condições: dados com sinais activos. | Fluxo: abrir painel → itens agrupados por regra com motivo → navegar para a entidade. | Resultado: intervenção dirigida. | Regras: R-AT-01..05 exactamente como no artefacto 06; entidades arquivadas excluídas. | Erros: — | Aceitação: cada regra dispara nas condições definidas e apresenta o motivo correcto. | Evidência: testes por regra (cenários positivos/negativos).
- **MVP-16.H2** — Como Owner, pretendo ajustar o prazo de revisão, para calibrar a regra ao meu ritmo.
  Pré-condições: empresa. | Fluxo: configurar prazo (defeito 30 dias). | Resultado: R-AT-01 usa o parâmetro. | Regras: parâmetro por empresa; valor positivo. | Erros: valor inválido → validação. | Aceitação: alteração reflecte-se no cálculo. | Evidência: teste parametrizado.

**Requisitos técnicos**
- MVP-16.R1 — Cálculo por consultas simples, sem persistência de indicadores nem "nível de atenção".
- MVP-16.R2 — Motivos gerados a partir da regra (textos do artefacto 06), não configuráveis no MVP.
- MVP-16.R3 — Endpoint de atenção agregado por empresa (arquitectura §10.3).

**Tarefas**
| ID | Tarefa | Resultado verificável | Dependências | Testes |
|---|---|---|---|---|
| MVP-16.T1 [V] | Serviço de cálculo das 5 regras | Regras testadas isoladamente | MVP-04/06/09/11 | unitários |
| MVP-16.T2 [V] | Painel de atenção na UI com navegação | H1 completa | T1 | e2e mínimo |
| MVP-16.T3 | Parâmetro de prazo por empresa | H2 completa | T1 | integração |
| MVP-16.T4 | Cenários combinados (múltiplos sinais por produto) | Independência das regras | T1 | integração |

**Conclusão** — Cada sinal apresentado com motivo compreensível (critério macro); valida VAL-011.

### MVP-17 — Histórico e auditoria básica

**Identificação** — Objectivo: garantir rastreabilidade das operações críticas. Problema: sem auditoria não há confiança nem reconstrução de eventos. Valor: operações críticas reconstruíveis. Artefactos F0: 10 (§8 — 21 eventos, campos, proibições), 02 (T1).

**Escopo** — Incluído: registo append-only dos 21 eventos da lista fechada, com actor/empresa/acção/entidade/data/resultado/correlação/metadados permitidos; consulta básica por entidade/produto. Excluído: linha temporal consolidada (V1), retenção configurável, exportação de auditoria avançada. Dependências: MVP-01 (base); consumido por todos os módulos. Pressupostos: lista fechada (novos eventos exigem alteração formal). Decisões vigentes: DB-12; RT-02. Reservas: nenhuma.

**Capacidades**
- MVP-17.C1 — Infra-estrutura de auditoria append-only com correlação.
- MVP-17.C2 — Consulta básica de auditoria por entidade.

**Histórias**
- **MVP-17.H1** — Como Owner, pretendo consultar o histórico de operações de uma entidade, para reconstruir quem fez o quê e quando.
  Pré-condições: operações realizadas. | Fluxo: abrir histórico da entidade → eventos com actor/acção/data/resultado. | Resultado: rastreabilidade utilizável. | Regras: append-only; sem conteúdo proibido (palavras-passe, tokens, prompts/documentos/resultados completos). | Erros: — | Aceitação: eventos correctos e sem dados sensíveis. | Evidência: inspecção + testes.

**Requisitos técnicos**
- MVP-17.R1 — Entidade AuditEvent (arquitectura §6.2) com `correlation_id` e `metadata` sem conteúdo sensível integral.
- MVP-17.R2 — API interna de emissão de eventos usada por todos os módulos (lista fechada validada).
- MVP-17.R3 — Tentativas de acesso entre empresas e falhas de armazenamento também auditadas (eventos 20–21).
- MVP-17.R4 — Sem alteração/remoção de eventos (append-only garantido ao nível aplicacional).

**Tarefas**
| ID | Tarefa | Resultado verificável | Dependências | Testes |
|---|---|---|---|---|
| MVP-17.T1 [V] | Entidade + serviço de emissão de eventos | Emissão testada | MVP-01 | unitários |
| MVP-17.T2 [V] | Integração dos eventos nos módulos do fluxo vertical | Eventos do fluxo gerados | T1 + módulos | integração |
| MVP-17.T3 | Consulta de auditoria por entidade (UI mínima) | H1 completa | T2 | e2e mínimo |
| MVP-17.T4 | Verificação de conteúdo proibido nos eventos/logs | Amostra limpa | T2 | segurança |
| MVP-17.T5 | Eventos de segurança (acesso cruzado, falha de armazenamento) | Eventos negativos gerados | T2, MVP-18 | segurança |

**Conclusão** — Operações críticas reconstruíveis pelo histórico (critério macro); valida VAL-012.

### MVP-18 — Segurança e isolamento do MVP

**Identificação** — Objectivo: impedir acesso indevido a empresas, produtos e documentos; consolidar o checklist de segurança. Problema: fuga entre empresas ou XSS destruiria a confiança no produto. Valor: segurança verificada, não presumida. Artefactos F0: 10 (SEC-ISO/AUT/DOC/SEC/EXP/AUTH/INJ), 08 (IS-01..04).

**Escopo** — Incluído: verificação sistemática dos controlos SEC-* implementados nos módulos (isolamento, autorização, sanitização, path traversal, segredos, rate limiting, anti-injecção no pacote); testes dedicados de segurança; correcção de lacunas. Excluído: pentest externo, MFA/SSO, tokens de agente (V1). Dependências: MVP-02, MVP-03, MVP-06 (mínimo); transversal a todos. Pressupostos: controlos definidos no artefacto 10 §7/§12. Decisões vigentes: DB-12. Reservas: RR-07 (eficácia comprovada nesta fase).

**Capacidades**
- MVP-18.C1 — Bateria de testes de isolamento e autorização (SEC-ISO-01..03, SEC-AUT-01..03).
- MVP-18.C2 — Bateria de conteúdo e segredos (SEC-DOC-01..04, SEC-SEC-01..03, SEC-INJ-01).

**Histórias**
- **MVP-18.H1** — Como Owner, pretendo garantia verificada de que nenhum acesso transversal entre empresas é possível, para confiar os meus dados ao produto.
  Pré-condições: duas empresas de teste com dados. | Fluxo: bateria de tentativas cruzadas (leitura, escrita, associação, exportação, ficheiros). | Resultado: todas rejeitadas com auditoria. | Regras: validação no servidor em todos os endpoints. | Erros: qualquer fuga → defeito bloqueante. | Aceitação: 100% das tentativas cruzadas falham (403/404) e são auditadas. | Evidência: suite de isolamento verde.

**Requisitos técnicos**
- MVP-18.R1 — Suite de testes de isolamento com duas empresas em todos os módulos (VAL-002).
- MVP-18.R2 — Testes de autorização directa à API (sem UI) para operações críticas (SEC-AUT-01/02).
- MVP-18.R3 — Testes de sanitização/XSS e path traversal sobre documentos e resultados importados (SEC-DOC-02/04; VAL-014).
- MVP-18.R4 — Inspecção de configuração: segredos fora do código, TLS em ambientes partilhados, logs sem conteúdo proibido (SEC-SEC-01..03).
- MVP-18.R5 — Teste anti-injecção do pacote (instrução plantada em documento não obedecida/estruturalmente separada — SEC-INJ-01).

**Tarefas**
| ID | Tarefa | Resultado verificável | Dependências | Testes |
|---|---|---|---|---|
| MVP-18.T1 [V] | Suite de isolamento entre empresas (módulos core) | Suite verde | MVP-03..06 | isolamento |
| MVP-18.T2 | Testes de autorização de operações críticas via API | Suite verde | MVP-14/15/19 | autorização |
| MVP-18.T3 | Testes XSS/traversal/sanitização | Payloads neutralizados | MVP-06/13 | segurança |
| MVP-18.T4 | Inspecção de segredos/logs/config + correcções | Checklist SEC-SEC verde | MVP-01/17 | inspecção |
| MVP-18.T5 | Teste anti-injecção do pacote de contexto | Injecção não executada | MVP-12 | segurança |
| MVP-18.T6 | Relatório de conformidade com o checklist do artefacto 10 | Matriz §12 preenchida | T1–T5 | evidência |

**Conclusão** — Testes confirmam inacessibilidade fora do contexto autorizado (critério macro); valida VAL-002 e VAL-014; matriz do artefacto 10 §12 com evidências.

### MVP-19 — Exportação e portabilidade

**Identificação** — Objectivo: permitir retirar dados essenciais e documentos. Problema: sem portabilidade não há confiança nem RT-06. Valor: o cliente é dono dos seus dados. Artefactos F0: 05 (versões), 10 (SEC-EXP-01/02), DEC-F0-FINAL-08 (`export_policy`).

**Escopo** — Incluído: exportação de empresa (produtos, documentos com versões, decisões, pendências, relações principais) com manifesto simples; restrita ao Owner; respeita `export_policy`; auditada; síncrona se pequena. Excluído: exportação agendada/assíncrona, formatos configuráveis. Dependências: MVP-04, MVP-06, MVP-08/09. Pressupostos: volume pequeno no MVP. Decisões vigentes: DB-06; RT-06. Reservas: nenhuma.

**Capacidades**
- MVP-19.C1 — Exportação de documentos como Markdown normal com versões.
- MVP-19.C2 — Exportação de dados essenciais + manifesto de relações.

**Histórias**
- **MVP-19.H1** — Como Owner, pretendo exportar os meus documentos e dados essenciais, para os usar fora da aplicação.
  Pré-condições: empresa com dados. | Fluxo: pedir exportação → pacote com Markdown + dados + manifesto → descarregar. | Resultado: pacote legível fora da aplicação. | Regras: só Owner (SEC-EXP-01); sem URLs públicas permanentes (SEC-EXP-02); auditada (evento 18). | Erros: não-Owner → 403; volume excessivo → 413. | Aceitação: pacote abre e compreende-se fora da aplicação (critério macro). | Evidência: teste + inspecção do pacote.
- **MVP-19.H2** — Como Owner, pretendo que a política documental seja respeitada na exportação, para controlar o que sai.
  Pré-condições: documentos com `export_policy` variada. | Fluxo: exportar → `denied` excluído e assinalado; `confirm` exige confirmação. | Resultado: exportação conforme política. | Regras: aplicada no backend. | Erros: — | Aceitação: comportamentos testados. | Evidência: testes de segurança.

**Requisitos técnicos**
- MVP-19.R1 — Documentos exportados como ficheiros Markdown normais (sem formato proprietário — RT-06).
- MVP-19.R2 — Manifesto simples com relações principais (produto↔documentos↔decisões↔pendências↔execuções).
- MVP-19.R3 — `export_policy` e autorização aplicadas no servidor; evento 18 auditado.

**Tarefas**
| ID | Tarefa | Resultado verificável | Dependências | Testes |
|---|---|---|---|---|
| MVP-19.T1 [V] | Serviço de exportação (docs+dados+manifesto) | Pacote gerado | MVP-06/08/09 | integração |
| MVP-19.T2 [V] | UI/endpoint de exportação Owner-only | H1 completa | T1 | autorização |
| MVP-19.T3 | Aplicação de `export_policy` na exportação | H2 completa | T1, MVP-06.T5 | segurança |
| MVP-19.T4 | Verificação de legibilidade externa do pacote | Manifesto compreensível | T1 | demonstração |
| MVP-19.T5 | Auditoria de exportação | Evento gerado | T1, MVP-17.T1 | auditoria |

**Conclusão** — Pacote exportado abre e compreende-se fora da aplicação (critério macro); valida VAL-013.

### MVP-20 — Operação mínima do MVP

**Identificação** — Objectivo: garantir execução controlada do produto (logs, health, backups, migrações, deploy, rollback). Problema: sem operação mínima, o piloto não é estável nem recuperável. Valor: ambiente de piloto fiável. Artefactos F0: 09 (§3.3 requisitos mínimos), 10 (§11-A backup/recuperação), DEC-F0-FINAL-02.

**Escopo** — Incluído: **tarefa explícita de selecção da plataforma** (avaliar → seleccionar → registar DEC → verificar requisitos mínimos), logs estruturados, health checks live/ready, backups BD+armazenamento, pipeline de migrações controladas, deploy documentado, rollback testado, teste de restauro. Excluído: Kubernetes dedicado (salvo plataforma existente), observabilidade avançada, auto-scaling. Dependências: MVP-01, MVP-17, MVP-18. Pressupostos: requisitos mínimos vigentes (DEC-F0-FINAL-02). Decisões vigentes: DEC-F0-FINAL-02. Reservas: **selecção da plataforma concreta — nesta fase, antes da implementação operacional deste item.**

**Capacidades**
- MVP-20.C1 — Decisão de plataforma (avaliação, selecção, registo formal).
- MVP-20.C2 — Observabilidade mínima (logs estruturados, health checks, captura de erros).
- MVP-20.C3 — Continuidade (backups, restauro testado, migrações controladas, deploy+rollback).

**Histórias**
- **MVP-20.H1** — Como operador do serviço, pretendo um ambiente de piloto estável, recuperável e observável, para conduzir o piloto sem perda de dados.
  Pré-condições: aplicação funcional; plataforma seleccionada (T1). | Fluxo: deploy → health checks OK → backups agendados → simulação de restauro → rollback ensaiado. | Resultado: ambiente de piloto operacional. | Regras: requisitos mínimos de DEC-F0-FINAL-02 todos verificados; migrações compatíveis com rollback (duas fases quando destrutivas). | Erros: health check falha → deploy não activa. | Aceitação: deploy, restauro e rollback demonstrados. | Evidência: execução documentada + evidências em `resultados_execucao/evidencias/`.

**Requisitos técnicos**
- MVP-20.R1 — Logs estruturados com correlação, sem conteúdo sensível (SEC-SEC-03; arquitectura §12.1).
- MVP-20.R2 — `/health/live` e `/health/ready` com verificação de BD e armazenamento.
- MVP-20.R3 — Backup da BD e do armazenamento documental; procedimento de restauro documentado e testado (SEC-BAK-01).
- MVP-20.R4 — Pipeline de deploy: build → testes → backup → migrações compatíveis → deploy → health → activação (arquitectura §13.7); rollback com imagem anterior.
- MVP-20.R5 — TLS e gestão de segredos conforme a plataforma seleccionada.

**Tarefas**
| ID | Tarefa | Resultado verificável | Dependências | Testes |
|---|---|---|---|---|
| MVP-20.T1 | **Avaliar plataformas disponíveis, seleccionar uma, registar DEC no log e verificar compatibilidade com os requisitos mínimos** (antes da implementação operacional deste item) | Decisão DEC registada + matriz de compatibilidade | MVP-01 | inspecção |
| MVP-20.T2 | Logs estruturados + captura de erros | Amostra conforme | MVP-01 | inspecção |
| MVP-20.T3 | Health checks live/ready | Endpoints verdes | MVP-01 | integração |
| MVP-20.T4 | Backups BD+armazenamento + procedimento de restauro | Restauro testado | T1 | recuperação |
| MVP-20.T5 | Pipeline de deploy com migrações controladas | Deploy demonstrado | T1, CI | demonstração |
| MVP-20.T6 | Rollback ensaiado | Rollback demonstrado | T5 | demonstração |
| MVP-20.T7 | Verificação TLS/segredos no ambiente | Checklist verde | T1 | inspecção |

**Conclusão** — Ambiente de piloto estável, recuperável e observável (critério macro); valida VAL-015 e VAL-016.

### MVP-21 — Testes dos fluxos críticos

**Identificação** — Objectivo: validar funcionalidade, segurança e consistência de ponta a ponta. Problema: módulos verdes isolados não garantem o fluxo completo. Valor: confiança para o piloto. Artefactos F0: 10 (§12 matriz), 02 (fluxo), plano de teste implícito nos critérios de cada item.

**Escopo** — Incluído: teste E2E do fluxo vertical completo (os 16 passos), consolidação das suites (isolamento, versões, transições, aprovações, exportação), relatório de cobertura dos fluxos críticos. Excluído: testes de carga, fuzzing, pentest externo. Dependências: todos os itens core (01–19). Pressupostos: suites parciais criadas em cada item. Decisões vigentes: RT-10. Reservas: nenhuma.

**Capacidades**
- MVP-21.C1 — Suite E2E do fluxo vertical (16 passos) em ambiente limpo.
- MVP-21.C2 — Consolidação e relatório das suites críticas.

**Histórias**
- **MVP-21.H1** — Como equipa, pretendo uma suite que percorra o fluxo completo do MVP num ambiente limpo, para garantir que o todo funciona, não só as partes.
  Pré-condições: aplicação integrada. | Fluxo: executar E2E: autenticar → empresa → produto → ficha → documento → decisão/pendência → função → execução → pacote → resultado → revisão → aplicação → atenção → auditoria → exportação. | Resultado: fluxo verde reproduzível. | Regras: dados de teste isolados; sem dependências externas. | Erros: qualquer passo falha → suite falha. | Aceitação: E2E verde em CI. | Evidência: execução em CI + relatório.

**Requisitos técnicos**
- MVP-21.R1 — Suite E2E automatizada e executável em CI.
- MVP-21.R2 — Consolidação: isolamento (MVP-18), versões (MVP-06), transições (03), aprovações (MVP-14/15), exportação (MVP-19) num relatório único.
- MVP-21.R3 — Critério de saída: zero falhas críticas; lacunas documentadas.

**Tarefas**
| ID | Tarefa | Resultado verificável | Dependências | Testes |
|---|---|---|---|---|
| MVP-21.T1 | Suite E2E do fluxo vertical | E2E verde | MVP-01..19 | e2e |
| MVP-21.T2 | Casos negativos críticos no E2E (aplicar sem aprovar; acesso cruzado; export denied) | Negativos verdes | T1 | e2e |
| MVP-21.T3 | Consolidação das suites + relatório | Relatório produzido | T1 | evidência |
| MVP-21.T4 | Integração das suites em CI como gate | CI bloqueia regressões | T1 | CI |
| MVP-21.T5 | Correcção de defeitos encontrados | Zero críticos abertos | T1–T4 | re-teste |

**Conclusão** — Conjunto mínimo de testes aprovado e executado com sucesso (critério macro); pré-condição de MVP-22.

### MVP-22 — Execução do piloto

**Identificação** — Objectivo: validar o MVP com produtos e utilizadores reais. Problema: sem uso real, a tese não é validada. Valor: evidência de valor (ou da sua ausência). Artefactos F0: 11 (plano, actividades, critérios), DEC-F0-FINAL-03/04.

**Escopo** — Incluído: preparação do ambiente de piloto, instrumentos de feedback (questionário pré/pós, guião de entrevista), onboarding do participante mínimo (Aldino Ramos), registo de produtos reais (VentureOps AI + segundo produto a seleccionar), execução das 7 actividades do plano durante 4 semanas, recolha de dados de utilização. Excluído: participantes inventados, dados sensíveis, marketing. Dependências: MVP-01..21 concluídos; plano do piloto (artefacto 11). Pressupostos: piloto pode arrancar com um participante. Decisões vigentes: DB-13; DEC-F0-FINAL-03. Reservas: RR-06 (execução do piloto — cumprida por este item); segundo produto real a seleccionar antes do arranque.

**Capacidades**
- MVP-22.C1 — Preparação do piloto (ambiente, instrumentos, onboarding).
- MVP-22.C2 — Condução e recolha (actividades, métricas, feedback).

**Histórias**
- **MVP-22.H1** — Como participante do piloto, pretendo usar o MVP com os meus produtos reais durante 4 semanas, para avaliar se reduz a minha fragmentação.
  Pré-condições: ambiente de piloto; conta criada. | Fluxo: onboarding → registar 2+ produtos reais → actividades 1–7 do plano → questionários pré/pós → entrevista final. | Resultado: dados de utilização e feedback. | Regras: dados reais não sensíveis; metas PH-01..03 como hipóteses a medir. | Erros: incidentes registados e triados. | Aceitação: as 10 validações do roadmap §4.7 têm dados recolhidos. | Evidência: dados de utilização + questionários + entrevista.
- **MVP-22.H2** — Como gestor do piloto, pretendo acompanhar a utilização e os incidentes, para intervir e registar evidência fiável.
  Pré-condições: piloto a decorrer. | Fluxo: acompanhamento semanal → registo de incidentes/fricções → ajustes não estruturais. | Resultado: piloto conduzido com evidência. | Regras: alterações estruturais exigem controlo de alteração. | Erros: incidente crítico → avaliação de suspensão. | Aceitação: registo semanal completo. | Evidência: diário do piloto.

**Requisitos técnicos**
- MVP-22.R1 — Ambiente de piloto operacional (MVP-20) com backups activos.
- MVP-22.R2 — Instrumentos de feedback preparados antes do arranque (P-05 do artefacto 11).
- MVP-22.R3 — Contagens de utilização extraíveis (produtos, documentos, decisões, pendências, execuções, validações).

**Tarefas**
| ID | Tarefa | Resultado verificável | Dependências | Testes |
|---|---|---|---|---|
| MVP-22.T1 | Preparar instrumentos (questionário pré/pós, guião, diário) | Instrumentos prontos | artefacto 11 | inspecção |
| MVP-22.T2 | Seleccionar e registar o segundo produto real | Produto confirmado | DEC-F0-FINAL-03 | registo |
| MVP-22.T3 | Onboarding do participante mínimo no ambiente de piloto | Conta+empresa+produtos criados | MVP-20/21 | demonstração |
| MVP-22.T4 | Conduzir as 4 semanas com acompanhamento semanal | Diário completo | T3 | evidência |
| MVP-22.T5 | Recolher e consolidar dados/feedback | Dataset + questionários | T4 | evidência |

**Conclusão** — Piloto concluído com evidências de uso e problemas registados (critério macro); alimenta todas as VAL com evidência real.

### MVP-23 — Avaliação e fecho do MVP

**Identificação** — Objectivo: decidir continuar, corrigir, reduzir ou pausar com base em evidência. Problema: sem decisão formal, o produto deriva. Valor: próxima fase fundamentada. Artefactos F0: 11 (critérios de sucesso), 12 (§12 controlo de alterações), roadmap §11.2.

**Escopo** — Incluído: relatório de validação (métricas vs critérios de sucesso; 10 validações do roadmap §4.7; matriz VAL-001..016 actualizada com evidências), análise de esforço/valor/segurança, decisão formal sobre a Versão 1 registada no log de decisões. Excluído: início da Versão 1. Dependências: MVP-22. Pressupostos: critérios do artefacto 11 §2.5. Decisões vigentes: DB-13. Reservas: nenhuma.

**Capacidades**
- MVP-23.C1 — Relatório de validação e decisão formal de fecho do MVP.

**Histórias**
- **MVP-23.H1** — Como fundador, pretendo um relatório de validação com decisão formal, para saber se avanço para a Versão 1, corrijo ou pauso.
  Pré-condições: piloto concluído. | Fluxo: consolidar métricas vs critérios → actualizar matriz VAL → redigir relatório → registar decisão (DEC). | Resultado: decisão fundamentada. | Regras: critérios de saída da Fase 1 verificados com evidência; decisão append-only. | Erros: — | Aceitação: relatório cobre os 5 critérios de sucesso e as 10 validações; decisão registada. | Evidência: relatório + DEC no log.

**Requisitos técnicos**
- MVP-23.R1 — Matriz `04_matriz_validacao_global.md` actualizada com estados e evidências reais (VAL-001..016).
- MVP-23.R2 — Relatório referencia evidências por caminho (sem logs extensos).

**Tarefas**
| ID | Tarefa | Resultado verificável | Dependências | Testes |
|---|---|---|---|---|
| MVP-23.T1 | Consolidar métricas do piloto vs critérios de sucesso | Análise completa | MVP-22.T5 | evidência |
| MVP-23.T2 | Actualizar matriz de validação global com evidências | VAL-001..016 com estado real | T1 | inspecção |
| MVP-23.T3 | Redigir relatório de validação do MVP | Relatório produzido | T1/T2 | revisão |
| MVP-23.T4 | Registar decisão formal sobre a Versão 1 (DEC) | DEC no log | T3 | registo |

**Conclusão** — Relatório de validação e decisão formal sobre a Versão 1 (critério macro); fecha a Fase 1.

---

## 8. Requisitos transversais (RT-01 a RT-10)

Cada requisito tem proprietários concretos; não existe item transversal órfão.

| RT | Requisito | Itens responsáveis | Capacidade/tarefa âncora | Validação | Evidência |
|---|---|---|---|---|---|
| RT-01 | Isolamento | MVP-01 (R2), 03 (R1), todos os módulos; consolidado em MVP-18 | MVP-18.C1 / MVP-18.T1 | Suite de isolamento | Testes verdes (VAL-002) |
| RT-02 | Rastreabilidade | MVP-17; emissores em 02–16, 19 | MVP-17.C1 / MVP-17.T2 | Testes de auditoria por evento | Eventos da lista fechada (VAL-012) |
| RT-03 | Versionamento documental | MVP-06 | MVP-06.C2 / T2, T4 | Teste de versões e recuperação | VAL-004 |
| RT-04 | Fonte de verdade | MVP-06 (metadados/conteúdo), 05 (agregadas), 12 (pacote derivado) | MVP-06.R1/R5; revisão de código | Revisão + testes de concorrência | Sem valores concorrentes |
| RT-05 | Validação humana | MVP-13/14/15 | MVP-14.C1; MVP-15.T4 | Prova negativa "sem aplicação sem aprovação" | VAL-010 |
| RT-06 | Portabilidade | MVP-19 | MVP-19.C1/C2 | Abertura externa do pacote | VAL-013 |
| RT-07 | Segurança de conteúdo | MVP-06 (R3), 13 (T3), 12 (anti-injecção) | MVP-18.T3/T5 | Testes XSS/traversal/injecção | VAL-014 |
| RT-08 | Recuperação | MVP-06 (versões), 20 (backup/restauro/rollback) | MVP-20.C3 / T4, T6 | Teste de restauro e rollback | VAL-015/016 |
| RT-09 | Simplicidade | Todos (princípio 7); guarda-costas em revisões | Critério de revisão de cada tarefa | Revisão de código | Ausência de infra-estrutura especulativa |
| RT-10 | Evidência | Todos; consolidado em MVP-21/23 | MVP-21.C2; MVP-23.C1 | Relatórios e matriz VAL | Evidências por caminho |

## 9. Dependências

### 9.1. Matriz resumida (item → depende de)

| Item | Depende de | Item | Depende de |
|---|---|---|---|
| MVP-01 | — | MVP-13 | 11, 06/07 |
| MVP-02 | 01 | MVP-14 | 13 |
| MVP-03 | 02 | MVP-15 | 14, 06, 08, 09 |
| MVP-04 | 03 | MVP-16 | 04/05, 06, 09, 11–14 |
| MVP-05 | 04 (+06/08/09/11 p/ agregadas) | MVP-17 | 01 (consumido por todos) |
| MVP-06 | 03, 01.T5 | MVP-18 | 02, 03, 06 (transversal) |
| MVP-07 | 06 | MVP-19 | 04, 06, 08/09 |
| MVP-08 | 04, 06 | MVP-20 | 01, 17, 18 (+T1 plataforma) |
| MVP-09 | 04 (+08 opcional) | MVP-21 | 01–19 |
| MVP-10 | 06 | MVP-22 | 01–21, artefacto 11 |
| MVP-11 | 04, 06, 10 | MVP-23 | 22 |
| MVP-12 | 11 (+06.T5) | | |

### 9.2. Grafo resumido

```text
01 → 02 → 03 → 04 → 05
           03 → 06 → 07
      04+06 → 08   04 → 09   06 → 10
   04+06+10 → 11 → 12 → (uso manual de IA) → 13 → 14 → 15
04/06/09/11..14 → 16
01 → 17 (transversal, consumido por 02..19)
02/03/06 → 18 (transversal)
04/06/08/09 → 19
01+17+18 → 20 → 22
01..19 → 21 → 22 → 23
```

Sem dependências circulares: a aparente circularidade 05↔(06/08/09/11) resolve-se
porque as vistas agregadas da ficha (MVP-05.T3) são progressivas — a ficha mínima
(T1/T2) só depende de MVP-04.

### 9.3. Caminho crítico

MVP-01 → 02 → 03 → 04(+05 mínimo) → 06 → 10 → 11 → 12 → 13 → 14 → 15 → 21(E2E) → 22 → 23.
É o caminho do fluxo vertical: qualquer atraso aqui atrasa o piloto.

### 9.4. Itens paralelizáveis

* Após MVP-04/06: MVP-07, 08, 09 em paralelo entre si.
* MVP-16 em paralelo com MVP-19 (após os emissores existirem).
* MVP-17.T1 (infra-estrutura de auditoria) logo após MVP-01, em paralelo com MVP-02.
* MVP-18 progressivo: T1 pode começar após MVP-03; consolidação após os módulos.
* MVP-20.T1 (selecção da plataforma) pode decorrer em paralelo desde cedo; a implementação operacional (T2–T7) após 17/18.

### 9.5. Pré-requisitos de segurança e do piloto

* Segurança: `organisation_id` e autorização no servidor desde MVP-01/03 (não retrofit); auditoria (17.T1) antes da integração dos emissores; MVP-18 e MVP-21 verdes antes do piloto.
* Piloto: MVP-20 (ambiente + backups + restauro) e MVP-21 (E2E) concluídos; instrumentos (22.T1) e segundo produto (22.T2) prontos antes do arranque.

## 10. Caminho crítico

Ver §9.3. Marcos de controlo: (M1) fluxo vertical mínimo funcional em ambiente
local (fim das tarefas [V] até MVP-15); (M2) segurança e testes consolidados
(MVP-18, MVP-21); (M3) ambiente de piloto operacional (MVP-20); (M4) piloto
concluído (MVP-22); (M5) decisão formal (MVP-23).

## 11. Itens paralelizáveis

Ver §9.4. Regra: paralelizar apenas o que não disputa as mesmas fronteiras de
módulo; integração sempre através do fluxo vertical.

## 12. Matriz de validação global (VAL-001 a VAL-016)

| VAL | Capacidade | Itens responsáveis | Testes/demonstrações | Momento | Critério de sucesso |
|---|---|---|---|---|---|
| VAL-001 | Autenticação | MVP-02 | Sessão/CSRF/rate-limit | M1 | Acesso autenticado e sessão segura testados |
| VAL-002 | Isolamento entre empresas | MVP-03, 18 | Suite de isolamento (duas empresas) | M2 | Zero acessos transversais |
| VAL-003 | Portefólio de produtos | MVP-04, 05 | CRUD+arquivo+ficha | M1 | Ciclo completo testado |
| VAL-004 | Documentos e versões | MVP-06 | Versões criadas/recuperáveis | M1 | Recuperação preserva histórico |
| VAL-005 | Decisões | MVP-08 | Registo+associação+substituição | M1 | Decisão ligada a produto |
| VAL-006 | Pendências administrativas | MVP-09 | Tipos+estados+prazos | M1 | 5 tipos e transições testados |
| VAL-007 | Funções organizacionais | MVP-10, 11 | Função usada numa execução | M1 | Selecção + snapshot verificados |
| VAL-008 | Pacote de contexto | MVP-11, 12 | Fidelidade às versões exactas | M1 | Pacote = versões seleccionadas |
| VAL-009 | Resultados de IA | MVP-13 | Registo com origem na execução certa | M1 | Associação correcta testada |
| VAL-010 | Revisão e aprovação | MVP-14, 15 | Prova negativa sem validação humana | M1/M2 | Nenhuma aplicação sem aprovação |
| VAL-011 | Visão de atenção | MVP-16 | 5 regras com motivos | M1 | Sinais explicáveis e correctos |
| VAL-012 | Auditoria | MVP-17 | Eventos da lista fechada | M2 | Operações críticas reconstruíveis |
| VAL-013 | Exportação | MVP-19 | Pacote externo legível + export_policy | M2 | Dados/Markdown exportáveis |
| VAL-014 | Segurança de Markdown | MVP-06, 13, 18 | XSS/sanitização | M2 | Payloads neutralizados |
| VAL-015 | Backup e recuperação | MVP-20 | Teste de restauro | M3 | Restauro validado |
| VAL-016 | Deploy e rollback | MVP-01 (CI), 20 | Deploy+rollback demonstrados | M3 | Reversão executável |

Cobertura completa: 16/16, sem validações órfãs. A matriz global
(`04_matriz_validacao_global.md`) é actualizada com evidências em MVP-23.T2.

## 13. Riscos

| ID | Risco | Mitigação | Origem |
|---|---|---|---|
| FR-01 | MVP crescer para além do escopo congelado | Controlo de alterações (artefacto 12 §12); toda a nova funcionalidade tem de provar que bloqueia o fluxo principal | Roadmap §4.6 |
| FR-02 | Construção horizontal antes do fluxo vertical | Tarefas [V] priorizadas; M1 como gate | §6 |
| FR-03 | Inconsistência BD↔ficheiros | Escrita coordenada pelo backend (SEC-STO-01); testes de consistência | Arquitectura §15.2 |
| FR-04 | Pendências evoluírem para gestor de projectos | Enumeração fechada de tipos; sem estados por tipo; revisão de escopo | DEC-F0-FINAL-07 |
| FR-05 | Retrofit de isolamento | `organisation_id` e autorização desde a primeira migração | IS-01 |
| FR-06 | Aplicação de resultados sem validação | Prova negativa obrigatória (MVP-15.T4); RT-05 | SEC-HUM |
| FR-07 | Selecção tardia da plataforma atrasar MVP-20/22 | MVP-20.T1 executável cedo e em paralelo | DEC-F0-FINAL-02 |
| FR-08 | Capacidade de execução (equipa reduzida) | Incrementos pequenos; caminho crítico curto; opcionais só após M1 | Visão §13.5 |
| FR-09 | Tarefas demasiado grandes para execução assistida | Tarefas com objectivo único e resultado verificável; partir na geração de prompts se necessário | §17 do prompt |

## 14. Reservas transferidas (da Fase 0)

| Reserva | Destino neste backlog |
|---|---|
| Selecção da plataforma concreta de deploy | **MVP-20.T1** (antes da implementação operacional de MVP-20) |
| Execução efectiva do piloto | **MVP-22** (participante mínimo: Aldino Ramos; segundo produto em MVP-22.T2) |
| Implementação e validação dos controlos de segurança | **MVP-18** (+ consolidação em MVP-21; matriz do artefacto 10 §12 com evidências) |
| Confirmação do pacote de contexto com modelo de IA externo (recomendação) | **MVP-12** — incluir na validação de MVP-12/MVP-22 um uso real com modelo externo (o piloto usa IA externa manualmente, cumprindo-a naturalmente) |
| Calibração do prazo de revisão (30 dias) | **MVP-16.T3** + feedback do piloto (MVP-22) |

## 15. Pipelines recomendadas (sem prompts nesta iteração)

| ID | Pipeline | Objectivo | Itens cobertos | Pré-requisitos | Resultado |
|---|---|---|---|---|---|
| F1-P02 | Fundação, autenticação e isolamento | Base executável com identidade, contexto de empresa e auditoria | MVP-01, 02, 03, 17.T1 | Backlog aprovado | App arranca com login, empresa e auditoria base |
| F1-P03 | Portefólio e ficha do produto | Produtos geríveis com ficha mínima | MVP-04, 05 | F1-P02 | Portefólio funcional |
| F1-P04 | Documentos, tipos, decisões e pendências | Contexto documental versionado e registos administrativos | MVP-06, 07, 08, 09 | F1-P03 | Documentos/decisões/pendências funcionais |
| F1-P05 | Funções, execuções e pacote de contexto | Preparação de trabalho de IA rastreável | MVP-10, 11, 12 | F1-P04 | Pacote gerado fiel às versões |
| F1-P06 | Resultados, revisão e aplicação controlada | Ciclo de validação humana completo | MVP-13, 14, 15 | F1-P05 | Fluxo vertical E1–E6 completo (M1) |
| F1-P07 | Atenção, auditoria, segurança e exportação | Sinais, rastreabilidade, segurança consolidada, portabilidade | MVP-16, 17 (consolidação), 18, 19 | F1-P06 | M2 atingido |
| F1-P08 | Operação, testes críticos, piloto e avaliação | Ambiente estável, E2E, piloto e decisão | MVP-20, 21, 22, 23 | F1-P07 (M2); MVP-20.T1 pode antecipar-se | M3–M5; decisão formal |

Ordem recomendada: F1-P02 → P03 → P04 → P05 → P06 → P07 → P08, com MVP-20.T1
(plataforma) e MVP-18.T1 (isolamento) iniciáveis em paralelo mais cedo.

## 16. Critérios de saída da Fase 1

Do backlog macro + roadmap §11.2, verificáveis com evidência:

1. fluxo completo funciona de ponta a ponta (E2E verde — MVP-21);
2. vários produtos geríveis (VAL-003);
3. documentos com versões recuperáveis (VAL-004);
4. decisões e pendências relacionadas com produtos (VAL-005/006);
5. função utilizável numa execução (VAL-007);
6. pacote preserva versões exactas (VAL-008);
7. resultados registados, aprovados ou rejeitados (VAL-009/010);
8. visão de atenção com motivos compreensíveis (VAL-011);
9. operações críticas auditadas (VAL-012);
10. exportação funciona (VAL-013);
11. isolamento e autorização testados (VAL-002/014);
12. backup/recuperação e deploy/rollback validados (VAL-015/016);
13. piloto real concluído com feedback registado (MVP-22);
14. decisão formal sobre continuar/ajustar/pausar registada (MVP-23);
15. sem vulnerabilidades críticas conhecidas (MVP-18).

## 17. Matriz de rastreabilidade

| Item macro | Capacidades | Artefactos F0 | RT | VAL |
|---|---|---|---|---|
| MVP-01 | C1–C2 | 09, 10, 05 | RT-01, RT-09 | (VAL-016 parcial) |
| MVP-02 | C1–C2 | 08, 09, 10 | RT-01, RT-02 | VAL-001 |
| MVP-03 | C1–C2 | 08, 02 | RT-01, RT-02 | VAL-002 |
| MVP-04 | C1–C2 | 02, 03, 04 | RT-01, RT-02, RT-10 | VAL-003 |
| MVP-05 | C1 | 04, 06 | RT-04 | VAL-003, VAL-011 |
| MVP-06 | C1–C3 | 05, 10, 02 | RT-03, RT-04, RT-07, RT-08 | VAL-004, VAL-014 |
| MVP-07 | C1 | 02, 07 | RT-09 | (suporta VAL-004/007/009) |
| MVP-08 | C1 | 03, 02 | RT-02 | VAL-005 |
| MVP-09 | C1 | 03, 06, DEC-07 | RT-02, RT-09 | VAL-006 |
| MVP-10 | C1 | 02, 03, DEC-06 | RT-02 | VAL-007 |
| MVP-11 | C1–C2 | 02, 03, 07, DEC-06 | RT-02, RT-10 | VAL-007, VAL-008 |
| MVP-12 | C1–C2 | 07, 10, DEC-08 | RT-04, RT-07 | VAL-008, VAL-013 |
| MVP-13 | C1 | 02, 07, DEC-05 | RT-05, RT-07 | VAL-009 |
| MVP-14 | C1 | 03, 10, DEC-05 | RT-05, RT-02 | VAL-010 |
| MVP-15 | C1–C2 | 02, 05, DEC-05 | RT-05, RT-03 | VAL-010, VAL-004 |
| MVP-16 | C1 | 06, 02 | RT-10 | VAL-011 |
| MVP-17 | C1–C2 | 10 (§8), 02 | RT-02 | VAL-012 |
| MVP-18 | C1–C2 | 10, 08 | RT-01, RT-07 | VAL-002, VAL-014 |
| MVP-19 | C1–C2 | 05, 10, DEC-08 | RT-06 | VAL-013 |
| MVP-20 | C1–C3 | 09, 10, DEC-02 | RT-08 | VAL-015, VAL-016 |
| MVP-21 | C1–C2 | 10 (§12), 02 | RT-10 | (verifica todas) |
| MVP-22 | C1–C2 | 11, DEC-03/04 | RT-10 | (evidência real de todas) |
| MVP-23 | C1 | 11, 12 | RT-10 | (fecha a matriz) |

**Totais da decomposição:** 23 itens macro; **39 capacidades**; **40 histórias
funcionais**; **81 requisitos técnicos**; **110 tarefas de implementação**
(das quais 40, marcadas [V], compõem o fluxo vertical mínimo).

## 18. Próximo passo recomendado

Gerar as **pipelines controladas de execução da Fase 1** (F1-P02 a F1-P08),
convertendo as tarefas deste backlog em prompts de execução com contexto
limitado, critérios de verificação e fecho de registo — pela ordem recomendada
em §15, começando por F1-P02. Não iniciado nesta iteração.
