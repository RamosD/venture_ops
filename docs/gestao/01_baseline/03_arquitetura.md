# Arquitectura de Solução — VentureOps AI

## 1. Síntese da arquitectura

### Tipo de solução

Aplicação web SaaS, multiempresa, baseada num **monólito modular**, com:

* frontend web;
* API backend;
* base de dados relacional;
* armazenamento de ficheiros Markdown;
* auditoria;
* exportação de pacotes de contexto para IA;
* integração futura com agentes locais através de API.

Não se recomenda uma arquitectura de microserviços no MVP.

### Principais componentes

1. **Frontend web**

   * gestão da empresa e dos produtos;
   * documentos;
   * decisões;
   * pendências;
   * funções humanas e de IA;
   * execuções assistidas;
   * revisões e aprovações.

2. **Backend modular**

   * regras de negócio;
   * autenticação e autorização;
   * API;
   * controlo documental;
   * preparação de contextos;
   * validação de resultados;
   * auditoria.

3. **PostgreSQL**

   * dados estruturados;
   * estados;
   * relações;
   * permissões;
   * versões;
   * auditoria;
   * metadados documentais.

4. **Armazenamento de ficheiros**

   * conteúdo Markdown;
   * versões imutáveis dos documentos;
   * resultados extensos;
   * pacotes exportados.

5. **Integrações**

   * nenhuma integração externa obrigatória para o núcleo do MVP;
   * exportação e importação manual para utilização com IA local ou externa;
   * API limitada para agentes locais numa fase posterior.

### Fluxo geral

1. O utilizador cria uma empresa e os respectivos produtos.
2. Regista dados administrativos, documentos, decisões e pendências.
3. Define funções humanas, de IA ou híbridas.
4. Selecciona um produto, uma função e os documentos necessários para uma execução.
5. A aplicação gera um pacote de contexto.
6. O pacote é utilizado numa IA local ou num serviço externo.
7. O resultado é devolvido à aplicação.
8. Um utilizador revê, aprova ou rejeita o resultado.
9. As alterações aprovadas são aplicadas de forma controlada.
10. Todas as operações relevantes ficam auditadas.

### Fronteiras do MVP

O MVP inclui:

* aplicação web;
* uma ou várias empresas por conta, conforme decisão comercial;
* produtos;
* documentos Markdown;
* decisões;
* pendências mínimas;
* funções;
* execuções assistidas;
* validação humana;
* auditoria;
* exportação.

O MVP não inclui:

* agentes autónomos;
* execução directa sobre sistemas;
* sincronização Git bidireccional;
* filas distribuídas;
* microserviços;
* pesquisa semântica;
* workflows configuráveis;
* gestão completa de projectos;
* ERP ou contabilidade.

### Decisões assumidas

* monólito modular;
* React e TypeScript no frontend;
* Django e Django REST Framework no backend;
* PostgreSQL para dados estruturados;
* ficheiros Markdown fora da base de dados;
* armazenamento de objectos em produção;
* aprovação humana antes de alterações relevantes;
* integração com IA local preparada, mas não obrigatória no MVP;
* sem Redis, Celery, Kafka ou Kubernetes por defeito.

---

## 2. Princípios arquitecturais

### 2.1. Monólito primeiro

Os módulos devem estar separados logicamente, mas executados inicialmente na mesma aplicação backend.

Separação em serviços só deverá ocorrer quando existir:

* necessidade comprovada de escala independente;
* equipas distintas;
* isolamento de segurança;
* carga significativamente diferente;
* dependência operacional justificada.

### 2.2. Simplicidade antes de flexibilidade

Não criar inicialmente:

* motores de workflow;
* sistemas genéricos de regras;
* modelos de dados configuráveis;
* barramentos de eventos;
* plugins;
* múltiplos métodos de sincronização.

### 2.3. Uma fonte oficial por tipo de informação

* PostgreSQL controla estado, relações e permissões.
* Markdown controla conteúdo documental.
* A mesma informação não deve ser editável de forma independente nos dois locais.

### 2.4. Segurança por defeito

* acesso mínimo necessário;
* isolamento entre empresas;
* validação humana;
* nenhuma execução automática de código;
* nenhuma alteração automática de documentos no MVP;
* tokens e credenciais fora do código;
* logs sem conteúdo sensível.

### 2.5. Humano no circuito

Uma resposta de IA não constitui:

* decisão aprovada;
* tarefa concluída;
* documento actualizado;
* verdade oficial.

A passagem para estado aprovado exige uma acção explícita de um utilizador autorizado.

### 2.6. API como fronteira funcional

Frontend, integrações futuras e agentes locais devem comunicar através de uma API controlada.

A IA não deverá aceder directamente à base de dados.

### 2.7. Ficheiros portáveis

Os documentos devem poder ser exportados como Markdown normal, sem formato proprietário obrigatório.

### 2.8. Evolução incremental

A solução deve suportar evolução sem exigir que funcionalidades futuras sejam implementadas antecipadamente.

### 2.9. Observabilidade proporcional

Começar com:

* logs estruturados;
* identificadores de correlação;
* auditoria funcional;
* health checks;
* monitorização básica de erros.

Não introduzir uma plataforma pesada de observabilidade no MVP.

### 2.10. Compatibilidade com a stack existente

Caso o repositório actual já utilize React, Django, DRF, PostgreSQL, Docker e CI/CD, estes padrões devem ser reutilizados.

Se existir autenticação ou estrutura comum, deve ser integrada em vez de substituída.

---

## 3. Componentes principais

