
# Pipeline: Resultados, revisão e aplicação controlada

## Prompt 01 (opus) — Registar tentativas imutáveis de resultado

```prompt
Iteração 01
Actua como engenheiro backend sénior especializado em Django, PostgreSQL, armazenamento privado, máquinas de estado e rastreabilidade.

Implementa o registo manual e imutável dos resultados externos associados às execuções do VentureOps AI.

Identificação:
- Fase: F1 — MVP
- Pipeline: F1-P06 — Resultados, revisão e aplicação controlada
- Prompt: F1-P06-PR01
- Item: MVP-13
- Capacidade: MVP-13.C1
- História: MVP-13.H1
- Tarefas: MVP-13.T1, MVP-13.T3 e MVP-13.T4, parcialmente
- Requisitos transversais: RT-01, RT-02, RT-03, RT-05, RT-07, RT-09 e RT-10
- Validação preparada: VAL-009

Condição de entrada:
- confirma que F1-P05 está Concluída, 6/6;
- confirma que o código de F1-P05 está commitado ou que a árvore de trabalho não contém alterações não relacionadas;
- confirma que AIExecution, Document, DocumentVersion, armazenamento e auditoria estão funcionais;
- se existir defeito estrutural pendente em F1-P05, não alteres código e regista o bloqueio;
- não corrijas silenciosamente módulos anteriores.

Objectivo:
Permitir importar manualmente um resultado produzido fora da aplicação, materializá-lo como documento do tipo resultado, criar uma tentativa imutável e transitar a execução de prepared para result_pending_validation.

O resultado verificável deve provar:
- resultado associado à execução correcta;
- tentativa numerada e imutável;
- conteúdo guardado no armazenamento privado;
- estado alterado apenas para result_pending_validation;
- nenhuma aprovação ou aplicação automática.

Contexto obrigatório:
Lê apenas:
- docs/gestao/03_fase_1_mvp/01_backlog.md: MVP-13;
- docs/gestao/03_fase_1_mvp/02_mapa_pipelines.md: F1-P06;
- artefactos 02, 03, 05, 07 e 10 da Fase 0, apenas as secções sobre E4, estados, fonte de verdade, importação e SEC-HUM;
- DEC-F0-FINAL-05 e CLR-04;
- resultado final de F1-P05-PR06;
- código actual de executions, documents, storage, organisations e audit;
- lista fechada AuditAction;
- política central de transições criada em F1-P05.

Inspecção inicial:
1. Confirma os nomes reais dos estados da execução.
2. Confirma o serviço público usado para criar documentos e versões.
3. Confirma a coordenação actual entre BD e armazenamento.
4. Confirma os eventos 13–17 existentes na lista fechada.
5. Confirma como são implementados expected_version, select_for_update e erros 409.
6. Não assumes nomes de classes, serviços ou eventos sem inspeccionar o código.

Cria ResultAttempt no módulo executions com:
- id UUID;
- organisation obrigatória;
- execution obrigatória;
- attempt_number inteiro positivo;
- result_document_version obrigatória;
- imported_by obrigatório;
- source_mode fechado: pasted ou file;
- source_tool obrigatório;
- source_model opcional;
- source_notes opcional e curto;
- created_at.

Regras de ResultAttempt:
- é append-only;
- não pode ser actualizado nem eliminado por instância ou queryset;
- execution + attempt_number é único;
- cada tentativa referencia uma DocumentVersion exacta;
- DocumentVersion pertence a um Document do tipo resultado;
- documento e execução pertencem à mesma Organisation;
- documento está associado ao Product da execução;
- conteúdo nunca é guardado em ResultAttempt ou AIExecution;
- tentativa 1 é a primeira importação;
- após pedido de correcção, a nova importação cria tentativa 2, 3, etc.;
- uma tentativa anterior nunca é substituída;
- o cliente não escolhe attempt_number;
- relações históricas usam PROTECT.

Acrescenta a AIExecution:
- current_result_attempt opcional, gerado no servidor;
- aponta apenas para uma tentativa da própria execução;
- nunca é fornecido pelo cliente;
- preserva a tentativa actual mesmo depois de aprovação, rejeição ou conclusão;
- qualquer migração deve ser aditiva e segura para execuções prepared existentes.

Importação:
- disponível apenas quando execution.status=prepared;
- exige expected_version da execução;
- aceita exactamente uma das entradas:
  - content, texto Markdown colado;
  - file, ficheiro Markdown ou texto UTF-8;
- rejeita ambas ou nenhuma;
- source_tool é obrigatório;
- source_model e source_notes são opcionais;
- source_mode é derivado no servidor;
- aplica o mesmo limite de bytes documental;
- ficheiro binário ou UTF-8 inválido é rejeitado;
- nome original do ficheiro não é usado como storage_key;
- não guardar caminho local, cookie, token ou metadados sensíveis;
- resultado é tratado como conteúdo não confiável.

Documento de resultado:
- criar Document com document_type=resultado;
- associar ao Product da execução;
- gerar título determinístico e legível com execução e tentativa;
- criar exactamente uma DocumentVersion inicial;
- conteúdo exclusivamente no armazenamento privado;
- result_document_version da tentativa aponta para essa versão exacta;
- a política de exportação deve seguir a decisão vigente do módulo documental, sem inventar excepções silenciosas;
- documentos de resultado criados por uma tentativa são geridos pela execução;
- a API documental genérica não pode criar arbitrariamente documentos do tipo resultado depois desta implementação;
- a API documental genérica não pode editar ou recuperar um documento já ligado a ResultAttempt;
- leitura continua permitida;
- caso existam documentos resultado anteriores, não os apagar nem converter silenciosamente; regista a política de compatibilidade.

Operação atómica:
1. bloqueia AIExecution;
2. valida expected_version e estado prepared;
3. determina attempt_number;
4. valida e escreve o objecto no storage;
5. cria Document, DocumentVersion e ResultAttempt;
6. define current_result_attempt;
7. aplica a transição prepared→result_pending_validation através da política central;
8. incrementa AIExecution.version exactamente uma vez;
9. emite auditoria;
10. confirma a transacção.

Coordenação BD↔storage:
- falha de escrita não cria documento, versão, tentativa ou transição;
- falha de BD depois da escrita tenta remover o objecto órfão;
- se a limpeza falhar, usa storage.failure;
- current_result_attempt nunca aponta para tentativa incompleta;
- execução nunca muda de estado se a importação falhar;
- não declarar transacção distribuída inexistente.

API recomendada:
- POST /api/v1/executions/{execution_id}/result-attempts
- GET /api/v1/executions/{execution_id}/result-attempts
- GET /api/v1/executions/{execution_id}/result-attempts/{attempt_number}

Podes ajustar caminhos às convenções reais.

POST:
- suporta JSON para content;
- suporta multipart/form-data para file;
- mantém CSRF e sessão;
- rejeita organisation, attempt_number, document ids, status e campos internos;
- devolve tentativa, metadados da versão exacta e estado actualizado da execução.

Listagem:
- ordem crescente por attempt_number;
- não devolve conteúdo integral;
- inclui source_tool, source_model, source_mode, checksum, byte_size, versão documental e data;
- não revela caminhos de storage.

Detalhe:
- devolve metadados e conteúdo da versão exacta da tentativa;
- nunca usa Document.current_version para substituir a versão;
- inclui contexto mínimo da execução necessário à revisão;
- não devolve pacote integral de contexto;
- não devolve segredos ou auditoria interna.

Auditoria:
- usa exclusivamente o evento real correspondente a result.imported;
- entity deve permitir relacionar evento com execução e tentativa;
- metadados mínimos: operation, attempt_number, source_mode, document_id, document_version_id, checksum abreviado e execution_version;
- não incluir resultado, source_notes, source_tool completo quando sensível, prompt, pacote ou conteúdo;
- acesso cruzado usa security.cross_org_attempt.

Testes obrigatórios:
1. importação por content cria tentativa 1;
2. importação por file cria tentativa;
3. ambas as entradas são rejeitadas;
4. ausência de conteúdo é rejeitada;
5. conteúdo acima do limite devolve 413;
6. UTF-8 inválido é rejeitado;
7. source_tool obrigatório;
8. execução nasce prepared antes da importação;
9. importação transita para result_pending_validation;
10. importação não aprova;
11. importação não altera Product, documentos existentes, decisões ou pendências;
12. tentativa referencia versão exacta;
13. conteúdo não fica na BD;
14. checksum corresponde ao ficheiro;
15. tentativa é imutável;
16. attempt_number é atribuído no servidor;
17. segunda importação enquanto result_pending_validation devolve 409;
18. versão obsoleta da execução devolve 409;
19. duas importações concorrentes produzem exactamente uma tentativa;
20. falha de storage não altera execução;
21. falha de BD tenta limpar objecto;
22. documento resultado não pode ser criado pela API genérica;
23. documento ligado a tentativa não pode ser alterado pela API genérica;
24. listagem não devolve conteúdo;
25. detalhe devolve a versão exacta;
26. execução alheia devolve 404 indistinguível e é auditada;
27. auditoria não contém resultado integral;
28. migrações aplicam sem drift;
29. suite anterior permanece verde.

Não implementar:
- interface frontend;
- revisão;
- aprovação;
- rejeição;
- pedido de correcção;
- aplicação;
- parsing estruturado;
- chamada a IA;
- importação automática;
- anexos binários;
- comparação de resultados.

Fecho:
- cria docs/gestao/03_fase_1_mvp/pipelines/06_resultados_revisao_aplicacao/resultados_execucao/prompt_01_resultado.md;
- actualiza F1-P06 como Em execução, 1/6 concluído;
- actualiza painel, diário e matriz apenas com evidência real;
- VAL-009 permanece Parcial até UI e validação integrada;
- não valida VAL-010;
- não cria decisão global salvo desvio estrutural real.

Expectativa verificável:
- resultado externo pode ser importado;
- tentativa imutável e numerada é criada;
- conteúdo fica no armazenamento;
- execução passa apenas para result_pending_validation;
- nenhuma aprovação ou aplicação ocorre;
- testes e migrações passam;
- próximo prompt recomendado: F1-P06-PR02;
- relatório final lista modelo, contratos, transição, storage, testes, auditoria, problemas e pendências.

Não avances para o prompt seguinte.
```

