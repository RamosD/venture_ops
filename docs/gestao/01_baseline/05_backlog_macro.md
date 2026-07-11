# Backlog Macro/Baseline — VentureOps AI

## 1. Identificação

**Produto:** VentureOps AI
**Tipo de artefacto:** Backlog macro/baseline
**Estado:** Baseline inicial
**Objectivo:** Estruturar o produto em blocos funcionais e técnicos verificáveis, preparados para decomposição posterior em backlogs detalhados.
**Abrangência:** Fase 0, MVP, Versão 1 e evoluções condicionais.

Este backlog não contém:

* user stories detalhadas;
* tarefas técnicas;
* estimativas;
* prompts de implementação;
* decisões de implementação ao nível de código;
* decomposição por ficheiro, endpoint ou componente.

---

## 2. Objectivo da baseline

A baseline deve permitir:

* delimitar o produto;
* organizar a implementação por fases;
* identificar dependências;
* impedir crescimento indevido do MVP;
* estabelecer critérios verificáveis;
* orientar a posterior criação de backlogs funcionais e técnicos;
* servir como referência para revisão de escopo;
* garantir rastreabilidade entre visão, arquitectura, roadmap e execução.

---

## 3. Princípios do backlog

1. O MVP deve validar o valor administrativo do produto antes de automatizar a execução com IA.

2. A gestão de produtos, documentos, decisões e resultados de IA é prioritária sobre a gestão detalhada de tarefas.

3. Cada tipo de informação deve possuir uma fonte oficial claramente definida.

4. A base de dados deve controlar estado, relações, permissões e auditoria.

5. Os ficheiros Markdown devem controlar documentação, conhecimento e contexto narrativo.

6. Resultados produzidos por IA não são automaticamente considerados aprovados ou aplicados.

7. A integração directa com IA local não deve bloquear a entrega do MVP.

8. Funcionalidades avançadas só devem avançar depois de validação real.

9. Segurança, isolamento e auditoria fazem parte do produto mínimo, não de uma fase opcional.

10. Cada item macro deve gerar evidência verificável antes de ser considerado concluído.

---

## 4. Classificação dos itens

### Obrigatório

Necessário para cumprir o objectivo da fase.

### Condicional

Só deve avançar se uma hipótese, dependência ou necessidade for validada.

### Posterior

Não pertence ao MVP nem à Versão 1 inicial.

### Descartado do núcleo

Não deve ser incluído no produto sem revisão estratégica formal.

---

# Fase 0 — Preparação e alinhamento

## Objectivo da fase

Eliminar decisões bloqueadoras e produzir uma base suficientemente clara para decompor o MVP sem reabrir continuamente o escopo.

---

