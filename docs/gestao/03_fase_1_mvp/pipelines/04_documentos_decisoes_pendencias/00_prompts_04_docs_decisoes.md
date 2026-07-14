# Pipeline: Documentos, decisões e pendências

## Prompt 01 (opus) — Criar o modelo documental versionado

```prompt
Iteração 01

Actua como engenheiro backend sénior especializado em Django, PostgreSQL, armazenamento privado e modelação documental.

Implementa a fundação persistente da gestão documental do VentureOps AI.

Identificação:
- Fase: F1 — MVP
- Pipeline: F1-P04 — Documentos, tipos, decisões e pendências
- Prompt: F1-P04-PR01
- Itens: MVP-06 e MVP-07, parcialmente
- Capacidades: MVP-06.C1, MVP-06.C2, MVP-06.C3 e MVP-07.C1, parcialmente
- Tarefas: MVP-06.T1 e MVP-07.T1
- Requisitos transversais: RT-01, RT-03, RT-04, RT-08, RT-09 e RT-10
- Validações preparadas: VAL-004 e VAL-014

Condição obrigatória:
- confirma que F1-P03-PR06 terminou;
- confirma que F1-P03 foi revista e aceite para avanço;
- se F1-P03 continuar Em execução, bloqueada ou com defeito estrutural pendente, não alteres código e regista o bloqueio;
- não corrijas silenciosamente F1-P03 nesta execução.

Objectivo:
Criar os modelos Document e DocumentVersion, a enumeração fixa de tipos documentais, os marcadores estruturados e as migrações iniciais, sem implementar ainda API ou interface.

Contexto obrigatório:
Lê apenas:
- docs/gestao/03_fase_1_mvp/01_backlog.md: MVP-06 e MVP-07;
- docs/gestao/03_fase_1_mvp/02_mapa_pipelines.md: F1-P04;
- resultado final de F1-P03-PR06;
- docs/gestao/02_fase_0_preparacao/artefactos/05_fonte_de_verdade_bd_markdown.md;
- docs/gestao/02_fase_0_preparacao/artefactos/10_requisitos_seguranca_mvp.md: SEC-DOC e SEC-STO;
- DEC-F0-FINAL-08 e DEC-20260712-05;
- código actual de documents, storage, organisations, portfolio, accounts e audit;
- decisões técnicas actuais.

Inspecção inicial:
1. Confirma as convenções reais de UUID, timestamps, OrganisationScopedModel e migrações.
2. Confirma o contrato actual do StorageAdapter.
3. Confirma o modelo Product concluído em F1-P03.
4. Confirma a lista fechada AuditAction.
5. Confirma que não existem alterações inesperadas a sobrescrever.

Cria a enumeração fechada de tipos:
- contexto_da_empresa;
- visao_de_produto;
- instrucoes;
- decisao_detalhada;
- resultado.

Novos tipos exigem alteração formal. Não criar tipos configuráveis ou templates.

Cria a enumeração de export_policy:
- allowed;
- confirm;
- denied.

O valor por defeito é confirm.

Cria Document com:
- UUID;
- organisation obrigatória;
- product opcional;
- title obrigatório;
- document_type obrigatório;
- current_version opcional durante a criação técnica, mas obrigatório após a primeira versão;
- is_outdated com default false;
- export_policy com default confirm;
- version ou outro campo de concorrência estrutural, conforme o padrão real;
- created_at;
- updated_at.

Regras de Document:
- organisation deriva sempre do contexto do servidor;
- product, quando fornecido, pertence à mesma organisation;
- title não pode estar vazio;
- conteúdo Markdown não é guardado na BD;
- is_outdated e export_policy existem apenas na BD;
- não duplicar estes marcadores dentro do Markdown;
- não implementar eliminação física;
- não implementar pesquisa, comparação de versões ou classificação avançada.

Cria DocumentVersion com:
- UUID;
- document obrigatório;
- version_number sequencial;
- storage_key gerada no servidor;
- checksum SHA-256;
- byte_size;
- author;
- change_summary curto e opcional;
- created_at.

Regras de DocumentVersion:
- conteúdo fica exclusivamente no armazenamento privado;
- cada submissão cria uma nova versão;
- versão é imutável;
- combinação document + version_number é única;
- storage_key não é fornecida pelo cliente;
- não permitir update ou delete normal de versões;
- current_version deve apontar para uma versão do próprio Document;
- não guardar conteúdo ou HTML renderizado na BD.

Associações:
- documento pode ser empresarial, com product null;
- documento pode pertencer a um Product da mesma organisation;
- nenhuma associação entre empresas é válida;
- não ligar ainda documentos a funções ou execuções;
- a ligação decisao_detalhada será implementada em PR04.

Migrações:
- cria as migrações do módulo documents;
- aplica numa base vazia e na base de desenvolvimento existente;
- demonstra reversibilidade estrutural numa base controlada;
- não reverta dados documentais que devam ser preservados;
- verifica drift.

Testes obrigatórios:
1. Document exige organisation;
2. title é obrigatório;
3. tipo inválido é rejeitado;
4. export_policy inválida é rejeitada;
5. defaults is_outdated=false e export_policy=confirm;
6. Product de outra empresa é rejeitado;
7. documento empresarial sem Product é aceite;
8. DocumentVersion exige Document;
9. version_number é único por Document;
10. storage_key não é editável pelo cliente;
11. DocumentVersion não contém campo de conteúdo;
12. DocumentVersion não pode ser alterada;
13. current_version não pode apontar para versão de outro documento;
14. conteúdo não existe na BD;
15. migrações aplicam sem drift;
16. suite anterior permanece verde.

Não implementar:
- API;
- escrita real no armazenamento;
- editor;
- preview;
- histórico;
- recuperação;
- decisões;
- pendências;
- exportação ou pacote de contexto.

Fecho:
- cria docs/gestao/03_fase_1_mvp/pipelines/04_documentos_decisoes_pendencias/resultados_execucao/prompt_01_resultado.md;
- cria ou actualiza F1-P04 no status como Em execução, 1/6 concluído;
- actualiza painel e diário de forma curta;
- não cries decisão global sem desvio estrutural real.

Expectativa verificável:
- Document e DocumentVersion existem;
- tipos e políticas estão fechados;
- conteúdo não é persistido na BD;
- isolamento estrutural está aplicado;
- migrações e testes passam;
- nenhuma API ou UI foi antecipada;
- próximo prompt recomendado: F1-P04-PR02;
- o relatório lista modelos, campos, constraints, migrações, testes, problemas e pendências.

Não avances para o prompt seguinte.
```