## Prompt 02 (sonnet) — Criar a interface de importação e histórico de tentativas

```prompt
Iteração 02
Actua como engenheiro frontend sénior especializado em React, TypeScript, upload seguro e apresentação de conteúdo não confiável.

Implementa a interface de importação, consulta e histórico dos resultados de uma execução.

Identificação:
- Fase: F1 — MVP
- Pipeline: F1-P06
- Prompt: F1-P06-PR02
- Item: MVP-13
- Capacidade: MVP-13.C1
- História: MVP-13.H1 e MVP-13.H2
- Tarefas: MVP-13.T2 e MVP-13.T3
- Validações: VAL-009 e VAL-014, parcialmente

Objectivo:
Permitir que o utilizador importe manualmente um resultado por texto ou ficheiro, consulte a tentativa exacta e veja o histórico preservado, sem aprovar ou aplicar.

Pré-requisitos:
- PR01 concluído;
- endpoints de ResultAttempt funcionais;
- ExecutionDetail e cliente HTTP central existentes;
- preview segura de Markdown existente.

Contexto obrigatório:
Lê apenas:
- contratos reais implementados em PR01;
- componentes actuais de execução e pacote;
- cliente HTTP central;
- preview documental segura;
- resultado de PR01;
- backlog MVP-13.

Integração:
- acrescenta ResultAttemptsPanel ao ExecutionDetail;
- preserva snapshots, contexto e ContextPackagePanel;
- em status prepared apresenta importação;
- em result_pending_validation apresenta tentativa actual e indicação de revisão pendente;
- em approved, rejected ou completed apresenta histórico em modo leitura;
- não apresenta botões de revisão ou aplicação nesta etapa.

Cliente HTTP:
- reutiliza o cliente central;
- acrescenta apenas suporte mínimo a multipart/form-data, se ainda não existir;
- mantém sessão, CSRF e tratamento uniforme de erros;
- não define manualmente Content-Type multipart quando o browser precisa gerar boundary;
- não cria segundo cliente HTTP.

Formulário de importação:
- escolha explícita entre Colar resultado e Carregar ficheiro;
- content em textarea;
- file limitado a formatos textuais coerentes com o backend;
- source_tool obrigatório;
- source_model opcional;
- source_notes opcional;
- mostra o limite de tamanho;
- envia expected_version actual da execução;
- evita submissão duplicada;
- não permite enviar content e file ao mesmo tempo;
- pede confirmação antes de importar, explicando:
  - importar regista uma tentativa;
  - importar não aprova;
  - importar não aplica alterações;
  - a tentativa ficará imutável.

Depois da importação:
- actualiza o detalhe;
- mostra status Resultado por validar;
- abre a tentativa criada;
- não mostra qualquer dado como oficial;
- não altera documentos, decisões ou pendências na UI.

Histórico:
- lista attempt_number, data, origem, modo, modelo quando exista, checksum e versão documental;
- ordem crescente;
- tentativa actual identificada;
- permite abrir qualquer tentativa;
- nunca usa o current_version actual do Document para substituir a versão da tentativa;
- não permite editar ou eliminar;
- não permite recuperar versões de documento de resultado;
- prepara espaço para revisão futura sem a implementar.

Apresentação do resultado:
- disponibiliza duas vistas simples:
  - texto original em pre/textarea read-only;
  - preview segura usando o endpoint backend já existente;
- nunca renderiza Markdown directamente no browser;
- apenas HTML sanitizado devolvido pelo backend pode ser inserido;
- scripts, handlers e URLs perigosas não executam;
- código é texto;
- preview não altera o conteúdo guardado.

Ficheiro:
- mostra apenas o nome local antes da submissão;
- não persiste nome ou caminho no browser;
- não usa FileReader para executar ou interpretar HTML;
- tamanho pode ser validado preventivamente, mas o backend continua a ser autoridade;
- erro 413 deve ser apresentado claramente.

Conflitos:
- 409 por estado ou versão deve recarregar a execução;
- não repetir automaticamente a importação;
- se outra tentativa tiver sido criada, apresentar o estado actual;
- não perder o conteúdo local sem aviso quando ocorrer conflito.

Testes obrigatórios:
1. formulário aparece apenas em prepared;
2. importação por texto;
3. importação por ficheiro;
4. source_tool obrigatório;
5. ambas as entradas não podem coexistir;
6. confirmação explica importar≠aprovar≠aplicar;
7. submissão duplicada evitada;
8. erro 413 apresentado;
9. erro 409 recarrega o estado;
10. após importar aparece result_pending_validation;
11. tentativa actual é apresentada;
12. histórico lista várias tentativas;
13. abertura de tentativa histórica usa conteúdo exacto;
14. resultado não é editável;
15. resultado não é eliminável;
16. preview usa o backend;
17. conteúdo hostil não executa;
18. texto original é mostrado como texto;
19. nenhuma acção de aprovação existe;
20. nenhuma acção de aplicação existe;
21. Product, documentos, decisões e pendências não mudam;
22. regressão de execuções e pacote permanece verde;
23. build e suite passam.

Demonstração:
- reconstruir frontend e backend no Compose;
- criar ou reutilizar execução prepared;
- gerar pacote manualmente;
- simular resultado externo com dados não sensíveis;
- importar por texto;
- confirmar tentativa 1 e estado result_pending_validation;
- abrir preview segura e texto original;
- não aprovar;
- não aplicar;
- confirmar no backend que nenhuma entidade oficial foi alterada.

Fecho:
- cria prompt_02_resultado.md;
- actualiza F1-P06 para 2/6 concluídos;
- actualiza painel, diário e matriz;
- VAL-009 permanece Parcial;
- VAL-014 permanece Parcial.

Expectativa verificável:
- resultado pode ser importado no browser;
- tentativa e histórico são consultáveis;
- conteúdo não confiável é apresentado com segurança;
- nenhuma revisão ou aplicação foi antecipada;
- próximo prompt recomendado: F1-P06-PR03;
- relatório final lista componentes, contratos, testes, demonstração, problemas e pendências.

Não avances para o prompt seguinte.
```

