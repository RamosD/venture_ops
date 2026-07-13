# Pipeline: Fundação, autenticação e isolamento

## Prompt 01 (opus) — Criar o esqueleto e fechar decisões de arranque

```prompt
Iteração 01

Actua como engenheiro de software sénior e executa o primeiro incremento da Fase 1 do VentureOps AI.

Identificação:
- Fase: F1 — MVP
- Pipeline: F1-P02 — Fundação, autenticação e isolamento
- Prompt: F1-P02-PR01
- Item: MVP-01
- Capacidade: MVP-01.C1
- História: MVP-01.H1, parcialmente
- Requisitos: MVP-01.R1 e MVP-01.R4
- Tarefa: MVP-01.T1
- Requisito transversal: RT-09
- Validação preparada: VAL-016, parcialmente

Objectivo:
Criar o esqueleto executável do backend Django, reservar a estrutura do frontend, estabelecer as fronteiras iniciais do monólito modular, implementar configuração mínima por ambiente e disponibilizar o endpoint técnico GET /api/system/ping.

Fechar também as decisões técnicas indispensáveis antes da primeira migração.

Contexto obrigatório:
Lê apenas:
- docs/gestao/03_fase_1_mvp/01_backlog.md: princípios de implementação e MVP-01;
- docs/gestao/03_fase_1_mvp/02_mapa_pipelines.md: F1-P02;
- docs/gestao/02_fase_0_preparacao/artefactos/09_stack_repositorio_padroes.md: stack e padrões;
- docs/gestao/01_baseline/03_arquitetura.md: monólito modular, configuração e API;
- docs/gestao/02_log_decisoes_execucao.md: DEC-20260712-05 e DEC-20260712-06.

Inspecção inicial:
1. Verifica o estado real do repositório.
2. Preserva integralmente docs/.
3. Confirma se já existe código inesperado.
4. Regista as versões locais de Python, Node e ferramentas relevantes.
5. Não apagues nem substituas silenciosamente trabalho existente.

Decisões a registar em docs/produto/00_decisoes_arranque.md:
1. Estrutura dos módulos e dependências permitidas.
2. CustomUser baseado no sistema de autenticação do Django.
3. Email único como identificador de autenticação.
4. Ausência de registo público irrestrito.
5. Mecanismo controlado previsto para criação da primeira conta.
6. Convenção única de identificadores das entidades de negócio.
7. Versões suportadas de Python, Django, Django REST Framework e Node.
8. Gestor de dependências Python e gestor de pacotes frontend.
9. Comandos oficiais de instalação, arranque, verificação, testes e build.
10. Prefixo da API e estratégia HTTP local.
11. Política restritiva de CORS.
12. Estratégia futura de CSRF para o frontend.
13. Email local de desenvolvimento sem fornecedor externo.
14. Contrato mínimo previsto para o adaptador de armazenamento.

Regra obrigatória sobre CustomUser:
- Confirma a decisão de utilizar CustomUser desde a primeira migração.
- Cria o módulo accounts, mas não cries ainda o modelo.
- Não configures AUTH_USER_MODEL para um modelo inexistente.
- Não executes makemigrations.
- Não executes migrate.
- Regista que PR02 criará CustomUser, activará AUTH_USER_MODEL e gerará a primeira migração de forma atómica.

Estrutura mínima:
- backend/manage.py
- backend/config/
- backend/apps/accounts/
- backend/apps/organisations/
- backend/apps/portfolio/
- backend/apps/documents/
- backend/apps/decisions/
- backend/apps/work_items/
- backend/apps/functions/
- backend/apps/executions/
- backend/apps/audit/
- backend/apps/storage/
- backend/apps/common/
- frontend/ apenas como pasta reservada
- docs/produto/00_decisoes_arranque.md

Os módulos podem ser pacotes ou aplicações Django vazias. Não cries modelos de domínio nem abstracções especulativas.

Implementa:
- projecto Django e Django REST Framework;
- configuração mínima por variáveis de ambiente;
- validação clara da configuração realmente necessária nesta etapa;
- routing mínimo;
- GET /api/system/ping;
- teste do endpoint sem utilização da base de dados;
- instruções técnicas mínimas de instalação e arranque.

O endpoint /api/system/ping:
- não consulta a base de dados;
- não usa armazenamento;
- não exige autenticação;
- devolve apenas uma resposta mínima equivalente a {"status": "ok"};
- não expõe versões, configuração ou dados sensíveis;
- não substitui /health/live nem /health/ready, que pertencem a PR05.

Fronteiras dos módulos:
- dependências explícitas e unidireccionais;
- sem ciclos;
- sem acesso directo indevido ao estado interno de outro módulo;
- common limitado a utilitários genuinamente partilhados;
- sem BaseRepository, BaseService, command bus, event bus ou sistema de plugins.

Não implementar:
- PostgreSQL;
- CustomUser;
- Organisation;
- Membership;
- migrações;
- autenticação;
- frontend React;
- Docker Compose;
- armazenamento filesystem;
- auditoria;
- CI;
- produtos ou restantes entidades de negócio;
- Redis, Celery, Kafka, Kubernetes ou microserviços;
- plataforma de deploy.

Validações obrigatórias:
1. backend/ existe;
2. frontend/ existe apenas como reserva;
3. docs/ foi preservado;
4. docs/produto/00_decisoes_arranque.md existe;
5. o documento cobre todas as decisões solicitadas;
6. python manage.py check passa;
7. o backend arranca;
8. GET /api/system/ping devolve HTTP 200;
9. o teste do ping passa sem base de dados;
10. configuração obrigatória em falta produz mensagem clara;
11. nenhum modelo de domínio foi criado;
12. AUTH_USER_MODEL não aponta para modelo inexistente;
13. nenhuma migração do projecto foi criada;
14. makemigrations e migrate não foram executados;
15. React não foi inicializado;
16. não existem dependências proibidas;
17. a baseline não foi alterada.

Fecho e registo:
- cria docs/gestao/03_fase_1_mvp/pipelines/02_fundacao_autenticacao_isolamento/resultados_execucao/prompt_01_resultado.md;
- actualiza F1-P02 em docs/gestao/01_status_pipelines.md para Em execução, 1/11 concluído;
- actualiza o painel global apenas com o estado actual e o próximo prompt;
- acrescenta uma linha ao diário de execução;
- não cries nova decisão global salvo desvio estrutural não coberto pelas decisões existentes.

Expectativa verificável:
- backend Django arranca;
- /api/system/ping funciona;
- decisões de arranque estão documentadas;
- não existem migrações;
- frontend ainda não foi inicializado;
- F1-P02 está Em execução;
- próximo prompt recomendado: F1-P02-PR02;
- relatório final indica ficheiros alterados, comandos executados, validações, dependências, pendências e riscos.

Não avances para o prompt seguinte.
```

