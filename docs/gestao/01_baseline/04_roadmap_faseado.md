# Roadmap faseado — VentureOps AI

## 1. Síntese do roadmap

O roadmap propõe uma implementação incremental, começando pela validação do núcleo administrativo do produto antes de introduzir integrações directas com IA local, automações ou capacidades avançadas.

O objectivo geral é demonstrar que uma plataforma central para gerir produtos, decisões, documentos, pendências e execuções assistidas reduz a fragmentação operacional de fundadores técnicos e microequipas.

A lógica de faseamento é:

1. fechar decisões funcionais e técnicas mínimas;
2. construir um MVP pequeno e utilizável;
3. validar utilização real;
4. consolidar segurança, colaboração e integração com IA;
5. expandir apenas funcionalidades cuja procura tenha sido demonstrada.

O MVP deverá concentrar-se em:

* uma empresa;
* vários produtos;
* visão administrativa;
* documentos;
* decisões;
* pendências;
* funções;
* execuções assistidas manuais;
* validação de resultados.

O principal risco a controlar é construir uma plataforma demasiado ampla antes de provar que a gestão administrativa de vários produtos constitui uma dor suficientemente relevante.

A passagem entre fases deve depender de:

* estabilidade funcional;
* utilização real;
* feedback recolhido;
* resolução de riscos críticos;
* evidência de valor;
* decisões pendentes fechadas.

---

## 2. Princípios de faseamento

### 2.1. Entregar valor antes de automatizar

O produto deve resolver primeiro o problema de organização, contexto e controlo.

A automação não deve ser utilizada para esconder um modelo funcional ainda pouco claro.

### 2.2. Validar o núcleo antes das integrações

A primeira versão deve demonstrar valor sem depender de:

* IA local integrada;
* Git;
* pesquisa semântica;
* APIs de modelos externos;
* ferramentas de gestão de projectos.

### 2.3. Manter o MVP pequeno

O MVP deve ser suficiente para executar um fluxo completo, mas não deve tentar cobrir toda a administração empresarial.

### 2.4. Evoluir mediante evidência

Cada nova funcionalidade deve responder a:

* comportamento observado;
* feedback recorrente;
* risco concreto;
* bloqueio de adopção;
* oportunidade comercial validada.

### 2.5. Separar produto de infraestrutura

Infraestrutura avançada só deve ser criada quando necessária para uma capacidade já validada.

### 2.6. Respeitar a arquitectura aprovada

O roadmap deve manter:

* monólito modular;
* PostgreSQL;
* Markdown para conteúdo documental;
* armazenamento de objectos;
* API REST;
* autorização por empresa;
* auditoria;
* aprovação humana.

### 2.7. Segurança desde o início

O isolamento de dados, a autorização e a protecção dos documentos não podem ser adiados para depois do piloto.

### 2.8. Adiar escala prematura

Não introduzir inicialmente:

* microserviços;
* filas distribuídas;
* Kubernetes dedicado;
* bases vectoriais;
* event sourcing;
* workflows genéricos.

### 2.9. Manter portabilidade

O utilizador deve conseguir exportar os documentos e os dados essenciais sem ficar dependente de um formato fechado.

### 2.10. Evitar reconstruir ferramentas existentes

O produto deve gerir apenas pendências administrativas mínimas.

Gestão detalhada de projectos, desenvolvimento, vendas ou contabilidade deve permanecer em ferramentas próprias.

---

## 3. Fase 0 — Preparação e alinhamento

## 3.1. Objectivo

Resolver as decisões que condicionam o modelo funcional, a experiência do MVP e a estrutura mínima de dados antes de iniciar implementação significativa.

Esta fase deve reduzir ambiguidade, não produzir documentação excessiva.

## 3.2. Actividades principais

### Fecho do fluxo principal

Definir o fluxo completo que o MVP deve suportar:

1. criar empresa;
2. criar produtos;
3. registar contexto e documentos;
4. registar decisão ou pendência;
5. preparar uma execução assistida;
6. utilizar IA externa ou local manualmente;
7. devolver resultado;
8. rever e aprovar;
9. actualizar o estado administrativo.

### Fecho do modelo funcional

Confirmar:

* empresa;
* produto;
* documento;
* decisão;
* pendência;
* função;
* execução;
* resultado;
* revisão;
* auditoria.