## Prompt 03 (opus) — Implementar revisão humana e histórico de decisões

```prompt
Iteração 03
Actua como engenheiro full-stack sénior especializado em máquinas de estado, registos append-only, autorização e controlo humano.

Implementa a revisão humana dos resultados importados.

Identificação:
- Fase: F1 — MVP
- Pipeline: F1-P06
- Prompt: F1-P06-PR03
- Item: MVP-14
- Capacidade: MVP-14.C1
- Histórias: MVP-14.H1 e MVP-14.H2
- Tarefas: MVP-14.T1, MVP-14.T2, MVP-14.T3 e MVP-14.T4
- Requisitos transversais: RT-01, RT-02, RT-05, RT-09 e RT-10
- Validação principal: VAL-010
- Validação reforçada: VAL-009

Objectivo:
Permitir ao Owner rever uma tentativa, aprovar, rejeitar ou pedir correcção, preservando o histórico e provando que aprovar não aplica nenhuma alteração oficial.

Pré-requisitos:
- PR01 e PR02 concluídos;
- execução em result_pending_validation;
- ResultAttempt imutável;
- política central de transições disponível;
- auditoria funcional.

Contexto obrigatório:
Lê apenas:
- backlog MVP-14;
- artefacto de estados e transições;
- requisitos SEC-HUM-01..06 e SEC-AUT-02;
- DEC-F0-FINAL-05 e CLR-04;
- implementação real de AIExecution e ResultAttempt;
- lista AuditAction;
- resultado de PR01 e PR02.

Cria ResultReview com:
- id UUID;
- organisation obrigatória;
- execution obrigatória;
- result_attempt obrigatória;
- reviewer obrigatório;
- decision fechada:
  - approved;
  - rejected;
  - correction_requested;
- observations opcional para aprovação;
- observations obrigatória para rejeição e pedido de correcção;
- created_at.

Regras de ResultReview:
- append-only;
- update e delete bloqueados por instância e queryset;
- uma tentativa aceita no máximo uma revisão;
- result_attempt pertence à execution;
- reviewer deriva do utilizador autenticado;
- no MVP, apenas Membership Owner activa pode rever;
- decisão não vem de campo genérico de estado;
- cada operação tem endpoint explícito;
- a revisão pertence à tentativa actual;
- tentativa histórica já revista não pode ser revista novamente;
- relações históricas usam PROTECT;
- conteúdo do resultado não é copiado para a revisão.

Comandos:

Aprovar:
- execução tem de estar result_pending_validation;
- tentativa indicada tem de ser current_result_attempt;
- expected_version obrigatório;
- cria ResultReview approved;
- aplica result_pending_validation→approved;
- incrementa execution.version exactamente uma vez;
- não cria DocumentVersion;
- não altera Product;
- não altera Decision;
- não altera WorkItem;
- não cria ResultApplication;
- não muda para completed.

Rejeitar:
- execução tem de estar result_pending_validation;
- observações obrigatórias;
- cria ResultReview rejected;
- aplica result_pending_validation→rejected;
- rejected é terminal no MVP;
- não aplica qualquer alteração oficial.

Pedir correcção:
- execução tem de estar result_pending_validation;
- observações obrigatórias;
- cria ResultReview correction_requested;
- aplica result_pending_validation→prepared;
- preserva current_result_attempt;
- preserva a tentativa e revisão;
- permite uma nova importação pelo mecanismo de PR01;
- nova tentativa recebe número seguinte;
- não elimina resultado anterior;
- não reabre uma execução rejected ou completed.

Concorrência:
- bloqueia AIExecution e ResultAttempt;
- valida expected_version;
- duas revisões concorrentes sobre a mesma tentativa produzem exactamente uma revisão;
- a segunda devolve 409;
- nenhuma dupla transição;
- constraint única em result_attempt como defesa final.

API recomendada:
- POST /api/v1/executions/{id}/result-attempts/{attempt_number}/approve
- POST /api/v1/executions/{id}/result-attempts/{attempt_number}/reject
- POST /api/v1/executions/{id}/result-attempts/{attempt_number}/request-correction
- GET /api/v1/executions/{id}/reviews

Podes ajustar caminhos às convenções reais.

Entrada:
- expected_version;
- observations;
- rejeita status, reviewer, decision e campos internos;
- nenhuma acção genérica review com decisão arbitrária.

Resposta:
- revisão criada;
- execução actualizada;
- tentativa;
- histórico mínimo;
- sem conteúdo integral na listagem de revisões.

Auditoria:
- usa os eventos reais correspondentes a resultado aprovado, rejeitado e correcção pedida;
- metadados incluem operation, attempt_number, review_id, transition e execution_version;
- não incluem resultado ou observations integrais;
- dupla revisão negada pode ser auditada como denied conforme o padrão vigente;
- acesso cruzado usa security.cross_org_attempt.

Frontend:
- acrescenta ValidationPanel ao detalhe da execução;
- aparece apenas em result_pending_validation;
- apresenta:
  - tentativa actual;
  - origem;
  - conteúdo original;
  - preview segura;
  - snapshots;
  - versões documentais de contexto;
  - histórico das tentativas e revisões;
- acções separadas:
  - Aprovar;
  - Rejeitar;
  - Pedir correcção;
- aprovação exige confirmação explícita com texto:
  - aprovar valida o resultado;
  - aprovar não aplica alterações;
  - aplicação será uma operação posterior;
- rejeição e correcção exigem observações;
- botões ficam desactivados durante submissão;
- 409 recarrega o estado;
- depois de correcção, volta ao formulário de importação;
- depois de aprovação, apresenta estado Aprovada sem botão de aplicação nesta etapa;
- depois de rejeição, apresenta estado final;
- histórico é só leitura.

Testes obrigatórios:
1. Owner aprova tentativa actual;
2. não-Owner é rejeitado;
3. aprovação muda apenas para approved;
4. aprovação não cria versões documentais;
5. aprovação não altera Product;
6. aprovação não altera Decision;
7. aprovação não altera WorkItem;
8. aprovação não cria aplicação;
9. rejeição exige observações;
10. rejeição muda para rejected;
11. rejected é terminal;
12. correcção exige observações;
13. correcção volta a prepared;
14. tentativa anterior permanece;
15. revisão anterior permanece;
16. nova importação após correcção cria tentativa seguinte;
17. tentativa histórica não pode ser revista novamente;
18. dupla revisão devolve 409;
19. duas revisões concorrentes criam exactamente uma;
20. versão obsoleta devolve 409;
21. revisão alheia devolve 404 e é auditada;
22. revisões são imutáveis;
23. eventos de aprovação, rejeição e correcção são emitidos;
24. auditoria não contém resultado ou observações integrais;
25. UI apresenta contexto completo;
26. UI aprova com confirmação;
27. UI rejeita;
28. UI pede correcção;
29. UI mostra histórico de tentativas e revisões;
30. UI não contém aplicação;
31. build e suites passam;
32. migrações sem drift.

Não implementar:
- aplicação;
- alteração automática de documentos;
- aplicação parcial;
- diffs;
- notificações;
- aprovação automática;
- excepções à revisão humana;
- chamada a IA.

Fecho:
- cria prompt_03_resultado.md;
- actualiza F1-P06 para 3/6 concluídos;
- actualiza painel, diário e matriz;
- VAL-010 permanece Parcial até aplicação e validação integrada;
- VAL-009 pode permanecer Parcial;
- não validar M1.

Expectativa verificável:
- aprovar, rejeitar e pedir correcção funcionam;
- tentativas e revisões permanecem históricas;
- aprovação não aplica alterações;
- autorização e concorrência estão demonstradas;
- próximo prompt recomendado: F1-P06-PR04;
- relatório final lista modelo, transições, endpoints, UI, testes, eventos, problemas e pendências.

Não avances para o prompt seguinte.
```