| Componente               | Responsabilidade                  | Tecnologia recomendada                                        | Dependências               | Principais riscos                            | Estado      |
| ------------------------ | --------------------------------- | ------------------------------------------------------------- | -------------------------- | -------------------------------------------- | ----------- |
| Frontend                 | Interface e fluxos do utilizador  | React, TypeScript e biblioteca visual já utilizada            | API backend                | Complexidade excessiva da UI                 | Obrigatório |
| Backend                  | Regras de negócio e API           | Django e Django REST Framework                                | PostgreSQL e armazenamento | Acoplamento entre domínios                   | Obrigatório |
| Base de dados            | Estado operacional e relações     | PostgreSQL                                                    | Backend                    | Modelo excessivo ou inconsistência tenant    | Obrigatório |
| Armazenamento documental | Ficheiros Markdown e versões      | S3 compatível; filesystem em desenvolvimento                  | Backend                    | Conflitos, acesso indevido, perda de versões | Obrigatório |
| Autenticação             | Identidade e sessões              | Reutilizar autenticação existente; caso contrário Django Auth | Backend                    | Gestão insegura de sessões                   | Obrigatório |
| Autorização              | Isolamento e permissões           | Políticas no backend                                          | Auth e memberships         | Fuga entre empresas                          | Obrigatório |
| API REST                 | Comunicação frontend/backend      | DRF                                                           | Backend                    | API demasiado ampla                          | Obrigatório |
| Auditoria                | Histórico de operações relevantes | Tabela append-only                                            | Backend e BD               | Exposição de dados em logs                   | Obrigatório |
| Exportação de contexto   | Preparar conteúdo para IA         | Serviço interno                                               | Documentos e funções       | Exportação excessiva de dados                | Obrigatório |
| Importação de resultado  | Receber resultado de IA           | Serviço interno                                               | Execuções                  | Conteúdo malicioso ou inválido               | Obrigatório |
| Jobs                     | Processos agendados               | Não necessário inicialmente                                   | —                          | Complexidade prematura                       | Adiado      |
| Filas                    | Processamento assíncrono          | Não necessário inicialmente                                   | —                          | Operação adicional                           | Adiado      |
| Conector local           | Comunicação com IA local          | Aplicação ou agente leve                                      | API e tokens               | Segurança e suporte                          | Versão 1    |
| Pesquisa semântica       | Pesquisa de conhecimento          | A definir                                                     | Índice e embeddings        | Custos e qualidade                           | Adiado      |
| Integração Git           | Sincronização documental          | A definir                                                     | Repositório externo        | Conflitos e segredos                         | Adiado      |
| Observabilidade avançada | Métricas e tracing                | A definir                                                     | Infraestrutura             | Overengineering                              | Adiado      |

---

## 4. Frontend

## 4.1. Abordagem

Aplicação web single-page, com navegação centrada em:

* empresa;
* portefólio;
* produto;
* atenção necessária;
* documentos;
* execuções.

Não deve ser centrada em quadros de tarefas.

### Tecnologia recomendada

* React;
* TypeScript;
* biblioteca visual já existente no projecto;
* cliente HTTP centralizado;
* biblioteca de cache e estado de servidor;
* formulários validados por esquema.

Não é necessário Redux no MVP, salvo se já fizer parte do projecto.

## 4.2. Áreas principais

### Entrada e selecção de empresa

* autenticação;
* selecção da empresa;
* criação inicial;
* resumo de configuração.

### Painel de atenção

Deve apresentar:

* produtos sem revisão recente;
* decisões pendentes;
* resultados de IA por validar;
* documentos sinalizados;
* pendências atrasadas ou próximas;
* produtos sem próximo passo administrativo.

### Portefólio de produtos

* lista;
* filtros;
* estado;
* responsável;
* última revisão;
* próximo ponto de atenção;
* indicadores mínimos.

### Ficha do produto

Separadores recomendados:

* visão geral;
* documentos;
* decisões;
* pendências;
* execuções;
* histórico.

### Documentos

* lista;
* editor;
* pré-visualização;
* histórico de versões;
* associação a produto;
* exportação.

### Funções

* funções humanas;
* funções de IA;
* funções híbridas;
* responsabilidades;
* instruções;
* restrições;
* documentos permitidos ou recomendados.

### Execuções de IA

* pedido;
* função;
* produto;
* documentos seleccionados;
* contexto preparado;
* estado;
* resultado;
* revisão;
* decisão final.

### Caixa de validação

* resultados pendentes;
* alterações propostas;
* aprovar;
* rejeitar;
* solicitar correcção;
* aplicar manualmente.

## 4.3. Componentes principais

* selector de empresa;
* cartão de produto;
* tabela de atenção;
* editor de ficha administrativa;
* editor Markdown;
* selector de documentos;
* construtor de contexto;
* visualizador de resultado;
* comparação entre versões;
* painel de aprovação;
* linha temporal de auditoria;
* formulários de decisão e pendência.

## 4.4. Estado

### Estado de servidor

Deve ser tratado por uma biblioteca de cache e sincronização de pedidos.

Inclui:

* empresas;
* produtos;
* documentos;
* decisões;
* funções;
* execuções;
* atenção.

### Estado local

Utilizado para:

* formulários;
* filtros temporários;
* modais;
* conteúdo não submetido;
* selecção de documentos.

Não guardar cópias persistentes do estado empresarial no browser.

## 4.5. Integração com APIs

* cliente HTTP único;
* tratamento centralizado de erros;
* renovação ou validação de sessão;
* cancelamento de pedidos;
* prevenção de submissões duplicadas;
* suporte a `ETag` ou versão para actualizações concorrentes, quando aplicável.

## 4.6. Validações

* campos obrigatórios;
* limites de tamanho;
* formatos de data;
* estados permitidos;
* transições válidas;
* confirmação em operações críticas;
* detecção de edição sobre versão desactualizada;
* bloqueio de submissão sem contexto mínimo.

## 4.7. Cuidados de UX

* não obrigar o utilizador a compreender a arquitectura interna;
* não expor Markdown como requisito técnico;
* não apresentar demasiadas entidades em simultâneo;
* diferenciar claramente proposta, aprovação e aplicação;
* mostrar sempre a empresa e produto activos;
* explicar por que um produto necessita de atenção;
* evitar que a configuração inicial seja longa;
* permitir começar com poucos campos.

## 4.8. Fora do MVP

* aplicação móvel;
* modo offline completo;
* dashboards personalizáveis;
* construtor de workflows;
* chat interno genérico;
* drag-and-drop avançado;
* organograma visual;
* personalização ilimitada;
* colaboração em tempo real no editor.

---

## 5. Backend

## 5.1. Abordagem

Monólito modular com módulos de domínio separados.

Estrutura conceptual:

```text
backend/
├── accounts
├── organisations
├── portfolio
├── documents
├── decisions
├── work_items
├── functions
├── executions
├── audit
├── storage
└── common
```

Os nomes reais devem respeitar o padrão do repositório.

## 5.2. Módulos

### Accounts

Responsável por:

* utilizadores;
* autenticação;
* perfil;
* sessões.

### Organisations

Responsável por:

* empresa ou workspace;
* memberships;
* papéis;
* isolamento de tenant.

### Portfolio

Responsável por:

* produtos;
* estado;
* revisões;
* responsáveis;
* indicadores de atenção.

### Documents

Responsável por:

* metadados;
* conteúdo Markdown;
* versões;
* exportação;
* associação a produtos;
* controlo de concorrência.

### Decisions

Responsável por:

* decisões;
* contexto;
* estado;
* impacto;
* relações.

### Work Items

Responsável por:

* pendências administrativas;
* prazos;
* estados;
* responsáveis.