## Prompt 02 (opus) — Criar PostgreSQL, identidade e fundação empresarial

```prompt
Iteração 02

Actua como engenheiro backend sénior e implementa a primeira migração estrutural do VentureOps AI.

Identificação:
- Fase: F1 — MVP
- Pipeline: F1-P02
- Prompt: F1-P02-PR02
- Itens: MVP-01, MVP-02 parcialmente e MVP-03 parcialmente
- Requisitos: MVP-01.R2, MVP-03.R1 e MVP-03.R2
- Tarefas: MVP-01.T2 e fundação de MVP-03.T1
- Requisito transversal: RT-01
- Validação preparada: VAL-002, parcialmente

Objectivo:
Configurar PostgreSQL e criar, de forma atómica, a fundação mínima de identidade e empresa:
- CustomUser;
- Organisation;
- Membership;
- AUTH_USER_MODEL;
- primeira migração do projecto;
- convenção reutilizável de entidades empresariais associadas obrigatoriamente a Organisation.

Pré-requisitos materiais:
- F1-P02-PR01 concluído;
- backend Django existente;
- docs/produto/00_decisoes_arranque.md existente;
- nenhuma migração do projecto criada anteriormente;
- nenhuma decisão silenciosa pelo User padrão do Django.

Contexto obrigatório:
Lê apenas:
- docs/gestao/03_fase_1_mvp/01_backlog.md: MVP-01, fundação de MVP-02 e MVP-03;
- docs/gestao/02_fase_0_preparacao/artefactos/08_modelo_utilizadores_empresas.md;
- docs/gestao/02_fase_0_preparacao/artefactos/05_fonte_de_verdade_bd_markdown.md: princípios de fonte oficial;
- docs/produto/00_decisoes_arranque.md;
- resultado de F1-P02-PR01.

Inspecção inicial:
1. Confirma que não existem migrações do projecto.
2. Confirma a convenção de identificadores decidida em PR01.
3. Confirma as versões e o gestor de dependências adoptados.
4. Verifica se existe alguma alteração inesperada antes de continuar.

Implementa PostgreSQL por configuração de ambiente.

Cria CustomUser:
- baseado no sistema de autenticação do Django;
- configurado através de AUTH_USER_MODEL;
- email único como identificador;
- nome e campos mínimos;
- sem perfil extenso;
- sem fluxo de registo, login ou recuperação neste prompt;
- presente na primeira migração aplicável.

Cria Organisation:
- identificador conforme a convenção decidida;
- nome;
- estado mínimo Activa ou Arquivada;
- datas de criação e actualização;
- sem regras de onboarding nesta etapa.

Cria Membership:
- relação com CustomUser;
- relação com Organisation;
- papel mínimo Owner;
- estado activo;
- restrições de unicidade coerentes;
- preparada para suportar o contexto empresarial;
- sem convites ou gestão de membros.

Cria uma convenção simples para entidades empresariais futuras:
- relação real e obrigatória com Organisation;
- pode ser modelo abstracto, mixin explícito ou outra solução simples do Django;
- não criar tabela fictícia apenas para testar a convenção;
- não aceitar organisation_id livremente do cliente;
- não criar repository pattern;
- não criar acesso directo indevido entre módulos.

Gera e aplica a primeira migração do projecto contendo:
- CustomUser;
- Organisation;
- Membership;
- restrições mínimas;
- configuração AUTH_USER_MODEL coerente.

Não implementar:
- login ou logout;
- recuperação de palavra-passe;
- onboarding;
- edição da empresa;
- selector de empresa;
- criação de segunda empresa pela UI;
- convites;
- papéis avançados;
- restantes entidades de domínio.

Testes obrigatórios:
1. migrações aplicam numa base PostgreSQL vazia;
2. migrações podem ser revertidas de forma controlada;
3. AUTH_USER_MODEL aponta para CustomUser;
4. email único é garantido;
5. Membership liga utilizador e empresa;
6. papel Owner é aceite;
7. restrições de Membership são aplicadas;
8. uma entidade que use a convenção empresarial exige Organisation;
9. não existe ainda endpoint ou serviço de onboarding;
10. /api/system/ping continua funcional.

Não uses SQLite como persistência da aplicação.

Fecho e registo:
- cria prompt_02_resultado.md na pasta de resultados da pipeline;
- actualiza F1-P02 para 2/11 concluídos;
- actualiza o painel apenas com o próximo prompt;
- acrescenta uma linha ao diário;
- regista decisão global apenas se houver desvio estrutural face a docs/produto/00_decisoes_arranque.md.

Expectativa verificável:
- PostgreSQL está configurado;
- primeira migração aplica numa base vazia;
- CustomUser, Organisation e Membership existem;
- AUTH_USER_MODEL está activo desde a primeira migração;
- testes estruturais passam;
- não existem fluxos de autenticação ou onboarding;
- próximo prompt recomendado: F1-P02-PR03;
- relatório final lista ficheiros, migrações, comandos, testes, problemas e pendências.

Não avances para o prompt seguinte.
```