| ID    | Item macro                                          | Objectivo                                                   | Escopo macro                                                                                                   | Evidência de conclusão                                                       | Dependências              | Classificação |
| ----- | --------------------------------------------------- | ----------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- | ------------------------- | ------------- |
| F0-01 | Definir o segmento inicial                          | Fixar o primeiro perfil de cliente e utilizador             | Características do utilizador, dimensão da equipa, número de produtos, maturidade técnica e utilização de IA   | Segmento inicial documentado, aprovado e distinguido dos públicos futuros    | Visão de produto          | Obrigatório   |
| F0-02 | Definir o caso de uso principal                     | Seleccionar o fluxo que deverá demonstrar valor no MVP      | Situação inicial, actor, necessidade, execução, resultado e valor esperado                                     | Caso de uso completo, compreendido e utilizável como referência de validação | F0-01                     | Obrigatório   |
| F0-03 | Fechar o fluxo funcional do MVP                     | Definir o ciclo ponta a ponta do utilizador                 | Empresa, produto, documentos, decisões, funções, execução assistida, resultado e validação                     | Fluxo aprovado sem etapas críticas em aberto                                 | F0-02                     | Obrigatório   |
| F0-04 | Fechar o modelo funcional mínimo                    | Confirmar as entidades necessárias ao MVP                   | Empresa, produto, documento, decisão, pendência, função, execução, resultado, revisão e auditoria              | Glossário funcional e relações de alto nível aprovados                       | F0-03                     | Obrigatório   |
| F0-05 | Definir estados e transições                        | Remover ambiguidades no ciclo de vida das entidades         | Estados de produto, documento, decisão, pendência, função, execução e revisão                                  | Matriz de estados e transições válidas aprovada                              | F0-04                     | Obrigatório   |
| F0-06 | Definir a fronteira entre BD e Markdown             | Evitar duplicação e dupla fonte de verdade                  | Dados estruturados, conteúdo documental, metadados, versões e regras de actualização                           | Matriz de fonte de verdade aprovada para cada tipo de informação             | F0-04                     | Obrigatório   |
| F0-07 | Definir a ficha administrativa mínima do produto    | Limitar os dados obrigatórios de cada produto               | Identificação, propósito, estado, responsável, revisão, riscos, documentos, decisões e pontos de atenção       | Ficha mínima aprovada e testada num produto real                             | F0-02, F0-04              | Obrigatório   |
| F0-08 | Definir as regras da visão de atenção               | Determinar como identificar assuntos que exigem intervenção | Produtos sem revisão, decisões pendentes, pendências vencidas, documentos sinalizados e resultados por validar | Regras determinísticas, explicáveis e aprovadas                              | F0-05, F0-07              | Obrigatório   |
| F0-09 | Definir o pacote de contexto                        | Padronizar a preparação de trabalho para IA                 | Objectivo, função, instruções, produto, documentos, restrições e formato esperado                              | Modelo de pacote produzido e testado manualmente                             | F0-03, F0-06              | Obrigatório   |
| F0-10 | Definir o modelo inicial de utilizadores e empresas | Fechar o nível de colaboração do MVP                        | Uma ou várias empresas, utilizador individual, papéis e memberships futuras                                    | Decisão formal registada                                                     | F0-01                     | Obrigatório   |
| F0-11 | Confirmar stack, repositório e padrões              | Garantir alinhamento com o ambiente real de desenvolvimento | Stack existente, autenticação, convenções, testes, deploy e armazenamento                                      | Levantamento técnico aprovado, sem pressupostos críticos pendentes           | Arquitectura aprovada     | Obrigatório   |
| F0-12 | Definir requisitos mínimos de segurança             | Estabelecer os controlos não adiáveis                       | Isolamento, autorização, protecção documental, auditoria, segredos e exportação                                | Checklist de segurança mínima aprovado                                       | F0-10, F0-11              | Obrigatório   |
| F0-13 | Preparar o piloto                                   | Definir como o MVP será validado                            | Utilizadores, produtos reais, dados, actividades, feedback e critérios de sucesso                              | Plano de piloto aprovado e participantes identificados                       | F0-01, F0-02              | Obrigatório   |
| F0-14 | Congelar o escopo do MVP                            | Impedir entrada de funcionalidades não essenciais           | Lista final de itens incluídos, excluídos, opcionais e adiados                                                 | Baseline do MVP aprovada e sujeita a controlo de mudança                     | Todos os itens anteriores | Obrigatório   |

## Critérios de saída da Fase 0

A Fase 0 considera-se concluída quando:

* o caso de uso principal está aprovado;
* o fluxo funcional está fechado;
* as entidades e estados estão definidos;
* a divisão entre base de dados e Markdown está aprovada;
* a ficha mínima de produto está fechada;
* as regras de atenção estão definidas;
* o pacote de contexto está testado;
* o modelo de utilizadores está decidido;
* a stack e os padrões existentes estão confirmados;
* o piloto está preparado;
* o escopo do MVP está formalmente congelado.

---

# Fase 1 — MVP

## Objectivo da fase

Entregar uma aplicação pequena e utilizável que permita a um fundador gerir administrativamente vários produtos, preservar contexto e completar uma execução assistida por IA com validação humana.

---

