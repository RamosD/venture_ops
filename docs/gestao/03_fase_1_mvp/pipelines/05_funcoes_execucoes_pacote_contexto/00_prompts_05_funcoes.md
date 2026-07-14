A pipeline cobre `MVP-10`, `MVP-11` e `MVP-12`: funções organizacionais reutilizáveis, execuções com snapshots e versões exactas, e pacote de contexto com as sete secções e aplicação efectiva de `export_policy`.   

# Pipeline: Funções, execuções e pacote de contexto

## Prompt 01 (opus) — Implementar o catálogo de funções organizacionais

```prompt
Iteração 01
Actua como engenheiro full-stack sénior especializado em Django, React, modelação de domínio e isolamento multi-tenant.

Implementa a gestão de funções organizacionais do VentureOps AI.

Identificação:
- Fase: F1 — MVP
- Pipeline: F1-P05 — Funções, execuções e pacote de contexto
- Prompt: F1-P05-PR01
- Item: MVP-10
- Capacidade: MVP-10.C1
- Histórias: MVP-10.H1 e MVP-10.H2
- Tarefas: MVP-10.T1, MVP-10.T2, MVP-10.T3 e MVP-10.T4
- Requisitos transversais: RT-01, RT-02, RT-04, RT-09 e RT-10
- Validação preparada: VAL-007

Condição de entrada:
- confirma que F1-P04 está Concluída, 6/6;
- confirma que o commit de F1-P04 existe ou que a árvore de trabalho não contém alterações não relacionadas;
- se existir defeito estrutural pendente em F1-P04, não alteres código e regista o bloqueio;
- não corrijas silenciosamente módulos anteriores.

Objectivo:
Criar um catálogo empresarial de funções humanas, de IA e híbridas, reutilizáveis em execuções futuras, com instruções documentais opcionais, ciclo Activa/Inactiva, concorrência optimista, isolamento, auditoria e interface funcional.

Contexto obrigatório:
Lê apenas:
- docs/gestao/03_fase_1_mvp/01_backlog.md: MVP-10;
- docs/gestao/03_fase_1_mvp/02_mapa_pipelines.md: F1-P05;
- docs/gestao/02_fase_0_preparacao/artefactos/02_fluxo_e_modelo_funcional.md: função organizacional;
- docs/gestao/02_fase_0_preparacao/artefactos/03_estados_e_transicoes.md: função Activa/Inactiva;
- docs/gestao/02_fase_0_preparacao/artefactos/05_fonte_de_verdade_bd_markdown.md;
- resultado final de F1-P04-PR06;
- código actual de functions, documents, organisations, audit e frontend;
- lista fechada AuditAction.

Inspecção inicial:
1. Confirma as convenções reais de UUID, timestamps, OrganisationScopedModel, version e erros 400/403/404/409.
2. Confirma os contratos reais de Document e DocumentVersion.
3. Confirma o tipo documental exacto instrucoes.
4. Confirma os eventos de auditoria disponíveis para funções.
5. Não assumes nomes de classes ou endpoints sem inspeccionar o código.

Cria FunctionProfile com:
- id UUID;
- organisation obrigatória;
- name obrigatório;
- actor_type fechado: human, ai ou hybrid;
- purpose obrigatório;
- responsibilities, texto obrigatório;
- constraints, texto opcional;
- instruction_document opcional;
- requires_approval;
- status: active ou inactive;
- version para concorrência optimista;
- created_at;
- updated_at.

Regras:
- função organizacional não é papel de autorização;
- função nasce active;
- não existe eliminação física;
- name, purpose e responsibilities não podem estar vazios nem conter apenas espaços;
- instruction_document, quando indicado, pertence à mesma Organisation;
- instruction_document tem obrigatoriamente document_type=instrucoes;
- instruction_document deve ser empresarial, sem associação exclusiva a um Product, porque a função é reutilizável;
- instruction_document deve possuir current_version válida;
- actor_type inválido é rejeitado;
- função inactive não é seleccionável em novas execuções;
- execuções passadas continuarão a preservar a referência e o snapshot;
- status não pode ser alterado pelo PATCH comum;
- inactivação e reactivação são operações explícitas;
- todas as mutações usam expected_version;
- versão obsoleta devolve 409;
- nenhum DELETE é disponibilizado.

Política requires_approval:
- para actor_type=ai ou hybrid, requires_approval é obrigatoriamente true no MVP;
- para actor_type=human, o valor por defeito pode ser false;
- este campo nunca pode enfraquecer a validação humana obrigatória de resultados de IA;
- documenta a política no resultado, sem criar mecanismo genérico de políticas.

API mínima:
- GET /api/v1/functions
- POST /api/v1/functions
- GET /api/v1/functions/{id}
- PATCH /api/v1/functions/{id}
- POST /api/v1/functions/{id}/deactivate
- POST /api/v1/functions/{id}/reactivate

Listagem:
- apenas funções da empresa do contexto;
- filtros status e actor_type;
- paginação e ordenação determinística;
- por defeito apresenta funções active;
- permite all e inactive explicitamente.

Edição:
- permite name, actor_type, purpose, responsibilities, constraints, instruction_document e requires_approval;
- exige expected_version;
- incrementa version exactamente uma vez;
- não altera status;
- função inactive pode ser consultada, mas a política de edição deve ser simples e explicitamente definida;
- recomendação: permitir edição de função inactive sem a tornar activa, preservando a separação entre conteúdo e estado.

Ciclo:
- active → inactive;
- inactive → active;
- transição inválida devolve 409;
- inactivação não elimina relações históricas;
- reactivação não cria nova entidade.

Auditoria:
- usa apenas as acções existentes da lista fechada;
- criação, alteração, inactivação e reactivação são auditadas;
- metadados incluem operação, actor_type, transição e nomes dos campos;
- nunca registar purpose, responsibilities, constraints ou instruções integrais;
- acesso cruzado usa security.cross_org_attempt.

Frontend:
- cria uma área empresarial “Funções” dentro da área autenticada, sem novo router obrigatório;
- lista funções;
- filtros por estado e tipo;
- criação e edição;
- selecção opcional de documento de instruções;
- inactivação com confirmação;
- reactivação explícita;
- função inactive claramente identificada;
- não criar modelos de funções, políticas avançadas ou gestão de permissões;
- reutiliza cliente HTTP central, sessão e CSRF.

Testes obrigatórios:
1. criação dos três actor_type;
2. actor_type inválido rejeitado;
3. defaults de status e requires_approval;
4. ai e hybrid não aceitam requires_approval=false;
5. human aceita a política definida;
6. documento instrucoes da mesma empresa aceite;
7. documento de outro tipo rejeitado;
8. documento de outra empresa rejeitado;
9. documento ligado exclusivamente a Product rejeitado;
10. documento sem current_version rejeitado;
11. listagem isolada;
12. detalhe alheio devolve 404 e é auditado;
13. edição válida incrementa version;
14. versão obsoleta devolve 409;
15. inactivação funciona;
16. função inactive não é devolvida na lista active;
17. reactivação funciona;
18. transição repetida devolve 409;
19. nenhum DELETE;
20. auditoria não contém texto integral;
21. UI cria, edita, inactiva e reactiva;
22. build e suites passam;
23. migração aplica, reverte em base controlada e não apresenta drift.

Não implementar:
- execuções;
- snapshot;
- pacote de contexto;
- chamada a modelos;
- resultados;
- aprovação;
- templates de função;
- permissões por função.

Fecho:
- cria docs/gestao/03_fase_1_mvp/pipelines/05_funcoes_execucoes_pacote_contexto/resultados_execucao/prompt_01_resultado.md;
- actualiza F1-P05 como Em execução, 1/6 concluído;
- actualiza painel, diário e matriz apenas com evidência real;
- VAL-007 permanece parcial até uma função ser utilizada numa execução;
- não cria decisão global salvo desvio estrutural real.

Expectativa verificável:
- FunctionProfile existe;
- API e UI estão funcionais;
- funções active/inactive preservam histórico;
- instruções só podem usar documento válido;
- isolamento, concorrência e auditoria estão demonstrados;
- próximo prompt recomendado: F1-P05-PR02;
- o relatório lista modelo, contratos, regras, migrações, testes, UI, eventos e pendências.

Não avances para o prompt seguinte.
```