## Prompt 03 (sonnet) — Inicializar o frontend e integrar o ping

```prompt
Iteração 03

Actua como engenheiro frontend e cria a fundação mínima React/TypeScript do VentureOps AI.

Identificação:
- Fase: F1 — MVP
- Pipeline: F1-P02
- Prompt: F1-P02-PR03
- Item: MVP-01
- Capacidade: MVP-01.C1
- Tarefa: MVP-01.T3
- Requisito transversal: RT-09

Objectivo:
Criar o frontend React/TypeScript mínimo, implementar um cliente HTTP central e demonstrar comunicação real com GET /api/system/ping.

Pré-requisitos:
- PR01 concluído e /api/system/ping funcional;
- PR02 concluído;
- frontend/ ainda não inicializado;
- decisões de toolchain e fronteira HTTP registadas em docs/produto/00_decisoes_arranque.md.

Contexto obrigatório:
Lê apenas:
- docs/gestao/03_fase_1_mvp/01_backlog.md: MVP-01.T3;
- docs/gestao/01_baseline/03_arquitetura.md: frontend e comunicação HTTP;
- docs/produto/00_decisoes_arranque.md;
- resultados de PR01 e PR02.

Implementa:
- projecto React com TypeScript;
- estrutura simples e não especulativa;
- cliente HTTP central;
- configuração da URL da API por ambiente;
- tratamento central mínimo de erros;
- prevenção de submissões duplicadas preparada no cliente ou camada de chamadas;
- página inicial que chama /api/system/ping;
- apresentação clara do estado: a carregar, disponível ou erro;
- teste mínimo da integração;
- build funcional.

Regras:
- não persistir credenciais no browser;
- não implementar autenticação;
- não criar Redux ou outra store global sem necessidade;
- não criar UI de produtos, empresa ou restantes domínios;
- não consumir /health/live nem /health/ready;
- respeitar a estratégia de CORS ou proxy decidida;
- evitar bibliotecas de UI sem justificação.

Validações:
1. frontend arranca;
2. build passa;
3. cliente HTTP central existe;
4. /api/system/ping é chamado;
5. resposta de sucesso é apresentada;
6. falha de comunicação é tratada;
7. não existem credenciais persistidas;
8. backend e migrações continuam funcionais;
9. nenhum ecrã de autenticação foi criado.

Fecho e registo:
- cria prompt_03_resultado.md;
- actualiza F1-P02 para 3/11 concluídos;
- actualiza o painel com o próximo prompt;
- acrescenta uma linha ao diário.

Expectativa verificável:
- frontend React/TypeScript existe;
- cliente HTTP central comunica com /api/system/ping;
- build e testes passam;
- nenhuma UI de domínio foi antecipada;
- próximo prompt recomendado: F1-P02-PR04;
- relatório final indica dependências adicionadas, comandos, testes, ficheiros, limitações e pendências.

Não avances para o prompt seguinte.
```

## Prompt 04 (sonnet) — Integrar armazenamento local e Docker Compose