Não deve evoluir silenciosamente para um gestor completo de projectos.

### Functions

Responsável por:

* funções humanas, de IA ou híbridas;
* instruções;
* responsabilidades;
* limites;
* contexto autorizado.

### Executions

Responsável por:

* pedidos;
* snapshots de instruções;
* documentos seleccionados;
* preparação de contexto;
* resultados;
* validações;
* estado de aplicação.

### Audit

Responsável por:

* registo append-only;
* actor;
* entidade;
* operação;
* estado anterior e posterior;
* correlação com pedido.

## 5.3. Regras de negócio principais

* toda a entidade pertence a uma empresa;
* um produto pertence a uma empresa;
* um utilizador só acede a empresas das quais é membro;
* documentos são lidos e alterados apenas através do backend;
* cada gravação documental cria uma versão;
* uma execução guarda a versão exacta das instruções e documentos utilizados;
* um resultado de IA começa como não validado;
* apenas utilizadores autorizados podem aprovar;
* uma aprovação não altera automaticamente documentos no MVP;
* a conclusão de uma execução deve ser explícita;
* o estado de um produto é mantido na base de dados;
* descrições e contexto extensos permanecem em Markdown.

## 5.4. Tratamento de erros

Utilizar um formato consistente de erro, com:

* código;
* título;
* descrição segura;
* campo afectado;
* identificador de correlação.

Classes principais:

* validação;
* autenticação;
* autorização;
* não encontrado;
* conflito de versão;
* estado inválido;
* tamanho excedido;
* indisponibilidade de armazenamento;
* erro interno.

Não devolver stack traces ao cliente.

## 5.5. Logs

Registar:

* início e fim de operações críticas;
* utilizador;
* empresa;
* recurso;
* resultado;
* duração;
* identificador de correlação.

Não registar:

* conteúdo integral dos documentos;
* prompts completos;
* respostas completas;
* tokens;
* palavras-passe;
* chaves de API.

## 5.6. Pontos de extensão

Preparar interfaces internas para:

* armazenamento documental;
* preparação de pacotes;
* fornecedores de IA;
* notificações;
* conectores locais;
* exportação;
* regras de atenção.

Estas interfaces devem ser pequenas e concretas, não sistemas genéricos de plugins.

---

## 6. Dados e base de dados

## 6.1. Estratégia

PostgreSQL deverá guardar:

* entidades;
* relações;
* estados;
* permissões;
* metadados;
* histórico funcional;
* referências às versões dos ficheiros.

O conteúdo Markdown deverá ser guardado como ficheiro num armazenamento próprio.

## 6.2. Entidades principais

### Organisation

Campos mínimos:

* `id`;
* `name`;
* `slug`;
* `status`;
* `created_at`;
* `created_by`.

### Membership

* `id`;
* `organisation_id`;
* `user_id`;
* `role`;
* `status`;
* `created_at`.

Restrição:

```text
unique(organisation_id, user_id)
```

### Product

* `id`;
* `organisation_id`;
* `name`;
* `slug`;
* `summary`;
* `status`;
* `stage`;
* `owner_user_id`;
* `last_reviewed_at`;
* `next_review_at`;
* `attention_level`;
* `created_at`;
* `updated_at`;
* `version`.

`attention_level` poderá ser calculado em vez de persistido, conforme as regras finais.

### Document

* `id`;
* `organisation_id`;
* `product_id`, opcional;
* `title`;
* `document_type`;
* `status`;
* `current_version_id`;
* `created_by`;
* `created_at`;
* `updated_at`.

### DocumentVersion

* `id`;
* `document_id`;
* `version_number`;
* `storage_key`;
* `checksum`;
* `size_bytes`;
* `created_by`;
* `created_at`;
* `change_summary`.

As versões devem ser imutáveis.

### Decision

* `id`;
* `organisation_id`;
* `product_id`, opcional;
* `title`;
* `summary`;
* `status`;
* `decision_date`;
* `owner_user_id`;
* `detail_document_id`, opcional;
* `created_at`;
* `updated_at`.

### WorkItem

* `id`;
* `organisation_id`;
* `product_id`, opcional;
* `title`;
* `type`;
* `status`;
* `priority`;
* `owner_user_id`;
* `due_date`;
* `related_decision_id`, opcional;
* `created_at`;
* `updated_at`.

### FunctionProfile

* `id`;
* `organisation_id`;
* `name`;
* `actor_type`;
* `purpose`;
* `responsibilities`;
* `constraints`;
* `instruction_document_id`, opcional;
* `requires_approval`;
* `status`;
* `created_at`;
* `updated_at`.

Valores de `actor_type`:

* `human`;
* `ai`;
* `hybrid`.

### AIExecution

* `id`;
* `organisation_id`;
* `product_id`;
* `function_profile_id`;
* `requested_by`;
* `title`;
* `objective`;
* `status`;
* `execution_mode`;
* `instruction_version_id`;
* `result_document_id`, opcional;
* `reviewed_by`, opcional;
* `reviewed_at`, opcional;
* `review_decision`, opcional;
* `created_at`;
* `updated_at`.

Valores possíveis de `execution_mode`:

* `manual_local`;
* `manual_external`;
* futuramente `connected_local`;
* futuramente `managed_api`.

### ExecutionContextDocument

* `execution_id`;
* `document_version_id`;
* `order`;
* `purpose`, opcional.

Esta associação garante que se sabe exactamente que versão foi utilizada.

### AuditEvent

* `id`;
* `organisation_id`;
* `actor_user_id`, opcional;
* `actor_type`;
* `action`;
* `entity_type`;
* `entity_id`;
* `correlation_id`;
* `metadata`;
* `created_at`.

O campo `metadata` não deve conter conteúdo sensível integral.

## 6.3. Relações essenciais

```text
Organisation
 ├── Memberships
 ├── Products
 ├── Documents
 ├── Decisions
 ├── WorkItems
 ├── FunctionProfiles
 ├── AIExecutions
 └── AuditEvents

Product
 ├── Documents
 ├── Decisions
 ├── WorkItems
 └── AIExecutions

Document
 └── DocumentVersions

AIExecution
 └── ExecutionContextDocuments
```

## 6.4. Integridade

* todas as chaves devem validar pertença à mesma empresa;
* não permitir ligar um documento de uma empresa a um produto de outra;
* `current_version_id` deve pertencer ao documento;
* números de versão devem ser únicos por documento;
* versões não devem ser actualizadas;
* entidades usadas numa execução não devem ser apagadas fisicamente;
* utilizar estados arquivados em vez de remoção sempre que exista histórico;
* campos de auditoria devem ser obrigatórios em operações críticas.