## Prompt 02 (opus) — Criar execuções com contexto e snapshots imutáveis

```prompt
Iteração 02
Actua como engenheiro backend sénior especializado em Django, PostgreSQL, snapshots, concorrência e rastreabilidade.

Implementa a fundação de execução assistida do VentureOps AI.

Identificação:
- Fase: F1 — MVP
- Pipeline: F1-P05
- Prompt: F1-P05-PR02
- Item: MVP-11
- Capacidades: MVP-11.C1 e MVP-11.C2
- Histórias: MVP-11.H1 e MVP-11.H2, parcialmente
- Tarefas: MVP-11.T1, MVP-11.T2, MVP-11.T4 e MVP-11.T5
- Requisitos transversais: RT-01, RT-02, RT-03, RT-04, RT-07, RT-09 e RT-10
- Validações preparadas: VAL-007, VAL-008 e VAL-009, parcialmente

Objectivo:
Criar AIExecution e ExecutionContextDocument, permitir criar/listar/consultar execuções em estado Preparada e congelar o contexto através de snapshots e referências a versões documentais exactas.

Não implementar execução automática nem resultados.

Pré-requisitos:
- PR01 concluído;
- Product, FunctionProfile, Document e DocumentVersion funcionais;
- armazenamento e auditoria funcionais;
- função active seleccionável.

Contexto obrigatório:
Lê apenas:
- docs/gestao/03_fase_1_mvp/01_backlog.md: MVP-11;
- artefactos 02, 03, 05 e 07 da Fase 0;
- DEC-F0-FINAL-06;
- implementação real de Product, FunctionProfile, DocumentVersion, contexto empresarial e auditoria;
- resultado de PR01;
- lista AuditAction.

Cria AIExecution com:
- id UUID;
- organisation obrigatória;
- product obrigatório;
- function_profile obrigatório;
- requested_by obrigatório;
- title obrigatório;
- objective obrigatório;
- request_instructions obrigatório;
- constraints opcional;
- expected_output_format obrigatório;
- execution_mode: manual_local ou manual_external;
- status com enumeração oficial completa;
- version para concorrência;
- function_snapshot gerado pelo servidor;
- product_snapshot gerado pelo servidor;
- instruction_version opcional;
- created_at;
- updated_at.

Estados oficiais:
- prepared;
- result_pending_validation;
- approved;
- rejected;
- completed.

Transição de correcção:
- result_pending_validation → prepared.

Implementa a política de transições no domínio:
- prepared → result_pending_validation;
- result_pending_validation → approved;
- result_pending_validation → rejected;
- result_pending_validation → prepared, quando for pedida correcção;
- approved → completed;
- restantes transições são inválidas.

Nesta pipeline:
- criação coloca sempre a execução em prepared;
- não expor endpoint genérico que permita ao cliente escolher estados;
- não implementar ainda importação de resultado, aprovação, rejeição, correcção ou conclusão;
- disponibilizar a política central de transições para ser consumida por F1-P06;
- testes unitários devem demonstrar a matriz, mas os comandos funcionais chegam em F1-P06.

function_snapshot:
- gerado exclusivamente no servidor;
- contém apenas os campos aprovados da função no instante da criação;
- inclui id, name, actor_type, purpose, responsibilities, constraints e requires_approval;
- não pode ser fornecido ou alterado pelo cliente;
- alterações posteriores à função não alteram o snapshot;
- inactivação posterior não invalida a execução existente.

product_snapshot:
- gerado exclusivamente no servidor;
- contém apenas os dados mínimos necessários à secção Produto do pacote;
- inclui identificador, nome, propósito, estado, fase e público-alvo quando existirem;
- não inclui credenciais, email ou dados pessoais desnecessários;
- alterações posteriores ao Product não alteram o snapshot.

instruction_version:
- se FunctionProfile não possuir instruction_document, fica null;
- se possuir, aponta exactamente para a current_version existente no instante da criação;
- o documento deve continuar a ser do tipo instrucoes e da mesma Organisation;
- a versão é imutável;
- alterações posteriores ao documento ou à função não mudam instruction_version;
- a política de exportação será reavaliada na geração do pacote;
- se o documento estiver denied no momento da criação, rejeita a execução;
- se estiver confirm, a execução pode ser criada, mas a geração exigirá confirmação.

Cria ExecutionContextDocument com:
- id ou chave conforme a convenção real;
- execution obrigatória;
- document_version obrigatória;
- order inteiro positivo;
- purpose opcional e curto;
- created_at, se coerente com a convenção.

Regras:
- combinação execution + order é única;
- combinação execution + document_version é única;
- associação é imutável após a criação;
- cada versão pertence à mesma Organisation;
- documento pode ser empresarial, com product null;
- documento associado a Product tem de pertencer ao Product da execução;
- versão de documento ligado a outro Product é rejeitada;
- a versão de instruções da função não deve ser repetida como documento de dados;
- pelo menos uma versão documental de contexto deve ser seleccionada;
- documentos com export_policy=denied são rejeitados na selecção;
- documentos confirm são permitidos, ficando sujeitos a confirmação na geração;
- is_outdated não bloqueia, mas será apresentado como aviso.

API:
- GET /api/v1/executions
- POST /api/v1/executions
- GET /api/v1/executions/{id}

Listagem:
- filtros product, status, function_profile e execution_mode;
- paginação e ordenação determinística;
- apenas empresa do contexto;
- não devolve conteúdo documental integral.

Criação:
- recebe Product, função, title, objective, request_instructions, constraints, expected_output_format, execution_mode e lista ordenada de document_version;
- rejeita organisation, status, snapshots e campos internos;
- função tem de estar active;
- Product tem de estar active;
- requested_by deriva de request.user;
- cria execução, snapshots e contexto numa transacção;
- não lê versão documental actual quando uma versão exacta foi seleccionada;
- audita a criação sem conteúdo integral.

Detalhe:
- apresenta metadados;
- snapshots;
- instruction_version;
- lista ordenada de documentos com título, tipo, version_number, checksum, export_policy actual e is_outdated;
- não devolve o conteúdo integral por defeito;
- conteúdo será montado apenas pelo serviço de pacote.

Concorrência e integridade:
- contexto não pode ser alterado depois de criada a execução;
- não disponibilizar PATCH ou DELETE;
- duas criações independentes são permitidas;
- nenhum cliente pode alterar snapshots ou versões exactas;
- relações históricas usam PROTECT ou política equivalente.

Auditoria:
- usa o evento 11 ou nome real correspondente;
- criação é auditada;
- metadados incluem Product, função, modo, número de documentos e identificadores das versões;
- não incluir objective, request_instructions, constraints, snapshots ou conteúdo documental integral;
- acesso cruzado usa security.cross_org_attempt.

Testes obrigatórios:
1. criação com função active;
2. função inactive rejeitada;
3. Product archived rejeitado;
4. contexto com versão exacta;
5. documento empresarial aceite;
6. documento do mesmo Product aceite;
7. documento de outro Product rejeitado;
8. documento de outra empresa rejeitado;
9. denied rejeitado na selecção;
10. confirm aceite para confirmação posterior;
11. instruction_version exacta preservada;
12. alteração posterior das instruções não altera a execução;
13. alteração posterior da função não altera function_snapshot;
14. alteração posterior do Product não altera product_snapshot;
15. versão actual posterior não substitui versão seleccionada;
16. ordem é preservada;
17. ordem duplicada rejeitada;
18. versão duplicada rejeitada;
19. contexto fica imutável;
20. execução nasce prepared;
21. matriz de transições válidas e inválidas;
22. cliente não escolhe status nem snapshots;
23. listagem isolada;
24. detalhe alheio devolve 404 e é auditado;
25. auditoria não contém conteúdo integral;
26. sem PATCH e DELETE;
27. migrações aplicam sem drift;
28. suite anterior permanece verde.

Não implementar:
- UI;
- pacote de contexto;
- chamadas a IA;
- resultados;
- revisão;
- aplicação de alterações;
- transições funcionais de F1-P06.

Fecho:
- cria prompt_02_resultado.md;
- actualiza F1-P05 para 2/6 concluídos;
- actualiza painel, diário e matriz com evidência parcial;
- VAL-007 e VAL-008 permanecem parciais;
- VAL-009 não pode ser validada sem resultados em F1-P06.

Expectativa verificável:
- execuções prepared podem ser criadas;
- snapshots e versões exactas permanecem imutáveis;
- contexto está ordenado e isolado;
- política de estados existe sem antecipar F1-P06;
- auditoria está limpa;
- próximo prompt recomendado: F1-P05-PR03;
- relatório final lista modelos, snapshots, contratos, estados, migrações, testes e reservas.

Não avances para o prompt seguinte.
```