### Definição dos estados

Fechar os estados mínimos de:

* produto;
* decisão;
* pendência;
* documento;
* função;
* execução;
* revisão.

### Divisão entre base de dados e Markdown

Documentar, por tipo de informação:

* fonte oficial;
* campos estruturados;
* conteúdo documental;
* regras de versão;
* regras de actualização.

### Definição da visão de atenção

Escolher regras simples e explicáveis, por exemplo:

* produto sem revisão;
* decisão pendente;
* pendência vencida;
* resultado aguardando validação;
* documento marcado como desactualizado.

### Confirmação da stack

Validar:

* estrutura do repositório;
* tecnologias já existentes;
* autenticação existente;
* padrões de API;
* biblioteca visual;
* estratégia de testes;
* plataforma de deploy.

### Preparação do piloto

Definir:

* perfil dos primeiros utilizadores;
* dados a utilizar;
* produtos reais a registar;
* critérios de feedback;
* critérios de sucesso;
* limites do piloto.

## 3.3. Decisões necessárias

* uma empresa ou várias empresas por conta no MVP;
* utilização individual ou multiutilizador;
* papéis mínimos;
* campos obrigatórios da ficha de produto;
* formato dos pacotes de contexto;
* formato de importação de resultados;
* política de versões documentais;
* forma de armazenamento dos ficheiros;
* regras mínimas de atenção;
* nível de auditoria;
* critérios do piloto.

## 3.4. Pré-requisitos

* visão de produto aprovada;
* arquitectura mínima aceite;
* stack ou repositório identificado;
* disponibilidade de pelo menos um cenário real de utilização;
* responsável funcional definido.

## 3.5. Dependências

* decisões de produto;
* requisitos mínimos de segurança;
* infraestrutura disponível;
* identificação dos utilizadores piloto;
* confirmação do modelo de autenticação.

## 3.6. Riscos

### Análise prolongada

Risco de continuar a produzir documentos sem avançar para validação prática.

**Mitigação:** limitar a fase às decisões que bloqueiam implementação.

### Escopo reabrir continuamente

**Mitigação:** criar uma lista formal de itens fora do MVP.

### Estados e entidades demasiado detalhados

**Mitigação:** manter apenas os campos necessários ao fluxo piloto.

## 3.7. Critérios de saída

A fase termina quando existirem:

* fluxo principal aprovado;
* entidades mínimas confirmadas;
* estados definidos;
* fronteira entre BD e Markdown documentada;
* regras de atenção fechadas;
* stack confirmada;
* utilizadores piloto identificados;
* critérios de sucesso definidos;
* lista explícita do que fica fora do MVP.

## 3.8. Resultado esperado

Uma especificação funcional e técnica mínima, suficientemente clara para gerar backlog sem reabrir decisões estruturais em cada funcionalidade.

---

## 4. Fase 1 — MVP

## 4.1. Objectivo

Entregar uma versão utilizável que permita a um fundador gerir administrativamente vários produtos e executar um ciclo completo de trabalho assistido por IA, sem integração automática.

O MVP deve validar se a plataforma reduz fragmentação e melhora a clareza sobre o estado dos produtos.

## 4.2. Funcionalidades incluídas

### Acesso e empresa

* autenticação;
* perfil de utilizador;
* uma empresa activa;
* configurações essenciais.

A estrutura de dados poderá estar preparada para várias empresas, mas a experiência do MVP não necessita de explorar essa capacidade.

### Portefólio de produtos

* criação e edição de produtos;
* estado;
* fase;
* responsável;
* resumo;
* data da última revisão;
* próximo ponto de atenção;
* arquivo.

### Ficha administrativa do produto

* propósito;
* estado actual;
* contexto resumido;
* riscos;
* documentos;
* decisões;
* pendências;
* execuções relacionadas;
* histórico básico.

### Documentos

* criação;
* edição;
* pré-visualização;
* conteúdo Markdown;
* associação a produto;
* tipos mínimos;
* controlo de versão;
* histórico;
* exportação.

### Decisões

* registo de decisão;
* contexto;
* estado;
* responsável;
* data;
* produto afectado;
* documento de detalhe opcional.

### Pendências administrativas

* criação;
* responsável;
* tipo;
* estado;
* prioridade;
* prazo;
* associação a produto;
* ligação opcional a decisão.