## 6.5. Dados sensíveis

Potencialmente sensíveis:

* estratégia empresarial;
* decisões;
* documentação;
* resultados de IA;
* dados pessoais;
* informação financeira futura;
* instruções internas.

Devem ser aplicadas:

* cifragem em trânsito;
* cifragem no armazenamento, quando disponibilizada pela infraestrutura;
* controlo de acesso;
* backups;
* minimização de logs;
* segregação de tenant.

## 6.6. Migrações

* migrações versionadas;
* executadas automaticamente no pipeline de deploy, com controlo;
* compatíveis com rollback da aplicação;
* alterações destrutivas executadas em duas fases;
* backup antes de migrações críticas.

## 6.7. Dados a validar

* estados de produto;
* tipos de decisão;
* tipos de pendência;
* regras de atenção;
* papéis de utilizador;
* estrutura das funções;
* limites de tamanho documental;
* política de retenção;
* política de eliminação;
* número de empresas por conta.

---

## 7. Autenticação e autorização

## 7.1. Autenticação

Se o sistema actual já possuir autenticação, deverá ser reutilizada.

Caso não exista:

* Django Auth;
* sessão segura em cookie `HttpOnly`;
* `Secure`;
* `SameSite`;
* protecção CSRF;
* recuperação de palavra-passe;
* verificação de correio electrónico, caso necessária.

Para frontend e backend no mesmo domínio, a sessão por cookie é preferível a guardar JWT no browser.

SSO e OIDC ficam para uma fase posterior.

## 7.2. Papéis mínimos

### Owner

* controla a empresa;
* gere membros;
* aprova operações;
* exporta dados;
* elimina ou arquiva a empresa.

### Editor

* gere produtos;
* documentos;
* decisões;
* pendências;
* execuções.

### Reviewer

* consulta informação;
* revê e aprova resultados;
* não gere membros.

### Viewer

* apenas leitura.

Para um MVP individual, o utilizador inicial será `Owner`.

## 7.3. Restrições por contexto

Toda a consulta deve incluir ou derivar o `organisation_id` autorizado.

Nunca confiar num `organisation_id` enviado pelo cliente sem validar a membership.

O backend deve verificar:

* acesso à empresa;
* papel;
* pertença do produto;
* pertença dos documentos;
* autorização da operação;
* estado actual da entidade.

## 7.4. Operações críticas

Exigem autorização explícita:

* convidar ou remover membros;
* alterar papéis;
* exportar toda a empresa;
* aprovar resultados de IA;
* alterar instruções de funções;
* arquivar produtos;
* eliminar documentos;
* emitir tokens para agentes locais;
* aplicar alterações automáticas futuras.

## 7.5. Riscos

* referência directa insegura a identificadores;
* fuga de dados entre empresas;
* links para ficheiros sem validação;
* tokens de agente demasiado amplos;
* utilizador rebaixado manter sessão activa;
* conteúdos exportados permanecerem acessíveis;
* permissões verificadas apenas no frontend.

A autorização deve ser sempre aplicada no backend.

---

## 8. Integrações

## 8.1. Armazenamento de objectos

### Objectivo

Guardar:

* Markdown;
* versões;
* exportações;
* resultados extensos.

### Comunicação

API compatível com S3 ou adaptador de filesystem em desenvolvimento.

### Dados trocados

* conteúdo;
* chave do objecto;
* checksum;
* tamanho;
* metadados técnicos.

### Riscos

* objectos públicos;
* URLs permanentes;
* inconsistência entre BD e armazenamento;
* perda de ficheiros;
* uploads maliciosos.

### Fallback

Filesystem local apenas em desenvolvimento ou instalação simples de piloto.

### Estado

Obrigatório.

---

## 8.2. IA local

### Objectivo

Permitir que um agente local consulte pedidos autorizados e submeta resultados.

### Comunicação futura

* API HTTPS;
* token limitado;
* operações específicas;
* polling controlado ou pedidos iniciados pelo utilizador.

### Dados trocados

* objectivo;
* instruções;
* versões de documentos;
* resultado;
* estado.

### Dependências

* agente local;
* autenticação por token;
* conectividade;
* gestão de versões.

### Riscos

* exfiltração;
* token comprometido;
* execução sobre contexto errado;
* incompatibilidade com modelos;
* suporte elevado.

### Fallback no MVP

Exportar pacote de contexto e importar resultado manualmente.

### Estado

Adiado para a versão 1.

---

## 8.3. Chats externos

### Objectivo

Permitir utilização manual de ChatGPT ou outras ferramentas.

### Comunicação

Sem integração directa no MVP.

### Dados trocados

O utilizador copia ou exporta manualmente o contexto.

### Riscos

* exposição de dados;
* perda de rastreabilidade;
* resultado incompleto;
* cópia para a execução errada.

### Fallback

Execução local manual.

### Estado

Suportado indirectamente no MVP.

---

## 8.4. Git

### Objectivo

Versionamento e colaboração documental técnica.

### Comunicação

Futuramente através de API ou repositório sincronizado.

### Riscos

* conflitos;
* segredos;
* force push;
* divergência da fonte oficial;
* estrutura de pastas não controlada.

### Fallback

Exportação de Markdown.

### Estado

Adiado.

---

## 8.5. Ferramentas de projectos

### Objectivo

Referenciar trabalho técnico existente sem o replicar.

### Comunicação

Inicialmente por URL externa.

### Dados trocados

* identificador;
* título opcional;
* URL;
* estado manual opcional.

### Estado

Referência simples poderá entrar na versão 1. Sincronização fica adiada.

---

## 9. Jobs, filas e automações

## 9.1. MVP

Não são necessários:

* Celery;
* Redis;
* RabbitMQ;
* Kafka;
* filas cloud;
* scheduler dedicado.

As operações do MVP são leves:

* CRUD;
* escrita de ficheiro;
* criação de versão;
* exportação de pacote;
* registo de resultado;
* aprovação.

## 9.2. Processos assíncronos futuros

Poderão justificar jobs:

* geração de grandes pacotes;
* pesquisa semântica;
* indexação;
* envio de notificações;
* sincronização Git;
* importações extensas;
* execução de agentes;
* geração de relatórios;
* análise de documentos.

## 9.3. Estratégia incremental

Primeiro nível:

* comando agendado executado pela plataforma;
* tabela de jobs simples, se necessário.

Segundo nível:

* fila com worker quando houver carga real ou retries complexos.

## 9.4. Requisitos futuros

Qualquer job deverá incluir:

* identificador;
* estado;
* tentativas;
* erro seguro;
* timestamps;
* idempotency key;
* correlação;
* retry limitado;
* dead-letter ou estado de falha permanente;
* monitorização.

Não implementar estes mecanismos sem processo assíncrono real.

---

## 10. APIs

Prefixo recomendado:

```text
/api/v1/
```

O formato exacto deve respeitar os padrões existentes.

## 10.1. Empresa activa

| Elemento   | Definição                                 |
| ---------- | ----------------------------------------- |
| Método     | `GET`                                     |
| Endpoint   | `/api/v1/organisations/{organisation_id}` |
| Objectivo  | Obter a empresa                           |
| Input      | Identificador                             |
| Output     | Dados básicos e permissões do utilizador  |
| Validações | Membership activa                         |
| Permissões | Membro da empresa                         |
| Erros      | `401`, `403`, `404`                       |

## 10.2. Produtos

| Elemento   | Definição                                          |
| ---------- | -------------------------------------------------- |
| Método     | `GET`                                              |
| Endpoint   | `/api/v1/organisations/{organisation_id}/products` |
| Objectivo  | Listar produtos                                    |
| Input      | Filtros de estado, responsável e atenção           |
| Output     | Lista paginada                                     |
| Validações | Filtros permitidos                                 |
| Permissões | Viewer ou superior                                 |
| Erros      | `400`, `403`                                       |

| Elemento   | Definição                                          |
| ---------- | -------------------------------------------------- |
| Método     | `POST`                                             |
| Endpoint   | `/api/v1/organisations/{organisation_id}/products` |
| Objectivo  | Criar produto                                      |
| Input      | Nome, resumo, estado, responsável                  |
| Output     | Produto criado                                     |
| Validações | Nome, slug, responsável da mesma empresa           |
| Permissões | Editor ou Owner                                    |
| Erros      | `400`, `403`, `409`, `422`                         |

| Elemento   | Definição                                      |
| ---------- | ---------------------------------------------- |
| Método     | `PATCH`                                        |
| Endpoint   | `/api/v1/products/{product_id}`                |
| Objectivo  | Actualizar produto                             |
| Input      | Campos alterados e versão actual               |
| Output     | Produto actualizado                            |
| Validações | Transição de estado e controlo de concorrência |
| Permissões | Editor ou Owner                                |
| Erros      | `400`, `403`, `404`, `409`, `422`              |

## 10.3. Atenção

| Elemento   | Definição                                              |
| ---------- | ------------------------------------------------------ |
| Método     | `GET`                                                  |
| Endpoint   | `/api/v1/organisations/{organisation_id}/attention`    |
| Objectivo  | Obter assuntos que exigem atenção                      |
| Input      | Filtros opcionais                                      |
| Output     | Produtos, decisões, pendências e execuções sinalizadas |
| Validações | Membership                                             |
| Permissões | Viewer ou superior                                     |
| Erros      | `403`, `404`                                           |

As regras devem ser determinísticas e explicáveis.

## 10.4. Documentos

| Elemento   | Definição                                           |
| ---------- | --------------------------------------------------- |
| Método     | `POST`                                              |
| Endpoint   | `/api/v1/organisations/{organisation_id}/documents` |
| Objectivo  | Criar documento                                     |
| Input      | Título, tipo, produto e conteúdo Markdown           |
| Output     | Documento e primeira versão                         |
| Validações | Tamanho, tipo e pertença do produto                 |
| Permissões | Editor ou Owner                                     |
| Erros      | `400`, `403`, `413`, `422`, `503`                   |

| Elemento   | Definição                             |
| ---------- | ------------------------------------- |
| Método     | `GET`                                 |
| Endpoint   | `/api/v1/documents/{document_id}`     |
| Objectivo  | Consultar metadados e conteúdo actual |
| Input      | Identificador                         |
| Output     | Documento, conteúdo e versão          |
| Validações | Pertença à empresa                    |
| Permissões | Viewer ou superior                    |
| Erros      | `403`, `404`, `503`                   |

| Elemento   | Definição                                          |
| ---------- | -------------------------------------------------- |
| Método     | `PUT`                                              |
| Endpoint   | `/api/v1/documents/{document_id}/content`          |
| Objectivo  | Criar nova versão                                  |
| Input      | Markdown, versão base e resumo da alteração        |
| Output     | Nova versão                                        |
| Validações | Tamanho, versão actual, UTF-8 e conteúdo permitido |
| Permissões | Editor ou Owner                                    |
| Erros      | `400`, `403`, `404`, `409`, `413`, `503`           |

| Elemento   | Definição                                  |
| ---------- | ------------------------------------------ |
| Método     | `GET`                                      |
| Endpoint   | `/api/v1/documents/{document_id}/versions` |
| Objectivo  | Listar histórico                           |
| Input      | Paginação                                  |
| Output     | Versões                                    |
| Permissões | Viewer ou superior                         |
| Erros      | `403`, `404`                               |

## 10.5. Decisões

| Elemento   | Definição                                           |
| ---------- | --------------------------------------------------- |
| Método     | `POST`                                              |
| Endpoint   | `/api/v1/organisations/{organisation_id}/decisions` |
| Objectivo  | Registar decisão                                    |
| Input      | Produto, título, resumo, estado e responsável       |
| Output     | Decisão criada                                      |
| Validações | Entidades da mesma empresa                          |
| Permissões | Editor ou Owner                                     |
| Erros      | `400`, `403`, `422`                                 |

## 10.6. Pendências

| Elemento   | Definição                                            |
| ---------- | ---------------------------------------------------- |
| Método     | `POST`                                               |
| Endpoint   | `/api/v1/organisations/{organisation_id}/work-items` |
| Objectivo  | Criar pendência administrativa                       |
| Input      | Título, tipo, produto, responsável, prazo            |
| Output     | Pendência criada                                     |
| Validações | Estado, tipo, responsável e prazo                    |
| Permissões | Editor ou Owner                                      |
| Erros      | `400`, `403`, `422`                                  |

## 10.7. Funções

| Elemento   | Definição                                           |
| ---------- | --------------------------------------------------- |
| Método     | `POST`                                              |
| Endpoint   | `/api/v1/organisations/{organisation_id}/functions` |
| Objectivo  | Criar função                                        |
| Input      | Nome, tipo, propósito, responsabilidades e limites  |
| Output     | Função criada                                       |
| Validações | Tipo e instruções                                   |
| Permissões | Owner ou Editor autorizado                          |
| Erros      | `400`, `403`, `409`, `422`                          |

## 10.8. Execuções

