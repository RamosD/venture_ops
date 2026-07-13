# Pipeline: Portefólio e ficha do produto

Base funcional: MVP-04, MVP-05 e mapa just-in-time da F1-P03.  

## Prompt 01 (opus) — Criar o modelo de produto e a migração

```prompt
Iteração 01
Actua como engenheiro backend sénior especializado em Django e PostgreSQL.

Implementa a fundação persistente do portefólio e da ficha administrativa do produto no VentureOps AI.

Identificação:
- Fase: F1 — MVP
- Pipeline: F1-P03 — Portefólio e ficha do produto
- Prompt: F1-P03-PR01
- Itens: MVP-04 e MVP-05, parcialmente
- Capacidades: MVP-04.C1 e MVP-05.C1, parcialmente
- Requisitos: MVP-04.R1, MVP-05.R1 e MVP-05.R3
- Tarefa principal: MVP-04.T1, fundação do modelo
- Requisitos transversais: RT-01, RT-04, RT-09 e RT-10
- Validações preparadas: VAL-002 e VAL-003

Objectivo:
Criar a entidade Product, a primeira migração do módulo de portefólio e os testes estruturais do modelo, reutilizando as convenções reais implementadas em F1-P02.

O resultado verificável deve ser um modelo Product persistente, isolado por Organisation, com os campos da ficha administrativa, estados mínimos e controlo de versão preparado.

Pré-requisitos materiais:
- F1-P02 concluída;
- CustomUser, Organisation, Membership e contexto empresarial existentes;
- UUIDPrimaryKeyModel e OrganisationScopedModel existentes ou convenções equivalentes;
- PostgreSQL e Docker Compose funcionais;
- auditoria append-only disponível;
- suite actual de testes verde.

Contexto obrigatório:
Lê apenas:
- docs/gestao/03_fase_1_mvp/01_backlog.md: MVP-04, MVP-05 e princípios de implementação;
- docs/gestao/03_fase_1_mvp/02_mapa_pipelines.md: F1-P03;
- docs/gestao/02_fase_0_preparacao/artefactos/03_estados_e_transicoes.md: estados do produto;
- docs/gestao/02_fase_0_preparacao/artefactos/04_ficha_administrativa_produto.md;
- docs/gestao/02_fase_0_preparacao/artefactos/08_modelo_utilizadores_empresas.md: isolamento;
- docs/produto/00_decisoes_arranque.md;
- código actual de backend/apps/portfolio, accounts, organisations, audit e common;
- resultados finais de F1-P02-PR11 e F1-P02-PR12.

Inspecção inicial:
1. Confirma o estado real do módulo portfolio.
2. Confirma como UUID, timestamps e organisation são implementados.
3. Confirma a convenção de enums e migrações.
4. Confirma que a árvore de trabalho não contém alterações inesperadas que possam ser sobrescritas.
5. Não assumes nomes de classes ou helpers sem os verificar.

Cria Product com os campos mínimos:

- id, conforme a convenção UUID existente;
- organisation, obrigatória e derivada de OrganisationScopedModel ou equivalente;
- name, obrigatório;
- purpose, obrigatório;
- status, com valores active e archived;
- responsible, relação obrigatória com CustomUser;
- last_reviewed_at, obrigatório após a criação;
- target_audience, opcional;
- phase, opcional;
- next_review_at, opcional;
- notes, opcional;
- version, inteiro positivo iniciado em 1;
- created_at;
- updated_at.

Regras do modelo:
- Product pertence obrigatoriamente a uma Organisation;
- responsável deve ser utilizador com Membership activa na mesma Organisation;
- na criação, o responsável por defeito será o utilizador autenticado, mas essa regra será aplicada pelo serviço/API em PR02;
- status inicial será active;
- last_reviewed_at será inicializado na criação;
- edições comuns não podem actualizar automaticamente last_reviewed_at;
- last_reviewed_at só volta a mudar através da operação explícita “marcar como revisto”, implementada em PR04;
- version suporta concorrência optimista;
- attention_level não deve ser persistido;
- não criar eliminação física do produto;
- não criar estados adicionais;
- não criar fases ou gates de projecto;
- não criar indicadores de portefólio.

Validações de domínio:
- name e purpose não podem ser vazios ou compostos apenas por espaços;
- normalizar apenas espaços exteriores, sem alterar silenciosamente o conteúdo;
- responsible deve pertencer à mesma Organisation;
- valores inválidos de status são rejeitados;
- campos opcionais permanecem realmente opcionais;
- arquivamento será uma transição, não eliminação.

Não implementar ainda:
- endpoints;
- serializers;
- serviços CRUD;
- interface frontend;
- arquivo/reactivação;
- filtros;
- paginação;
- operação marcar como revisto;
- agregados de documentos, decisões, pendências ou execuções;
- regras de atenção.

Migração:
- cria a migração inicial do módulo portfolio;
- deve aplicar numa base vazia e na base de desenvolvimento existente;
- deve ser reversível;
- não deve alterar migrações históricas;
- verifica drift com makemigrations --check --dry-run.

Testes obrigatórios:
1. Product exige Organisation;
2. Product exige name;
3. Product exige purpose;
4. status inicial é active;
5. version inicial é 1;
6. last_reviewed_at é inicializado na criação;
7. campos opcionais aceitam null ou vazio conforme a política adoptada;
8. responsible da mesma Organisation é aceite;
9. responsible de outra Organisation é rejeitado pelo domínio;
10. status inválido é rejeitado;
11. attention_level não existe como campo persistido;
12. migração aplica e reverte;
13. suite anterior permanece verde.

Regras gerais:
- reutiliza padrões reais de F1-P02;
- não cries BaseProduct, repository pattern ou serviço genérico;
- não introduzas novas dependências sem necessidade;
- não alteres autenticação, empresa, rate limiting ou armazenamento;
- não alteres artefactos da Fase 0;
- não avances para funcionalidades de F1-P04.

Fecho e registo:
- cria docs/gestao/03_fase_1_mvp/pipelines/03_portefolio_ficha_produto/resultados_execucao/prompt_01_resultado.md;
- adiciona ou actualiza F1-P03 em docs/gestao/01_status_pipelines.md como Em execução, 1/6 concluído;
- actualiza o painel global com o próximo prompt;
- acrescenta uma linha curta ao diário;
- não cries decisão global salvo desvio estrutural real.

Expectativa verificável:
- Product e a sua migração existem;
- isolamento estrutural por Organisation está aplicado;
- todos os campos da ficha estão representados;
- last_reviewed_at não está ligado automaticamente a qualquer edição;
- testes de modelo e migração passam;
- nenhuma API ou UI foi antecipada;
- próximo prompt recomendado: F1-P03-PR02;
- o relatório indica ficheiros, migrações, comandos, testes, decisões, problemas e pendências.

Não avances para o prompt seguinte.
```