```prompt
Iteração 04

Actua como engenheiro de plataforma e implementa a fundação local integrada do VentureOps AI.

Identificação:
- Fase: F1 — MVP
- Pipeline: F1-P02
- Prompt: F1-P02-PR04
- Item: MVP-01
- Capacidade: MVP-01.C1
- Requisito: MVP-01.R3
- Tarefas: MVP-01.T4 e MVP-01.T5
- Requisito transversal: RT-08, apenas fundação
- Validação preparada: VAL-016, parcialmente

Objectivo:
Implementar o contrato mínimo de armazenamento, a implementação filesystem e o Docker Compose local que integra PostgreSQL, backend, frontend e armazenamento privado.

Pré-requisitos:
- PR01 a PR03 concluídos;
- backend, PostgreSQL e frontend funcionais;
- contrato previsto de armazenamento documentado em docs/produto/00_decisoes_arranque.md.

Contexto obrigatório:
Lê apenas:
- docs/gestao/03_fase_1_mvp/01_backlog.md: MVP-01.R3, T4 e T5;
- docs/gestao/02_fase_0_preparacao/artefactos/05_fonte_de_verdade_bd_markdown.md: regras de armazenamento;
- docs/gestao/02_fase_0_preparacao/artefactos/09_stack_repositorio_padroes.md;
- docs/gestao/02_fase_0_preparacao/artefactos/10_requisitos_seguranca_mvp.md: SEC-DOC-03;
- docs/produto/00_decisoes_arranque.md.

Implementa contrato mínimo com operações estritamente necessárias:
- escrever;
- ler;
- verificar existência;
- calcular ou devolver checksum;
- remoção controlada, apenas se necessária.

Implementa filesystem:
- chaves geradas no servidor;
- prevenção de path traversal;
- conteúdo fora de directórios públicos;
- objectos não acessíveis directamente por URL;
- checksum verificável;
- ponto de extensão futuro para S3 sem implementar S3.

Implementa Docker Compose com:
- PostgreSQL;
- backend;
- frontend;
- volume privado para armazenamento;
- variáveis por ficheiro de exemplo;
- dependências e health checks locais suficientes;
- sem segredos reais no repositório.

Não implementar:
- S3;
- URLs temporárias;
- conteúdo documental;
- deploy;
- Redis, Celery, Kafka ou Kubernetes;
- observabilidade avançada.

Validações:
1. docker compose up inicia os serviços;
2. PostgreSQL fica disponível;
3. backend responde;
4. frontend responde;
5. frontend comunica com /api/system/ping;
6. escrita e leitura no filesystem funcionam;
7. checksum é estável;
8. path traversal é rejeitado;
9. objectos não ficam públicos;
10. migrações aplicam numa base vazia dentro do ambiente;
11. testes backend passam;
12. build frontend passa.

Fecho e registo:
- cria prompt_04_resultado.md;
- actualiza F1-P02 para 4/11 concluídos;
- actualiza painel e diário;
- não alteres artefactos da Fase 0.

Expectativa verificável:
- aplicação integrada sobe com Docker Compose;
- armazenamento filesystem está funcional e testado;
- frontend, backend e PostgreSQL comunicam;
- não existe implementação S3;
- próximo prompt recomendado: F1-P02-PR05;
- relatório final inclui comandos, testes, ficheiros, volumes, dependências, problemas e pendências.

Não avances para o prompt seguinte.
```

## Prompt 05 (sonnet) — Criar health checks, testes base e CI

```prompt
Iteração 05

Actua como engenheiro de qualidade e cria a fundação de testes e integração contínua do VentureOps AI.

Identificação:
- Fase: F1 — MVP
- Pipeline: F1-P02
- Prompt: F1-P02-PR05
- Item: MVP-01
- Capacidade: MVP-01.C2
- Requisito: MVP-01.R5
- Tarefa: MVP-01.T6
- Requisito transversal: RT-10
- Validação: VAL-016, parcial

Objectivo:
Implementar health checks técnicos, consolidar os testes base e configurar CI mínimo de build e testes, sem deploy automático.

Pré-requisitos:
- PR01 a PR04 concluídos;
- ambiente local integrado por Docker Compose;
- PostgreSQL e armazenamento funcionais.

Contexto obrigatório:
Lê apenas:
- docs/gestao/03_fase_1_mvp/01_backlog.md: MVP-01.C2 e MVP-01.R5;
- docs/gestao/01_baseline/03_arquitetura.md: health checks, testes e CI;
- resultados de PR01 a PR04.

Implementa:
- GET /health/live, verificando apenas o processo;
- GET /health/ready, verificando PostgreSQL e armazenamento;
- respostas mínimas sem informação sensível;
- estrutura organizada de testes unitários e de integração;
- testes de configuração obrigatória;
- CI mínimo com instalação, migrações numa base limpa, testes backend, build frontend e verificações relevantes;
- sem deploy automático.

Distingue:
- /api/system/ping: smoke técnico da aplicação;
- /health/live: processo activo;
- /health/ready: dependências prontas.

Não implementar:
- observabilidade avançada;
- métricas;
- alertas;
- deploy;
- rollback;
- plataforma de produção.

Validações:
1. /health/live responde quando o processo está activo;
2. /health/ready fica saudável com BD e armazenamento disponíveis;
3. /health/ready falha de forma controlada quando uma dependência falha;
4. respostas não expõem segredos;
5. testes backend passam;
6. build frontend passa;
7. CI executa numa base limpa;
8. configuração em falta falha com mensagem clara;
9. CI não realiza deploy;
10. Docker Compose continua funcional.

Matriz de validação:
- anota VAL-016 apenas como parcial;
- referencia evidência concreta;
- não declares deploy ou rollback validados.

Fecho e registo:
- cria prompt_05_resultado.md;
- actualiza F1-P02 para 5/11 concluídos;
- actualiza painel e diário;
- actualiza a matriz global apenas com evidência real e estado parcial.

Expectativa verificável:
- health checks funcionam;
- testes base passam;
- CI executa build e testes;
- VAL-016 permanece parcial;
- próximo prompt recomendado: F1-P02-PR06;
- relatório final indica configuração de CI, comandos, testes, evidências, falhas e pendências.

Não avances para o prompt seguinte.
```