## Prompt 02 (opus) — Implementar a API documental e o versionamento

```prompt
Iteração 02

Actua como engenheiro backend sénior especializado em Django REST Framework, armazenamento privado, concorrência e auditoria.

Implementa a API documental completa sobre os modelos criados em F1-P04-PR01.

Identificação:
- Fase: F1 — MVP
- Pipeline: F1-P04
- Prompt: F1-P04-PR02
- Itens: MVP-06 e MVP-07
- Capacidades: MVP-06.C1, MVP-06.C2, MVP-06.C3 e MVP-07.C1
- Tarefas: MVP-06.T2, T4, T5, T6, T7 e MVP-07.T2
- Requisitos transversais: RT-01, RT-02, RT-03, RT-04, RT-07, RT-08 e RT-10
- Validações: VAL-004, VAL-014, VAL-002 e VAL-012, parcialmente

Objectivo:
Permitir criar, listar, consultar, editar, recuperar e marcar documentos, preservando conteúdo em ficheiros privados, versões imutáveis, concorrência optimista, isolamento e auditoria.

Pré-requisitos:
- PR01 concluído;
- StorageAdapter filesystem funcional;
- Document e DocumentVersion existentes;
- Product, contexto empresarial e auditoria funcionais.

Contexto obrigatório:
Lê apenas:
- implementação actual de documents e storage;
- resultado de PR01;
- backlog MVP-06/MVP-07;
- artefacto 05 de fonte de verdade;
- requisitos SEC-DOC/SEC-STO;
- lista real AuditAction;
- padrões reais da API Product.

Implementa endpoints coerentes com a API actual:

- GET /api/v1/documents
- POST /api/v1/documents
- GET /api/v1/documents/{document_id}
- PATCH /api/v1/documents/{document_id}
- GET /api/v1/documents/{document_id}/versions
- GET /api/v1/documents/{document_id}/versions/{version_number}
- POST /api/v1/documents/{document_id}/restore
- POST /api/v1/documents/preview

Podes ajustar os caminhos às convenções reais, preservando contratos explícitos.

Criação:
- recebe title, document_type, conteúdo Markdown e product opcional;
- aceita is_outdated e export_policy, se explicitamente fornecidos;
- conteúdo deve ser texto UTF-8 válido;
- aplica limite configurável de bytes;
- excesso devolve 413;
- organisation deriva da Membership;
- product deve pertencer à mesma organisation;
- gera storage_key no servidor;
- calcula checksum;
- cria DocumentVersion 1;
- define current_version;
- operação é auditada.

Edição:
- recebe conteúdo Markdown, expected_version e change_summary opcional;
- pode actualizar title, marcadores e associações apenas segundo contrato explícito;
- cada alteração de conteúdo cria nova DocumentVersion;
- versão anterior permanece imutável;
- expected_version obsoleta devolve 409;
- não existe sobrescrita silenciosa;
- edição apenas de metadados também deve ter concorrência coerente;
- não aceitar organisation, storage_key, checksum ou version_number do cliente.

Coordenação BD e armazenamento:
- escreve o objecto privado antes de criar a referência oficial na BD;
- enquanto a transacção não for confirmada, o objecto não pode ser exposto pela aplicação;
- se a escrita falhar, não criar DocumentVersion nem alterar current_version;
- se a transacção de BD falhar depois da escrita, tenta remover o objecto órfão de forma controlada;
- regista falhas de armazenamento usando apenas evento existente da lista fechada;
- nunca deixar current_version a apontar para objecto inexistente;
- documenta a limitação residual de falha abrupta entre sistemas sem introduzir fila ou transacção distribuída.

Consulta:
- detalhe devolve metadados e conteúdo Markdown da versão actual;
- consulta de versão devolve o conteúdo daquela versão exacta;
- listagem não devolve conteúdo integral;
- suporta filtros product, document_type, is_outdated e export_policy;
- paginação e ordenação determinística;
- filtros nunca atravessam empresas.

Recuperação:
- recebe version_number e expected_version actual;
- lê a versão antiga;
- cria uma nova DocumentVersion com novo número;
- não muda nem apaga versões anteriores;
- actualiza current_version para a nova versão;
- preserva checksum e origem no resumo ou metadados mínimos;
- operação auditada;
- versão inexistente devolve 404;
- versão actual obsoleta devolve 409.

Marcadores:
- is_outdated é booleano;
- export_policy aceita apenas allowed, confirm ou denied;
- denied não elimina nem oculta o documento dentro da aplicação;
- não implementar geração de pacote ou exportação nesta pipeline;
- regista claramente que F1-P05 aplicará o bloqueio de selecção e geração;
- não excluir silenciosamente documentos denied.

Preview segura:
- recebe Markdown não guardado;
- aplica o mesmo limite de tamanho;
- renderiza no backend;
- HTML bruto, scripts, handlers, javascript:, data: perigosos e conteúdo executável são bloqueados;
- código é apresentado como texto, nunca executado;
- devolve apenas HTML sanitizado;
- não guarda o conteúdo.

Auditoria:
- usa apenas eventos 5–7 ou os nomes reais correspondentes;
- criação, alteração, nova versão e recuperação são auditadas;
- metadados contêm apenas operação, versão, checksum abreviado quando permitido e nomes de campos;
- não registar conteúdo Markdown integral;
- tentativas cruzadas usam security.cross_org_attempt;
- falhas de storage usam o evento aprovado correspondente.

Testes obrigatórios:
1. criação gera v1 e ficheiro privado;
2. edição gera v2 e preserva v1;
3. conteúdo não aparece na BD;
4. checksum corresponde ao ficheiro;
5. conteúdo acima do limite devolve 413;
6. UTF-8 inválido é rejeitado;
7. Product alheio é rejeitado;
8. documento alheio devolve 404;
9. conflito de versão devolve 409;
10. duas edições concorrentes não produzem lost update;
11. histórico mantém todas as versões;
12. recuperação cria nova versão;
13. versão recuperada corresponde ao conteúdo histórico;
14. marcadores persistem na BD;
15. filtro por tipo funciona;
16. filtro por Product funciona;
17. filtro por política funciona;
18. preview neutraliza XSS;
19. URLs perigosas são removidas;
20. falha de armazenamento não cria versão;
21. falha de BD tenta limpar objecto não referenciado;
22. auditoria não contém conteúdo integral;
23. migrações sem drift;
24. suite anterior permanece verde.

Não implementar:
- interface frontend;
- comparação visual de versões;
- pesquisa;
- exportação;
- integração com função ou execução;
- decisões ou pendências.

Fecho:
- cria prompt_02_resultado.md;
- actualiza F1-P04 para 2/6 concluídos;
- actualiza painel, diário e matriz apenas com evidência real;
- VAL-004 e VAL-014 permanecem parciais até existir UI e validação integrada.

Expectativa verificável:
- API documental funciona;
- conteúdo está em armazenamento privado;
- versões são imutáveis e recuperáveis;
- conflitos devolvem 409;
- preview é sanitizada;
- marcadores e tipos são filtráveis;
- auditoria está limpa;
- próximo prompt recomendado: F1-P04-PR03;
- relatório final apresenta contratos, estratégia BD↔storage, testes, eventos, problemas e reservas.

Não avances para o prompt seguinte.
```