## Prompt 02 (opus) — Implementar a API CRUD isolada e auditada

```prompt
Iteração 02
Actua como engenheiro backend sénior especializado em Django REST Framework, isolamento multi-tenant e concorrência optimista.

Implementa a API inicial do portefólio de produtos sobre o modelo criado em F1-P03-PR01.

Identificação:
- Fase: F1 — MVP
- Pipeline: F1-P03
- Prompt: F1-P03-PR02
- Item: MVP-04
- Capacidade: MVP-04.C1
- História: MVP-04.H1, parcialmente
- Requisitos: MVP-04.R1 e MVP-04.R3
- Tarefas: MVP-04.T1 e MVP-04.T5, parcialmente
- Requisitos transversais: RT-01, RT-02, RT-09 e RT-10
- Validações: VAL-002, VAL-003 e VAL-012, parcialmente

Objectivo:
Implementar criação, listagem, consulta e edição de produtos, com contexto empresarial derivado no servidor, autorização Owner, concorrência optimista e auditoria.

O resultado verificável deve permitir criar um produto informando apenas name e purpose, consultá-lo e editá-lo sem risco de acesso cruzado ou sobrescrita silenciosa.

Pré-requisitos:
- PR01 concluído;
- Product e migração existentes;
- require_context e padrão de acesso cruzado de F1-P02 existentes;
- autenticação, Membership e auditoria funcionais;
- suite actual verde.

Contexto obrigatório:
Lê apenas:
- docs/gestao/03_fase_1_mvp/01_backlog.md: MVP-04 e MVP-05.H1;
- docs/gestao/02_fase_0_preparacao/artefactos/04_ficha_administrativa_produto.md;
- implementação actual de portfolio, organisations/context.py, audit e API de organisation;
- enum AuditAction e lista fechada de eventos;
- resultado de F1-P03-PR01.

Implementa os endpoints:

- GET /api/v1/products
- POST /api/v1/products
- GET /api/v1/products/{product_id}
- PATCH /api/v1/products/{product_id}

Não implementar DELETE.

Criação:
- cliente envia obrigatoriamente apenas name e purpose;
- campos opcionais podem ser enviados, mas não são obrigatórios;
- organisation é derivada da Membership activa;
- responsible é definido no servidor como request.user por defeito;
- status é active;
- last_reviewed_at é definido no momento da criação;
- version é 1;
- o cliente não pode definir organisation;
- o cliente não pode atribuir responsável de outra empresa;
- criação é transaccional.

Consulta e listagem:
- devolvem apenas produtos da Organisation do contexto;
- Product de outra Organisation deve ser indistinguível de um identificador inexistente;
- pedido autenticado sem Membership activa deve ser rejeitado;
- resposta inclui version;
- listagem inicial pode ser simples; filtros e paginação completos entram em PR04.

Edição:
- PATCH exige expected_version ou campo version equivalente;
- usa transacção e bloqueio ou actualização condicional para evitar lost update;
- se a versão fornecida não corresponder à versão actual, devolver 409;
- alteração válida incrementa version exactamente uma vez;
- edição comum não actualiza last_reviewed_at;
- organisation nunca é alterável;
- status não deve ser alterado pelo PATCH comum;
- arquivo e reactivação entram em PR04;
- Product archived não pode ser editado pelo PATCH comum;
- campos desconhecidos ou proibidos são rejeitados.

Responsável:
- no MVP individual, o responsável por defeito é o utilizador actual;
- caso a API permita alteração de responsável, só aceita utilizador com Membership activa na mesma Organisation;
- não criar interface multiutilizador;
- não criar convites ou selector de membros.

Auditoria:
- inspecciona a lista fechada AuditAction;
- utiliza apenas eventos já aprovados;
- não acrescenta eventos fora da lista fechada;
- audita criação e alteração do produto;
- se existir uma acção genérica de produto, indica a operação nos metadados mínimos;
- metadados devem conter apenas identificadores, operação e nomes dos campos alterados;
- não registar purpose ou notes completos;
- tentativas de acesso cruzado usam o evento de segurança já existente.

Tratamento de erros:
- 400 para validação;
- 401 para ausência de autenticação;
- 403 para ausência de contexto autorizado;
- 404 para produto inexistente ou de outra Organisation;
- 409 para conflito de versão ou estado incompatível;
- sem stack trace ou detalhes internos.

Testes obrigatórios:
1. Owner cria produto apenas com name e purpose;
2. defaults são aplicados no servidor;
3. organização não pode ser escolhida pelo cliente;
4. listagem contém apenas produtos da empresa actual;
5. detalhe próprio funciona;
6. produto alheio devolve 404;
7. tentativa cruzada é auditada;
8. edição válida incrementa version;
9. edição com versão obsoleta devolve 409;
10. edição comum não altera last_reviewed_at;
11. produto archived não pode ser editado;
12. responsável alheio é rejeitado;
13. criação e edição são auditadas;
14. conteúdo integral da ficha não entra na auditoria;
15. regressão de autenticação, onboarding e isolamento permanece verde.

Não implementar:
- interface frontend;
- arquivo/reactivação;
- filtros completos;
- paginação;
- marcar como revisto;
- regras de atenção;
- documentos ou agregados futuros.

Fecho e registo:
- cria prompt_02_resultado.md na pasta de resultados de F1-P03;
- actualiza F1-P03 para 2/6 concluídos;
- actualiza painel e diário;
- acrescenta evidência parcial a VAL-003 apenas se materialmente demonstrada;
- mantém VAL-002 e VAL-012 parciais, acrescentando apenas evidência do módulo Product.

Expectativa verificável:
- API CRUD inicial funciona;
- criação exige apenas name e purpose;
- isolamento e autorização são aplicados no backend;
- concorrência optimista devolve 409 em versão obsoleta;
- operações são auditadas sem conteúdo sensível;
- testes passam;
- próximo prompt recomendado: F1-P03-PR03;
- relatório final lista contratos, serviços, testes, eventos, problemas e pendências.

Não avances para o prompt seguinte.
```