## Prompt 04 (opus) — Aplicar resultado aprovado a um documento

```prompt
Iteração 04
Actua como engenheiro full-stack sénior especializado em operações transaccionais, armazenamento privado, idempotência e controlo humano.

Implementa a primeira aplicação oficial de um resultado aprovado: criação controlada de uma nova versão documental.

Identificação:
- Fase: F1 — MVP
- Pipeline: F1-P06
- Prompt: F1-P06-PR04
- Item: MVP-15
- Capacidade: MVP-15.C1
- História: MVP-15.H1
- Tarefas: MVP-15.T1, MVP-15.T2, MVP-15.T4 e MVP-15.T5, parcialmente
- Requisitos transversais: RT-01, RT-02, RT-03, RT-05, RT-09 e RT-10
- Validações: VAL-010 e VAL-004, parcialmente

Objectivo:
Permitir que um resultado aprovado seja aplicado, por comando humano explícito, a um documento alvo através de uma nova DocumentVersion ligada à execução e à tentativa aprovada.

A aplicação não deve interpretar automaticamente o resultado nem calcular diffs.

Pré-requisitos:
- PR01 a PR03 concluídos;
- execução em approved;
- tentativa actual com ResultReview approved;
- documentos versionados e armazenamento funcionais.

Contexto obrigatório:
Lê apenas:
- backlog MVP-15;
- artefacto 05 sobre fonte de verdade e versão;
- artefacto 02 sobre E6;
- DEC-F0-FINAL-05;
- implementação real de documentos, ResultAttempt, ResultReview e AIExecution;
- serviços públicos de documentos;
- lista AuditAction.

Cria ResultApplication no módulo executions com:
- id UUID;
- organisation obrigatória;
- execution obrigatória e única;
- result_attempt obrigatória;
- review obrigatória;
- application_type fechado, inicialmente:
  - document;
  - decision;
  - work_item;
  - no_change;
- applied_by obrigatório;
- request_fingerprint SHA-256;
- rationale ou change_summary curto;
- target_document opcional;
- base_document_version opcional;
- created_document_version opcional;
- target_decision opcional;
- created_decision opcional;
- target_work_item opcional;
- created_at.

Neste prompt implementa apenas application_type=document.

Regras estruturais:
- ResultApplication é append-only;
- não pode ser alterada ou eliminada;
- uma execution tem no máximo uma aplicação ou fecho;
- result_attempt é a tentativa actual aprovada;
- review pertence à tentativa e tem decision=approved;
- execution, tentativa, revisão e alvo pertencem à mesma Organisation;
- request_fingerprint permite idempotência;
- relações usam PROTECT;
- constraints garantem coerência mínima dos campos de cada application_type;
- não usar GenericForeignKey;
- não adicionar FK de executions dentro de DocumentVersion, evitando dependência circular;
- a ligação oficial entre execução e versão criada é ResultApplication.created_document_version.

Comando de aplicação documental:
- endpoint explícito;
- apenas Owner activo;
- execution.status tem de ser approved;
- expected_execution_version obrigatório;
- target_document obrigatório;
- expected_document_version obrigatório;
- content obrigatório e explicitamente fornecido pelo utilizador;
- change_summary obrigatório;
- confirmation obrigatório com valor explícito definido pelo contrato;
- o servidor nunca extrai automaticamente conteúdo do resultado;
- o servidor nunca aplica o resultado integral por omissão;
- a UI pode pré-preencher o editor com o resultado, mas o utilizador tem de rever e confirmar o conteúdo final;
- target_document pertence ao Product da execução;
- documento empresarial ou de outro Product é rejeitado nesta versão;
- documento do tipo resultado não pode ser alvo;
- documento gerido por ResultAttempt não pode ser alvo;
- target_document não pode estar em conflito;
- cria uma nova DocumentVersion usando o serviço documental;
- preserva todas as versões anteriores;
- ResultApplication guarda base_document_version e created_document_version;
- após sucesso aplica approved→completed;
- incrementa AIExecution.version exactamente uma vez;
- a execução só passa a completed depois de versão e ResultApplication existirem.

Idempotência:
- request_fingerprint é calculado no servidor sobre representação canónica:
  - execution;
  - attempt;
  - application_type;
  - target;
  - expected versions;
  - checksum do conteúdo;
  - change_summary normalizado;
- repetir exactamente o mesmo comando depois de timeout devolve a aplicação existente sem criar nova versão;
- repetir com conteúdo, alvo ou parâmetros diferentes devolve 409;
- apenas um evento de aplicação bem-sucedida;
- a unicidade por execution é defesa final.

Atomicidade BD↔storage:
- bloqueia execution e target_document;
- valida estado e versões;
- escreve o objecto;
- cria DocumentVersion;
- cria ResultApplication;
- muda execution para completed;
- confirma tudo;
- falha de storage deixa execution approved;
- falha de BD remove objecto órfão quando possível;
- conflito deixa alvo e execução intactos;
- não existe estado completed sem ResultApplication;
- não existe ResultApplication sem versão criada.

API recomendada:
- POST /api/v1/executions/{id}/apply/document
- GET /api/v1/executions/{id}/application

Entrada:
- attempt_id ou attempt_number;
- target_document;
- expected_execution_version;
- expected_document_version;
- content;
- change_summary;
- confirmation;
- rejeita application_type arbitrário, review, created version e campos internos.

Resposta:
- ResultApplication;
- versão documental criada;
- execução completed;
- sem devolver conteúdo integral desnecessário.

Auditoria:
- usa o evento real correspondente à aplicação;
- metadados incluem application_type, attempt_number, review_id, target_document_id, base_version, created_version, checksum abreviado e transition;
- não incluir resultado, conteúdo aplicado, observations ou change_summary integral;
- falhas de storage usam storage.failure;
- tentativas sem aprovação podem ser auditadas como denied;
- acesso cruzado usa security.cross_org_attempt.

Frontend:
- acrescenta ApplicationPanel ao detalhe da execução;
- só aparece quando status=approved;
- apresenta:
  - tentativa aprovada;
  - revisão;
  - resultado original;
  - lista de documentos elegíveis do Product;
  - versão actual do alvo;
  - editor de conteúdo a aplicar;
  - change_summary;
- pode oferecer “Usar resultado como ponto de partida”, mas nunca aplicar directamente;
- exige confirmação final:
  - o conteúdo foi revisto;
  - será criada nova versão oficial;
  - a execução ficará completed;
- mostra claramente que a aprovação anterior não aplicou nada;
- conflito 409 recarrega documento e execução sem sobrescrever;
- depois do sucesso mostra versão criada e ligação à execução;
- não apresenta decisões ou pendências ainda.

Testes obrigatórios:
1. aplicação em execution approved;
2. execution prepared não pode aplicar;
3. result_pending_validation não pode aplicar;
4. rejected não pode aplicar;
5. completed não pode aplicar novamente com comando diferente;
6. tentativa tem de estar aprovada;
7. aprovação sem aplicação não altera documento;
8. conteúdo explícito é obrigatório;
9. confirmation é obrigatória;
10. target_document do Product é aceite;
11. documento empresarial é rejeitado;
12. documento de outro Product é rejeitado;
13. documento alheio é rejeitado;
14. documento resultado é rejeitado;
15. versão base exacta é guardada;
16. nova versão é criada;
17. versão anterior permanece;
18. versão criada é ligada pela ResultApplication;
19. execution passa a completed só após sucesso;
20. versão obsoleta do documento devolve 409;
21. versão obsoleta da execução devolve 409;
22. falha de storage deixa execution approved;
23. falha de BD não deixa aplicação parcial;
24. repetição idêntica é idempotente;
25. repetição diferente devolve 409;
26. duas aplicações concorrentes criam exactamente uma versão;
27. ResultApplication é imutável;
28. aplicação é auditada;
29. auditoria não contém conteúdo;
30. UI exige escolha e confirmação;
31. UI trata conflito;
32. UI mostra resultado aplicado;
33. build e suites passam;
34. drift zero.

Não implementar:
- decisão;
- pendência;
- fecho sem alteração;
- aplicação de múltiplos alvos;
- parsing automático;
- diff automático;
- rollback automático;
- aplicação parcial;
- chamada a IA.

Fecho:
- cria prompt_04_resultado.md;
- actualiza F1-P06 para 4/6 concluídos;
- actualiza painel, diário e matriz;
- VAL-010 permanece Parcial até os outros caminhos e validação integrada;
- VAL-004 recebe evidência da versão aplicada;
- M1 ainda não é declarado.

Expectativa verificável:
- resultado aprovado pode criar nova versão documental;
- a operação é explícita, idempotente e auditada;
- execução só conclui depois do sucesso;
- nenhuma aplicação sem aprovação é possível;
- próximo prompt recomendado: F1-P06-PR05;
- relatório final lista modelo, comando, atomicidade, idempotência, UI, testes, eventos e reservas.

Não avances para o prompt seguinte.
```