## Prompt 06 (opus) — Implementar auditoria append-only

```prompt
Iteração 06

Actua como arquitecto backend e implementa a fundação de auditoria do VentureOps AI.

Identificação:
- Fase: F1 — MVP
- Pipeline: F1-P02
- Prompt: F1-P02-PR06
- Item: MVP-17
- Capacidade: MVP-17.C1
- Requisitos: MVP-17.R1, MVP-17.R2 parcialmente e MVP-17.R4
- Tarefa: MVP-17.T1
- Requisito transversal: RT-02
- Validação: VAL-012, parcial

Objectivo:
Criar AuditEvent e um serviço mínimo de emissão append-only, com correlation_id, actor e organização opcionais e protecção contra conteúdo proibido.

Pré-requisitos:
- PR02 concluído;
- CustomUser e Organisation existentes;
- PostgreSQL funcional;
- testes e CI disponíveis.

Contexto obrigatório:
Lê apenas:
- docs/gestao/03_fase_1_mvp/01_backlog.md: MVP-17;
- docs/gestao/02_fase_0_preparacao/artefactos/10_requisitos_seguranca_mvp.md: lista fechada de eventos, campos e conteúdo proibido;
- decisões técnicas actuais;
- resultados anteriores da pipeline.

AuditEvent deve suportar:
- actor opcional;
- organisation opcional;
- acção;
- tipo e identificador da entidade;
- data;
- resultado;
- correlation_id;
- metadados mínimos permitidos;
- snapshots mínimos de identificadores, quando necessários.

Regras de preservação:
- eventos sem utilizador autenticado são permitidos;
- eventos antes de determinar a empresa são permitidos;
- apagar ou desactivar actor não pode apagar eventos;
- arquivar ou remover logicamente empresa não pode apagar eventos;
- não usar CASCADE de User ou Organisation para AuditEvent;
- não duplicar integralmente utilizador ou empresa;
- eventos são append-only ao nível aplicacional;
- não disponibilizar update ou delete normal.

Conteúdo proibido:
- palavras-passe;
- tokens;
- cookies;
- segredos;
- prompts completos;
- documentos completos;
- resultados completos;
- payloads sensíveis integrais.

Implementa:
- modelo e migração;
- serviço público mínimo de emissão;
- validação do tipo de evento segundo a lista fechada;
- correlation_id;
- protecção ou filtragem de metadados;
- testes positivos e negativos.

Não integrar ainda todos os módulos emissores. Essa integração começa nos prompts posteriores e consolida-se em F1-P07.

Validações:
1. emissão com actor e organização;
2. emissão sem actor;
3. emissão sem organização;
4. correlation_id preservado;
5. evento não pode ser actualizado;
6. evento não pode ser apagado pela API normal;
7. remoção ou alteração do actor não elimina o evento;
8. organização não elimina eventos associados;
9. conteúdo proibido é rejeitado ou removido de forma controlada;
10. migração aplica e reverte;
11. testes e CI passam.

Fecho e registo:
- cria prompt_06_resultado.md;
- actualiza F1-P02 para 6/11 concluídos;
- actualiza painel e diário;
- anota VAL-012 como parcial com evidência concreta.

Expectativa verificável:
- AuditEvent existe;
- serviço de emissão funciona;
- eventos são preservados e append-only;
- conteúdo proibido não é registado;
- VAL-012 permanece parcial;
- próximo prompt recomendado: F1-P02-PR07;
- relatório final lista modelo, migração, eventos testados, comandos, evidências e limitações.

Não avances para o prompt seguinte.
```

## Prompt 07 (opus) — Implementar autenticação backend com sessão e CSRF