## Prompt 03 (sonnet) — Criar a interface de preparação da execução

```prompt
Iteração 03
Actua como engenheiro frontend sénior especializado em React, TypeScript e fluxos de preparação rastreável.

Implementa a interface de criação, listagem e detalhe das execuções assistidas.

Identificação:
- Fase: F1 — MVP
- Pipeline: F1-P05
- Prompt: F1-P05-PR03
- Item: MVP-11
- Capacidades: MVP-11.C1 e MVP-11.C2
- História: MVP-11.H1 e MVP-11.H2
- Tarefa: MVP-11.T3
- Validações: VAL-007 e VAL-008, parcialmente

Objectivo:
Permitir preparar uma execução no browser escolhendo Product, função active, modo manual e versões documentais exactas, e consultar o contexto congelado.

Pré-requisitos:
- PR01 e PR02 concluídos;
- API de funções e execuções funcional;
- documentos, versões e Product disponíveis;
- cliente HTTP central, autenticação e OrganisationGate funcionais.

Contexto obrigatório:
Lê apenas:
- contratos reais de FunctionProfile e AIExecution;
- resultado de PR02;
- frontend actual;
- componentes de Product, documentos e funções;
- artefacto 07 do pacote de contexto, apenas para os campos necessários à execução.

Integração:
- substitui a indicação “Execuções indisponíveis” da ficha do Product por uma secção real;
- não remove DocumentSection, DecisionSection ou WorkItemSection;
- não cria contagens simuladas;
- a execução pertence sempre ao Product cuja ficha está aberta.

Componentes mínimos:
- ExecutionSection;
- ExecutionList;
- ExecutionCreateForm;
- ExecutionDetail;
- ContextDocumentSelector;
- FunctionSnapshotView;
- labels e tipos API.

Formulário:
- title;
- objective;
- request_instructions;
- constraints opcional;
- expected_output_format;
- execution_mode: manual_local ou manual_external;
- selecção de FunctionProfile active;
- selecção de pelo menos uma DocumentVersion;
- ordenação explícita das versões seleccionadas;
- purpose opcional por documento.

Funções:
- apresenta apenas active;
- mostra actor_type, propósito e requires_approval;
- função inactive não pode ser escolhida;
- não permite criar ou editar função dentro do formulário de execução;
- catálogo continua na área própria.

Documentos candidatos:
- documentos empresariais e documentos do Product actual;
- não apresenta documentos de outros produtos;
- permite abrir o histórico e escolher uma versão exacta;
- mostra título, tipo, version_number, checksum abreviado, is_outdated e export_policy;
- denied aparece desactivado e não pode ser seleccionado;
- confirm apresenta aviso de que exigirá confirmação antes da geração;
- is_outdated apresenta aviso, mas permanece seleccionável;
- documento de instruções usado pela função é apresentado separadamente e não pode ser duplicado nos dados;
- usa endpoints existentes; acrescenta apenas filtro de leitura mínimo para documentos empresariais se ainda não existir.

Ordenação:
- usar controlos simples Subir/Descer;
- não introduzir drag-and-drop nem biblioteca adicional;
- order enviado ao backend deve corresponder à ordem visível.

Após criação:
- abrir o detalhe;
- mostrar status Preparada;
- mostrar snapshots de função e Product;
- mostrar instruction_version;
- mostrar versões documentais exactas por ordem;
- distinguir claramente snapshot de informação actual;
- alterações posteriores à função ou documentos não devem alterar a apresentação congelada.

Lista:
- apresenta título, função, modo, estado e data;
- filtra por Product actual;
- não apresenta estados ou resultados fictícios;
- permite abrir detalhe.

Regras:
- não disponibilizar edição ou eliminação da execução;
- não disponibilizar transições de estado;
- não chamar IA;
- não criar resultado simulado nesta etapa;
- reutiliza cliente HTTP central;
- trata 400, 403, 404 e 409;
- evita submissão duplicada.

Testes obrigatórios:
1. estado vazio;
2. listagem de execuções;
3. apenas funções active;
4. denied indisponível;
5. confirm com aviso;
6. is_outdated com aviso;
7. selecção de versão exacta;
8. selecção de versão histórica;
9. ordenação Subir/Descer;
10. exigência de pelo menos um documento;
11. criação em manual_local;
12. criação em manual_external;
13. detalhe mostra status prepared;
14. detalhe mostra function_snapshot;
15. detalhe mostra product_snapshot;
16. detalhe mostra instruction_version;
17. detalhe mostra ordem, versão e checksum;
18. submissão duplicada evitada;
19. erros tratados;
20. nenhuma transição, resultado ou chamada a IA;
21. regressão de portefólio/documentos/decisões/pendências;
22. build e suite passam.

Demonstração ao vivo:
- criar ou reutilizar documento instrucoes;
- criar função IA active;
- criar documentos com versões;
- abrir Product;
- preparar execução manual_local;
- seleccionar versão histórica de pelo menos um documento;
- confirmar snapshots e versões exactas no detalhe;
- editar depois a função ou documento;
- confirmar que a execução não muda.

Fecho:
- cria prompt_03_resultado.md;
- actualiza F1-P05 para 3/6 concluídos;
- actualiza painel, diário e matriz com evidência de UI.

Expectativa verificável:
- execução prepared pode ser criada no browser;
- função e versões exactas são seleccionáveis;
- snapshots são visíveis e permanecem congelados;
- nenhuma execução automática ou resultado foi criado;
- próximo prompt recomendado: F1-P05-PR04;
- relatório final lista componentes, contratos, testes, demonstração e pendências.

Não avances para o prompt seguinte.
```