### Funções

* função humana;
* função de IA;
* função híbrida;
* propósito;
* responsabilidades;
* limites;
* documento de instruções;
* indicação de aprovação obrigatória.

### Execuções assistidas

* criar pedido;
* seleccionar produto;
* seleccionar função;
* seleccionar versões documentais;
* preparar pacote de contexto;
* copiar ou exportar contexto;
* registar resultado manualmente;
* rever;
* aprovar ou rejeitar;
* manter ligação entre pedido, contexto e resultado.

### Visão de atenção

* produtos sem revisão;
* decisões pendentes;
* pendências vencidas;
* execuções por validar;
* documentos sinalizados como desactualizados.

### Auditoria básica

* criação;
* edição;
* aprovação;
* rejeição;
* arquivo;
* exportação;
* versão documental.

### Portabilidade

* exportação de documentos;
* exportação dos dados essenciais;
* manifesto simples com relações principais.

## 4.3. Funcionalidades excluídas

* múltiplos utilizadores complexos;
* convites;
* permissões avançadas;
* ligação directa a IA local;
* utilização automática de APIs de IA;
* sincronização Git;
* pesquisa semântica;
* execução recorrente;
* notificações avançadas;
* integração com gestores de projectos;
* gestão financeira;
* CRM;
* agentes autónomos;
* workflows configuráveis;
* aplicação móvel.

## 4.4. Entregáveis técnicos

* estrutura do monólito modular;
* frontend web;
* API REST;
* PostgreSQL;
* armazenamento de objectos;
* autenticação;
* autorização mínima;
* versionamento de documentos;
* auditoria;
* testes dos fluxos críticos;
* Docker para desenvolvimento;
* pipeline de integração e deploy;
* ambiente de piloto;
* backups mínimos;
* logs estruturados;
* health checks.

## 4.5. Dependências

* decisões da Fase 0;
* armazenamento disponível;
* autenticação confirmada;
* infraestrutura de desenvolvimento;
* dados de piloto;
* utilizadores para teste.

## 4.6. Riscos

### MVP tornar-se uma versão completa

**Mitigação:** qualquer nova funcionalidade deve demonstrar que bloqueia o fluxo principal.

### Utilizador não manter os dados actualizados

**Mitigação:** formulários curtos, revisões simples e visão de atenção útil.

### Pouco valor sem integração automática

**Mitigação:** validar explicitamente se o contexto organizado e a rastreabilidade já geram valor.

### Complexidade documental

**Mitigação:** poucos tipos de documento e editor simples.

### Visão de atenção pouco útil

**Mitigação:** regras transparentes e ajustadas com feedback do piloto.

## 4.7. Validações necessárias

Durante o piloto, validar:

* facilidade de configuração;
* utilidade da ficha de produto;
* clareza do painel de atenção;
* esforço necessário para manter informação;
* valor do registo de decisões;
* utilidade do pacote de contexto;
* frequência das execuções assistidas;
* valor do histórico;
* relevância da aprovação;
* necessidade real de IA local integrada.

## 4.8. Critérios de saída

O MVP pode ser considerado concluído quando:

* o fluxo completo funciona;
* dados de diferentes empresas não se misturam, caso o modelo multiempresa esteja activo;
* documentos possuem versões recuperáveis;
* execuções guardam as versões exactas do contexto;
* resultados podem ser aprovados ou rejeitados;
* regras de atenção são compreensíveis;
* exportação funciona;
* operações críticas estão auditadas;
* testes dos fluxos core passam;
* não existem vulnerabilidades críticas conhecidas;
* pelo menos um piloto real foi executado;
* feedback foi registado e analisado.

## 4.9. Resultado esperado

Uma aplicação utilizável por um fundador real para gerir vários produtos, manter contexto e executar trabalho assistido por IA com rastreabilidade.

O resultado da fase não é uma plataforma completa. É evidência de que o núcleo administrativo resolve um problema relevante.

---

## 5. Fase 2 — Versão 1

## 5.1. Objectivo

Consolidar o produto após a validação do MVP, tornando-o adequado a utilização recorrente por pequenas equipas e reduzindo os principais atritos identificados no piloto.

## 5.2. Melhorias funcionais

### Colaboração

* múltiplos utilizadores;
* convites;
* papéis;
* responsável por produto;
* revisor;
* histórico por utilizador.