| ID     | Item macro                             | Objectivo                                                           | Escopo macro                                                                                                  | Evidência de conclusão                                                             | Dependências                          | Classificação |
| ------ | -------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ------------------------------------- | ------------- |
| MVP-01 | Fundação operacional do produto        | Disponibilizar a base executável e testável do MVP                  | Estrutura da aplicação, configuração, ambientes, persistência, armazenamento e pipeline mínimo                | Aplicação executável nos ambientes previstos, com validação automática básica      | F0-11, F0-12                          | Obrigatório   |
| MVP-02 | Autenticação e acesso inicial          | Garantir acesso controlado à aplicação                              | Entrada, saída, sessão, recuperação de acesso e perfil mínimo                                                 | Utilizador autenticado consegue aceder apenas ao seu contexto autorizado           | MVP-01                                | Obrigatório   |
| MVP-03 | Gestão da empresa                      | Representar a entidade empresarial principal                        | Criação, consulta, edição e configuração mínima da empresa                                                    | Empresa criada e utilizada como contexto obrigatório das entidades                 | MVP-02, F0-10                         | Obrigatório   |
| MVP-04 | Gestão do portefólio de produtos       | Permitir gerir vários produtos numa visão consolidada               | Criar, editar, consultar, filtrar, arquivar e rever produtos                                                  | Utilizador consegue manter e consultar vários produtos reais                       | MVP-03, F0-07                         | Obrigatório   |
| MVP-05 | Ficha administrativa do produto        | Concentrar o contexto essencial de cada produto                     | Estado, fase, propósito, responsável, revisão, riscos, documentos, decisões e pendências                      | Ficha apresenta informação coerente e suficiente para compreender o produto        | MVP-04                                | Obrigatório   |
| MVP-06 | Gestão documental em Markdown          | Manter conhecimento e contexto de forma portável                    | Criar, editar, visualizar, relacionar, versionar e consultar documentos                                       | Documento pode ser criado, alterado e recuperado por versão                        | MVP-03, F0-06                         | Obrigatório   |
| MVP-07 | Tipos documentais mínimos              | Organizar documentos sem criar um sistema documental genérico       | Contexto da empresa, visão de produto, instruções, decisão detalhada e resultado                              | Tipos mínimos disponíveis e utilizados no piloto                                   | MVP-06                                | Obrigatório   |
| MVP-08 | Gestão de decisões                     | Preservar decisões e a respectiva justificação                      | Registo, estado, responsável, data, impacto, produto e documento relacionado                                  | Decisão pode ser registada, consultada e relacionada com um produto                | MVP-04, MVP-06                        | Obrigatório   |
| MVP-09 | Gestão mínima de pendências            | Controlar assuntos administrativos sem criar um gestor de projectos | Acção, revisão, validação, obrigação, responsável, prazo e estado                                             | Pendências reais podem ser acompanhadas até à conclusão ou cancelamento            | MVP-04, F0-05                         | Obrigatório   |
| MVP-10 | Gestão de funções organizacionais      | Representar responsabilidades humanas, de IA e híbridas             | Nome, tipo, propósito, responsabilidades, limites e instruções                                                | Função pode ser criada e seleccionada numa execução                                | MVP-06                                | Obrigatório   |
| MVP-11 | Criação de execução assistida          | Registar uma necessidade a executar com apoio de IA                 | Produto, função, objectivo, modo, documentos e estado                                                         | Execução criada com contexto rastreável                                            | MVP-04, MVP-06, MVP-10                | Obrigatório   |
| MVP-12 | Geração do pacote de contexto          | Preparar informação coerente para execução externa ou local manual  | Instruções, objectivo, produto, versões documentais, restrições e formato esperado                            | Pacote gerado corresponde às versões seleccionadas e pode ser exportado ou copiado | MVP-11, F0-09                         | Obrigatório   |
| MVP-13 | Registo do resultado da IA             | Preservar o resultado produzido fora da aplicação                   | Origem, conteúdo, data, operador, relação com a execução e documento de resultado                             | Resultado registado e associado à execução correcta                                | MVP-11                                | Obrigatório   |
| MVP-14 | Revisão e aprovação de resultados      | Manter controlo humano sobre os resultados de IA                    | Aprovar, rejeitar, solicitar correcção e registar observações                                                 | Resultado não altera o estado oficial sem revisão explícita                        | MVP-13                                | Obrigatório   |
| MVP-15 | Actualização controlada após aprovação | Reflectir os resultados aprovados sem automação perigosa            | Orientar ou executar manualmente actualizações de documentos, decisões ou pendências                          | Alterações aprovadas ficam relacionadas com a execução e são auditáveis            | MVP-14, MVP-06, MVP-08, MVP-09        | Obrigatório   |
| MVP-16 | Visão de atenção                       | Mostrar os produtos e assuntos que exigem intervenção               | Produtos sem revisão, decisões pendentes, pendências vencidas, documentos sinalizados e execuções por validar | Cada sinal é apresentado com motivo compreensível                                  | MVP-04, MVP-08, MVP-09, MVP-14, F0-08 | Obrigatório   |
| MVP-17 | Histórico e auditoria básica           | Garantir rastreabilidade das operações críticas                     | Actor, acção, entidade, data, alteração e execução relacionada                                                | Operações críticas podem ser reconstruídas através do histórico                    | Todos os módulos core                 | Obrigatório   |
| MVP-18 | Segurança e isolamento do MVP          | Impedir acesso indevido a empresas, produtos e documentos           | Autorização, validação de contexto, protecção de ficheiros e sanitização                                      | Testes confirmam que dados não são acessíveis fora do contexto autorizado          | MVP-02, MVP-03, MVP-06                | Obrigatório   |
| MVP-19 | Exportação e portabilidade             | Permitir retirar os dados essenciais e documentos                   | Exportação de empresa, produtos, documentos e relações principais                                             | Pacote exportado pode ser aberto e compreendido fora da aplicação                  | MVP-04, MVP-06, MVP-08                | Obrigatório   |
| MVP-20 | Operação mínima do MVP                 | Garantir execução controlada do produto                             | Logs, health checks, backups, migrações, deploy e rollback mínimo                                             | Ambiente de piloto estável, recuperável e observável                               | MVP-01, MVP-17, MVP-18                | Obrigatório   |
| MVP-21 | Testes dos fluxos críticos             | Validar funcionalidade, segurança e consistência                    | Fluxo ponta a ponta, versões, isolamento, estados e aprovações                                                | Conjunto mínimo de testes aprovado e executado com sucesso                         | Todos os itens core                   | Obrigatório   |
| MVP-22 | Execução do piloto                     | Validar o MVP com produtos e utilizadores reais                     | Configuração, utilização acompanhada, recolha de feedback e análise                                           | Piloto concluído com evidências de uso e problemas registados                      | MVP-01 a MVP-21, F0-13                | Obrigatório   |
| MVP-23 | Avaliação e fecho do MVP               | Decidir continuar, corrigir, reduzir ou pausar                      | Avaliação de valor, esforço, adopção, segurança e adequação ao problema                                       | Relatório de validação e decisão formal sobre a Versão 1                           | MVP-22                                | Obrigatório   |