```prompt
Iteração 07

Actua como especialista em segurança Django e implementa a autenticação backend do VentureOps AI.

Identificação:
- Fase: F1 — MVP
- Pipeline: F1-P02
- Prompt: F1-P02-PR07
- Item: MVP-02
- Capacidade: MVP-02.C1
- História: MVP-02.H1
- Requisitos: MVP-02.R1 e MVP-02.R4
- Tarefa: MVP-02.T1
- Requisitos transversais: RT-01 e RT-02
- Validação: VAL-001, parcial

Objectivo:
Implementar login e logout com Django Auth, sessão por cookie segura, CSRF e auditoria dos eventos relevantes.

Pré-requisitos:
- PR01 a PR06 concluídos;
- CustomUser activo;
- mecanismo de criação controlada da conta decidido;
- auditoria disponível;
- frontend ainda sem ecrãs de autenticação.

Contexto obrigatório:
Lê apenas:
- docs/gestao/03_fase_1_mvp/01_backlog.md: MVP-02.H1, R1 e R4;
- docs/gestao/02_fase_0_preparacao/artefactos/09_stack_repositorio_padroes.md: autenticação;
- docs/gestao/02_fase_0_preparacao/artefactos/10_requisitos_seguranca_mvp.md: SEC-AUTH-01 e eventos de autenticação;
- docs/produto/00_decisoes_arranque.md;
- implementação actual.

Implementa:
- criação controlada da conta inicial conforme a decisão existente;
- endpoint para obtenção ou preparação do token CSRF;
- login;
- consulta da sessão actual;
- logout;
- invalidação da sessão;
- hashing segundo os mecanismos suportados pelo Django;
- eventos de auditoria relevantes.

Cookies e sessão:
- HttpOnly;
- SameSite adequado;
- Secure em ambiente com TLS;
- configuração distinta e explícita para desenvolvimento;
- sem tokens de autenticação em localStorage;
- sem credenciais no frontend.

Regras:
- não abrir registo público;
- não implementar recuperação de palavra-passe;
- não implementar rate limiting, que pertence a PR09;
- não implementar MFA, SSO ou OIDC;
- mensagens de erro não devem revelar se o email existe;
- autorização sempre no backend.

Validações:
1. conta inicial pode ser criada pelo mecanismo controlado;
2. login válido cria sessão;
3. login inválido é rejeitado sem detalhe sensível;
4. cookie possui flags correctas;
5. CSRF é exigido em operações mutáveis;
6. logout invalida a sessão;
7. pedido autenticado devolve o utilizador actual;
8. evento de autenticação é auditado;
9. segredos e palavra-passe não aparecem em logs ou auditoria;
10. testes e CI passam.

Fecho e registo:
- cria prompt_07_resultado.md;
- actualiza F1-P02 para 7/11 concluídos;
- actualiza painel e diário;
- anota VAL-001 como parcial.

Expectativa verificável:
- login, sessão e logout funcionam no backend;
- CSRF está activo;
- eventos relevantes são auditados;
- não existe registo público nem recuperação;
- próximo prompt recomendado: F1-P02-PR08;
- relatório final indica endpoints, testes, cookies, eventos, problemas e pendências.

Não avances para o prompt seguinte.
```

## Prompt 08 (sonnet) — Criar a interface de autenticação

```prompt
Iteração 08

Actua como engenheiro frontend e implementa a interface mínima de autenticação do VentureOps AI.

Identificação:
- Fase: F1 — MVP
- Pipeline: F1-P02
- Prompt: F1-P02-PR08
- Item: MVP-02
- Capacidade: MVP-02.C1
- História: MVP-02.H1, interface
- Tarefa: MVP-02.T2
- Validação: VAL-001, parcial

Objectivo:
Criar os ecrãs de login e logout, integrar a sessão do backend e disponibilizar uma área autenticada mínima.

Pré-requisitos:
- frontend de PR03 funcional;
- autenticação backend de PR07 funcional;
- estratégia de CSRF e cookies definida;
- cliente HTTP central existente.

Contexto obrigatório:
Lê apenas:
- docs/gestao/03_fase_1_mvp/01_backlog.md: MVP-02.T2;
- docs/gestao/01_baseline/03_arquitetura.md: entrada e cliente HTTP;
- docs/produto/00_decisoes_arranque.md;
- contratos reais implementados em PR07.

Implementa:
- formulário de login;
- obtenção ou preparação do CSRF;
- submissão pelo cliente HTTP central;
- estado de sessão actual;
- rota ou área autenticada mínima;
- logout;
- redireccionamento coerente;
- tratamento de sessão expirada;
- mensagens de erro sem detalhe sensível;
- estados de carregamento;
- prevenção de submissão duplicada.

Não implementar:
- recuperação de palavra-passe;
- perfil;
- onboarding;
- produtos ou restantes ecrãs de domínio;
- persistência de credenciais em localStorage ou sessionStorage;
- store global complexa sem necessidade.

Validações:
1. utilizador consegue entrar pela UI;
2. área autenticada só fica acessível com sessão;
3. logout termina a sessão;
4. sessão expirada é tratada;
5. CSRF funciona;
6. erro de login não revela dados sensíveis;
7. credenciais não são persistidas;
8. e2e mínimo login → área autenticada → logout passa;
9. build e testes passam.

Fecho e registo:
- cria prompt_08_resultado.md;
- actualiza F1-P02 para 8/11 concluídos;
- actualiza painel e diário.

Expectativa verificável:
- autenticação é utilizável pela interface;
- sessão e logout funcionam;
- e2e mínimo passa;
- recuperação e onboarding não foram antecipados;
- próximo prompt recomendado: F1-P02-PR09;
- relatório final lista componentes, rotas, testes, contratos utilizados, problemas e pendências.

Não avances para o prompt seguinte.
```

## Prompt 09 (opus) — Implementar recuperação, rate limiting e perfil