### Permissões

* leitura;
* edição;
* revisão;
* administração;
* exportação;
* restrições por empresa;
* restrições por função, quando justificadas.

### Revisão de produtos

* ciclos de revisão;
* confirmação de estado;
* registo de alterações;
* próxima revisão;
* produtos sem revisão.

### Templates

* modelos de produto;
* modelos documentais;
* modelos de função;
* modelos de execução;
* modelos de revisão.

### Pesquisa

* pesquisa por título e conteúdo;
* filtros por produto;
* filtros por estado;
* pesquisa transversal básica.

### Notificações

* pendências próximas;
* resultados por validar;
* produtos sem revisão;
* decisões pendentes.

### Histórico consolidado

* linha temporal por produto;
* comparação de versões;
* histórico de decisões;
* histórico de execuções.

### Referências externas

* ligação manual a repositórios;
* ligação a projectos;
* ligação a tarefas externas;
* identificação do sistema de origem.

## 5.3. Melhorias técnicas

* endurecimento de permissões;
* testes de segurança adicionais;
* melhoria de performance;
* paginação consistente;
* limites de utilização;
* gestão de quotas;
* melhor tratamento de conflitos;
* política de retenção;
* restauro validado;
* observabilidade ampliada;
* captura de erros;
* documentação operacional.

## 5.4. Integração prioritária

### Conector de IA local limitado

A primeira integração directa deverá manter escopo restrito:

* autenticar um agente;
* consultar execuções explicitamente disponibilizadas;
* obter pacote de contexto;
* submeter resultado;
* consultar estado da revisão.

O agente não deverá poder:

* editar produtos livremente;
* alterar documentos directamente;
* aprovar resultados;
* executar acções empresariais;
* consultar informação fora do contexto atribuído.

A integração só deve entrar se o MVP confirmar procura real.

## 5.5. Qualidade, segurança e observabilidade

* testes de autorização por papel;
* testes de isolamento;
* auditoria completa de tokens;
* rate limiting;
* métricas de utilização;
* alertas operacionais;
* monitorização de falhas do armazenamento;
* revisão dos dados incluídos em logs;
* política de backup e recuperação;
* tratamento de revogação de acesso.

## 5.6. Dependências

* MVP utilizado em cenário real;
* feedback priorizado;
* modelo de colaboração validado;
* necessidade de integração local confirmada;
* operação básica estável;
* decisões de monetização preliminares.

## 5.7. Riscos

### Tentar resolver todo o feedback

**Mitigação:** seleccionar apenas problemas repetidos ou bloqueadores.

### Integração local gerar suporte excessivo

**Mitigação:** suportar inicialmente um contrato de API simples, sem assumir instalação de modelos.

### Permissões tornarem-se demasiado complexas

**Mitigação:** manter papéis fixos antes de introduzir permissões configuráveis.

### Templates reduzirem flexibilidade

**Mitigação:** permitir adaptação limitada sem criar um construtor genérico.

## 5.8. Critérios de saída

* utilização recorrente por utilizadores piloto;
* colaboração funcional;
* permissões testadas;
* revisão de produtos utilizada;
* pesquisa e histórico estáveis;
* integração local validada, se incluída;
* incidentes críticos resolvidos;
* backups e recuperação testados;
* proposta comercial inicial testada;
* documentação de utilizador e operação actualizada.

## 5.9. Resultado esperado

Primeira versão consolidada, adequada a pequenas equipas, com segurança, colaboração e integração controlada com IA local.

---

## 6. Fase 3 — Melhorias posteriores

## 6.1. Objectivo

Expandir o produto apenas depois de existir adopção recorrente, procura clara e evidência de que as melhorias aumentam retenção, eficiência ou receita.

## 6.2. Funcionalidades avançadas

### Automação controlada

* execuções agendadas;
* revisões periódicas;
* geração automática de relatórios;
* actualizações propostas;
* notificações inteligentes;
* aprovação por excepção.

### Integrações de IA

* mais conectores locais;
* APIs de modelos externos;
* escolha de fornecedor;
* utilização de chaves próprias;
* IA gerida pela plataforma;
* políticas por destino dos dados.

### Pesquisa e conhecimento

* pesquisa semântica;
* recuperação de contexto;
* recomendações documentais;
* detecção de inconsistências;
* identificação de documentação desactualizada.