## Critérios de saída da Fase 1

O MVP considera-se concluído quando:

* o fluxo completo funciona de ponta a ponta;
* vários produtos podem ser geridos;
* documentos possuem versões recuperáveis;
* decisões e pendências podem ser relacionadas com produtos;
* uma função pode ser utilizada numa execução;
* o pacote de contexto preserva as versões utilizadas;
* resultados podem ser registados, aprovados ou rejeitados;
* a visão de atenção apresenta motivos compreensíveis;
* operações críticas estão auditadas;
* exportação funciona;
* isolamento e autorização estão testados;
* o piloto real foi concluído;
* existe uma decisão formal sobre continuar, ajustar ou pausar.

---

# Fase 2 — Versão 1

## Objectivo da fase

Consolidar o MVP como produto utilizável de forma recorrente por pequenas equipas, acrescentando colaboração, segurança reforçada, melhor recuperação de informação e integração limitada com IA local.

A entrada nesta fase depende da validação do MVP.

---

| ID    | Item macro                              | Objectivo                                             | Escopo macro                                                                   | Evidência de conclusão                                                            | Dependências                       | Classificação       |
| ----- | --------------------------------------- | ----------------------------------------------------- | ------------------------------------------------------------------------------ | --------------------------------------------------------------------------------- | ---------------------------------- | ------------------- |
| V1-01 | Multiutilizador e convites              | Permitir utilização por pequenas equipas              | Convites, memberships, activação, remoção e estado                             | Vários utilizadores colaboram na mesma empresa sem perda de isolamento            | MVP-23                             | Obrigatório para V1 |
| V1-02 | Papéis e permissões consolidados        | Diferenciar administração, edição, revisão e consulta | Owner, Editor, Reviewer e Viewer, ou modelo equivalente aprovado               | Matriz de permissões implementada e testada                                       | V1-01                              | Obrigatório para V1 |
| V1-03 | Ciclos de revisão de produto            | Tornar a manutenção administrativa recorrente         | Revisão, confirmação de estado, alterações, próxima revisão e histórico        | Produto pode ser revisto através de um fluxo curto e auditável                    | MVP-05, MVP-16                     | Obrigatório para V1 |
| V1-04 | Templates funcionais                    | Reduzir esforço de configuração                       | Modelos de produto, documento, função, execução e revisão                      | Novo contexto pode ser iniciado com um modelo sem configuração extensa            | Evidências do piloto               | Importante          |
| V1-05 | Pesquisa transversal                    | Melhorar recuperação de informação                    | Pesquisa por título, conteúdo, produto, estado e tipo                          | Utilizador encontra documentos, decisões e execuções sem navegação manual extensa | MVP-06, MVP-08, MVP-11             | Obrigatório para V1 |
| V1-06 | Histórico consolidado por produto       | Reunir os eventos relevantes numa linha temporal      | Revisões, decisões, documentos, pendências, execuções e aprovações             | Evolução de um produto pode ser compreendida cronologicamente                     | MVP-17                             | Importante          |
| V1-07 | Notificações essenciais                 | Reduzir esquecimento de assuntos relevantes           | Revisões, pendências, resultados por validar e decisões pendentes              | Utilizador recebe avisos configurados sem excesso de ruído                        | Regras de atenção validadas        | Condicional         |
| V1-08 | Referências a sistemas externos         | Relacionar trabalho externo sem o replicar            | URLs e identificadores de repositórios, tarefas ou projectos                   | Produto pode referenciar trabalho existente noutras ferramentas                   | Procura confirmada                 | Condicional         |
| V1-09 | API limitada para IA local              | Permitir execução local controlada                    | Obter execuções autorizadas, descarregar contexto e submeter resultados        | Agente autorizado completa o ciclo sem acesso livre aos restantes dados           | Procura validada no MVP            | Condicional crítico |
| V1-10 | Gestão de tokens de agente              | Controlar identidades não humanas                     | Emissão, escopo, expiração, revogação e auditoria                              | Token comprometido pode ser revogado sem afectar utilizadores humanos             | V1-09                              | Condicional crítico |
| V1-11 | Segurança reforçada                     | Consolidar a utilização por equipas e agentes         | Rate limiting, políticas de sessão, revisão de acessos e auditoria alargada    | Revisão de segurança concluída sem riscos críticos em aberto                      | V1-01, V1-02, V1-09                | Obrigatório para V1 |
| V1-12 | Observabilidade e operação consolidadas | Melhorar diagnóstico e continuidade                   | Métricas, alertas, restauro testado, monitorização e capacidade operacional    | Incidentes principais podem ser detectados, diagnosticados e recuperados          | MVP-20                             | Obrigatório para V1 |
| V1-13 | Onboarding orientado                    | Reduzir o tempo até ao primeiro valor                 | Criação assistida da empresa, primeiro produto, documentos e primeira execução | Novo utilizador completa o fluxo inicial sem apoio intensivo                      | Aprendizagem do piloto             | Importante          |
| V1-14 | Preparação comercial inicial            | Validar o produto como oferta SaaS                    | Planos, limites, apresentação, activação, termos e suporte mínimo              | Pelo menos uma oferta comercial pode ser testada com clientes                     | MVP-23                             | Condicional         |
| V1-15 | Validação da Versão 1                   | Confirmar adopção recorrente e valor                  | Uso por pequenas equipas, feedback, retenção e decisão de evolução             | Relatório de validação e decisão sobre a Fase 3                                   | Todos os itens seleccionados da V1 | Obrigatório         |