```prompt
Iteração 09

Actua como especialista em autenticação e segurança e completa as capacidades de acesso do MVP.

Identificação:
- Fase: F1 — MVP
- Pipeline: F1-P02
- Prompt: F1-P02-PR09
- Item: MVP-02
- Capacidade: MVP-02.C2
- História: MVP-02.H2
- Requisitos: MVP-02.R2 e MVP-02.R3
- Tarefas: MVP-02.T3, MVP-02.T4 e MVP-02.T5
- Requisito transversal: RT-02
- Validação: VAL-001

Objectivo:
Implementar recuperação de palavra-passe com token temporário, rate limiting persistente para login e recuperação, invalidação de sessões e perfil mínimo.

Pré-requisitos:
- PR07 e PR08 concluídos;
- mecanismo de email de desenvolvimento decidido;
- PostgreSQL e auditoria disponíveis.

Contexto obrigatório:
Lê apenas:
- docs/gestao/03_fase_1_mvp/01_backlog.md: MVP-02.H2, R2 e R3;
- docs/gestao/02_fase_0_preparacao/artefactos/10_requisitos_seguranca_mvp.md: SEC-AUTH-01, SEC-AUTH-02 e eventos relacionados;
- docs/produto/00_decisoes_arranque.md;
- implementação actual de autenticação.

Recuperação:
- pedido de recuperação sem revelar se o email existe;
- token temporário e de utilização única;
- expiração;
- redefinição da palavra-passe;
- invalidação das sessões anteriores;
- mecanismo local de email sem fornecedor externo;
- preparação configurável para email real no piloto.

Rate limiting:
- proteger login e recuperação;
- não depender exclusivamente de memória local;
- funcionar em ambiente com vários processos;
- não introduzir Redis;
- preferir mecanismo simples compatível com PostgreSQL ou cache persistente já disponível;
- justificar qualquer dependência adicional;
- distinguir controlo de segurança de throttling de conveniência;
- auditar falhas repetidas relevantes;
- não guardar palavras-passe ou payloads sensíveis.

Perfil:
- consulta do próprio perfil;
- edição apenas dos campos mínimos;
- email com regras coerentes de unicidade e segurança;
- autorização no backend.

Frontend:
- interface mínima de recuperação;
- interface mínima do perfil;
- sem funcionalidades adicionais.

Validações:
1. pedido de recuperação não revela existência da conta;
2. token válido funciona;
3. token expirado é rejeitado;
4. token reutilizado é rejeitado;
5. redefinição invalida sessões antigas;
6. rate limit bloqueia no limiar definido;
7. janela expira;
8. acesso recupera depois da janela;
9. comportamento é persistente entre processos;
10. evento de falhas repetidas é auditado;
11. perfil só permite editar o próprio utilizador;
12. testes backend, frontend e CI passam;
13. VAL-001 possui evidência completa para o escopo do MVP.

Fecho e registo:
- cria prompt_09_resultado.md;
- actualiza F1-P02 para 9/11 concluídos;
- actualiza painel e diário;
- actualiza VAL-001 com evidência real.

Expectativa verificável:
- recuperação funciona;
- rate limiting persistente funciona sem Redis;
- perfil mínimo funciona;
- VAL-001 está validada para o escopo implementado;
- próximo prompt recomendado: F1-P02-PR10;
- relatório final indica mecanismo adoptado, testes, eventos, dependências, limitações e pendências.

Não avances para o prompt seguinte.
```

## Prompt 10 (opus) — Implementar onboarding e gestão mínima da empresa

```prompt
Iteração 10

Actua como engenheiro backend e frontend sénior e implementa o onboarding empresarial do VentureOps AI.

Identificação:
- Fase: F1 — MVP
- Pipeline: F1-P02
- Prompt: F1-P02-PR10
- Item: MVP-03
- Capacidades: MVP-03.C1 e MVP-03.C2
- Histórias: MVP-03.H1 e MVP-03.H2
- Requisitos: MVP-03.R1, MVP-03.R2 e MVP-03.R3
- Tarefas: MVP-03.T2 e MVP-03.T3
- Requisitos transversais: RT-01 e RT-02
- Validação: VAL-002, parcial

Objectivo:
Implementar o serviço de onboarding que cria uma Organisation activa e uma Membership Owner na primeira utilização, permitir edição mínima da empresa e bloquear a criação de uma segunda empresa na experiência do MVP.

Pré-requisitos:
- Organisation e Membership já existem desde PR02;
- autenticação concluída;
- auditoria disponível;
- frontend autenticado funcional.

Contexto obrigatório:
Lê apenas:
- docs/gestao/03_fase_1_mvp/01_backlog.md: MVP-03;
- docs/gestao/02_fase_0_preparacao/artefactos/08_modelo_utilizadores_empresas.md;
- docs/gestao/02_fase_0_preparacao/artefactos/10_requisitos_seguranca_mvp.md: evento da empresa;
- implementação actual.

Não recries:
- Organisation;
- Membership;
- respectivas migrações estruturais iniciais.

Migrações adicionais só são permitidas se forem indispensáveis para comportamento não previsível em PR02 e devem ser justificadas.

Implementa:
- detecção de utilizador autenticado sem Membership activa;
- onboarding com nome mínimo da empresa;
- criação transaccional de Organisation e Membership Owner;
- prevenção de duplicação em pedidos concorrentes;
- bloqueio de segunda empresa por utilizador no MVP;
- consulta da empresa actual;
- edição mínima;
- autorização Owner no backend;
- interface mínima de onboarding;
- interface mínima de dados da empresa;
- auditoria da criação e alteração.

Regras:
- cliente não define livremente o papel;
- Owner é atribuído pelo serviço;
- cliente não escolhe organisation_id operacional;
- associação deve ser validada no servidor;
- selector de empresa, convites e gestão de membros ficam fora do MVP;
- não criar papéis diferenciados;
- não criar produtos.

Validações:
1. primeira entrada sem empresa conduz ao onboarding;
2. onboarding cria Organisation e Membership Owner;
3. operação é transaccional;
4. pedidos duplicados não criam duas empresas;
5. tentativa de segunda empresa é bloqueada;
6. utilizador não autorizado não edita empresa alheia;
7. edição válida é persistida;
8. evento de criação e alteração é auditado;
9. frontend completa o onboarding;
10. testes negativos passam;
11. autenticação e recuperação continuam funcionais.

Fecho e registo:
- cria prompt_10_resultado.md;
- actualiza F1-P02 para 10/11 concluídos;
- actualiza painel e diário.

Expectativa verificável:
- onboarding funciona;
- empresa e Membership Owner são criadas;
- segunda empresa é bloqueada;
- edição mínima é autorizada no backend;
- próximo prompt recomendado: F1-P02-PR11;
- relatório final lista endpoints, serviços, componentes, testes, eventos, problemas e pendências.

Não avances para o prompt seguinte.
```