## Prompt 03 (opus) — Criar editor, preview e histórico documental

```prompt
Iteração 03

Actua como engenheiro frontend sénior com foco em React, TypeScript e segurança de conteúdo.

Implementa a experiência documental do VentureOps AI sobre a API concluída em F1-P04-PR02.

Identificação:
- Fase: F1 — MVP
- Pipeline: F1-P04
- Prompt: F1-P04-PR03
- Itens: MVP-06 e MVP-07
- Tarefas: MVP-06.T3, T4, T5 e MVP-07.T2
- Validações: VAL-004 e VAL-014, parcialmente

Objectivo:
Permitir listar, criar, visualizar, editar, pré-visualizar, consultar histórico, recuperar versões e gerir marcadores documentais através da interface.

Pré-requisitos:
- PR01 e PR02 concluídos;
- endpoints documentais funcionais;
- PortfolioWorkspace e ProductDetail existentes;
- cliente HTTP central, CSRF e autenticação funcionais.

Contexto obrigatório:
Lê apenas:
- contratos reais da API de documentos;
- implementação frontend actual;
- resultado de PR02;
- backlog MVP-06/MVP-07;
- tipos e políticas exactos definidos no backend;
- requisitos SEC-DOC relevantes.

Cria uma área documental real associada à ficha do produto.

Componentes mínimos:
- DocumentList;
- DocumentCreateForm;
- DocumentEditor;
- DocumentDetail;
- DocumentPreview;
- DocumentHistory;
- confirmação de recuperação;
- controlos is_outdated e export_policy.

Listagem:
- filtra pelo Product actual;
- apresenta título, tipo, versão actual, marcador desactualizado e política de exportação;
- permite filtrar por tipo;
- permite abrir documento;
- não carrega conteúdo integral de todos os documentos na listagem;
- suporta estados vazio, carregamento, erro e paginação.

Criação:
- título;
- tipo documental;
- conteúdo Markdown;
- marcadores opcionais;
- Product derivado da ficha actual;
- apresenta os cinco tipos com labels claras em português;
- não permite tipos arbitrários;
- não permite escolher organisation.

Editor:
- textarea ou editor simples;
- não introduzir editor rich-text complexo;
- apresenta versão base;
- envia expected_version;
- exige resumo de alteração curto quando fizer sentido;
- conflito 409 mostra aviso e opção de recarregar;
- nunca substitui silenciosamente o conteúdo do servidor;
- evita submissões duplicadas.

Preview:
- usa obrigatoriamente o endpoint seguro do backend;
- não renderiza Markdown bruto por innerHTML antes da sanitização;
- o único HTML inserido é o HTML sanitizado devolvido pelo backend;
- scripts, handlers e URLs perigosas não podem executar;
- links externos seguros devem usar atributos defensivos apropriados;
- blocos de código são apenas apresentação;
- não criar execução de diagramas, HTML, JavaScript ou plugins.

Histórico:
- lista número, autor, data, checksum ou resumo seguro;
- permite abrir uma versão exacta;
- recuperar exige confirmação explícita;
- explica que a recuperação cria uma nova versão;
- nunca apresenta recuperação como eliminação do histórico;
- actualiza a versão actual depois do sucesso.

Marcadores:
- is_outdated pode ser activado/desactivado;
- export_policy permite allowed, confirm e denied;
- denied deve apresentar aviso de que o documento não poderá ser seleccionado para pacote de contexto;
- não implementar ainda exportação;
- não omitir o documento da lista interna.

Integração na ficha:
- substitui apenas a parte de documentos do placeholder de contexto relacionado;
- decisões e pendências continuam como indisponíveis até PR04/PR05;
- não criar contagens simuladas.

Testes obrigatórios:
1. estado vazio;
2. criação de documento;
3. selecção dos cinco tipos;
4. tipo inválido não pode ser enviado pela UI;
5. preview segura;
6. tentativa de script não executa;
7. javascript: não permanece no HTML;
8. edição cria nova versão;
9. conflito 409 permite recarregar;
10. histórico lista versões;
11. abertura de versão exacta;
12. recuperação exige confirmação;
13. recuperação cria nova versão na UI;
14. is_outdated pode ser alterado;
15. export_policy pode ser alterada;
16. denied apresenta aviso;
17. listagem não recebe conteúdo integral;
18. autenticação, empresa e portefólio continuam funcionais;
19. build e testes passam.

Demonstração ao vivo:
- autenticar;
- abrir um Product;
- criar documento de visao_de_produto;
- escrever Markdown com títulos, lista, link e bloco de código;
- tentar conteúdo XSS controlado;
- confirmar preview segura;
- editar para criar v2;
- abrir v1;
- recuperar v1, criando v3;
- marcar como desactualizado;
- definir export_policy denied;
- confirmar os dados no backend e no armazenamento.

Não implementar:
- comparação lado a lado;
- pesquisa;
- upload de ficheiros;
- exportação;
- integração com IA;
- documentos de resultado automáticos.

Fecho:
- cria prompt_03_resultado.md;
- actualiza F1-P04 para 3/6 concluídos;
- actualiza painel, diário e matriz com evidência de UI e segurança.

Expectativa verificável:
- gestão documental é utilizável no browser;
- preview não executa conteúdo;
- histórico e recuperação funcionam;
- marcadores são visíveis e editáveis;
- ficha do produto mostra documentos reais;
- próximo prompt recomendado: F1-P04-PR04;
- relatório final lista componentes, contratos, testes, demonstração, problemas e pendências.

Não avances para o prompt seguinte.
```