## Prompt 03 (sonnet) — Criar a interface inicial do portefólio

```prompt
Iteração 03
Actua como engenheiro frontend sénior em React e TypeScript.

Implementa a interface inicial do portefólio de produtos, integrada com a API criada em F1-P03-PR02.

Identificação:
- Fase: F1 — MVP
- Pipeline: F1-P03
- Prompt: F1-P03-PR03
- Itens: MVP-04 e MVP-05, parcialmente
- Capacidades: MVP-04.C1, MVP-04.C2 e MVP-05.C1, parcialmente
- Histórias: MVP-04.H1, MVP-04.H2 e MVP-05.H1, parcialmente
- Tarefa: MVP-04.T2
- Validação: VAL-003, parcialmente

Objectivo:
Criar uma interface funcional para listar, criar, consultar e editar produtos, usando o cliente HTTP central e os padrões de autenticação e OrganisationGate existentes.

O resultado verificável deve permitir ao utilizador autenticado criar um produto escrevendo apenas nome e propósito, vê-lo no portefólio e editar a sua ficha básica.

Pré-requisitos:
- PR01 e PR02 concluídos;
- API Product funcional;
- AuthContext, OrganisationGate e cliente HTTP central existentes;
- frontend actual verde.

Contexto obrigatório:
Lê apenas:
- docs/gestao/03_fase_1_mvp/01_backlog.md: MVP-04.T2 e MVP-05.H1;
- docs/gestao/02_fase_0_preparacao/artefactos/04_ficha_administrativa_produto.md;
- componentes actuais de autenticação e empresa;
- cliente HTTP central;
- contratos reais implementados no backend em PR02;
- resultados de PR01 e PR02.

Implementa uma área de portefólio depois do onboarding empresarial.

Componentes mínimos:
- PortfolioWorkspace ou equivalente;
- ProductList;
- ProductCreateForm;
- ProductEditForm;
- ProductDetail ou ficha de visão geral;
- estados de carregamento, vazio e erro.

Listagem:
- apresenta nome;
- estado;
- responsável;
- data da última revisão;
- versão, apenas se útil para controlo técnico, sem destaque desnecessário;
- permite seleccionar um produto;
- não inventa métricas ou nível de atenção.

Criação:
- exige visualmente apenas Nome e Propósito;
- não obriga o utilizador a escolher estado, responsável ou data de revisão;
- defaults são aplicados pelo backend;
- campos opcionais podem ficar fora do formulário inicial ou numa área claramente opcional;
- evita submissão duplicada;
- após sucesso, actualiza a lista e abre a ficha criada.

Edição:
- permite editar name, purpose e campos opcionais suportados;
- envia a version actual;
- trata 409 como conflito de edição;
- perante conflito, informa que o produto foi alterado e oferece recarregar os dados;
- não substitui silenciosamente a versão do servidor;
- edição comum não deve apresentar que o produto foi “revisto”.

Integração:
- reutiliza o cliente HTTP central;
- mantém sessão por cookie e CSRF;
- não cria outro cliente HTTP;
- não cria store global complexa;
- não introduz router apenas para esta funcionalidade, salvo necessidade demonstrada;
- mantém a experiência existente de perfil e empresa.

Não implementar ainda:
- arquivar/reactivar;
- filtros completos;
- paginação visual;
- botão marcar como revisto;
- documentos, decisões, pendências ou execuções;
- indicadores de atenção;
- pesquisa.

Testes obrigatórios:
1. estado vazio do portefólio;
2. listagem de produtos;
3. criação com name e purpose;
4. defaults apresentados depois da criação;
5. selecção e detalhe;
6. edição válida;
7. conflito 409 apresentado sem sobrescrita;
8. erro da API tratado;
9. submissão duplicada evitada;
10. autenticação, perfil e empresa continuam funcionais;
11. build e testes frontend passam.

Validação ao vivo:
- autenticar;
- concluir ou reutilizar onboarding;
- criar um produto real de teste;
- abrir a ficha;
- editar o propósito;
- confirmar que a versão aumentou;
- confirmar que last_reviewed_at não mudou na edição comum.

Fecho e registo:
- cria prompt_03_resultado.md;
- actualiza F1-P03 para 3/6 concluídos;
- actualiza painel e diário;
- acrescenta evidência parcial a VAL-003.

Expectativa verificável:
- portefólio é utilizável pela interface;
- produto pode ser criado com dois campos;
- ficha básica pode ser consultada e editada;
- conflitos não provocam sobrescrita silenciosa;
- funcionalidades futuras não foram antecipadas;
- próximo prompt recomendado: F1-P03-PR04;
- relatório final lista componentes, contratos, testes, demonstração, problemas e pendências.

Não avances para o prompt seguinte.
```