## Critérios de saída da Fase 2

A Versão 1 considera-se concluída quando:

* a utilização por mais de um utilizador está funcional, caso faça parte do produto validado;
* papéis e permissões estão testados;
* revisões de produto são utilizadas;
* pesquisa e histórico estão estáveis;
* o onboarding foi simplificado;
* a integração local foi validada, caso incluída;
* segurança e operação foram reforçadas;
* existem sinais de utilização recorrente;
* a proposta comercial inicial foi testada, caso o produto avance como SaaS;
* existe decisão fundamentada sobre as evoluções posteriores.

---

# Fase 3 — Melhorias posteriores

## Objectivo da fase

Expandir o produto apenas perante evidência de procura, adopção, retorno ou risco operacional.

Nenhum item desta fase é automaticamente aprovado.

---

| ID    | Item macro                                    | Objectivo                                               | Escopo macro                                                          | Condição de entrada                                            | Evidência de conclusão                                 | Classificação |
| ----- | --------------------------------------------- | ------------------------------------------------------- | --------------------------------------------------------------------- | -------------------------------------------------------------- | ------------------------------------------------------ | ------------- |
| EV-01 | Automação controlada                          | Automatizar actividades frequentes e de baixo risco     | Execuções programadas, propostas automáticas e aprovação por excepção | Actividades repetidas e regras estáveis                        | Automação reduz esforço sem aumentar incidentes        | Condicional   |
| EV-02 | Pesquisa semântica                            | Melhorar recuperação de conhecimento em volumes maiores | Indexação, pesquisa contextual e fontes apresentadas                  | Pesquisa textual comprovadamente insuficiente                  | Resultados relevantes, explicáveis e seguros           | Condicional   |
| EV-03 | Detecção de documentação desactualizada       | Identificar incoerências e lacunas documentais          | Comparação de sinais, datas, decisões e documentos                    | Utilizadores mantêm volume documental significativo            | Alertas úteis e com taxa aceitável de falsos positivos | Condicional   |
| EV-04 | Integração Git controlada                     | Relacionar documentos com repositórios técnicos         | Importação, exportação e propostas de alteração                       | Segmento utiliza Git como parte central do processo            | Fluxo validado sem conflito de fonte de verdade        | Condicional   |
| EV-05 | Integrações com ferramentas de trabalho       | Relacionar execução administrativa e trabalho externo   | GitHub, GitLab, Linear, Jira, ClickUp ou equivalentes                 | Procura repetida por integrações específicas                   | Integração reduz trabalho manual mensurável            | Condicional   |
| EV-06 | Integração com IA externa                     | Reduzir dependência do copiar e colar                   | Modelos externos, chaves próprias ou serviço gerido                   | Procura por utilizadores sem IA local                          | Custos, privacidade e experiência validados            | Condicional   |
| EV-07 | Analytics de portefólio                       | Apoiar decisões sobre produtos                          | Saúde, atenção, revisões, decisões e utilização de IA                 | Dados suficientes e decisões reais dependentes dos indicadores | Indicadores influenciam decisões e são compreendidos   | Condicional   |
| EV-08 | Administração financeira leve                 | Acrescentar contexto económico sem criar contabilidade  | Receitas resumidas, custos recorrentes e subscrições                  | Clientes consideram esta informação essencial                  | Informação melhora a gestão sem duplicar ERP           | Condicional   |
| EV-09 | Gestão leve de activos e fornecedores         | Centralizar informação administrativa complementar      | Activos digitais, contratos resumidos, fornecedores e renovações      | Necessidade recorrente validada                                | Redução comprovada de fragmentação                     | Condicional   |
| EV-10 | Versão privada ou self-hosted                 | Servir clientes com exigências especiais                | Deploy privado, configuração e operação empresarial                   | Clientes dispostos a pagar e requisitos de segurança concretos | Instalação suportável e modelo comercial sustentável   | Condicional   |
| EV-11 | Aplicação móvel ou experiência móvel avançada | Facilitar consulta e validação fora do computador       | Painel, notificações, revisões e aprovações                           | Utilização móvel relevante                                     | Fluxos móveis utilizados de forma recorrente           | Condicional   |
| EV-12 | Escalabilidade avançada                       | Suportar crescimento comprovado                         | Processamento assíncrono, filas, cache e optimização                  | Limites reais de desempenho ou operação                        | Ganho de capacidade comprovado                         | Condicional   |