## Prompt 11 (opus) — Aplicar contexto empresarial e validar isolamento

```prompt
Iteração 11

Actua como especialista em segurança multi-tenant e conclui a pipeline F1-P02.

Identificação:
- Fase: F1 — MVP
- Pipeline: F1-P02
- Prompt: F1-P02-PR11
- Itens: MVP-03 e semente de MVP-18
- Capacidade: MVP-03.C2 e início de MVP-18.C1
- Requisito: MVP-03.R1
- Tarefas: MVP-03.T4 e semente de MVP-18.T1
- Requisitos transversais: RT-01 e RT-02
- Validações: VAL-002 e VAL-012, parciais

Objectivo:
Derivar o contexto de empresa a partir da Membership no servidor, rejeitar pedidos sem Membership e criar a primeira bateria de testes de isolamento entre empresas.

Pré-requisitos:
- PR01 a PR10 concluídos;
- autenticação, empresa, Membership e auditoria funcionais;
- endpoints empresariais existentes.

Contexto obrigatório:
Lê apenas:
- docs/gestao/03_fase_1_mvp/01_backlog.md: MVP-03.R1 e MVP-18.C1;
- docs/gestao/02_fase_0_preparacao/artefactos/08_modelo_utilizadores_empresas.md: IS-01 a IS-04;
- docs/gestao/02_fase_0_preparacao/artefactos/10_requisitos_seguranca_mvp.md: SEC-ISO-01 a SEC-ISO-03 e evento de acesso cruzado;
- implementação actual e resultados anteriores da pipeline.

Implementa contexto empresarial:
- derivado exclusivamente da Membership activa do utilizador autenticado;
- cliente não escolhe organisation_id operacional;
- pedidos autenticados sem Membership são rejeitados;
- queries empresariais são filtradas pela organização do contexto;
- operações por identificador validam a pertença à organização;
- associações futuras devem validar que as entidades pertencem à mesma empresa;
- solução simples e explícita, sem middleware genérico excessivo.

Testes com duas empresas:
- cria utilizadores e empresas através de factories ou fixtures;
- a regra de uma empresa por conta na experiência do MVP não impede cenários técnicos com vários utilizadores e empresas;
- testa leitura cruzada;
- testa alteração cruzada;
- testa tentativa por identificador conhecido;
- testa ausência de Membership;
- testa Membership inactiva;
- testa acesso permitido dentro da própria empresa.

Auditoria:
- tentativas cruzadas relevantes geram o evento definido;
- não registar payloads completos;
- correlation_id presente;
- não revelar se o recurso alheio existe;
- utilizar 403 ou 404 de forma consistente e documentada.

Escopo:
- aplica o contexto apenas aos endpoints actualmente existentes;
- não criar produtos ou módulos de pipelines posteriores;
- não executar ainda a suite completa de MVP-18;
- não declarar VAL-002 completa para módulos que ainda não existem.

Validações:
1. contexto é derivado da Membership;
2. cliente não consegue trocar a empresa por parâmetro;
3. pedido sem Membership é rejeitado;
4. leitura cruzada falha;
5. alteração cruzada falha;
6. tentativa por ID alheio falha;
7. tentativas cruzadas são auditadas;
8. acesso legítimo continua funcional;
9. 100% dos testes de isolamento dos endpoints existentes passam;
10. testes backend, frontend e CI passam;
11. VAL-002 e VAL-012 são actualizadas apenas como parciais, com evidência concreta.

Fecho da pipeline:
- cria prompt_11_resultado.md;
- actualiza F1-P02 para Concluído, 11/11, se todos os critérios forem cumpridos;
- actualiza o painel global;
- acrescenta uma linha ao diário;
- actualiza VAL-002 e VAL-012 como parciais;
- regista bloqueios reais, se existirem;
- não cries automaticamente a pipeline seguinte.

Expectativa verificável:
- contexto empresarial é aplicado no servidor;
- acessos cruzados aos endpoints existentes são rejeitados;
- eventos de segurança são auditados;
- F1-P02 fica Concluída com 11/11 prompts;
- VAL-002 e VAL-012 permanecem parciais;
- próximo passo recomendado: analisar o estado real do repositório e gerar a pipeline F1-P03;
- relatório final apresenta comportamento implementado, testes, evidências, ficheiros alterados, pendências e riscos.

Não avances para o prompt seguinte.
```