## Prompt 04 (opus) — Gerar o pacote de contexto com políticas efectivas

```prompt
Iteração 04
Actua como engenheiro backend sénior especializado em geração determinística, segurança de conteúdo, políticas de exportação e auditoria.

Implementa o serviço e a API de geração do pacote de contexto da execução.

Identificação:
- Fase: F1 — MVP
- Pipeline: F1-P05
- Prompt: F1-P05-PR04
- Item: MVP-12
- Capacidades: MVP-12.C1 e MVP-12.C2
- História: MVP-12.H1 e MVP-12.H2
- Tarefas: MVP-12.T1 a MVP-12.T5
- Requisitos transversais: RT-01, RT-02, RT-03, RT-04, RT-07, RT-09 e RT-10
- Validações: VAL-008, VAL-012 e VAL-014, parcialmente

Objectivo:
Gerar um pacote determinístico e seguro a partir dos snapshots e das DocumentVersion exactas da execução, aplicando export_policy no servidor e suportando Markdown único e ficheiros separados.

Pré-requisitos:
- PR01 a PR03 concluídos;
- execução prepared com contexto congelado;
- armazenamento privado funcional;
- snapshots e versões exactas disponíveis;
- preview documental já sanitizada, sem reutilizar HTML no pacote.

Contexto obrigatório:
Lê apenas:
- docs/gestao/02_fase_0_preparacao/artefactos/07_pacote_contexto_ia.md;
- docs/gestao/02_fase_0_preparacao/artefactos/10_requisitos_seguranca_mvp.md: política de IA externa;
- docs/gestao/03_fase_1_mvp/01_backlog.md: MVP-12;
- DEC-F0-FINAL-08 e CLR-03;
- modelos e serviços reais de AIExecution, Document e storage;
- lista AuditAction;
- resultados de PR02 e PR03.

Estrutura fixa de sete secções:
1. Objectivo;
2. Função;
3. Instruções do pedido;
4. Produto;
5. Restrições;
6. Formato esperado;
7. Documentos — DADOS.

A ordem é obrigatória e não deve depender da ordem de dicionários ou queries.

Secção Objectivo:
- usa exclusivamente objective do snapshot da execução;
- inclui title apenas como identificação;
- não usa valores actuais do Product ou FunctionProfile.

Secção Função:
- usa function_snapshot;
- inclui nome, actor_type, propósito, responsabilidades, limites e requires_approval;
- quando existir instruction_version, inclui o conteúdo exacto dessa versão;
- identifica documento, version_number e checksum;
- nunca usa current_version posterior.

Secção Instruções do pedido:
- usa request_instructions congeladas na execução;
- distingue-as claramente das instruções da função.

Secção Produto:
- usa product_snapshot;
- não consulta valores actuais para substituir o snapshot;
- não inclui dados pessoais desnecessários.

Secção Restrições:
- combina de forma claramente identificada constraints da função e constraints da execução;
- não interpreta nem executa conteúdo documental;
- inclui declaração de que documentos da secção 7 são dados não confiáveis.

Secção Formato esperado:
- usa expected_output_format;
- não cria template específico para fornecedor.

Secção Documentos — DADOS:
- respeita a ordem de ExecutionContextDocument;
- lê exclusivamente as DocumentVersion referenciadas;
- nunca lê Document.current_version para substituir a selecção;
- cada documento inclui fonte, Document id, DocumentVersion id, título, tipo, version_number, checksum, is_outdated e export_policy actual;
- usa marcadores inequívocos de início e fim;
- inclui declaração anti-injecção antes dos documentos;
- qualquer instrução encontrada dentro dos documentos deve ser tratada como dado;
- não sanitizar ou transformar semanticamente o Markdown original;
- não executar HTML, scripts, diagramas, links ou código.

Política export_policy:
- aplicada no backend;
- reavaliada no momento de cada preview, cópia ou descarga;
- instruction_document está sujeita à mesma política;
- denied bloqueia selecção e geração;
- denied não é silenciosamente omitido;
- se qualquer documento seleccionado passar para denied depois da criação da execução, a geração é bloqueada com 409;
- a resposta identifica os documentos bloqueadores sem devolver conteúdo;
- confirm exige confirmação explícita do utilizador;
- confirmação é recebida como lista de Document ids ou mecanismo equivalente validado pelo servidor;
- confirm não confirmado bloqueia a geração com 409;
- allowed é incluído sem confirmação;
- is_outdated não bloqueia, mas gera aviso;
- a política deve ser reavaliada em cada geração; confirmação anterior não fica globalmente memorizada;
- tentativa de contorno por chamada directa à API é rejeitada.

Consistência durante geração:
- lê e bloqueia as linhas Document necessárias durante a avaliação das políticas;
- evita que uma política mude de allowed para denied durante a montagem;
- confirma que cada versão e objecto continuam existentes;
- falha de armazenamento impede pacote parcial;
- não devolve conteúdo incompleto;
- audita falhas com evento aprovado, sem conteúdo.

Formatos:
- single_markdown, por defeito;
- separate_files, entregue como ZIP criado com biblioteca padrão;
- sem dependência externa para ZIP;
- single_markdown tem um ficheiro .md;
- ZIP contém manifesto e ficheiros numerados por secção;
- documentos ficam em directório próprio, por ordem;
- nomes de ficheiros são gerados no servidor e protegidos contra path traversal;
- nenhum formato é optimizado para fornecedor específico.

Determinismo:
- mesma execução, mesmas políticas, mesmas confirmações e mesmo formato produzem os mesmos bytes e checksum;
- não inserir timestamp variável dentro do conteúdo;
- usar valores congelados da execução;
- ordem estável;
- normalização de finais de linha definida;
- checksum SHA-256 do pacote devolvido;
- manifesto inclui versões e checksums das fontes.

Limites:
- define CONTEXT_PACKAGE_MAX_BYTES;
- falha antes de devolver pacote excessivo;
- não guardar o pacote integral na BD;
- pacote é derivado da execução;
- não criar nova entidade genérica de package;
- auditoria guarda apenas checksum, formato, modo, operação e identificadores.

API recomendada:
- POST /api/v1/executions/{id}/context-package/preview
- POST /api/v1/executions/{id}/context-package/download

Podes ajustar os caminhos às convenções reais.

Entrada:
- format;
- confirmed_document_ids;
- operation ou destination_label curto quando necessário;
- nenhum conteúdo, snapshot ou versão pode vir do cliente.

Preview:
- devolve avisos, manifesto, checksum e conteúdo Markdown quando single_markdown;
- para separate_files, pode devolver manifesto e lista de ficheiros sem ZIP;
- não devolve conteúdo quando a política bloquear.

Download:
- devolve .md ou .zip;
- reavalia todas as políticas;
- usa Content-Disposition seguro;
- nunca envia automaticamente para uma IA.

Estado:
- apenas execução prepared pode gerar pacote;
- outros estados devolvem 409;
- geração não altera o estado da execução;
- não cria resultado;
- não marca execução como concluída.

Auditoria:
- usa evento 12 ou nome exacto da lista;
- preview, copy e download são distinguíveis pelos metadados;
- regista execution id, modo, formato, checksum, ids das versões, documentos confirmados e destino genérico quando fornecido;
- não regista conteúdo, instruções, snapshots ou nomes de ficheiros sensíveis;
- bloqueios denied/confirm podem ser auditados como denied;
- acesso cruzado usa security.cross_org_attempt.

Testes obrigatórios:
1. pacote contém sete secções na ordem;
2. função usa snapshot;
3. Product usa snapshot;
4. instruções usam instruction_version exacta;
5. documentos usam versões exactas;
6. alteração de current_version não muda o pacote;
7. alteração da função não muda o pacote;
8. alteração do Product não muda o pacote;
9. order é preservada;
10. fontes e checksums aparecem;
11. marcadores início/fim existem;
12. declaração anti-injecção existe;
13. instrução hostil dentro de documento permanece em DADOS;
14. allowed é incluído;
15. confirm sem confirmação bloqueia;
16. confirm confirmado inclui;
17. denied bloqueia;
18. alteração posterior para denied bloqueia;
19. tentativa de contorno directo bloqueada;
20. is_outdated gera aviso;
21. instruction_document confirm exige confirmação;
22. instruction_document denied bloqueia;
23. execução não prepared devolve 409;
24. single_markdown determinístico;
25. separate_files determinístico;
26. ZIP sem path traversal;
27. checksum estável;
28. limite total aplicado;
29. objecto de versão ausente bloqueia;
30. nenhuma resposta parcial;
31. isolamento por empresa;
32. auditoria sem conteúdo integral;
33. nenhuma chamada externa;
34. suites e drift verdes.

Fecho:
- cria prompt_04_resultado.md;
- actualiza F1-P05 para 4/6 concluídos;
- actualiza painel, diário e matriz;
- VAL-008 pode permanecer parcial até UI e validação integrada;
- VAL-014 permanece parcial até F1-P07;
- VAL-012 permanece parcial.

Expectativa verificável:
- pacote é fiel aos snapshots e versões;
- os três valores de export_policy são aplicados no servidor;
- os formatos Markdown e ZIP funcionam;
- checksum é determinístico;
- nenhuma IA é chamada;
- próximo prompt recomendado: F1-P05-PR05;
- relatório final lista estrutura, política, endpoints, determinismo, testes, auditoria e reservas.

Não avances para o prompt seguinte.
```

