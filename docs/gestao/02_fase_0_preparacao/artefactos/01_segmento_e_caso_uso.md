# Segmento inicial e caso de uso principal — VentureOps AI

* Fase: F0 — Preparação e alinhamento
* Itens tratados: F0-B01 (F0-01), F0-B02 (F0-02)
* Decisões bloqueadoras: DB-01, DB-02
* Estado do artefacto: Proposta — sujeito a revisão humana
* Prompt de origem: F0-P02-PR01

Este artefacto separa deliberadamente **factos** (com fonte),
**decisões propostas**, **hipóteses assumidas** e **pontos a validar por
humano**. Nada aqui é uma decisão fechada: todas as decisões ficam **A validar**
até revisão humana.

---

## 1. Factos

Referências: `docs/gestao/01_baseline/02_visao_do_produto.md` (visão) e
`docs/gestao/02_fase_0_preparacao/01_backlog.md` (backlog).

### 1.1. Sobre o público e o segmento

* F-01 — O público prioritário definido é "fundadores técnicos e microequipas que gerem vários produtos digitais e utilizam IA de forma recorrente" (visão §3.1).
* F-02 — Características prováveis indicadas: 1 a 5 colaboradores humanos; 2 ou mais produtos/iniciativas activas; utilização frequente de IA; alguma maturidade técnica; documentação distribuída; necessidade de preservar contexto; interesse em controlo sobre dados; abertura a IA local ou modelos próprios (visão §3.1).
* F-03 — "O tamanho exacto da equipa e o número mínimo de produtos são A validar" (visão §3.1).
* F-04 — Utilizador final típico: fundador, gestor operacional, Product Owner, responsável por produto, colaborador que supervisiona execuções de IA e responsável pela documentação e decisões (visão §3.2).
* F-05 — Públicos secundários futuros (agências orientadas a IA, consultoras de automação, venture studios pequenos, empresas técnicas focadas em soberania de dados, equipas de produto em organizações maiores) "não devem condicionar o MVP" (visão §3.8).

### 1.2. Sobre o problema

* F-06 — Problema principal: fundadores técnicos e microequipas conseguem criar e operar vários produtos com apoio de IA, mas têm dificuldade em manter uma visão consolidada e actualizada da empresa (visão §2, problema principal).
* F-07 — A informação fica dispersa por chats de IA, documentos, repositórios, ferramentas de tarefas, folhas de cálculo, notas, memória individual e sistemas externos (visão §2).
* F-08 — O problema não é executar trabalho, mas manter controlo sobre o que existe, o estado de cada produto, o que foi decidido, que informação é válida, que resultados foram produzidos por IA e o que aguarda validação (visão §2).
* F-09 — A dor aumenta com a combinação de poucos colaboradores, vários produtos simultâneos, uso recorrente de IA, documentação dispersa e necessidade de continuidade entre sessões (visão §2, contexto).

### 1.3. Sobre a tese do MVP e os casos de uso

* F-10 — Tese única do MVP: "uma visão administrativa central de vários produtos, combinada com decisões, documentos e execuções de IA, reduz a fragmentação e melhora o controlo do fundador" (visão §15.1).
* F-11 — Escopo do MVP: uma empresa; vários produtos; ficha administrativa do produto; documentos; decisões; funções; execuções assistidas; resultados; validações; pendências mínimas; visão de atenção; auditoria básica; exportação. A integração directa com IA local é opcional e limitada (visão §15.1).
* F-12 — A visão enumera dez casos de uso principais (visão §7.1 a §7.10), que vão de consultar o estado da empresa (§7.1) a identificar produtos negligenciados (§7.10), passando pela preparação de execução de IA (§7.6) e registo/validação de resultado (§7.7).
* F-13 — O parecer da visão coloca como primeira questão a fechar "qual é exactamente o fluxo principal do MVP" e, na secção de perguntas em aberto, "qual é o fluxo central que gera valor na primeira semana?" (visão §16 e §14.1).

---

## 2. Decisões propostas

Todas com estado **Proposta / A validar**.

### D-01 — Segmento inicial do MVP

**Proposta:** fixar como segmento inicial o **fundador técnico ou microequipa
(1–5 pessoas) que opera 2 ou mais produtos digitais em simultâneo, com
maturidade técnica média a alta, e que utiliza IA de forma recorrente (semanal
ou diária) na criação e operação desses produtos.**

Parâmetros propostos (a confirmar):