### Git

* exportação para repositório;
* importação controlada;
* propostas de alteração;
* comparação de versões;
* sincronização limitada.

Sincronização bidireccional automática só deve ser considerada se houver procura concreta.

### Analytics

* saúde do portefólio;
* produtos sem atenção;
* decisões pendentes;
* tempo até validação;
* utilização por função;
* utilização de IA;
* qualidade documental;
* tendências operacionais.

### Gestão administrativa adicional

Poderá incluir, caso validado:

* activos digitais;
* subscrições;
* custos recorrentes;
* fornecedores;
* contratos;
* receitas resumidas;
* obrigações.

Não deve evoluir para contabilidade ou ERP.

## 6.3. Optimizações

* processamento assíncrono;
* filas;
* cache;
* indexação;
* armazenamento optimizado;
* geração assíncrona de exportações;
* quotas;
* controlo de custos de IA;
* melhoria de latência.

## 6.4. Escalabilidade

Só deve ser considerada quando existirem sinais como:

* crescimento relevante de dados;
* operações pesadas;
* múltiplas instâncias;
* necessidade de workers;
* pesquisas lentas;
* exportações extensas;
* elevado número de agentes.

## 6.5. Integrações secundárias

* GitHub;
* GitLab;
* Linear;
* Jira;
* ClickUp;
* correio electrónico;
* calendário;
* armazenamento documental;
* ferramentas de automação.

Cada integração deve resolver um fluxo validado, não apenas aumentar o catálogo.

## 6.6. Melhorias de experiência

* onboarding assistido;
* importação orientada;
* recomendações;
* personalização controlada;
* aplicações móveis;
* experiência offline parcial;
* dashboards configuráveis.

## 6.7. Critérios para justificar implementação

Uma melhoria posterior deve cumprir pelo menos uma condição:

* resolve bloqueio recorrente;
* aumenta retenção;
* reduz suporte;
* desbloqueia cliente pagante;
* reduz risco relevante;
* automatiza trabalho frequente;
* permite monetização adicional;
* responde a procura de vários clientes;
* resolve limitação comprovada de escala.

---

## 7. Itens opcionais

| Item                                 | Benefício                                   | Custo ou complexidade                          | Condição para avançar                                 | Fase recomendada |
| ------------------------------------ | ------------------------------------------- | ---------------------------------------------- | ----------------------------------------------------- | ---------------- |
| Múltiplas empresas por utilizador    | Permite gerir vários negócios               | Aumenta complexidade de navegação e permissões | Utilizadores piloto demonstrarem necessidade          | Fase 2           |
| Pesquisa semântica                   | Facilita recuperação de contexto            | Embeddings, indexação, custos e segurança      | Pesquisa textual tornar-se insuficiente               | Fase 3           |
| Integração directa com IA externa    | Reduz copiar e colar                        | Custos, chaves, privacidade e limites          | Procura por utilizadores sem IA local                 | Fase 2 ou 3      |
| Conector de IA local                 | Automatiza obtenção e submissão de trabalho | Autenticação, distribuição e suporte           | Utilizadores piloto considerarem integração essencial | Fase 2           |
| Importação inicial de Markdown       | Reduz esforço de migração                   | Mapeamento e resolução de duplicados           | Pilotos já possuírem documentação organizada          | Fase 1 ou 2      |
| Templates por tipo de produto        | Acelera onboarding                          | Manutenção e risco de excesso                  | Padrões repetidos identificados                       | Fase 2           |
| Integração Git de leitura            | Facilita acesso a documentação existente    | Credenciais e estrutura variável               | Segmento técnico utilizar Git como fonte principal    | Fase 2 ou 3      |
| Notificações por correio electrónico | Melhora acompanhamento                      | Configuração e risco de ruído                  | Utilizadores não consultarem regularmente o painel    | Fase 2           |
| Indicadores de saúde do produto      | Melhora visão executiva                     | Regras podem ser arbitrárias                   | Existirem sinais administrativos validados            | Fase 2           |
| Aplicação móvel                      | Acesso rápido                               | Elevado custo de produto e manutenção          | Utilização móvel tornar-se relevante                  | Fase 3           |
| IA gerida pela plataforma            | Reduz barreira técnica                      | Custo variável, privacidade e margens          | Procura comercial e modelo de custos validados        | Fase 3           |
| Self-hosted                          | Privacidade e controlo                      | Deploy, actualizações e suporte elevados       | Clientes B2B exigirem instalação privada              | Fase 3           |