| Elemento   | Definição                                            |
| ---------- | ---------------------------------------------------- |
| Método     | `POST`                                               |
| Endpoint   | `/api/v1/organisations/{organisation_id}/executions` |
| Objectivo  | Criar pedido de execução                             |
| Input      | Produto, função, objectivo, modo e documentos        |
| Output     | Execução criada                                      |
| Validações | Mesma empresa, documentos válidos e função activa    |
| Permissões | Editor ou Owner                                      |
| Erros      | `400`, `403`, `404`, `422`                           |

| Elemento   | Definição                                           |
| ---------- | --------------------------------------------------- |
| Método     | `POST`                                              |
| Endpoint   | `/api/v1/executions/{execution_id}/context-package` |
| Objectivo  | Gerar pacote de contexto                            |
| Input      | Formato: texto, Markdown ou arquivo                 |
| Output     | Conteúdo ou ficheiro temporário                     |
| Validações | Estado e permissões                                 |
| Permissões | Criador, Editor ou Owner                            |
| Erros      | `403`, `404`, `409`, `413`, `503`                   |

| Elemento   | Definição                                  |
| ---------- | ------------------------------------------ |
| Método     | `POST`                                     |
| Endpoint   | `/api/v1/executions/{execution_id}/result` |
| Objectivo  | Submeter resultado                         |
| Input      | Conteúdo, origem e notas                   |
| Output     | Resultado registado                        |
| Validações | Estado da execução e tamanho               |
| Permissões | Criador, Editor ou Owner                   |
| Erros      | `400`, `403`, `409`, `413`, `422`          |

| Elemento   | Definição                                  |
| ---------- | ------------------------------------------ |
| Método     | `POST`                                     |
| Endpoint   | `/api/v1/executions/{execution_id}/review` |
| Objectivo  | Aprovar ou rejeitar resultado              |
| Input      | Decisão e comentário                       |
| Output     | Estado revisto                             |
| Validações | Resultado existente e transição válida     |
| Permissões | Reviewer ou Owner                          |
| Erros      | `400`, `403`, `404`, `409`, `422`          |

## 10.9. Exportação

| Elemento   | Definição                                         |
| ---------- | ------------------------------------------------- |
| Método     | `POST`                                            |
| Endpoint   | `/api/v1/organisations/{organisation_id}/exports` |
| Objectivo  | Exportar dados e documentos                       |
| Input      | Escopo e formato                                  |
| Output     | Exportação ou identificador futuro                |
| Validações | Escopo e volume                                   |
| Permissões | Owner                                             |
| Erros      | `403`, `413`, `503`                               |

Se a exportação for pequena, poderá ser síncrona no MVP.

---

## 11. Segurança

## 11.1. Autenticação

* cookies de sessão seguros;
* palavras-passe com hashing robusto;
* recuperação com token temporário;
* invalidar sessões após mudanças críticas;
* MFA posterior, salvo requisito imediato.

## 11.2. Autorização

* validação em cada endpoint;
* isolamento por empresa;
* autorização por acção;
* nunca confiar apenas em filtros do frontend;
* testes automáticos de isolamento entre tenants.

## 11.3. Validação de input

* schemas de entrada;
* tamanho máximo;
* enumerações controladas;
* datas válidas;
* sanitização de nomes de ficheiro;
* nunca construir caminhos a partir de input sem validação;
* rejeitar Markdown acima do limite.

## 11.4. Segurança de conteúdo Markdown

Markdown deve ser tratado como conteúdo não confiável.

Na apresentação:

* sanitizar HTML;
* desactivar scripts;
* impedir URLs perigosas;
* restringir conteúdo incorporado;
* proteger contra XSS;
* não executar blocos de código.

## 11.5. Ficheiros

* objectos privados;
* acesso através do backend ou URLs temporárias;
* chaves geradas pelo servidor;
* checksum;
* limites de tamanho;
* nenhuma execução de ficheiros;
* backups;
* política de retenção.

## 11.6. Dados sensíveis

* TLS obrigatório;
* segredos em variáveis ou secret manager;
* cifragem do armazenamento quando disponível;
* não incluir conteúdo integral em logs;
* separar configuração por ambiente;
* limitar acesso administrativo.

## 11.7. Rate limiting

Aplicável especialmente a:

* login;
* recuperação de palavra-passe;
* exportação;
* upload;
* geração de pacotes;
* futuros endpoints de agentes.

Pode ser aplicado inicialmente no reverse proxy ou backend.

## 11.8. Auditoria

Auditar:

* login relevante;
* alteração de papéis;
* criação e edição documental;
* exportação;
* submissão de resultados;
* aprovação;
* arquivamento;
* emissão ou revogação futura de tokens.

## 11.9. Integrações futuras

* tokens com escopo;
* expiração;
* rotação;
* revogação;
* identificação do agente;
* limites por produto ou função;
* protecção contra replay;
* nenhuma credencial partilhada entre empresas.

## 11.10. Protecção contra prompt injection

No MVP, a IA não executa acções directamente.

Ainda assim:

* documentos devem ser tratados como dados, não instruções de sistema;
* instruções da função devem ser distinguidas do conteúdo documental;
* o contexto exportado deve identificar fontes;
* resultados devem ser revistos;
* pedidos de acção presentes em documentos não devem gerar acções automáticas.

---

## 12. Observabilidade

## 12.1. Logs

Formato estruturado com:

* timestamp;
* nível;
* serviço;
* ambiente;
* request ID;
* correlation ID;
* user ID, quando permitido;
* organisation ID;
* endpoint;
* duração;
* código de resposta;
* tipo de erro.

## 12.2. Eventos importantes

* autenticação falhada repetida;
* tentativa de acesso entre tenants;
* falha de armazenamento;
* conflito de versão;
* exportação;
* aprovação;
* alteração de papel;
* erro de migração;
* resultado de IA rejeitado.

## 12.3. Métricas mínimas

* pedidos por minuto;
* erros por endpoint;
* latência;
* ligações à base de dados;
* armazenamento utilizado;
* número de documentos;
* geração de pacotes;
* falhas de escrita;
* exportações;
* resultados pendentes de revisão.

## 12.4. Health checks

* `/health/live`;
* `/health/ready`;
* ligação à base de dados;
* acesso ao armazenamento.

## 12.5. Alertas

No MVP:

* aplicação indisponível;
* taxa elevada de erros;
* base de dados indisponível;
* armazenamento indisponível;
* disco ou quota próxima do limite;
* falha de backup.

## 12.6. Ferramentas

Reutilizar a monitorização já existente.

Caso não exista, começar com:

* logs centralizados da plataforma;
* monitorização de disponibilidade;
* captura de erros da aplicação;
* métricas básicas da infraestrutura.