## Prompt 04 (opus) — Implementar ciclo de vida, revisão, filtros e paginação

```prompt
Iteração 04
Actua como engenheiro backend sénior especializado em regras de negócio, concorrência e APIs Django REST Framework.

Completa o comportamento backend do portefólio e da ficha administrativa.

Identificação:
- Fase: F1 — MVP
- Pipeline: F1-P03
- Prompt: F1-P03-PR04
- Itens: MVP-04 e MVP-05
- Capacidades: MVP-04.C1, MVP-04.C2 e MVP-05.C1
- Histórias: MVP-04.H1, MVP-04.H2 e operação explícita de revisão
- Requisitos: MVP-04.R1, MVP-04.R2, MVP-04.R3, MVP-05.R1 e MVP-05.R3
- Tarefas: MVP-04.T3, MVP-04.T4, MVP-04.T5 e MVP-05.T4
- Requisitos transversais: RT-01, RT-02, RT-08 e RT-10
- Validações: VAL-002, VAL-003 e VAL-012

Objectivo:
Implementar arquivo e reactivação, filtros, paginação, ordenação e a operação explícita “marcar como revisto”, preservando concorrência optimista, isolamento e auditoria.

Pré-requisitos:
- PR01 a PR03 concluídos;
- API e frontend básicos funcionais;
- version existente em Product;
- auditoria e contexto empresarial funcionais.

Contexto obrigatório:
Lê apenas:
- docs/gestao/03_fase_1_mvp/01_backlog.md: MVP-04 e MVP-05;
- docs/gestao/02_fase_0_preparacao/artefactos/03_estados_e_transicoes.md;
- docs/gestao/02_fase_0_preparacao/artefactos/04_ficha_administrativa_produto.md;
- docs/gestao/02_fase_0_preparacao/artefactos/06_regras_visao_atencao.md: apenas relação com last_reviewed_at;
- DEC-20260712-05, apenas a clarificação da revisão explícita;
- implementação actual do módulo portfolio e audit;
- resultados de PR01 a PR03.

Implementa transições:

1. active → archived
2. archived → active

Endpoints recomendados:
- POST /api/v1/products/{product_id}/archive
- POST /api/v1/products/{product_id}/reactivate
- POST /api/v1/products/{product_id}/mark-reviewed

Podes ajustar os caminhos às convenções reais, mantendo contratos claros e separados.

Todas as operações:
- exigem expected_version;
- são atómicas;
- validam a versão;
- incrementam version exactamente uma vez;
- validam a Organisation;
- devolvem 409 em versão obsoleta;
- são auditadas;
- não aceitam organisation do cliente.

Arquivo:
- não elimina dados;
- produto já archived não pode ser arquivado novamente;
- produto archived não pode ser editado nem marcado como revisto;
- arquivo não actualiza last_reviewed_at.

Reactivação:
- apenas produto archived pode ser reactivado;
- não actualiza last_reviewed_at;
- preserva todos os dados;
- não cria nova entidade.

Marcar como revisto:
- apenas produto active;
- actualiza last_reviewed_at para o instante da operação;
- incrementa version;
- é acção explícita separada da edição;
- não altera purpose, notes ou outros campos;
- deve ser auditada sem guardar conteúdo integral;
- edições normais continuam sem actualizar last_reviewed_at.

Filtros e paginação:
- GET /api/v1/products suporta filtro por status;
- suporta filtro por responsible;
- suporta paginação simples e determinística;
- define tamanho inicial razoável e limite máximo;
- ordenação inicial estável, preferencialmente por updated_at descendente e id como desempate;
- por defeito, apresenta produtos active;
- permite pedir archived ou todos através de valor explícito;
- não criar pesquisa textual nesta fase;
- filtros não podem atravessar empresas.

Validação dos campos opcionais:
- target_audience;
- phase;
- next_review_at;
- notes.

Não acrescentes obrigatoriedade ou taxonomias não aprovadas.

Auditoria:
- usa apenas AuditAction existente;
- audita criação, edição, arquivo, reactivação e revisão conforme a lista fechada;
- se a lista usar uma acção agregada, identifica a operação nos metadados mínimos;
- regista apenas nomes de campos alterados e transições;
- não regista purpose ou notes completos.

Testes obrigatórios:
1. active pode ser archived;
2. archived não pode ser arquivado novamente;
3. archived pode ser reactivado;
4. active não pode ser reactivado;
5. versão obsoleta falha em cada comando;
6. arquivo não apaga o produto;
7. arquivo não altera last_reviewed_at;
8. reactivação não altera last_reviewed_at;
9. edição comum não altera last_reviewed_at;
10. mark-reviewed altera last_reviewed_at;
11. mark-reviewed incrementa version;
12. archived não pode ser marcado como revisto;
13. filtro active funciona;
14. filtro archived funciona;
15. filtro por responsável funciona;
16. paginação é estável;
17. filtro não expõe produtos de outra empresa;
18. operações de ciclo de vida são auditadas;
19. conteúdo integral não entra na auditoria;
20. migrações não apresentam drift;
21. suite anterior permanece verde.

Concorrência:
- acrescenta pelo menos um teste real em PostgreSQL com duas actualizações usando a mesma version;
- exactamente uma deve ser aceite;
- a outra deve receber conflito;
- não deve haver lost update.

Não implementar:
- regras de atenção;
- revisão periódica automática;
- notificações;
- pesquisa;
- eliminação física;
- agregados de módulos futuros.

Fecho e registo:
- cria prompt_04_resultado.md;
- actualiza F1-P03 para 4/6 concluídos;
- actualiza painel e diário;
- acrescenta evidência real a VAL-003, VAL-002 e VAL-012, sem as declarar completas prematuramente.

Expectativa verificável:
- ciclo active/archived funciona;
- produtos não são eliminados;
- revisão só ocorre por acção explícita;
- filtros e paginação funcionam dentro da empresa;
- concorrência optimista está demonstrada;
- auditoria cobre as operações;
- próximo prompt recomendado: F1-P03-PR05;
- relatório final indica endpoints, regras, testes, concorrência, eventos e pendências.

Não avances para o prompt seguinte.
```