---

## 8. Itens adiados ou fora de escopo

## 8.1. Gestão completa de projectos

Inclui:

* sprints;
* épicos;
* user stories;
* dependências;
* Gantt;
* capacidade;
* timesheets.

### Justificação

Mercado já coberto por ferramentas maduras e desalinhado com o foco administrativo.

---

## 8.2. ERP e contabilidade

Inclui:

* facturação;
* contabilidade;
* folha salarial;
* impostos;
* inventário.

### Justificação

Complexidade funcional, legal e operacional muito elevada.

---

## 8.3. CRM completo

### Justificação

Aumentaria o escopo e colocaria o produto em concorrência com plataformas consolidadas.

---

## 8.4. Agentes autónomos

### Justificação

* risco elevado;
* baixa previsibilidade;
* necessidade de governação avançada;
* valor central ainda não validado.

---

## 8.5. Equipas multiagente

### Justificação

Complexidade prematura e ausência de caso de uso prioritário validado.

---

## 8.6. Marketplace de agentes ou templates

### Justificação

Exige base instalada, oferta, procura, avaliação e controlo de qualidade.

---

## 8.7. Sincronização Git bidireccional automática

### Justificação

* conflitos;
* segredos;
* múltiplas fontes de verdade;
* suporte elevado;
* falta de validação.

---

## 8.8. Construtor genérico de workflows

### Justificação

Transformaria o produto numa plataforma de automação horizontal.

---

## 8.9. Alojamento de modelos de IA

### Justificação

Não faz parte da proposta principal e acrescenta custos operacionais significativos.

---

## 8.10. Microserviços e infraestrutura distribuída

### Justificação

Não existe escala que justifique:

* microserviços;
* Kafka;
* service mesh;
* CQRS;
* event sourcing;
* Kubernetes dedicado.

---

## 8.11. Representação excessivamente humana das IAs

Inclui:

* salários;
* avatares;
* personalidades;
* organogramas artificiais;
* simulação de relações laborais.

### Justificação

Não melhora a governação e pode criar expectativas erradas sobre autonomia e responsabilidade.

---

## 9. Dependências entre fases

## 9.1. Fase 0 para Fase 1

A Fase 1 depende de:

* estados fechados;
* entidades mínimas definidas;
* divisão BD/Markdown aprovada;
* fluxo do MVP validado;
* autenticação decidida;
* regras de atenção fechadas;
* cenário de piloto preparado.

Bloqueadores:

* ausência de definição da ficha do produto;
* dúvida sobre fonte de verdade;
* inexistência de infraestrutura mínima;
* inexistência de utilizador piloto.

## 9.2. Fase 1 para Fase 2

A Fase 2 depende de:

* MVP estável;
* piloto concluído;
* feedback analisado;
* uso recorrente demonstrado;
* principais problemas de UX identificados;
* modelo de colaboração confirmado;
* necessidade de integração local validada.

Bloqueadores:

* ausência de valor percebido;
* abandono após configuração;
* esforço de manutenção superior ao benefício;
* falhas críticas de segurança;
* modelo funcional incompreendido.

## 9.3. Fase 2 para Fase 3

A Fase 3 depende de:

* utilização recorrente;
* clientes ou pilotos activos;
* necessidades repetidas;
* modelo comercial mais claro;
* capacidade de suporte;
* estabilidade operacional;
* procura por automação ou integrações.

## 9.4. Trabalho que pode avançar em paralelo

Na Fase 0:

* protótipo de UX;
* validação funcional;
* preparação de infraestrutura;
* definição de segurança.

Na Fase 1:

* frontend e backend por módulos;
* armazenamento documental;
* testes de autorização;
* preparação do piloto;
* documentação de utilização.

Na Fase 2:

* colaboração;
* melhoria de pesquisa;
* endurecimento de segurança;
* desenvolvimento limitado do conector local.

## 9.5. Trabalho que não deve avançar em paralelo prematuramente

Não iniciar antes da validação do MVP:

* pesquisa semântica;
* Git bidireccional;
* agentes autónomos;
* múltiplas integrações de IA;
* aplicação móvel;
* self-hosting;
* analytics avançado.