## Prompt 05 (sonnet) — Criar a interface do pacote e simular o handoff manual

```prompt
Iteração 05
Actua como engenheiro frontend sénior especializado em React, TypeScript, UX de segurança e fluxos manuais de IA.

Implementa a interface de pré-visualização, confirmação, cópia e descarga do pacote de contexto.

Identificação:
- Fase: F1 — MVP
- Pipeline: F1-P05
- Prompt: F1-P05-PR05
- Item: MVP-12
- Capacidades: MVP-12.C1 e MVP-12.C2
- História: MVP-12.H1 e MVP-12.H2
- Validações: VAL-008, VAL-012 e VAL-014, parcialmente

Objectivo:
Permitir ao utilizador preparar e transferir manualmente o pacote de uma execução prepared, sem ligação automática a qualquer modelo de IA.

A “execução simulada” desta pipeline significa simular o handoff manual:
- gerar;
- rever;
- confirmar documentos;
- copiar ou descarregar;
- usar o pacote fora da aplicação.

Não significa:
- chamar um modelo;
- gerar um resultado automaticamente;
- importar resultado;
- mudar o estado da execução;
- aprovar ou aplicar alterações.

Pré-requisitos:
- PR01 a PR04 concluídos;
- ExecutionDetail funcional;
- API de pacote funcional;
- políticas aplicadas no backend.

Contexto obrigatório:
Lê apenas:
- contratos reais dos endpoints de pacote;
- frontend actual de execuções;
- artefacto 07 do pacote;
- resultado de PR04;
- labels reais de export_policy e execution_mode.

Integração:
- acrescenta ContextPackagePanel ao detalhe da execução;
- só aparece para execução prepared;
- nos restantes estados apresenta explicação sem tentar gerar;
- não remove snapshots nem lista de versões.

Fluxo:
1. seleccionar formato single_markdown ou separate_files;
2. ver análise das políticas;
3. ler avisos;
4. confirmar explicitamente cada documento confirm;
5. gerar preview;
6. copiar Markdown ou descarregar .md;
7. descarregar ZIP para separate_files.

Políticas na UI:
- allowed: indicação simples;
- confirm: checkbox individual, inicialmente desmarcada;
- denied: estado bloqueado, sem botão de contorno;
- is_outdated: aviso visível;
- instruction_document aparece na mesma análise de políticas;
- alteração de política detectada no backend deve actualizar a UI após nova tentativa;
- a UI não deve confiar apenas no estado local;
- erro 409 deve apresentar o motivo e recarregar a análise.

Confirmação:
- texto claro de que o conteúdo poderá sair da aplicação;
- em manual_external, aviso explícito sobre partilha com serviço externo;
- em manual_local, aviso de que o pacote deve permanecer no ambiente autorizado;
- cada documento confirm exige acção explícita;
- “Confirmar todos” só é permitido se mostrar a lista e exigir confirmação adicional;
- não persistir confirmações em localStorage;
- nova geração reavalia as confirmações.

Preview:
- mostra as sete secções;
- conteúdo apresentado como texto ou Markdown não executável;
- não usar dangerouslySetInnerHTML;
- não renderizar HTML documental;
- documentos DADOS claramente delimitados;
- mostra checksum e manifesto;
- permite comparar apenas os identificadores e versões, não implementar comparação de documentos.

Cópia:
- usa Clipboard API com tratamento de falha;
- só disponível para single_markdown;
- após copiar, mostra confirmação visual;
- não guarda o pacote no browser.

Download:
- .md para single_markdown;
- .zip para separate_files;
- nome de ficheiro fornecido ou validado pelo backend;
- revogar URLs temporárias criadas no browser;
- não adicionar biblioteca externa sem necessidade.

Simulação manual obrigatória:
- usar dados de demonstração não sensíveis;
- criar execução manual_local;
- gerar e copiar o pacote;
- criar execução manual_external;
- confirmar documento confirm;
- descarregar pacote;
- abrir o Markdown e o ZIP fora da aplicação;
- verificar as sete secções, manifesto e documentos;
- não enviar o pacote a serviço real nesta etapa;
- não importar resposta;
- manter as execuções em prepared;
- registar apenas checksum, formato e resultado da verificação no relatório.

Integração na ficha:
- lista de execuções já existente permanece;
- abrir execução permite preparar o pacote;
- não criar separador global novo salvo necessidade real;
- execuções passa a ser uma área real e deixa de aparecer como indisponível.

Testes obrigatórios:
1. painel só aparece em prepared;
2. sete secções visíveis;
3. allowed não exige confirmação;
4. confirm exige checkbox;
5. denied bloqueia;
6. alteração para denied é apresentada após 409;
7. is_outdated mostra aviso;
8. instruction_document aparece na política;
9. manual_external mostra aviso externo;
10. manual_local mostra aviso local;
11. preview é texto não executável;
12. copy usa Clipboard API;
13. falha de clipboard é tratada;
14. download Markdown;
15. download ZIP;
16. URLs temporárias são revogadas;
17. checksum e manifesto apresentados;
18. confirmação não é persistida;
19. nova geração reavalia políticas;
20. nenhuma chamada a IA;
21. nenhum resultado criado;
22. estado permanece prepared;
23. regressão de funções, documentos e portefólio;
24. build e suite passam.

Fecho:
- cria prompt_05_resultado.md;
- actualiza F1-P05 para 5/6 concluídos;
- actualiza painel, diário e matriz com evidência da interface e simulação;
- não declares validação externa com modelo real;
- essa confirmação fica para F1-P08/piloto.

Expectativa verificável:
- pacote pode ser revisto, confirmado, copiado e descarregado;
- políticas são compreensíveis e não contornáveis;
- handoff manual foi simulado sem chamar IA;
- execução permanece prepared;
- próximo prompt recomendado: F1-P05-PR06;
- relatório final lista componentes, testes, simulação, checksums, avisos e pendências.

Não avances para o prompt seguinte.
```