* dimensão da equipa: 1 a 5 colaboradores humanos;
* número de produtos: mínimo de 2 activos em simultâneo;
* maturidade técnica: média a alta (confortável com Markdown, Git e ferramentas de IA);
* utilização de IA: recorrente, pelo menos semanal, em tarefas reais de produto.

**Justificação:** corresponde directamente ao público prioritário da visão
(F-01, F-02) e à condição em que a dor é maior (F-09). A exigência de "2 ou mais
produtos" é o que activa a proposta de valor central — a visão consolidada de
portefólio (F-10) — que não faz sentido para quem gere um único produto.
**Estado:** A validar (os limiares exactos de equipa, número de produtos e
frequência de IA estão explicitamente em aberto na visão — F-03).

### D-02 — Exclusões do segmento inicial

**Proposta:** ficam **fora** do segmento inicial:

* fundadores ou empresas com um único produto (não activam a visão de portefólio);
* equipas sem utilização recorrente de IA no trabalho de produto;
* equipas não técnicas ou de baixa maturidade técnica;
* organizações grandes e unidades de inovação/produto de empresas maiores;
* agências orientadas a IA, consultoras de automação e venture studios como alvo primário;
* clientes cujo requisito central seja self-hosting, SSO ou conformidade empresarial avançada.

**Justificação:** a visão declara estes grupos como públicos secundários futuros
que não devem condicionar o MVP (F-05), e o roadmap mantém colaboração avançada,
integrações e self-hosting fora do MVP. **Estado:** A validar.

### D-03 — Caso de uso principal do MVP

**Proposta:** eleger como caso de uso principal o **ciclo de execução assistida
por IA sobre um produto, com validação humana e actualização do estado
administrativo** — isto é, preparar contexto a partir da informação do produto,
executar o trabalho com uma IA (externa ou local, manualmente), registar o
resultado, revê-lo/aprová-lo e reflectir a alteração aprovada no estado
administrativo do produto (documentos, decisões ou pendências).

Este caso de uso integra e atravessa os casos de uso da visão §7.4 (consultar
contexto), §7.6 (preparar execução de IA), §7.7 (registar e validar resultado) e
§7.8 (actualizar documentação), tratados como um único fluxo de valor.

**Justificação:**

1. É o caso de uso que materializa a tese do MVP na sua forma completa (F-10): combina produto + documentos + decisões + execução de IA + validação, e não apenas uma vista de consulta.
2. É o principal diferenciador face a ferramentas genéricas de notas ou gestão documental, porque incorpora a governação humano–IA e a rastreabilidade da execução.
3. É o ciclo que o roadmap identifica como núcleo a validar no MVP ("executar um ciclo completo de trabalho assistido por IA", roadmap §4.1) e cuja conclusão constitui a evidência de valor da fase (roadmap §4.9).

**Alternativa considerada (não eleita):** o caso de uso de entrada recorrente
"consultar o estado / visão de atenção" (visão §7.1 e §7.10). É o ponto de
entrada diário e o candidato a "valor na primeira semana" (F-13), mas por si só
não demonstra a tese completa nem o diferenciador de execução assistida.
Proposta: tratá-lo como **caso de uso de suporte/entrada**, não como principal.
**Estado:** A validar — a escolha entre "ciclo de execução assistida" e "visão
de atenção" como caso de uso principal é uma decisão de produto que requer
confirmação humana (ver P-01).

---

## 3. Descrição do caso de uso principal proposto

Seis elementos exigidos (F0-02). Descrição ao nível funcional, sem implementação.

* **Situação inicial:** um fundador técnico gere vários produtos no VentureOps AI; um produto específico tem informação administrativa e documentos registados e necessita de uma peça de trabalho apoiada por IA (por exemplo, rever a visão do produto, redigir uma decisão fundamentada, ou produzir documentação a partir do contexto existente).
* **Actor:** operador humano do produto (fundador, responsável de produto ou colaborador que supervisiona execuções de IA — F-04). Actor de apoio: função organizacional de IA seleccionada; revisor/aprovador humano (pode ser o mesmo operador no MVP individual).
* **Necessidade:** obter trabalho assistido por IA que use o contexto correcto e actualizado do produto, sem reconstruir esse contexto manualmente a partir de fontes dispersas, e manter o resultado rastreável e sujeito a validação antes de se tornar oficial.
* **Execução:** o operador selecciona o produto, a função e os documentos relevantes; a aplicação prepara um pacote de contexto com as versões exactas; o operador usa esse pacote numa IA externa ou local (manualmente, no MVP); regista o resultado devolvido; revê-o e aprova ou rejeita; ao aprovar, a alteração é reflectida de forma controlada no documento, decisão ou pendência correspondente.
* **Resultado:** um resultado de IA associado à execução correcta, com o contexto e versões que o originaram, um estado de validação explícito (aprovado/rejeitado) e o estado administrativo do produto actualizado de forma auditável.
* **Valor esperado:** redução do tempo e do esforço de preparar contexto e de reconstruir a memória do produto; preservação de continuidade entre sessões; controlo e rastreabilidade sobre o que a IA produziu e sobre o que foi validado; menor dependência de chats e ferramentas isoladas (F-06 a F-08).