## Prompt 05 (opus) — Aplicar a decisão, pendência ou fechar sem alteração

```prompt
Iteração 05
Actua como engenheiro full-stack sénior especializado em comandos de domínio, transições, idempotência e segurança de aplicação.

Completa a aplicação controlada com os caminhos de decisão, pendência e fecho explícito sem alteração.

Identificação:
- Fase: F1 — MVP
- Pipeline: F1-P06
- Prompt: F1-P06-PR05
- Item: MVP-15
- Capacidade: MVP-15.C2
- História: MVP-15.H2
- Tarefas: MVP-15.T2, MVP-15.T3, MVP-15.T4 e MVP-15.T5
- Requisitos transversais: RT-01, RT-02, RT-05, RT-09 e RT-10
- Validação principal: VAL-010

Objectivo:
Permitir que uma execução approved seja concluída exactamente uma vez através de:
- substituição controlada de uma decisão;
- conclusão controlada de uma pendência;
- fecho explícito sem alteração oficial.

Pré-requisitos:
- PR01 a PR04 concluídos;
- ResultApplication e idempotência existentes;
- serviços de Decision e WorkItem funcionais;
- execução approved com tentativa e revisão aprovadas.

Contexto obrigatório:
Lê apenas:
- backlog MVP-15;
- modelos e serviços reais de Decision e WorkItem;
- ResultApplication de PR04;
- política de estados da execução;
- DEC-F0-FINAL-05;
- lista AuditAction;
- resultados de PR03 e PR04.

Regra global:
Uma execução produz no máximo uma ResultApplication.

No MVP não se aplicam múltiplas alterações oficiais a partir da mesma execução.

Esta limitação:
- deve ser explícita na UI e documentação;
- é coerente com a idempotência por execução;
- evita aplicação parcial;
- pode ser revista em versão posterior através de controlo formal;
- não deve ser contornada por endpoints distintos.

Aplicação a decisão:
- application_type=decision;
- execution.status=approved;
- decisão alvo pertence ao Product da execução e à mesma Organisation;
- decisão alvo está active;
- expected_execution_version obrigatório;
- expected_decision_version obrigatório;
- utilizador fornece explicitamente os campos da nova decisão;
- não extrair nem estruturar automaticamente o resultado;
- usa o serviço de substituição já existente;
- cria nova Decision active;
- marca anterior superseded;
- ResultApplication guarda target_decision e created_decision;
- preserva a cadeia;
- depois do sucesso, execution passa a completed;
- falha deixa execution approved e decisão intacta.

Aplicação a pendência:
- application_type=work_item;
- execution.status=approved;
- WorkItem pertence ao Product da execução e à mesma Organisation;
- WorkItem está open;
- expected_execution_version obrigatório;
- expected_work_item_version obrigatório;
- usa o comando existente de conclusão;
- não altera title, notes, tipo ou prazo automaticamente;
- ResultApplication guarda target_work_item;
- depois do sucesso, execution passa a completed;
- falha deixa execution approved e pendência open.

Fecho sem alteração:
- application_type=no_change;
- apenas execution approved;
- exige rationale não vazio;
- exige confirmação explícita de que:
  - o resultado foi aprovado;
  - nenhuma fonte oficial será alterada;
  - a execução será concluída;
- cria ResultApplication sem alvo;
- passa execution para completed;
- é auditado como fecho explícito;
- não cria documento, decisão ou pendência.

Idempotência:
- reutiliza request_fingerprint canónico de PR04;
- fingerprint inclui application_type, target, expected versions e dados explícitos relevantes;
- repetição idêntica devolve a aplicação existente;
- repetição diferente devolve 409;
- endpoints diferentes não podem aplicar a mesma execution duas vezes;
- constraint única por execution permanece a defesa final.

Atomicidade:
- bloqueia execution;
- bloqueia alvo quando existir;
- valida tentativa e review approved;
- executa mutação;
- cria ResultApplication;
- muda execution approved→completed;
- tudo na mesma transacção quando apenas BD;
- nenhuma entidade fica parcialmente alterada;
- falha de auditoria deve seguir a política transaccional vigente sem criar inconsistência.

API recomendada:
- POST /api/v1/executions/{id}/apply/decision
- POST /api/v1/executions/{id}/apply/work-item
- POST /api/v1/executions/{id}/close-without-application

Podes ajustar às convenções reais.

Aplicação a decisão recebe:
- attempt_id;
- target_decision;
- expected_execution_version;
- expected_decision_version;
- title;
- context;
- decision_text;
- impact opcional;
- decided_at opcional;
- detail_document opcional;
- confirmation.

Aplicação a pendência recebe:
- attempt_id;
- target_work_item;
- expected_execution_version;
- expected_work_item_version;
- confirmation.

Fecho recebe:
- attempt_id;
- expected_execution_version;
- rationale;
- confirmation.

Auditoria:
- usa o mesmo evento real de aplicação;
- distingue document, decision, work_item e no_change;
- regista target e entidade criada quando existir;
- regista transition approved→completed;
- não regista resultado, observações, contexto da decisão, decision_text, notes ou rationale integral;
- tentativas sem aprovação são denied;
- acesso cruzado é auditado.

Frontend:
- completa ApplicationPanel;
- oferece quatro opções:
  - Criar nova versão documental;
  - Substituir decisão;
  - Concluir pendência;
  - Fechar sem alteração;
- apresenta apenas alvos elegíveis do Product;
- decisão:
  - lista apenas active;
  - formulário explícito da nova decisão;
  - mostra a decisão substituída;
- pendência:
  - lista apenas open;
  - confirmação de conclusão;
- no_change:
  - rationale obrigatório;
  - confirmação adicional;
- nenhum formulário é preenchido automaticamente por parsing do resultado;
- o resultado pode ser consultado como referência;
- antes da confirmação mostra resumo exacto da mutação;
- após completed apresenta o ResultApplication e ligação ao alvo;
- não permite segunda aplicação;
- conflitos recarregam dados;
- aplicação não deve parecer parte da aprovação.

Testes obrigatórios:
1. decisão active pode ser substituída;
2. decisão superseded não pode ser alvo;
3. decisão de outro Product é rejeitada;
4. decisão alheia é rejeitada;
5. nova decisão fica active;
6. anterior fica superseded;
7. cadeia é preservada;
8. ResultApplication liga ambas;
9. WorkItem open pode ser concluído;
10. WorkItem final não pode ser aplicado;
11. WorkItem de outro Product é rejeitado;
12. WorkItem alheio é rejeitado;
13. conclusão preserva os outros campos;
14. no_change exige rationale;
15. no_change não altera entidades oficiais;
16. no_change conclui a execução;
17. todos os caminhos exigem aprovação;
18. todos os caminhos exigem confirmação;
19. execução completed não aceita outro caminho;
20. aplicação documental seguida de decisão é rejeitada;
21. decisão seguida de pendência é rejeitada;
22. repetição idêntica é idempotente;
23. repetição diferente devolve 409;
24. concorrência entre dois tipos deixa apenas um vencedor;
25. falha não conclui execution;
26. eventos são emitidos uma única vez;
27. auditoria não contém conteúdo integral;
28. UI apresenta quatro opções;
29. UI mostra apenas alvos elegíveis;
30. UI exige confirmação;
31. UI mostra aplicação final;
32. UI impede segunda aplicação;
33. build e suites passam;
34. drift zero.

Provas negativas obrigatórias:
- importar resultado não altera Document, Decision ou WorkItem;
- aprovar resultado não altera Document, Decision ou WorkItem;
- rejeitar não altera entidades oficiais;
- pedir correcção não altera entidades oficiais;
- apenas apply ou close-without-application pode levar a completed;
- nenhum endpoint interno permite aplicar com execution prepared;
- nenhum endpoint interno permite aplicar com result_pending_validation;
- nenhum endpoint interno permite aplicar com rejected;
- nenhum endpoint genérico contorna a ResultApplication única.

Não implementar:
- múltiplas aplicações;
- aplicação parcial;
- criação automática de pendências;
- decisão gerada automaticamente;
- parsing ou diff;
- rollback de aplicação;
- agentes;
- chamadas a IA.

Fecho:
- cria prompt_05_resultado.md;
- actualiza F1-P06 para 5/6 concluídos;
- actualiza painel, diário e matriz;
- VAL-010 permanece Parcial até PR06;
- acrescenta evidência de aplicação a VAL-004 e VAL-005/006 quando aplicável;
- não iniciar F1-P07.

Expectativa verificável:
- execução aprovada pode ser concluída por um dos quatro caminhos;
- apenas uma aplicação é possível;
- decisões e pendências são actualizadas pelos serviços existentes;
- fecho sem alteração é explícito e auditado;
- provas negativas passam;
- próximo prompt recomendado: F1-P06-PR06;
- relatório final lista contratos, idempotência, transições, UI, testes, eventos, problemas e reservas.

Não avances para o prompt seguinte.
```