## Prompt 04 (opus) — Implementar decisões e substituição histórica

```prompt
Iteração 04

Actua como engenheiro full-stack sénior especializado em Django, React, histórico imutável e isolamento multi-tenant.

Implementa a gestão de decisões do VentureOps AI.

Identificação:
- Fase: F1 — MVP
- Pipeline: F1-P04
- Prompt: F1-P04-PR04
- Item: MVP-08
- Capacidade: MVP-08.C1
- Tarefas: MVP-08.T1, T2, T3 e T4
- Requisitos transversais: RT-01, RT-02, RT-04 e RT-10
- Validação: VAL-005

Objectivo:
Permitir registar, consultar e substituir decisões, preservando a cadeia histórica e ligações opcionais a Product e documento decisao_detalhada.

Pré-requisitos:
- PR01 a PR03 concluídos;
- Product funcional;
- documentos e tipos documentais funcionais;
- auditoria e contexto empresarial funcionais.

Contexto obrigatório:
Lê apenas:
- backlog MVP-08;
- artefacto de estados e transições;
- implementação real de Product e Document;
- tipos documentais;
- lista AuditAction;
- padrões de API e frontend existentes.

Cria Decision com os campos mínimos:
- UUID;
- organisation;
- title;
- context ou summary;
- decision_text ou descrição da decisão, conforme o modelo funcional vigente;
- responsible;
- decided_at;
- impact opcional;
- status active ou superseded;
- product opcional;
- detail_document opcional;
- supersedes ou replaced_by, conforme uma única direcção de relação escolhida;
- version, se necessário para proteger a substituição;
- created_at.

Regras:
- decisão nasce active;
- decisão não é eliminada;
- decisão histórica não é reescrita silenciosamente;
- responsável tem Membership activa na mesma empresa;
- Product pertence à mesma empresa;
- detail_document pertence à mesma empresa;
- detail_document tem tipo decisao_detalhada;
- se Product e documento forem ambos específicos, as associações devem ser coerentes;
- não criar workflow de aprovação;
- não criar tipos configuráveis.

API:
- listar decisões;
- criar decisão;
- consultar detalhe;
- substituir decisão activa;
- filtrar por Product e status;
- paginação simples;
- sem DELETE;
- edição comum só se estiver explicitamente permitida pelo modelo funcional; caso contrário, preservar a decisão e usar substituição.

Substituição:
- operação atómica;
- recebe os dados da nova decisão e versão esperada da anterior, se aplicável;
- cria nova decisão active;
- marca anterior superseded;
- liga a cadeia;
- não apaga nem altera a justificação histórica;
- decisão já superseded não pode ser substituída novamente;
- associação cruzada devolve 404 ou validação coerente;
- concorrência simultânea não pode criar duas substituições válidas.

Auditoria:
- usa apenas o evento 8 ou nome real equivalente;
- criação e substituição são auditadas;
- metadados contêm operação, transição e identificadores;
- não registar contexto ou decisão integral;
- tentativas cruzadas são auditadas pelo evento de segurança.

Frontend:
- secção Decisões na ficha do Product;
- listagem por estado;
- criação;
- detalhe;
- apresentação da cadeia de substituição;
- acção Substituir com confirmação;
- ligação ao documento de detalhe;
- não criar workflow de aprovação;
- não simular decisões.

Testes obrigatórios:
1. criação empresarial sem Product;
2. criação associada a Product;
3. responsável alheio rejeitado;
4. Product alheio rejeitado;
5. documento alheio rejeitado;
6. documento com tipo diferente é rejeitado;
7. listagem isolada;
8. detalhe alheio devolve 404;
9. substituição cria nova decisão;
10. anterior fica superseded;
11. cadeia é navegável;
12. decisão superseded não é substituída novamente;
13. concorrência não cria duas substituições;
14. histórico não é apagado;
15. criação e substituição auditadas;
16. conteúdo integral não entra na auditoria;
17. UI cria e consulta decisão;
18. UI substitui e mostra a cadeia;
19. build e suites passam.

Demonstração:
- criar documento decisao_detalhada;
- criar decisão ligada a Product e documento;
- substituir por nova decisão;
- confirmar cadeia e estados;
- confirmar eventos;
- remover dados de demonstração no fim, se essa for a prática vigente.

Fecho:
- cria prompt_04_resultado.md;
- actualiza F1-P04 para 4/6 concluídos;
- actualiza painel, diário e VAL-005 com evidência real;
- mantém VAL-002 e VAL-012 parciais com evidência adicional.

Expectativa verificável:
- decisões podem ser registadas e consultadas;
- substituição preserva o histórico;
- associações são isoladas;
- Product mostra decisões reais;
- auditoria é segura;
- próximo prompt recomendado: F1-P04-PR05;
- relatório final lista modelo, contratos, cadeia, testes, UI, eventos e reservas.

Não avances para o prompt seguinte.
```