Tracing distribuído não é necessário num monólito MVP.

---

## 13. Deploy e ambientes

## 13.1. Ambiente local

Docker Compose com:

* backend;
* PostgreSQL;
* armazenamento local ou MinIO;
* frontend em modo de desenvolvimento.

Não incluir Redis ou broker.

## 13.2. Desenvolvimento

Ambiente partilhado para integração contínua.

Deve permitir:

* dados fictícios;
* migrações;
* testes de API;
* validação de armazenamento;
* testes de permissões.

## 13.3. Testes

Testes automatizados em pipeline:

* unitários;
* integração;
* isolamento por empresa;
* permissões;
* versões documentais;
* transições de execução;
* API;
* segurança básica.

## 13.4. Staging

Recomendado antes do piloto externo.

Deve ser semelhante à produção quanto a:

* PostgreSQL;
* armazenamento;
* proxy;
* TLS;
* variáveis;
* migrações.

Não deve utilizar dados reais sem necessidade.

## 13.5. Produção

Para o MVP:

* containers;
* uma instância backend, ou poucas réplicas;
* frontend estático;
* PostgreSQL gerido ou dedicado;
* armazenamento S3 compatível;
* reverse proxy;
* TLS;
* backups.

Kubernetes não é necessário, salvo se a organização já dispuser de uma plataforma Kubernetes operacional e padronizada.

## 13.6. Variáveis de ambiente

* ligação à BD;
* segredo da aplicação;
* configuração de sessão;
* origem permitida;
* domínio;
* armazenamento;
* limite de ficheiro;
* correio electrónico;
* logging;
* funcionalidades activas.

Validar configuração no arranque.

## 13.7. Migrações

Pipeline sugerido:

1. build;
2. testes;
3. backup quando aplicável;
4. execução de migrações compatíveis;
5. deploy;
6. health check;
7. activação.

## 13.8. Rollback

Mínimo necessário:

* imagem anterior disponível;
* migrações retrocompatíveis;
* backups da BD;
* versionamento imutável de documentos;
* procedimento documentado.

Evitar migrações destrutivas no mesmo deploy em que o código antigo deixa de suportar a estrutura.

---

## 14. Escalabilidade e evolução futura

## 14.1. Necessário agora

* monólito modular;
* índices adequados;
* paginação;
* object storage;
* isolamento por empresa;
* API versionada;
* processamento síncrono;
* auditoria;
* backups.

## 14.2. Deve ficar preparado

* identificadores estáveis;
* `organisation_id` em entidades;
* adaptador de armazenamento;
* lifecycle explícito das execuções;
* endpoints de API consistentes;
* versões documentais;
* tokens de integração futuros;
* separação lógica entre módulos.

## 14.3. Só fazer com escala comprovada

* workers;
* filas;
* cache distribuída;
* replicação de leitura;
* particionamento;
* CDN para ficheiros;
* pesquisa externa;
* event bus;
* microserviços;
* auto-scaling;
* múltiplas regiões;
* Kubernetes.

## 14.4. Overengineering nesta fase

* Kafka;
* event sourcing;
* CQRS;
* service mesh;
* Kubernetes dedicado;
* GraphQL sem necessidade;
* base vectorial desde o início;
* motor BPM;
* sistema genérico de plugins;
* múltiplas bases de dados;
* microserviço por domínio;
* data lake;
* comunicação agent-to-agent;
* orchestrator multiagente.

---

## 15. Trade-offs técnicos

## 15.1. Monólito modular vs microserviços

### Recomendação

Monólito modular.

### Vantagens

* desenvolvimento mais rápido;
* deploy simples;
* transacções directas;
* menor custo operacional;
* debugging mais fácil.

### Desvantagens

* escalabilidade conjunta;
* risco de acoplamento interno;
* crescimento do código.

### Risco assumido

Será necessário impor fronteiras modulares por convenção e testes.

---

## 15.2. PostgreSQL e ficheiros vs apenas PostgreSQL

### Recomendação

PostgreSQL para estrutura e object storage para Markdown.

### Vantagens

* ficheiros reais e portáveis;
* versões independentes;
* melhor compatibilidade futura com IA local e Git;
* base de dados não sobrecarregada com conteúdo extenso.

### Desvantagens

* duas tecnologias de persistência;
* risco de inconsistência;
* operações precisam de coordenação.

### Alternativa

Guardar Markdown numa coluna `text`.

### Razão da escolha

A portabilidade documental é parte relevante da proposta.

### Risco assumido

O backend deve garantir a consistência entre metadados e objectos.

---

## 15.3. Object storage vs filesystem

### Recomendação

Filesystem em desenvolvimento; S3 compatível em produção.

### Vantagens

* escalabilidade;
* backups independentes;
* objectos privados;
* compatibilidade com múltiplas instâncias.

### Desvantagens

* dependência adicional;
* tratamento de falhas de rede.

### Risco assumido

Maior complexidade do que guardar tudo no disco da aplicação.

---

## 15.4. Sessão por cookie vs JWT no browser

### Recomendação

Sessão por cookie quando frontend e backend partilham domínio.

### Vantagens

* menor exposição a roubo de token por JavaScript;
* revogação simples;
* implementação madura;
* menos complexidade.

### Desvantagens

* protecção CSRF obrigatória;
* menos conveniente para clientes externos.

### Alternativa

JWT com refresh token.

### Risco assumido

A futura API para agentes utilizará tokens separados, não a sessão web.

---

## 15.5. Execução manual vs integração directa com IA

### Recomendação

Exportação/importação manual no MVP.

### Vantagens

* menor risco;
* suporta IA local e externa;
* valida a proposta sem integração complexa;
* menor custo.

### Desvantagens

* mais passos;
* menor fluidez;
* possibilidade de erro humano.

### Risco assumido

A experiência pode parecer menos diferenciadora.

---

## 15.6. Aprovação manual vs aplicação automática

### Recomendação

Aprovação e aplicação manual.

### Vantagens

* segurança;
* controlo;
* menor risco de corrupção;
* auditoria clara.

### Desvantagens

* menor automação;
* mais carga para o utilizador.

### Risco assumido

A produtividade inicial será inferior à visão futura.

---

## 15.7. Regras de atenção calculadas vs persistidas

### Recomendação

Calcular com queries simples no MVP.

### Vantagens

* menos estado derivado;
* menor risco de inconsistência;
* alteração mais fácil das regras.

### Desvantagens

* queries potencialmente mais pesadas.

### Risco assumido

Se o volume crescer, poderá ser necessário materializar indicadores.

---

## 16. Riscos e dependências