---

# Itens adiados ou descartados do núcleo

| ID     | Item                                              | Decisão              | Justificação                                                       |
| ------ | ------------------------------------------------- | -------------------- | ------------------------------------------------------------------ |
| OUT-01 | Gestão completa de projectos                      | Fora do núcleo       | Concorrência madura e desalinhamento com a proposta administrativa |
| OUT-02 | Sprints, épicos e user stories                    | Fora do núcleo       | Devem permanecer nas ferramentas especializadas                    |
| OUT-03 | Diagramas de Gantt e timesheets                   | Fora do núcleo       | Elevado escopo e baixo valor para a tese inicial                   |
| OUT-04 | ERP completo                                      | Descartado           | Complexidade funcional, legal e operacional                        |
| OUT-05 | Contabilidade e folha salarial                    | Descartado           | Exige especialização e regulação próprias                          |
| OUT-06 | CRM completo                                      | Descartado           | Desvio estratégico e forte concorrência                            |
| OUT-07 | Marketplace de agentes                            | Adiado sem previsão  | Depende de base instalada e efeito de rede                         |
| OUT-08 | Agentes autónomos com autoridade ampla            | Adiado               | Risco elevado e falta de validação                                 |
| OUT-09 | Equipas multiagente                               | Adiado               | Complexidade sem caso de uso prioritário                           |
| OUT-10 | Construtor genérico de workflows                  | Descartado do núcleo | Transformaria o produto numa plataforma horizontal                 |
| OUT-11 | Alojamento próprio de modelos                     | Descartado do núcleo | Não faz parte da proposta central                                  |
| OUT-12 | Sincronização Git bidireccional automática        | Adiado               | Conflitos, segurança e dupla fonte de verdade                      |
| OUT-13 | Microserviços por domínio                         | Adiado               | Overengineering sem escala comprovada                              |
| OUT-14 | Kafka, event sourcing e CQRS                      | Adiado               | Complexidade sem necessidade actual                                |
| OUT-15 | Representação lúdica de funcionários de IA        | Descartado do núcleo | Não melhora controlo, governação ou valor administrativo           |
| OUT-16 | Personalidades e avatares como proposta principal | Descartado do núcleo | Cria expectativas incorrectas e distrai do problema real           |