## Prompt 05 (sonnet) — Completar a experiência da ficha e do portefólio

```prompt
Iteração 05
Actua como engenheiro frontend sénior e completa a experiência de utilização do portefólio e da ficha administrativa.

Identificação:
- Fase: F1 — MVP
- Pipeline: F1-P03
- Prompt: F1-P03-PR05
- Itens: MVP-04 e MVP-05
- Capacidades: MVP-04.C1, MVP-04.C2 e MVP-05.C1
- Histórias: MVP-04.H1, MVP-04.H2 e MVP-05.H1
- Tarefas: MVP-04.T2, MVP-04.T3, MVP-04.T4 e MVP-05.T1 a MVP-05.T4
- Validação: VAL-003

Objectivo:
Completar a interface do portefólio com filtros, paginação, arquivo, reactivação, campos opcionais da ficha e operação explícita “marcar como revisto”.

Pré-requisitos:
- PR01 a PR04 concluídos;
- contratos backend de ciclo de vida, revisão e paginação disponíveis;
- interface básica de PR03 funcional;
- cliente HTTP central, autenticação e OrganisationGate funcionais.

Contexto obrigatório:
Lê apenas:
- docs/gestao/03_fase_1_mvp/01_backlog.md: MVP-04 e MVP-05;
- docs/gestao/02_fase_0_preparacao/artefactos/04_ficha_administrativa_produto.md;
- contratos reais implementados em PR04;
- componentes existentes do portefólio;
- cliente HTTP central;
- resultados de PR03 e PR04.

Completa a lista:
- filtros por estado: activos, arquivados e todos;
- filtro por responsável, sem criar gestão multiutilizador;
- paginação;
- estados vazio, carregamento e erro;
- apresentação de nome, estado, responsável e última revisão;
- ordem coerente com a API;
- preservação simples dos filtros durante a sessão da interface.

Completa a ficha:
- name;
- purpose;
- status, apenas leitura no formulário normal;
- responsible, conforme o escopo individual;
- last_reviewed_at, apenas leitura;
- target_audience;
- phase;
- next_review_at;
- notes;
- version usada internamente para concorrência.

Não mostrar attention_level persistido ou calculado nesta pipeline.

Acções:
- editar;
- arquivar;
- reactivar;
- marcar como revisto;
- recarregar dados após conflito.

Regras de UX:
- arquivar exige confirmação explícita;
- reactivar exige acção explícita;
- marcar como revisto deve explicar que confirma uma revisão real da ficha;
- editar e guardar não pode ser apresentado como revisão;
- last_reviewed_at só muda visualmente depois da acção marcar como revisto;
- produto archived deve apresentar estado claro e impedir edição normal;
- conflito 409 nunca deve sobrescrever os dados do servidor;
- perante conflito, oferecer recarregar a versão actual;
- evitar modais e abstracções complexas quando uma confirmação simples for suficiente.

Vistas agregadas progressivas:
- não criar dados falsos de documentos, decisões, pendências ou execuções;
- não criar APIs para módulos ainda inexistentes;
- a ficha pode reservar uma estrutura simples para essas áreas, mas deve indicar claramente que ainda não possuem dados ou integração;
- não criar contagens simuladas.

Integração:
- reutiliza o cliente HTTP central;
- mantém CSRF e sessão;
- não cria store global complexa;
- não adiciona biblioteca de UI sem justificação;
- não cria router apenas para esta funcionalidade, salvo necessidade demonstrada.

Testes obrigatórios:
1. filtro de activos;
2. filtro de arquivados;
3. filtro de todos;
4. paginação;
5. arquivo com confirmação;
6. produto arquivado deixa de ser editável;
7. reactivação;
8. marcação explícita como revisto;
9. edição comum não muda a data de revisão apresentada;
10. conflito 409 permite recarregar;
11. campos opcionais são editáveis;
12. estado e responsável são apresentados correctamente;
13. nenhum agregado futuro é simulado;
14. autenticação, perfil e empresa continuam funcionais;
15. build e suite frontend passam.

Demonstração ao vivo:
- autenticar;
- abrir portefólio;
- criar pelo menos dois produtos;
- editar um produto;
- marcar explicitamente como revisto;
- arquivar;
- filtrar arquivados;
- reactivar;
- confirmar os estados no backend e frontend.

Fecho e registo:
- cria prompt_05_resultado.md;
- actualiza F1-P03 para 5/6 concluídos;
- actualiza painel e diário;
- acrescenta evidência de UI a VAL-003.

Expectativa verificável:
- portefólio completo é utilizável pela interface;
- produtos podem ser filtrados, paginados, arquivados e reactivados;
- ficha mínima e campos opcionais estão disponíveis;
- revisão explícita está separada da edição;
- testes e demonstração passam;
- próximo prompt recomendado: F1-P03-PR06;
- relatório final lista componentes, contratos, testes, demonstração, problemas e pendências.

Não avances para o prompt seguinte.
```