## Prompt 05 (opus) — Implementar pendências tipificadas

```prompt
Iteração 05

Actua como engenheiro full-stack sénior especializado em regras de negócio simples, datas, estados e isolamento multi-tenant.

Implementa a gestão mínima de pendências administrativas do VentureOps AI.

Identificação:
- Fase: F1 — MVP
- Pipeline: F1-P04
- Prompt: F1-P04-PR05
- Item: MVP-09
- Capacidade: MVP-09.C1
- Tarefas: MVP-09.T1, T2, T3 e T4
- Requisitos transversais: RT-01, RT-02, RT-09 e RT-10
- Validação: VAL-006

Objectivo:
Permitir criar, editar, consultar, concluir e cancelar pendências com os cinco tipos fechados, sem transformar o produto num gestor de projectos.

Pré-requisitos:
- PR01 a PR04 concluídos;
- Product e Decision funcionais;
- autenticação, contexto empresarial e auditoria funcionais.

Contexto obrigatório:
Lê apenas:
- backlog MVP-09;
- artefacto de estados e transições;
- artefacto de regras de atenção, apenas R-AT-02 e R-AT-03;
- DEC-F0-FINAL-07;
- implementação real de Product e Decision;
- lista AuditAction;
- padrões de API e frontend vigentes.

Cria WorkItem com:
- UUID;
- organisation;
- product obrigatório, salvo se o artefacto vigente permitir pendência empresarial;
- decision opcional;
- title;
- work_type;
- responsible;
- priority segundo a enumeração vigente;
- due_at ou due_date;
- context ou notes opcional;
- status open, completed ou cancelled;
- version para concorrência optimista;
- completed_at opcional;
- cancelled_at opcional;
- created_at;
- updated_at.

Tipos fechados:
- action;
- review;
- validation;
- obligation;
- decision_follow_up.

Regras:
- tipo é atributo, não estado;
- um único ciclo de vida para todos os tipos;
- estado inicial open;
- transições permitidas: open→completed e open→cancelled;
- completed e cancelled são finais;
- não reabrir no MVP;
- não eliminar fisicamente;
- responsible tem Membership activa na mesma empresa;
- Product pertence à mesma empresa;
- Decision opcional pertence à mesma empresa;
- se houver Product e Decision, a associação deve ser coerente;
- is_overdue é calculado a partir do prazo e status, nunca persistido;
- decision_follow_up alimentará a regra de atenção futura;
- não implementar agora o painel de atenção.

API:
- listar com filtros Product, status, work_type, responsible e vencimento;
- criar;
- consultar;
- editar enquanto open;
- concluir;
- cancelar;
- paginação e ordenação determinística;
- expected_version em operações mutáveis;
- 409 em versão obsoleta;
- 404 para acesso cruzado;
- sem DELETE.

Auditoria:
- usa apenas evento 9 ou nome real equivalente;
- criação, edição, conclusão e cancelamento são auditados;
- metadados sem contexto ou notes integrais;
- tentativas cruzadas usam o evento de segurança.

Frontend:
- secção Pendências na ficha do Product;
- lista curta com título, tipo, prioridade, responsável, prazo e estado;
- criação;
- edição enquanto open;
- concluir;
- cancelar com confirmação;
- filtros mínimos;
- sinal visual de vencida calculado;
- ligação opcional à Decision;
- não criar quadro kanban, sprint, backlog, bug, história ou dependência.

Testes obrigatórios:
1. criação com cada um dos cinco tipos;
2. tipo inválido rejeitado;
3. estado inicial open;
4. prioridade inválida rejeitada;
5. prazo persistido;
6. vencimento calculado para pendência open;
7. completed não é vencida;
8. cancelada não é vencida;
9. conclusão válida;
10. cancelamento válido;
11. transição a partir de estado final devolve 409;
12. edição de estado final é rejeitada;
13. responsável alheio rejeitado;
14. Product alheio rejeitado;
15. Decision alheia rejeitada;
16. ligação Product–Decision incoerente rejeitada;
17. filtros e paginação isolados;
18. concorrência não produz dupla transição;
19. operações auditadas;
20. conteúdo integral não entra na auditoria;
21. UI cria, conclui e cancela;
22. UI apresenta vencimento;
23. sem conceitos de gestão de projectos;
24. suites e build passam.

Demonstração:
- criar as cinco tipologias;
- associar uma decision_follow_up a uma Decision;
- concluir uma;
- cancelar outra;
- deixar uma vencida;
- confirmar estados na UI e backend;
- confirmar auditoria.

Fecho:
- cria prompt_05_resultado.md;
- actualiza F1-P04 para 5/6 concluídos;
- actualiza painel, diário e VAL-006;
- mantém VAL-002 e VAL-012 parciais com evidência adicional.

Expectativa verificável:
- pendências são acompanháveis até conclusão ou cancelamento;
- cinco tipos funcionam;
- vencimento é calculado;
- associações são isoladas;
- não existe gestor de projectos disfarçado;
- próximo prompt recomendado: F1-P04-PR06;
- relatório final lista modelo, transições, contratos, testes, UI, auditoria e reservas.

Não avances para o prompt seguinte.
```