---

# Requisitos transversais da baseline

Os requisitos seguintes aplicam-se a todos os itens relevantes.

## RT-01 — Isolamento

Nenhum utilizador ou agente pode aceder a dados de uma empresa sem autorização explícita.

## RT-02 — Rastreabilidade

Operações críticas devem identificar:

* actor;
* empresa;
* entidade;
* operação;
* data;
* resultado;
* execução relacionada, quando aplicável.

## RT-03 — Versionamento documental

Alterações aprovadas a documentos devem gerar uma versão recuperável.

## RT-04 — Fonte de verdade

A base de dados e o Markdown não podem manter valores operacionais concorrentes.

## RT-05 — Validação humana

Resultados de IA não podem tornar-se informação oficial apenas por terem sido produzidos.

## RT-06 — Portabilidade

Documentos e dados essenciais devem poder ser exportados em formatos utilizáveis.

## RT-07 — Segurança de conteúdo

Markdown e resultados importados devem ser tratados como conteúdo não confiável.

## RT-08 — Recuperação

Deve existir capacidade mínima de recuperar dados e versões após falha ou alteração incorrecta.

## RT-09 — Simplicidade

Nenhum item deve introduzir um framework genérico quando uma regra específica for suficiente.

## RT-10 — Evidência

Cada item concluído deve possuir demonstração, teste, documento aprovado ou resultado de piloto correspondente.