## 16.1. Frontend

* interface demasiado densa;
* conceitos pouco claros;
* editor Markdown inadequado;
* dificuldade em explicar atenção;
* estados inconsistentes entre páginas;
* formulários extensos.

## 16.2. Backend

* transformação do módulo de pendências num gestor de projectos;
* regras espalhadas por serializers e views;
* acoplamento excessivo;
* autorização inconsistente;
* falta de transacções em operações de ficheiros.

## 16.3. Dados

* duplicação entre BD e Markdown;
* documentos órfãos;
* versão actual incorrecta;
* eliminação de entidades referenciadas;
* crescimento do histórico;
* regras de atenção ambíguas.

## 16.4. Integrações

* armazenamento indisponível;
* diferenças entre desenvolvimento e produção;
* futura integração local complexa;
* resultados importados em formatos inconsistentes;
* dependência de fornecedores.

## 16.5. Segurança

* fuga entre tenants;
* XSS em Markdown;
* exportação indevida;
* logs com conteúdo;
* objectos públicos;
* permissões excessivas;
* tokens futuros comprometidos;
* prompt injection.

## 16.6. Deploy

* migrações incompatíveis;
* falta de backup;
* configuração incorrecta;
* armazenamento não persistente;
* ausência de staging;
* dependência de uma única VM sem recuperação.

## 16.7. Operação

* documentos desactualizados;
* utilizadores não concluírem revisões;
* falta de processo de suporte;
* crescimento do armazenamento;
* pedidos de restauro;
* dificuldade em explicar erros de IA.

## 16.8. Equipa

* equipa pequena para produto, segurança, desenvolvimento e suporte;
* conhecimento concentrado;
* pressão para implementar automação cedo demais;
* manutenção de integrações consumir capacidade.

## 16.9. Prazo

* excesso de entidades no MVP;
* inclusão prematura de integração local;
* procura de UX perfeita antes do piloto;
* subestimação de autorização e isolamento;
* tentativa de construir versão comercial completa antes de validação.

---

## 17. Decisões pendentes

1. A primeira versão permite uma empresa por conta ou várias?

2. O MVP será já multiutilizador ou inicialmente individual?

3. Qual é o conjunto exacto de papéis do MVP?

4. Quais são os estados oficiais de produto?

5. Quais são os estados oficiais de decisão, pendência e execução?

6. Quais campos são obrigatórios na ficha administrativa do produto?

7. Como se calcula que um produto necessita de atenção?

8. Que tipos de documento existem inicialmente?

9. Qual é o tamanho máximo de cada documento?

10. Cada gravação cria obrigatoriamente uma versão ou apenas alterações submetidas?

11. O conteúdo Markdown é armazenado directamente em object storage desde o primeiro piloto?

12. Qual é o formato de exportação do pacote de contexto?

13. O pacote inclui ficheiros separados, um documento consolidado ou ambos?

14. Como é importado o resultado de IA: texto, Markdown ou ficheiro?

15. O resultado aprovado pode criar automaticamente uma nova versão documental ou apenas ser aplicado manualmente?

16. A autenticação existente pode ser reutilizada?

17. Que infraestrutura de armazenamento estará disponível em produção?

18. O primeiro piloto necessita de ligação directa a IA local?

19. Que informação pode ser enviada para serviços externos?

20. Qual é a política de eliminação e retenção de documentos?

21. O MVP necessita de convites e múltiplos utilizadores?

22. É necessária exportação completa da empresa desde o primeiro MVP?

23. Que requisitos de residência de dados se aplicam?

24. Que stack e convenções existem no repositório actual?

25. Qual é a plataforma de deploy disponível?

---

## 18. Recomendações para o backlog

Os seguintes blocos técnicos deverão aparecer no backlog, sem ainda serem detalhados em tarefas.

### Bloco 1 — Fundação da aplicação

* estrutura do projecto;
* configuração;
* ambientes;
* base de dados;
* armazenamento;
* testes;
* CI/CD.

### Bloco 2 — Identidade e empresas

* autenticação;
* empresa;
* memberships;
* papéis;
* isolamento.

### Bloco 3 — Portefólio

* produtos;
* ficha administrativa;
* estados;
* revisão;
* visão consolidada.

### Bloco 4 — Documentos

* metadados;
* Markdown;
* armazenamento;
* versões;
* edição;
* exportação.

### Bloco 5 — Decisões e pendências

* registo;
* estados;
* relações;
* prazos;
* responsáveis.

### Bloco 6 — Funções organizacionais

* tipos;
* responsabilidades;
* instruções;
* limites;
* estado.

### Bloco 7 — Execuções assistidas

* criação;
* contexto;
* exportação;
* resultado;
* revisão;
* aprovação.

### Bloco 8 — Visão de atenção

* regras;
* agregação;
* explicação;
* interface.

### Bloco 9 — Auditoria e segurança

* eventos;
* permissões;
* isolamento;
* validações;
* protecção de ficheiros;
* testes de segurança.

### Bloco 10 — Exportação e portabilidade

* exportação documental;
* exportação de dados;
* manifesto;
* recuperação.

### Bloco 11 — Operação

* logs;
* health checks;
* backups;
* deploy;
* rollback;
* documentação operacional.

### Bloco posterior — Integração local

* tokens;
* API limitada;
* conector;
* polling;
* submissão de resultados;
* revogação;
* auditoria.

---

## 19. Parecer crítico final

### Classificação: PRONTA COM AJUSTES

A arquitectura é suficientemente sólida para avançar para revisão crítica e preparação de roadmap, porque:

* utiliza um monólito modular;
* evita microserviços e filas prematuras;
* separa correctamente dados estruturados e Markdown;
* mantém aprovação humana;
* suporta o fluxo central do MVP;
* permite integração futura com IA local;
* prevê isolamento entre empresas;
* inclui controlo de versões e auditoria;
* reduz dependências operacionais;
* mantém Git, pesquisa semântica e agentes autónomos fora do MVP.

Os principais ajustes ainda necessários são:

1. fechar o modelo exacto de tenant e utilizadores;

2. definir os estados e campos mínimos das entidades;

3. validar o mecanismo de armazenamento documental;

4. fechar o formato do pacote de contexto;

5. decidir se a ligação directa a IA local entra no MVP ou na versão 1;

6. confirmar a stack e os padrões já existentes no repositório;

7. definir as regras mínimas de atenção;

8. confirmar requisitos de segurança e residência dos dados.

A arquitectura não deve avançar ainda para microserviços, agentes autónomos, Git bidireccional, pesquisa vectorial ou filas.

# Parecer final: PRONTA COM AJUSTES