**Relação com a tese do MVP:** este caso de uso é a instância operacional
directa da tese (F-10) — demonstra, num único fluxo, que a informação central de
vários produtos combinada com execuções de IA validadas reduz a fragmentação e
aumenta o controlo do fundador. A visão de atenção (caso de uso de suporte)
fornece a entrada recorrente que leva o utilizador a iniciar este ciclo.

---

## 4. Perfis candidatos a piloto

Arquétipos, sem dados pessoais. A identificação nominal de participantes reais é
um ponto a validar por humano (ver P-04) e será fechada em F0-B13.

* **Perfil A — Fundador técnico solo com portefólio pequeno:** 1 pessoa; 2 a 3 produtos digitais próprios em fases diferentes; maturidade técnica alta; usa IA diariamente na escrita de código e documentação; hoje mantém contexto disperso entre chats de IA, Obsidian/Notion e Git.
* **Perfil B — Microestúdio de produto:** 2 a 4 pessoas; 3 a 5 produtos próprios e/ou de clientes; maturidade técnica alta; IA usada em desenvolvimento, documentação e suporte; dor central na perda de contexto entre produtos e entre membros.
* **Perfil C — Consultora/estúdio técnico com múltiplos contextos:** 2 a 3 pessoas; vários contextos de produto simultâneos; uso recorrente de IA; necessidade forte de preservar e recuperar contexto validado entre sessões e entre clientes.

Cada perfil satisfaz os parâmetros de D-01 (≥ 2 produtos, ≥ 1–5 pessoas, uso
recorrente de IA, maturidade técnica média-alta).

---

## 5. Hipóteses assumidas

* H-01 — A frequência mínima "recorrente" de utilização de IA foi assumida como semanal para efeitos de delimitação; a visão não fixa um limiar (F-03).
* H-02 — Assumiu-se que "2 ou mais produtos" é o limiar mínimo que activa a proposta de valor de portefólio; o número mínimo exacto está em aberto (F-03).
* H-03 — Assumiu-se que, no MVP individual, o operador e o revisor/aprovador podem ser a mesma pessoa (coerente com visão §3.6 e o modelo de papéis a decidir em F0-B10).
* H-04 — Os perfis de piloto são arquétipos plausíveis; não representam participantes já comprometidos.

---

## 6. Pontos a validar por humano

* P-01 — Confirmar a eleição do caso de uso principal: "ciclo de execução assistida por IA com validação" (D-03) vs "visão de atenção / consultar estado" como principal. Decisão de produto.
* P-02 — Confirmar os limiares do segmento (D-01): dimensão da equipa, número mínimo de produtos e frequência mínima de utilização de IA (F-03).
* P-03 — Confirmar a lista de exclusões do segmento (D-02), em particular se consultoras/estúdios técnicos entram no segmento inicial ou ficam como público secundário.
* P-04 — Fornecer a identificação nominal de participantes reais de piloto correspondentes aos perfis A–C, ou indicar outros perfis (a fechar em F0-B13).
* P-05 — Confirmar se o caso de uso de suporte "visão de atenção" deve ser explicitamente incluído no fluxo do MVP como ponto de entrada (a articular em F0-B03).

---

## 7. Critérios de verificação deste artefacto

* O perfil do segmento cobre dimensão de equipa, número de produtos, maturidade técnica e uso de IA — secção 2, D-01. ✔
* As exclusões do segmento estão explícitas — secção 2, D-02. ✔
* Existe um único caso de uso principal com justificação — secção 2, D-03. ✔
* A descrição cobre os seis elementos exigidos — secção 3. ✔
* A relação com a tese do MVP está explícita — secção 3, parágrafo final. ✔
* Pelo menos um perfil real candidato a piloto está identificado — secção 4 (perfis A–C). ✔