---

# Critérios gerais de prontidão para decomposição

Um item macro está pronto para ser decomposto quando:

* o objectivo está claro;
* o actor principal está identificado;
* o resultado esperado está definido;
* o escopo incluído e excluído está delimitado;
* as dependências estão conhecidas;
* as regras de negócio essenciais estão disponíveis;
* os critérios de aceitação macro são verificáveis;
* as decisões bloqueadoras estão resolvidas;
* não exige redefinição da visão ou arquitectura.

---

# Critérios gerais de conclusão de um item macro

Um item macro apenas pode ser encerrado quando:

1. o resultado funcional ou técnico foi entregue;

2. os critérios de verificação foram cumpridos;

3. as dependências relevantes foram integradas;

4. as permissões e regras de segurança foram testadas;

5. os erros principais foram tratados;

6. a documentação mínima foi actualizada;

7. existe evidência de teste ou demonstração;

8. não foram introduzidas funcionalidades fora da baseline sem aprovação;

9. os riscos residuais estão documentados;

10. o estado do item está formalmente registado.

---

# Regras para decomposição posterior

A decomposição desta baseline deve seguir a hierarquia:

```text
Fase
└── Item macro
    └── Capacidade ou épico
        └── História funcional ou requisito técnico
            └── Tarefa de implementação
```

Cada backlog detalhado deverá:

* referenciar o ID do item macro;
* manter os limites definidos nesta baseline;
* separar requisitos funcionais e técnicos;
* incluir critérios de aceitação;
* indicar dependências;
* identificar riscos;
* incluir validação e documentação;
* evitar antecipar funcionalidades de fases posteriores;
* não transformar pendências administrativas em gestão completa de projectos;
* não introduzir integrações externas sem necessidade validada.

---

# Controlo de alterações da baseline

Uma alteração à baseline deve ser formalmente avaliada quando:

* adiciona nova entidade principal;
* altera a fonte de verdade;
* introduz integração crítica;
* aumenta autonomia da IA;
* altera o modelo de utilizadores;
* adiciona domínio funcional novo;
* antecipa item de uma fase posterior;
* remove requisito transversal;
* afecta isolamento ou segurança;
* aumenta significativamente o escopo do MVP.

Cada alteração deverá indicar:

* motivo;
* benefício esperado;
* impacto;
* dependências;
* risco;
* fase afectada;
* itens substituídos ou adicionados;
* decisão de aprovação.

---

# Parecer final da baseline

A baseline está estruturada para avançar para decomposição detalhada da **Fase 0** e, após o fecho das decisões bloqueadoras, para o backlog do **MVP**.

A decomposição não deve iniciar simultaneamente para todas as fases.

A ordem recomendada é:

1. decompor e executar a Fase 0;

2. actualizar a baseline com as decisões tomadas;

3. decompor o MVP por blocos funcionais e técnicos;

4. executar o piloto;

5. rever a Versão 1 com base em evidências;

6. manter a Fase 3 apenas como reserva estratégica condicionada.

## Estado final

**BASELINE PRONTA PARA DECOMPOSIÇÃO CONTROLADA DA FASE 0.**