## Prompt 06 (opus) — Validar integrações e encerrar F1-P04

```prompt
Iteração 06

Actua como revisor técnico sénior e conclui F1-P04 através de validação integrada, correcção de defeitos concretos e fecho de governação.

Identificação:
- Fase: F1 — MVP
- Pipeline: F1-P04 — Documentos, tipos, decisões e pendências
- Prompt: F1-P04-PR06
- Itens: MVP-06, MVP-07, MVP-08 e MVP-09
- Validações principais: VAL-004, VAL-005 e VAL-006
- Validações reforçadas: VAL-002, VAL-012 e VAL-014
- Tipo: integração, segurança, regressão e fecho

Objectivo:
Validar ponta a ponta os documentos versionados, tipos, decisões e pendências, integrar as áreas reais na ficha do produto e corrigir apenas defeitos encontrados.

Não criar novas funcionalidades nem iniciar F1-P05.

Pré-requisitos:
- PR01 a PR05 concluídos;
- F1-P03 concluída;
- aplicação e Docker Compose funcionais;
- suites anteriores verdes.

Contexto obrigatório:
Lê apenas:
- critérios de conclusão de MVP-06 a MVP-09;
- matriz VAL;
- resultados PR01 a PR05;
- código actual de documents, decisions, work_items e portfolio;
- componentes frontend associados;
- status, painel e diário.

Integração final na ficha:
- Documentos apresenta documentos reais do Product;
- Decisões apresenta decisões reais e cadeia de substituição;
- Pendências apresenta pendências reais e estados;
- Execuções continua identificada como indisponível até F1-P05;
- nenhuma contagem ou entidade é simulada;
- agregados derivam das associações, não de campos duplicados no Product.

Executa cenário documental:
1. criar Product;
2. criar documento visao_de_produto;
3. confirmar v1 no armazenamento privado;
4. editar e criar v2;
5. abrir v1;
6. recuperar v1 e criar v3;
7. confirmar histórico imutável;
8. marcar is_outdated;
9. testar allowed, confirm e denied;
10. confirmar que denied não é omitido internamente;
11. confirmar que não existe ainda geração de pacote;
12. testar preview com XSS, HTML bruto, javascript:, links e blocos de código.

Executa cenário de decisão:
1. criar documento decisao_detalhada;
2. criar decisão ligada ao Product e documento;
3. substituir a decisão;
4. confirmar active/superseded;
5. confirmar cadeia histórica;
6. confirmar ausência de edição destrutiva.

Executa cenário de pendência:
1. criar os cinco tipos;
2. ligar decision_follow_up à decisão;
3. concluir uma;
4. cancelar outra;
5. manter uma vencida;
6. confirmar que estados finais não transitam;
7. confirmar is_overdue calculado.

Isolamento:
- usa duas empresas;
- testa listagem, detalhe, edição, recuperação e marcadores de documento;
- testa decisão e substituição;
- testa pendência e transições;
- acessos cruzados devolvem resposta indistinguível de recurso inexistente;
- tentativas relevantes são auditadas;
- filtros não revelam contagens externas.

Concorrência:
- duas edições documentais na mesma versão;
- duas recuperações concorrentes;
- duas substituições da mesma decisão;
- duas transições da mesma pendência;
- executa os testes concorrentes repetidamente;
- exactamente uma operação incompatível deve vencer;
- sem lost update, versões duplicadas ou cadeias divergentes.

Armazenamento:
- checksum corresponde ao conteúdo;
- current_version nunca aponta para ficheiro inexistente;
- falha de storage não cria versão;
- objectos não são públicos;
- nomes/chaves são gerados no servidor;
- path traversal é rejeitado;
- não declarar transacção distribuída inexistente;
- registar qualquer limitação residual honestamente.

Auditoria:
- eventos documentais 5–7;
- decisão evento 8;
- pendência evento 9;
- eventos de acesso cruzado e falha de storage;
- correlation_id;
- ausência de Markdown, contexto, decisão, notes ou conteúdo integral nos metadados;
- VAL-012 permanece parcial até consolidação em F1-P07.

Migrações:
- drift zero;
- aplicar em base vazia;
- aplicar em base existente;
- reversibilidade estrutural numa base controlada;
- não sugerir que reverter migrações preserva conteúdo documental ou dados do módulo;
- confirmar que dados de outras aplicações permanecem intactos.

Regressão:
- suite backend completa;
- suite frontend completa;
- build frontend;
- health live e ready;
- autenticação;
- recuperação;
- perfil;
- onboarding;
- portefólio;
- concorrência de Product;
- armazenamento;
- auditoria append-only;
- Docker Compose.

Estados VAL:
- VAL-004 pode ser Validada se criação, edição, versões, histórico e recuperação forem demonstrados;
- VAL-005 pode ser Validada se decisão, associação e substituição forem demonstradas;
- VAL-006 pode ser Validada se pendências e transições forem demonstradas;
- VAL-014 permanece Parcial porque prompt injection e restantes controlos serão consolidados em F1-P07;
- VAL-002 permanece Parcial até todos os módulos e suite transversal;
- VAL-012 permanece Parcial até consolidação global.

Integrações adiadas:
- tipo instrucoes com função → F1-P05;
- tipo resultado com execução/resultado → F1-P05/F1-P06;
- aplicação efectiva de export_policy no pacote → F1-P05;
- atenção por documento/pendência/decisão → F1-P07;
- pesquisa e comparação de versões → V1.

Correcções permitidas:
- defeitos de isolamento;
- falhas de segurança;
- inconsistências de versões;
- erros de armazenamento;
- contratos incorrectos;
- falhas de UI;
- testes instáveis;
- auditoria incompleta.

Não permitir:
- refactorização ampla;
- pesquisa;
- exportação;
- motor de workflow;
- gestão de projectos;
- novos tipos;
- novas infra-estruturas;
- geração automática de F1-P05.

Governança:
1. cria prompt_06_resultado.md;
2. actualiza F1-P04 para Concluída, 6/6, se todos os critérios passarem;
3. define estado de revisão segundo o guia, sem confundir execução técnica com revisão humana;
4. actualiza VAL-004, VAL-005 e VAL-006 com evidências;
5. mantém VAL-002, VAL-012 e VAL-014 parciais;
6. actualiza painel e diário de forma curta;
7. não altera artefactos da Fase 0;
8. não cria decisão global sem desvio estrutural real.

O resultado deve incluir:
- veredicto;
- modelos e contratos finais;
- política BD/Markdown;
- estratégia de armazenamento;
- política de versões e recuperação;
- sanitização;
- tipos documentais;
- decisões e cadeia;
- pendências e transições;
- integrações na ficha;
- isolamento;
- concorrência;
- auditoria;
- migrações;
- testes e demonstração;
- VAL actualizadas;
- problemas corrigidos;
- reservas;
- estado final;
- próximo passo.

Expectativa verificável:
- F1-P04 está Concluída com 6/6;
- VAL-004, VAL-005 e VAL-006 estão Validadas, se houver evidência completa;
- VAL-002, VAL-012 e VAL-014 permanecem parciais;
- documentos, decisões e pendências são utilizáveis no browser;
- nenhuma funcionalidade de F1-P05 foi antecipada;
- próximo passo recomendado: efectuar commit de F1-P04 e gerar F1-P05 just-in-time.

Não avances para F1-P05.
```