---

## 10. Riscos do roadmap

## 10.1. Produto

### Risco

O produto continuar demasiado abstracto.

### Mitigação

Manter o MVP centrado num fluxo real e numa visão de atenção concreta.

### Risco

Adicionar funções solicitadas por um único utilizador.

### Mitigação

Distinguir personalização de necessidade repetível.

---

## 10.2. Técnica

### Risco

Inconsistência entre base de dados e ficheiros.

### Mitigação

Uma fonte oficial por campo, gravação controlada pelo backend e testes de integridade.

### Risco

Complexidade prematura na integração com IA.

### Mitigação

Fluxo manual primeiro e API limitada depois.

### Risco

Modelo modular degradar-se num monólito acoplado.

### Mitigação

Separação de módulos, serviços de domínio e testes de fronteira.

---

## 10.3. Equipa

### Risco

Equipa reduzida acumular produto, desenvolvimento, operações e suporte.

### Mitigação

Limitar escopo e priorizar apenas o fluxo principal.

### Risco

Conhecimento concentrado numa pessoa.

### Mitigação

Documentação mínima, testes e decisões registadas.

---

## 10.4. Prazo

### Risco

A Fase 0 prolongar-se indefinidamente.

### Mitigação

Critérios de saída objectivos e apenas decisões bloqueadoras.

### Risco

Integrações atrasarem o MVP.

### Mitigação

Proibir integrações directas não essenciais na Fase 1.

---

## 10.5. Adopção

### Risco

Onboarding exigir demasiado esforço.

### Mitigação

Uma empresa, poucos campos, templates simples e importação limitada.

### Risco

Utilizadores não manterem informação actualizada.

### Mitigação

Revisões curtas e valor visível no painel de atenção.

### Risco

Produto não superar a stack actual.

### Mitigação

Comparar explicitamente o fluxo antes e depois durante o piloto.

---

## 10.6. Dados

### Risco

Documentação inicial incompleta.

### Mitigação

Permitir começar com pouco conteúdo e evoluir incrementalmente.

### Risco

Duplicação ou informação contraditória.

### Mitigação

Campos estruturados claros e metadados documentais limitados.

---

## 10.7. Integrações

### Risco

Conector local depender de muitos ambientes.

### Mitigação

Contrato de API simples e suporte inicial restrito.

### Risco

Fornecedores externos alterarem APIs.

### Mitigação

Adaptadores isolados e nenhuma integração crítica no MVP.

---

## 10.8. Segurança

### Risco

Fuga de dados entre empresas.

### Mitigação

Autorização no backend, filtros por tenant e testes dedicados.

### Risco

XSS através de Markdown.

### Mitigação

Sanitização e proibição de execução de conteúdo.

### Risco

Contexto confidencial enviado para IA externa.

### Mitigação

Aviso explícito, selecção manual e classificação futura dos documentos.

---

## 11. Critérios de avanço entre fases

## 11.1. Fase 0 para Fase 1

* fluxo principal aprovado;
* campos mínimos fechados;
* estados definidos;
* fonte de verdade definida;
* regras de atenção aprovadas;
* stack confirmada;
* requisitos de segurança mínimos conhecidos;
* piloto preparado;
* backlog do MVP pode ser escrito sem decisões estruturais em aberto.

## 11.2. Fase 1 para Fase 2

* fluxo principal utilizável de ponta a ponta;
* testes mínimos concluídos;
* documentos versionados e recuperáveis;
* auditoria funcional;
* isolamento de dados validado;
* piloto real concluído;
* feedback recolhido;
* sinais de utilização repetida;
* valor percebido identificado;
* esforço de manutenção aceitável;
* riscos críticos mitigados;
* decisão sobre integração local tomada.

## 11.3. Fase 2 para Fase 3

* versão 1 estável;
* colaboração e permissões funcionais;
* operação e recuperação testadas;
* utilização recorrente;
* necessidades avançadas repetidas;
* benefício esperado documentado;
* capacidade da equipa confirmada;
* modelo comercial ou impacto interno suficientemente claro.

## 11.4. Critério de pausa

O roadmap deve ser pausado ou revisto se:

* utilizadores não regressarem;
* a configuração for considerada excessiva;
* a visão de atenção não gerar valor;
* o produto duplicar ferramentas sem reduzir esforço;
* não existir utilização recorrente dos documentos e decisões;
* a integração com IA for o único benefício percebido;
* não houver intenção real de adopção ou pagamento.