## Prompt 06 (opus) — Validar o fluxo vertical e encerrar F1-P06

```prompt
Iteração 06
Actua como revisor técnico sénior e conclui F1-P06 através de validação ponta a ponta, concorrência, provas negativas de segurança, regressão e fecho de governação.

Identificação:
- Fase: F1 — MVP
- Pipeline: F1-P06 — Resultados, revisão e aplicação controlada
- Prompt: F1-P06-PR06
- Itens: MVP-13, MVP-14 e MVP-15
- Validações principais: VAL-009 e VAL-010
- Validações reforçadas: VAL-002, VAL-004, VAL-005, VAL-006, VAL-012 e VAL-014
- Validação fora desta pipeline: VAL-011, que pertence à visão de atenção em F1-P07
- Marco: M1 — fluxo vertical ponta a ponta

Objectivo:
Validar o ciclo completo:
preparar execução → gerar pacote → importar tentativa → rever → pedir correcção → importar nova tentativa → aprovar → aplicar alteração controlada → concluir execução.

Corrige apenas defeitos concretos. Não inicia F1-P07.

Pré-requisitos:
- PR01 a PR05 concluídos;
- F1-P05 concluída;
- Docker Compose funcional;
- suites anteriores verdes.

Contexto obrigatório:
Lê apenas:
- critérios de conclusão de MVP-13 a MVP-15;
- matriz VAL;
- artefactos de estados, fonte de verdade, segurança humana e auditoria;
- resultados PR01 a PR05;
- código actual de executions;
- serviços de documents, decisions e work_items;
- frontend correspondente;
- status, painel e diário.

Cenário principal E1–E6:
1. autenticar como Owner;
2. criar ou reutilizar empresa;
3. criar Product active;
4. criar documentos de contexto;
5. criar função IA;
6. preparar execução;
7. gerar pacote de contexto;
8. simular resultado externo não sensível;
9. importar tentativa 1;
10. confirmar estado result_pending_validation;
11. confirmar que nenhuma entidade oficial mudou;
12. pedir correcção com observações;
13. confirmar estado prepared;
14. confirmar preservação da tentativa 1 e review correction_requested;
15. importar tentativa 2;
16. confirmar attempt_number=2;
17. aprovar tentativa 2;
18. confirmar estado approved;
19. confirmar que aprovação não alterou entidades oficiais;
20. aplicar a um documento;
21. confirmar nova DocumentVersion;
22. confirmar ResultApplication;
23. confirmar estado completed;
24. confirmar histórico completo e auditoria.

Cenários adicionais:
- execução A:
  - aplicar a documento;
- execução B:
  - aprovar e substituir decisão;
- execução C:
  - aprovar e concluir pendência;
- execução D:
  - aprovar e fechar sem alteração;
- execução E:
  - rejeitar resultado e confirmar estado terminal;
- não reutilizar a mesma execução para múltiplas aplicações.

Tentativas e revisões:
- múltiplas tentativas preservadas;
- cada tentativa usa versão documental exacta;
- uma revisão por tentativa;
- current_result_attempt é coerente;
- tentativa e revisão são append-only;
- resultado histórico não é alterado pelo Document.current_version;
- correcção não elimina histórico;
- rejeição não elimina histórico;
- aprovação identifica a tentativa exacta.

Importar ≠ aprovar ≠ aplicar:
Produz provas negativas explícitas por snapshots/contagens/checksums antes e depois:

Após importar:
- Product inalterado;
- documentos alvo inalterados;
- decisões inalteradas;
- pendências inalteradas;
- sem ResultApplication;
- status apenas result_pending_validation.

Após aprovar:
- mesmas entidades continuam inalteradas;
- sem ResultApplication;
- status apenas approved.

Depois de aplicar:
- exactamente o alvo escolhido muda;
- existe ResultApplication;
- execução passa a completed;
- nenhum alvo não seleccionado muda.

Aplicação documental:
- versão anterior preservada;
- nova versão ligada à aplicação;
- checksum correcto;
- falha de versão devolve 409;
- falha de storage não deixa estado parcial;
- repetição idêntica é idempotente.

Aplicação a decisão:
- cadeia linear;
- anterior superseded;
- nova active;
- aplicação ligada;
- nenhuma edição destrutiva.

Aplicação a pendência:
- open→completed;
- restantes campos preservados;
- transição final válida;
- aplicação ligada.

Fecho no_change:
- rationale obrigatório;
- nenhuma entidade oficial alterada;
- aplicação de fecho existe;
- execução completed.

Isolamento:
- utiliza duas empresas;
- tentativa alheia não pode ser lida;
- revisão alheia não pode ser executada;
- aplicação alheia não pode ser executada;
- alvos de outra empresa são rejeitados;
- listagens não revelam contagens externas;
- respostas são indistinguíveis de inexistente quando o padrão vigente exigir;
- tentativas cruzadas são auditadas.

Autorização:
- utilizador autenticado sem Owner não pode rever ou aplicar;
- importação segue a autorização definida pelo modelo MVP;
- alteração do actor no payload é rejeitada;
- revisão e aplicação nunca confiam no cliente para reviewer ou applied_by.

Concorrência:
- duas importações concorrentes;
- duas revisões concorrentes;
- duas aplicações documentais concorrentes;
- duas aplicações de tipos diferentes concorrentes;
- executar testes concorrentes pelo menos três rondas;
- exactamente uma operação incompatível vence;
- sem tentativas duplicadas;
- sem reviews duplicadas;
- sem versões duplicadas;
- sem duas ResultApplication;
- sem execução completed sem aplicação.

Conteúdo:
- resultado é não confiável;
- texto e preview não executam HTML ou JavaScript;
- auditoria não contém resultado;
- aplicação documental usa apenas conteúdo explicitamente confirmado;
- nenhum parsing automático;
- nenhum conteúdo do resultado altera campos estruturados sem acção humana;
- VAL-014 permanece Parcial até consolidação F1-P07.

Auditoria:
- evento 13 de importação;
- eventos 14–16 de revisão;
- evento 17 de aplicação;
- eventos de segurança;
- storage.failure quando aplicável;
- todos com correlation_id;
- nenhum contém resultado, observações, conteúdo aplicado, snapshots, pacote, prompts ou segredos;
- VAL-012 permanece Parcial até consulta consolidada em F1-P07.

Estados:
- prepared→result_pending_validation;
- result_pending_validation→prepared por correcção;
- result_pending_validation→approved;
- result_pending_validation→rejected;
- approved→completed por apply ou no_change;
- restantes transições inválidas;
- rejected e completed terminais.

Migrações:
- makemigrations --check sem drift;
- aplicar em base vazia;
- aplicar em base existente;
- reversibilidade estrutural em base controlada;
- declarar que reverter remove tentativas, revisões e aplicações;
- preservar outras aplicações.

Regressão:
- suite backend completa;
- suite frontend completa;
- build;
- health live e ready;
- autenticação;
- onboarding;
- portefólio;
- documentos e versões;
- decisões;
- pendências;
- funções;
- execuções e pacote;
- armazenamento;
- auditoria append-only;
- Docker Compose.

Demonstração no browser:
- reconstruir imagens;
- executar o cenário principal real;
- importar tentativa por texto;
- pedir correcção;
- importar segunda tentativa por ficheiro;
- aprovar;
- aplicar a documento;
- confirmar histórico e estado completed;
- não chamar modelo real;
- usar resultado simulado não sensível;
- guardar apenas evidências mínimas no relatório, nunca conteúdo integral.

Estados VAL:
- VAL-009 pode ser Validada se resultado é associado à execução correcta, preservado e apresentado com segurança;
- VAL-010 pode ser Validada se nenhuma aplicação ocorre sem revisão humana e todos os comandos exigem aprovação;
- VAL-004 permanece Validada e recebe evidência de nova versão aplicada;
- VAL-005 e VAL-006 permanecem Validadas e recebem evidência de aplicação;
- VAL-002 permanece Parcial até suite transversal F1-P07;
- VAL-012 permanece Parcial até consulta e consolidação F1-P07;
- VAL-014 permanece Parcial até suite completa F1-P07;
- VAL-011 não deve ser alterada nesta pipeline.

Correcções permitidas:
- falhas de isolamento;
- tentativas ou reviews mutáveis;
- transições incorrectas;
- aplicação sem aprovação;
- dupla aplicação;
- falha de idempotência;
- inconsistência BD↔storage;
- erros de UI;
- auditoria com conteúdo;
- testes instáveis.

Não permitir:
- chamadas automáticas a IA;
- parsing de resultados;
- diffs automáticos;
- múltiplas aplicações por execução;
- rollback automático;
- agentes;
- filas;
- Redis;
- Celery;
- notificações;
- refactorização ampla;
- criação automática de F1-P07.

Governança:
1. cria prompt_06_resultado.md;
2. actualiza F1-P06 para Concluída, 6/6, se todos os critérios passarem;
3. mantém estado de revisão segundo o guia, sem confundir execução técnica com revisão humana;
4. actualiza VAL-009 e VAL-010;
5. acrescenta evidência às VAL já validadas sem as redefinir;
6. mantém VAL-002, VAL-012 e VAL-014 parciais;
7. não altera VAL-011;
8. regista M1 como atingido apenas com fluxo completo demonstrado;
9. actualiza painel e diário de forma curta;
10. não altera artefactos da Fase 0;
11. não cria decisão global sem desvio estrutural real.

O resultado deve incluir:
- veredicto;
- modelos e contratos finais;
- política de tentativas;
- política de revisões;
- aplicação e idempotência;
- estados e transições;
- provas importar≠aprovar≠aplicar;
- aplicação a documento;
- aplicação a decisão;
- aplicação a pendência;
- fecho no_change;
- isolamento;
- autorização;
- concorrência;
- storage;
- segurança de conteúdo;
- auditoria;
- migrações;
- testes;
- demonstração;
- VAL actualizadas;
- marco M1;
- problemas corrigidos;
- reservas;
- estado final;
- próximo passo.

Expectativa verificável:
- F1-P06 está Concluída com 6/6;
- VAL-009 e VAL-010 estão Validadas, se houver evidência completa;
- M1 está atingido;
- tentativas e revisões são imutáveis;
- nenhuma aplicação sem aprovação é possível;
- cada execução tem no máximo uma aplicação;
- fluxo E1–E6 funciona no browser;
- nenhuma IA foi chamada automaticamente;
- próximo passo recomendado: efectuar commit de F1-P06 e gerar F1-P07 just-in-time.

Não avances para F1-P07.
```