## Prompt 06 (opus) — Validar o fluxo e encerrar F1-P05

```prompt
Iteração 06
Actua como revisor técnico sénior e conclui F1-P05 através de validação integrada, segurança, concorrência, regressão e fecho de governação.

Identificação:
- Fase: F1 — MVP
- Pipeline: F1-P05 — Funções, execuções e pacote de contexto
- Prompt: F1-P05-PR06
- Itens: MVP-10, MVP-11 e MVP-12
- Validações principais: VAL-007 e VAL-008
- Validações reforçadas: VAL-002, VAL-012 e VAL-014
- Validação ainda não concluível: VAL-009, que depende de resultados em F1-P06

Objectivo:
Validar ponta a ponta:
- função configurada previamente;
- execução created em prepared;
- snapshots imutáveis;
- versões documentais exactas;
- pacote determinístico;
- políticas de exportação;
- handoff manual simulado.

Corrige apenas defeitos concretos. Não inicia F1-P06.

Pré-requisitos:
- PR01 a PR05 concluídos;
- F1-P04 concluída;
- aplicação e Docker Compose funcionais;
- suites anteriores verdes.

Contexto obrigatório:
Lê apenas:
- critérios de conclusão de MVP-10 a MVP-12;
- matriz VAL;
- artefacto 07 do pacote;
- resultados PR01 a PR05;
- código actual de functions e executions;
- gerador de pacote;
- componentes frontend correspondentes;
- status, painel e diário.

Cenário integrado principal:
1. criar Product activo;
2. criar documento instrucoes v1 com export_policy=confirm;
3. criar função IA ligada ao documento;
4. criar documento de contexto A v1 com allowed;
5. criar documento B v1 com confirm;
6. criar documento C v1 com denied;
7. criar execução manual_local com A v1 e B v1;
8. confirmar que C não pode ser seleccionado;
9. confirmar snapshot da função e Product;
10. editar a função;
11. criar v2 do documento instrucoes;
12. criar v2 dos documentos A e B;
13. confirmar que a execução continua ligada às versões v1;
14. gerar pacote sem confirmar B e instruções, esperando bloqueio;
15. confirmar explicitamente;
16. gerar pacote Markdown;
17. gerar novamente e confirmar checksum idêntico;
18. gerar ZIP e abrir o manifesto;
19. confirmar as sete secções;
20. confirmar fontes, versões e checksums;
21. confirmar que conteúdo hostil nos documentos permanece apenas em DADOS;
22. confirmar que a execução permanece prepared.

Política alterada depois da execução:
1. alterar B de confirm para denied;
2. tentar gerar novamente;
3. confirmar bloqueio 409 sem conteúdo;
4. voltar B para allowed;
5. gerar e confirmar que a política actual é aplicada;
6. não alterar as versões congeladas.

Função:
- criar human, ai e hybrid;
- validar requires_approval;
- inactivar função;
- confirmar que não aparece em novas execuções;
- confirmar que execução passada mantém function_snapshot;
- reactivar;
- confirmar auditoria.

Isolamento:
- usar duas empresas;
- função de outra empresa não seleccionável;
- Product alheio rejeitado;
- DocumentVersion alheia rejeitada;
- execução alheia devolve 404;
- preview e download alheios devolvem 404;
- filtros não revelam contagens externas;
- tentativas cruzadas auditadas.

Concorrência e consistência:
- testar alteração de export_policy durante geração;
- a geração deve observar um estado coerente e nunca incluir documento que tenha sido bloqueado antes do fim da operação;
- testar duas gerações simultâneas da mesma execução;
- ambas podem ter sucesso se políticas e confirmações forem iguais;
- checksums devem ser idênticos;
- não criar registos duplicados de estado nem alterar a execução;
- contexto e snapshots permanecem imutáveis.

Armazenamento:
- todas as DocumentVersion referenciadas existem;
- checksum do conteúdo coincide;
- versão ausente bloqueia pacote;
- não existe pacote parcial;
- ZIP não contém path traversal;
- não guardar pacote integral na BD.

Segurança:
- documentos são DADOS;
- declaração anti-injecção presente;
- conteúdo documental não altera as secções 1–6;
- HTML, JavaScript e código não são executados pela aplicação;
- pacote não contém cookies, tokens, segredos, credenciais, variáveis de ambiente ou metadados de auditoria;
- conteúdo documental legítimo permanece fiel;
- não declarar protecção completa contra prompt injection;
- VAL-014 permanece parcial até F1-P07.

Auditoria:
- eventos de funções;
- criação de execução;
- geração/preview/cópia/download;
- bloqueios por política;
- acessos cruzados;
- todos com correlation_id;
- nenhum evento contém instructions, objective, constraints, snapshots, pacote ou conteúdo documental integral.

Migrações:
- drift zero;
- aplicar em base vazia;
- aplicar em base existente;
- reversibilidade estrutural em base controlada;
- declarar que reverter remove dados dos módulos;
- preservar outras aplicações.

Regressão:
- suite backend completa;
- suite frontend completa;
- build;
- health live e ready;
- autenticação;
- onboarding;
- portefólio;
- documentos;
- decisões;
- pendências;
- armazenamento;
- auditoria append-only;
- Docker Compose.

Simulação de execução:
- realizar handoff manual apenas com dados não sensíveis;
- copiar o pacote Markdown;
- descarregar e abrir o ZIP;
- confirmar que podem ser usados manualmente;
- não chamar modelo real;
- não criar resposta fictícia dentro da aplicação;
- não importar resultado;
- não aprovar nem aplicar;
- manter execution.status=prepared;
- registar evidência curta com checksum e estrutura, sem copiar o pacote integral para a governação.

Estados VAL:
- VAL-007 pode ser Validada se função é criada, gerida e efectivamente utilizada numa execução;
- VAL-008 pode ser Validada se snapshots e versões exactas são preservados e o pacote é fiel;
- VAL-009 permanece Pendente ou Parcial sem resultado importado;
- VAL-002 permanece Parcial até suite transversal completa de F1-P07;
- VAL-012 permanece Parcial até consulta e consolidação de auditoria em F1-P07;
- VAL-014 permanece Parcial até a suite completa de conteúdo e injecção em F1-P07.

Correcções permitidas:
- defeitos de isolamento;
- snapshots mutáveis;
- uso indevido de current_version;
- políticas contornáveis;
- pacote não determinístico;
- falhas de concorrência;
- erros de UI;
- auditoria com conteúdo;
- testes instáveis.

Não permitir:
- chamada automática a IA;
- importação de resultados;
- aprovação;
- aplicação de alterações;
- templates por fornecedor;
- filas;
- Redis;
- Celery;
- agentes;
- refactorização ampla;
- geração automática de F1-P06.

Governança:
1. cria prompt_06_resultado.md;
2. actualiza F1-P05 para Concluída, 6/6, se os critérios passarem;
3. mantém estado de revisão segundo o guia, sem confundir execução técnica com revisão humana;
4. actualiza VAL-007 e VAL-008 com evidências;
5. mantém VAL-002, VAL-012 e VAL-014 parciais;
6. não valida VAL-009 sem resultados;
7. actualiza painel e diário de forma curta;
8. não altera artefactos da Fase 0;
9. não cria decisão global sem desvio estrutural real.

O resultado deve incluir:
- veredicto;
- modelos e contratos finais;
- regras de FunctionProfile;
- snapshots;
- versões exactas;
- estados da execução;
- estrutura das sete secções;
- política export_policy;
- formatos;
- determinismo e checksum;
- simulação manual;
- isolamento;
- concorrência;
- segurança;
- auditoria;
- migrações;
- testes e demonstração;
- VAL actualizadas;
- problemas corrigidos;
- reservas;
- estado final;
- próximo passo.

Expectativa verificável:
- F1-P05 está Concluída com 6/6;
- VAL-007 e VAL-008 estão Validadas, se houver evidência completa;
- VAL-009 não está validada;
- funções, execuções prepared e pacote são utilizáveis no browser;
- políticas denied/confirm/allowed são aplicadas no servidor;
- nenhuma IA foi chamada;
- nenhum resultado foi criado;
- próximo passo recomendado: efectuar commit de F1-P05 e gerar F1-P06 just-in-time.

Não avances para F1-P06.
```