## Prompt 06 (opus) — Validar o fluxo integrado e encerrar F1-P03

```prompt
Iteração 06
Actua como revisor técnico sénior e conclui a pipeline F1-P03 através de validação integrada, correcção de defeitos concretos e fecho de governação.

Identificação:
- Fase: F1 — MVP
- Pipeline: F1-P03 — Portefólio e ficha do produto
- Prompt: F1-P03-PR06
- Itens: MVP-04 e MVP-05
- Validações principais: VAL-003
- Validações reforçadas: VAL-002 e VAL-012
- Tipo: integração, hardening delimitado e fecho

Objectivo:
Validar ponta a ponta o portefólio e a ficha administrativa, confirmar isolamento, concorrência, auditoria e experiência de utilização, corrigindo apenas defeitos encontrados.

Não criar novas funcionalidades e não iniciar F1-P04.

Pré-requisitos:
- PR01 a PR05 concluídos;
- Product, API e frontend completos;
- suite anterior verde;
- Docker Compose funcional.

Contexto obrigatório:
Lê apenas:
- docs/gestao/03_fase_1_mvp/01_backlog.md: critérios de conclusão de MVP-04 e MVP-05;
- docs/gestao/04_matriz_validacao_global.md: VAL-002, VAL-003 e VAL-012;
- código actual de portfolio;
- componentes frontend do portefólio;
- resultados de PR01 a PR05;
- estado actual de status, painel e diário.

Executa o cenário integrado:

1. iniciar a aplicação numa base limpa;
2. criar a conta inicial de forma segura;
3. autenticar;
4. concluir onboarding;
5. criar Produto A apenas com name e purpose;
6. confirmar defaults;
7. criar Produto B;
8. listar os dois produtos;
9. editar campos da ficha do Produto A;
10. confirmar que last_reviewed_at não muda;
11. marcar Produto A como revisto;
12. confirmar que last_reviewed_at muda;
13. provocar conflito com version obsoleta;
14. confirmar resposta 409 e ausência de lost update;
15. arquivar Produto B;
16. confirmar que não pode ser editado;
17. filtrar arquivados;
18. reactivar Produto B;
19. confirmar paginação e ordem;
20. verificar eventos de auditoria;
21. exportar ou inspeccionar apenas os dados necessários para confirmar o comportamento, sem criar funcionalidade de exportação do MVP-19.

Isolamento:
- usa duas empresas e utilizadores de teste;
- confirma que listagem não mistura empresas;
- confirma que detalhe alheio devolve 404;
- confirma que edição alheia falha;
- confirma que arquivo, reactivação e revisão alheios falham;
- confirma auditoria das tentativas cruzadas;
- não declara VAL-002 completa para módulos ainda inexistentes.

Concorrência:
- executa o teste concorrente de edição pelo menos três vezes;
- confirma que uma actualização vence e a outra recebe conflito;
- não aceita testes instáveis;
- corrige apenas problemas reais encontrados.

Auditoria:
- confirma criação;
- edição;
- arquivo;
- reactivação;
- marcação como revisto;
- tentativa cruzada;
- correlation_id;
- ausência de purpose e notes completos nos metadados;
- não declara VAL-012 completa, pois a consolidação global pertence a F1-P07.

Migrações:
- makemigrations --check --dry-run sem drift;
- aplicar numa base vazia;
- aplicar sobre base existente;
- reverter e reaplicar a migração de portfolio quando seguro;
- confirmar preservação dos dados fora do módulo.

Regressão:
- suite backend completa;
- suite frontend completa;
- build frontend;
- health live e ready;
- login;
- recuperação;
- perfil;
- onboarding;
- isolamento;
- armazenamento;
- auditoria append-only;
- Docker Compose.

VAL-003:
Só marcar como Validada quando houver evidência de:
- vários produtos geríveis;
- criação com ficha mínima;
- consulta e edição;
- arquivo e reactivação;
- filtros e paginação;
- revisão explícita;
- isolamento;
- controlo de concorrência;
- UI funcional;
- testes e demonstração.

Não validar nesta pipeline:
- agregados reais de documentos, decisões, pendências e execuções;
- atenção;
- pesquisa;
- funcionalidades de F1-P04+.

Correcções permitidas:
- defeitos de validação;
- falhas de autorização;
- inconsistências de contratos;
- problemas de concorrência;
- erros de UI;
- testes insuficientes;
- documentação técnica directamente afectada.

Não permitir:
- refactorização ampla;
- redesign;
- novos módulos;
- bibliotecas sem necessidade;
- hardening especulativo;
- criação automática de F1-P04.

Governança:
1. cria prompt_06_resultado.md;
2. actualiza F1-P03 para Concluída, 6/6, se todos os critérios passarem;
3. define estado de revisão conforme o guia vigente;
4. actualiza VAL-003 com evidências;
5. mantém VAL-002 e VAL-012 parciais, acrescentando evidência do módulo Product;
6. actualiza painel e diário com registo curto;
7. não altera artefactos da Fase 0;
8. não cria decisão global salvo desvio estrutural real.

O resultado deve incluir:
- veredicto;
- comportamento implementado;
- contratos finais;
- campos finais de Product;
- estados e transições;
- política de revisão;
- política de concorrência;
- isolamento;
- auditoria;
- migrações;
- testes backend e frontend;
- demonstração ponta a ponta;
- VAL actualizadas;
- ficheiros alterados;
- problemas corrigidos;
- reservas;
- estado final da pipeline;
- próximo passo recomendado.

Expectativa verificável:
- F1-P03 está Concluída com 6/6 prompts;
- VAL-003 está Validada, se toda a evidência material existir;
- VAL-002 e VAL-012 permanecem parciais;
- portefólio e ficha são utilizáveis no browser;
- nenhuma funcionalidade de F1-P04 foi antecipada;
- próximo passo recomendado: efectuar commit de F1-P03 e gerar F1-P04 just-in-time.

Não avances para F1-P04.
```