---

## 12. Roadmap em tabela

| Fase                    | Objectivo                                                 | Funcionalidades incluídas                                                                                                  | Funcionalidades excluídas                                                                                            | Dependências                        | Riscos                                                        | Critérios de saída                                              | Resultado esperado                                   |
| ----------------------- | --------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- | ----------------------------------- | ------------------------------------------------------------- | --------------------------------------------------------------- | ---------------------------------------------------- |
| **Fase 0 — Preparação** | Fechar decisões mínimas e preparar piloto                 | Fluxo, entidades, estados, divisão BD/Markdown, regras de atenção, stack, critérios de piloto                              | Implementação extensa, integrações, automação                                                                        | Visão e arquitectura aprovadas      | Análise prolongada, escopo instável                           | Decisões bloqueadoras resolvidas e MVP delimitado               | Base suficiente para backlog técnico                 |
| **Fase 1 — MVP**        | Validar a gestão administrativa de vários produtos        | Empresa, produtos, documentos, decisões, pendências, funções, execuções manuais, validação, atenção, auditoria, exportação | Multiutilizador avançado, IA integrada, Git, pesquisa semântica, projectos completos                                 | Fase 0, infraestrutura, piloto      | MVP crescer, pouco valor sem integração, manutenção excessiva | Fluxo completo, testes, piloto, feedback e segurança mínima     | Produto pequeno, útil e testado em contexto real     |
| **Fase 2 — Versão 1**   | Consolidar colaboração, segurança e utilização recorrente | Multiutilizador, papéis, revisões, templates, pesquisa, notificações, histórico, conector local limitado                   | Agentes autónomos, multiagente, ERP, sincronização Git completa                                                      | MVP validado e procura confirmada   | Suporte elevado, permissões complexas, excesso de feedback    | Utilização recorrente, operação estável, colaboração validada   | Primeira versão comercial ou operacional consolidada |
| **Fase 3 — Melhorias**  | Expandir apenas mediante evidência                        | Automação controlada, IA externa, pesquisa semântica, Git limitado, analytics, integrações, administração adicional        | Funcionalidades sem procura, infraestrutura de escala prematura                                                      | Versão 1 estável, adopção e procura | Dispersão estratégica, custos de integração, regressões       | Benefício, procura e capacidade demonstrados                    | Evolução orientada por utilização e valor            |
| **Adiado**              | Evitar desvio e overengineering                           | —                                                                                                                          | ERP, CRM completo, project management completo, marketplace, agentes autónomos, microserviços, alojamento de modelos | —                                   | Complexidade e desalinhamento                                 | Só reconsiderar com mudança comprovada de mercado ou estratégia | Protecção do foco do produto                         |

---

## 13. Parecer crítico final

### Classificação: PRONTO COM AJUSTES PARA BACKLOG TÉCNICO

O roadmap é realista porque:

* mantém o MVP limitado;
* separa validação de consolidação;
* não exige integração directa com IA para provar valor;
* respeita o monólito modular;
* mantém gestão de projectos e ERP fora do núcleo;
* condiciona automação a utilização real;
* utiliza critérios de passagem entre fases;
* inclui condições de pausa;
* distingue claramente obrigatório, opcional e adiado.

Antes de gerar o backlog técnico, ainda devem ser fechados:

1. estados exactos das entidades;

2. campos mínimos da ficha do produto;

3. regras da visão de atenção;

4. modo inicial de armazenamento de Markdown;

5. uma ou várias empresas por conta;

6. modelo individual ou multiutilizador do MVP;

7. formato do pacote de contexto;

8. critérios concretos do piloto;

9. stack e convenções efectivas do repositório;

10. requisitos mínimos de deploy e segurança.

Estas decisões pertencem à Fase 0 e não justificam reabrir a visão ou a arquitectura.

O roadmap deve ser considerado inválido se a Fase 1 passar a incluir:

* integração completa com IA local;
* gestão avançada de equipas;
* pesquisa semântica;
* Git bidireccional;
* agentes autónomos;
* funcionalidades financeiras;
* múltiplas integrações.

# Parecer final: PRONTO COM AJUSTES PARA BACKLOG TÉCNICO
