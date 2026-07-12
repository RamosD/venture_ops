# Fluxo funcional e modelo funcional do MVP — VentureOps AI

* Fase: F0 — Preparação e alinhamento
* Itens tratados: F0-B03 (F0-03) — fluxo funcional e limites (F0-P02-PR02); F0-B04 (F0-04) — modelo funcional (F0-P03-PR01)
* Decisão bloqueadora: DB-03
* Estado do artefacto: Confirmado com reservas (DEC-20260712-04); INC-02 e INC-04 resolvidas (DEC-F0-FINAL-06/07)
* Prompt de origem: F0-P02-PR02; F0-P03-PR01 (modelo funcional); incoerências fechadas no fecho formal da Fase 0 (2026-07-12)

Nota de âmbito: este artefacto tem três secções previstas — **fluxo funcional**
(secção 2), **limites funcionais preliminares** (secção 3) e **modelo funcional**
(secção 6, reservada para a pipeline F0-P03). As secções 2 e 3 foram
preenchidas em F0-P02-PR02 (não reescritas nesta iteração); a secção 6 (modelo
funcional) é preenchida em F0-P03-PR01. Separação obrigatória entre factos,
decisões propostas, hipóteses e pontos a validar.

---

## 1. Factos

Referências: `docs/gestao/01_baseline/04_roadmap_faseado.md` (roadmap),
`docs/gestao/01_baseline/03_arquitetura.md` (arquitectura),
`docs/gestao/01_baseline/02_visao_do_produto.md` (visão) e
`docs/gestao/02_fase_0_preparacao/artefactos/01_segmento_e_caso_uso.md` (artefacto 01).

### 1.1. Fluxo proposto pela baseline

* F-01 — O roadmap propõe um fluxo do MVP em nove passos: (1) criar empresa; (2) criar produtos; (3) registar contexto e documentos; (4) registar decisão ou pendência; (5) preparar uma execução assistida; (6) utilizar IA externa ou local manualmente; (7) devolver resultado; (8) rever e aprovar; (9) actualizar o estado administrativo (roadmap §3.2).
* F-02 — O fluxo geral da arquitectura (§1) acrescenta, antes da execução, um passo explícito de **definir funções humanas, de IA ou híbridas**, e torna a auditoria transversal a todas as operações relevantes (arquitectura §1).
* F-03 — A arquitectura recomenda, no passo de actualização, que as alterações aprovadas sejam **aplicadas de forma controlada** e que uma resposta de IA não constitua documento actualizado sem acção humana explícita (arquitectura §1, §2.5, §15.6).

### 1.2. Caso de uso principal e escopo

* F-04 — O caso de uso principal proposto (artefacto 01, D-03, a validar) é o ciclo de execução assistida por IA sobre um produto, com validação humana e actualização do estado administrativo, atravessando consulta de contexto, preparação, registo/validação de resultado e actualização documental.
* F-05 — Escopo incluído no MVP (visão §15.1): uma empresa; vários produtos; ficha administrativa; documentos; decisões; funções; execuções assistidas; resultados; validações; pendências mínimas; visão de atenção; auditoria básica; exportação. A integração directa com IA local é "opcional e limitada".
* F-06 — Funcionalidades excluídas do MVP pelo roadmap (§4.3): múltiplos utilizadores complexos, convites, permissões avançadas, ligação directa a IA local, uso automático de APIs de IA, sincronização Git, pesquisa semântica, execução recorrente, notificações avançadas, integração com gestores de projectos, gestão financeira, CRM, agentes autónomos, workflows configuráveis, aplicação móvel.
* F-07 — Itens fora do MVP pela visão (§9): gestão completa de projectos, sprints, backlogs de desenvolvimento, Gantt, timesheets, CRM completo, contabilidade, facturação, folha salarial, gestão de contratos/clientes/fornecedores, alojamento de modelos de IA, execução autónoma, marketplace de agentes, chat genérico incorporado, construtor visual de workflows, app móvel nativa, automações sem aprovação, entre outros.
* F-08 — Itens de Versão 1 e posteriores (visão §15.2 e §15.4): múltiplos utilizadores, permissões, pesquisa, modelos, revisões periódicas, indicadores, API controlada, uma integração de IA local, uma integração documental, notificações, histórico e comparação de versões, classificação de documentos; e, adiados, agentes autónomos, multiagente, self-hosting, múltiplas integrações, CRM, gestão financeira completa, marketplace, app móvel.

---

## 2. Fluxo funcional ponta a ponta do MVP (decisão proposta)

Estado: **Proposta / A validar**. Os rótulos de estado são provisórios; os
estados e transições canónicos são definidos em F0-B05 (pipeline F0-P03). Actor
por defeito no MVP individual: **operador humano (Owner)**; os papéis são
confirmados em F0-B10.

### 2.1. Pré-requisitos de configuração (uma vez por empresa/produto)

Passos de preparação, não repetidos a cada ciclo.

* **C1 — Criar empresa.** Actor: fundador (Owner). Entrada: dados básicos da empresa. Saída: empresa registada e activa. Estado resultante: empresa *Activa*.
* **C2 — Criar produto.** Actor: operador. Entrada: ficha administrativa mínima (definida em F0-B07). Saída: produto registado. Estado resultante: produto *Activo*.
* **C3 — Registar contexto e documentos.** Actor: operador. Entrada: conteúdo Markdown e metadados. Saída: documento com a sua primeira versão, associado ao produto. Estado resultante: documento *Actual* (versão 1).
* **C4 — Definir função organizacional.** Actor: operador (Owner). Entrada: nome, tipo (humana/IA/híbrida), propósito, responsabilidades, limites, instruções. Saída: função disponível para selecção numa execução. Estado resultante: função *Activa*. **Confirmado (DEC-F0-FINAL-06, resolve INC-04):** a função é criada e configurada previamente, como parte da configuração inicial ou da manutenção da função — **não** faz parte do ciclo recorrente de cada execução.

### 2.2. Ciclo principal (recorrente) — execução assistida por IA

Suporta o caso de uso principal (F-04). Entrada recorrente através da visão de
atenção (ver D-03 e P-05).

* **E1 — Registar decisão ou pendência.** Actor: operador. Entrada: contexto da decisão/pendência e produto associado. Saída: decisão ou pendência registada e ligada ao produto. Estado resultante: decisão/pendência no seu estado inicial (F0-B05). Passo condicional: ocorre quando há uma decisão ou pendência a registar; não é obrigatório em todos os ciclos.
* **E2 — Preparar a execução assistida.** Actor: operador. Entrada: selecção de produto, **função organizacional já existente e activa** (ver C4) e documentos com as respectivas versões. Saída: execução criada, referenciando a função seleccionada com um **snapshot das instruções da função** utilizadas (rastreabilidade da versão/configuração), e pacote de contexto gerado com as versões exactas. Estado resultante: execução *Preparada / contexto gerado*. A execução **não** exige recriar nem redefinir a função (DEC-F0-FINAL-06).
* **E3 — Utilizar a IA (manual, externa ou local).** Actor: operador + IA seleccionada. Entrada: pacote de contexto exportado ou copiado. Saída: resultado produzido fora da aplicação. Estado resultante: execução *Aguarda registo de resultado*. Nota: no MVP a utilização é **manual** (exportar/copiar e importar), sem ligação automática (ver D-01).
* **E4 — Registar o resultado.** Actor: operador. Entrada: conteúdo do resultado, origem e notas. Saída: resultado associado à execução, ainda não validado. Estado resultante: resultado *Por validar*.
* **E5 — Rever e aprovar ou rejeitar.** Actor: revisor/aprovador humano (no MVP individual, o próprio operador). Entrada: resultado registado e contexto que o originou. Saída: decisão de validação (aprovado / rejeitado / correcção pedida) com observações. Estado resultante: resultado *Validado* ou *Rejeitado*.
* **E6 — Actualizar o estado administrativo (aplicação controlada).** Actor: operador. Entrada: resultado aprovado. Saída: alteração aplicada de forma controlada ao documento, decisão ou pendência correspondente, com ligação à execução. Estado resultante: entidade actualizada e execução *Concluída*. Nota: aplicação **manual/controlada**, sem mutação automática de documentos (F-03).

### 2.3. Transversal

* **T1 — Auditoria.** Cada operação relevante dos passos acima é registada (actor, entidade, acção, data, correlação). Transversal, não é um passo sequencial (F-02).
* **T2 — Visão de atenção.** Ponto de entrada recorrente que sinaliza produtos e assuntos que exigem intervenção e leva o operador a iniciar o ciclo 2.2. Alimentada pelos estados de E1–E6 (regras definidas em F0-B08).

### 2.4. Correspondência com os nove passos do roadmap

Passo 1 → C1; passo 2 → C2; passo 3 → C3; passo 4 → E1; passo 5 → E2; passo 6 →
E3; passo 7 → E4; passo 8 → E5; passo 9 → E6. O passo C4 (definir função) é
acrescentado a partir do fluxo da arquitectura (F-02); a auditoria (T1) e a visão
de atenção (T2) são transversais.

---

## 3. Limites funcionais preliminares do MVP

Estado: **Proposta / A validar**. Lista **preliminar**; o congelamento formal do
escopo é feito em F0-B14 (pipeline F0-P05).

### 3.1. Incluído no MVP

Uma empresa; vários produtos; ficha administrativa do produto; documentos
Markdown com versões; decisões; pendências mínimas; funções organizacionais;
execuções assistidas (manuais); pacote de contexto; registo e validação de
resultados; visão de atenção; auditoria básica; exportação (fonte: visão §15.1).

### 3.2. Opcional no MVP (condicional, decisão em F0-B14)

* Utilização de IA **local** de forma manual e limitada — a visão classifica a integração local como "opcional e limitada" no MVP (F-05); a ligação **automática** fica excluída (ver 3.3).
* Importação inicial de documentação Markdown existente (referida como opcional em fase inicial no roadmap §7); reduz esforço de onboarding.
* Referência simples (por URL) a trabalho externo — a baseline coloca a referência simples possivelmente na Versão 1; fica como candidato opcional a confirmar.

### 3.3. Excluído do MVP mas previsto para fase posterior (adiado)

Múltiplos utilizadores e convites; permissões avançadas; ligação **automática**
a IA local ou APIs de IA; sincronização Git; pesquisa (textual e semântica);
notificações; modelos/templates; revisões periódicas; histórico consolidado e
comparação de versões; classificação de documentos; API controlada; indicadores
de portefólio (fonte: roadmap §4.3; visão §15.2 e §15.4).

### 3.4. Excluído do núcleo do produto (não previsto)

Gestão completa de projectos (sprints, backlogs, Gantt, timesheets); ERP,
contabilidade, facturação, folha salarial; CRM completo; gestão de
contratos/clientes/fornecedores; agentes autónomos e multiagente; marketplace;
alojamento de modelos de IA; construtor visual de workflows; chat genérico
incorporado; avatares/personalidades de IA; app móvel nativa; automações sem
aprovação (fonte: visão §9; roadmap §8).

---

## 4. Hipóteses assumidas

* H-01 — Assumiu-se que C1–C4 são passos de configuração não repetidos a cada ciclo, e que E1–E6 formam o ciclo recorrente; a baseline apresenta os nove passos de forma linear (F-01).
* H-02 — Assumiu-se que a definição de função (C4) é, por defeito, um passo de configuração reutilizável e não uma acção por execução; **confirmado** (DEC-F0-FINAL-06, ver P-02).
* H-03 — Assumiu-se que, no MVP individual, operador e revisor podem ser a mesma pessoa (coerente com artefacto 01, H-03).
* H-04 — Assumiu-se que "utilizar IA local de forma manual" (exportar contexto e importar resultado) é compatível com o MVP, distinguindo-o da ligação automática, que fica adiada (arquitectura §8.2).

---

## 5. Pontos a validar por humano

* P-01 — Confirmar o fluxo ponta a ponta proposto (secção 2), incluindo a separação entre passos de configuração (C1–C4) e ciclo recorrente (E1–E6).
* P-02 — ~~Confirmar a colocação do passo "definir função" (C4)~~ — **Resolvido**: configuração única reutilizável, fora do ciclo recorrente (DEC-F0-FINAL-06).
* P-03 — Confirmar que, no passo E6, a aplicação da alteração aprovada é sempre manual/controlada e **não** cria automaticamente uma nova versão documental (questão em aberto na arquitectura §17, ponto 15).
* P-04 — Confirmar se a utilização de IA local manual e limitada é **incluída** ou **opcional** no MVP (secção 3.1 vs 3.2), dependente também de F0-B11.
* P-05 — Confirmar se a visão de atenção (T2) é o ponto de entrada explícito do fluxo do MVP (liga a P-05 do artefacto 01).
* P-06 — Confirmar a lista preliminar de limites (secção 3) antes do congelamento em F0-B14, em especial a classificação da referência externa por URL (opcional vs adiado).

---

## 6. Modelo funcional (F0-B04)

Secção acrescentada em F0-P03-PR01. Linguagem de negócio, sem esquema físico
(campos, tipos, chaves e migrações ficam fora do âmbito da Fase 0). Os estados e
transições de cada entidade são tratados em F0-B05 (prompt seguinte) e não são
antecipados aqui.

### 6.1. Factos

Referências: `docs/gestao/01_baseline/03_arquitetura.md` §6.2 e §6.3 (indicativas)
e `docs/gestao/01_baseline/04_roadmap_faseado.md` §3.2.

* MF-01 — O roadmap (§3.2) lista as entidades a confirmar: empresa, produto, documento, decisão, pendência, função, execução, resultado, revisão e auditoria.
* MF-02 — A arquitectura (§6.2, indicativa) modela o **resultado** como documento referenciado pela execução e os campos de **revisão** (revisor, data, decisão) na própria execução, e não como entidades autónomas.
* MF-03 — A arquitectura (§6.2) trata as **versões de documento** como instantâneos imutáveis e a associação **execução–versões de documento** como o mecanismo que preserva as versões exactas usadas (contexto).
* MF-04 — A arquitectura (§15.7) recomenda calcular a visão de atenção por consulta simples, sem persistir indicadores.
* MF-05 — As relações de alto nível da arquitectura (§6.3): tudo pertence a uma empresa; produto relaciona-se com documentos, decisões, pendências e execuções; documento tem versões; execução liga produto, função e versões de documentos.

### 6.2. Glossário funcional (decisão proposta)

Estado: **Proposta / A validar**. Cada entidade é validada contra o fluxo
aprovado (secção 2); a coluna "usada em" refere os passos do fluxo.

* **Empresa** — organização ou workspace que detém todo o contexto e constitui a unidade de isolamento; toda a informação pertence a uma empresa. Usada em: C1 e como contexto de tudo.
* **Produto** — item do portefólio: iniciativa ou produto digital contínuo, com estado administrativo próprio, agregando o contexto que lhe diz respeito. Usada em: C2, E1–E6, T2.
* **Documento** — peça de conhecimento e contexto em Markdown, associada à empresa e opcionalmente a um produto, que evolui por versões. Usada em: C3, E2, E6.
* **Versão de documento** — instantâneo imutável do conteúdo de um documento num dado momento; permite recuperar e referenciar o conteúdo exacto. Sub-conceito de Documento. Usada em: C3, E2 (contexto), E6.
* **Decisão** — registo de uma escolha relevante, com contexto e responsável, ligada à empresa e opcionalmente a um produto. Usada em: E1, E6.
* **Pendência** — assunto administrativo a acompanhar, com responsável, prazo e estado; deliberadamente mínima, não constitui gestão de projectos. **Tipos mínimos confirmados (DEC-F0-FINAL-07, resolve INC-02):** `action` (acção administrativa concreta), `review` (revisão de produto/documento/informação), `validation` (validação de resultado, decisão ou alteração), `obligation` (obrigação com prazo ou responsabilidade), `decision_follow_up` (seguimento decorrente de uma decisão). Não incluem sprint, história, bug ou tarefa técnica; trabalho técnico detalhado permanece em ferramentas externas; novos tipos exigem necessidade funcional demonstrada. Usada em: E1, E6, T2.
* **Função organizacional** — perfil de actor (humano, IA ou híbrido) que descreve propósito, responsabilidades, limites e necessidade de aprovação, seleccionável numa execução. Não é papel de acesso (ver 6.3). Usada em: C4, E2.
* **Execução assistida** — pedido de trabalho apoiado por IA, associado a um produto e a uma função, que agrega o contexto usado (versões de documentos), o resultado e o estado de validação. Usada em: E2–E6.
* **Evento de auditoria** — registo append-only de uma operação relevante (actor, entidade, acção, data, correlação). Usada em: T1 (transversal).

Conceitos funcionais do fluxo realizados através das entidades acima (ver 6.5):
**resultado**, **revisão/validação**, **pacote de contexto** e **visão de
atenção**.

### 6.3. Funções organizacionais (decisão proposta)

Estado: **Proposta / A validar**. A função organizacional é um conceito de
**conteúdo/configuração**, não de controlo de acesso.

* **Tipos:** humana, IA ou híbrida.
* **Propósito:** descrever para que serve a função numa execução (por exemplo, redigir documentação, propor uma decisão, rever conteúdo).
* **Responsabilidades:** o que a função faz no âmbito de uma execução.
* **Limites:** que contexto está autorizada a consultar e o que não pode fazer.
* **Necessidade de aprovação:** se o resultado produzido sob esta função exige validação humana antes de ser aplicado.

**Distinção obrigatória face aos papéis de utilizador (F0-B10):** a função
organizacional responde a "que perfil executa o trabalho" e é seleccionada numa
execução; o papel de utilizador (por exemplo Owner, Editor, Reviewer, Viewer)
responde a "que permissões de acesso tem a pessoa autenticada" e é tratado em
F0-B10. São conceitos independentes e não devem ser fundidos.

### 6.4. Relações de alto nível (decisão proposta)

Estado: **Proposta / A validar**. Coerentes com a arquitectura §6.3; não
acrescentam relações novas.

* Empresa contém: produtos, documentos, decisões, pendências, funções, execuções e eventos de auditoria. (Utilizadores e memberships ficam para F0-B10.)
* Produto relaciona-se com: documentos, decisões, pendências e execuções.
* Documento contém: versões de documento.
* Execução assistida liga: um produto, uma função e as versões de documentos que compõem o contexto; agrega o resultado e a validação.
* Evento de auditoria referencia: um actor e a entidade afectada.

### 6.5. Entidades dispensáveis como entidade autónoma no MVP (decisão proposta)

Estado: **Proposta / A validar**. Os conceitos permanecem no fluxo, mas
propõe-se que **não** sejam modelados como entidades autónomas no MVP,
seguindo a arquitectura §6.2 (MF-02, MF-03).

* **Resultado** — proposto como conceito associado à Execução (conteúdo, origem e estado de validação), materializável como documento de resultado; não entidade autónoma. Justificação: evita duplicar informação já detida pela execução e pelo documento (MF-02).
* **Revisão/validação** — proposta como acto e estado no ciclo de vida da Execução (aprovar, rejeitar, pedir correcção), não entidade autónoma. Nota: o sentido "revisão periódica de produto" é distinto e pertence à Versão 1 (visão §15.2), pelo que não entra no MVP.
* **Pacote de contexto** — proposto como associação entre Execução e versões de documento (mais objectivo e instruções), não entidade de negócio autónoma; é o mecanismo que garante a preservação das versões exactas (MF-03).
* **Visão de atenção** — proposta como vista derivada e calculada, não persistida e não entidade (MF-04).

Resultado líquido proposto: **oito entidades núcleo** — Empresa, Produto,
Documento (com Versão de documento), Decisão, Pendência, Função organizacional,
Execução assistida e Evento de auditoria — todas com uso no fluxo aprovado.

### 6.6. Hipóteses assumidas

* MH-01 — Assumiu-se a versão de documento como sub-conceito essencial, por o versionamento documental ser núcleo do MVP (visão §15.1).
* MH-02 — Assumiu-se resultado e revisão como conceitos folded na execução, seguindo o modelo indicativo da arquitectura §6.2 (MF-02); a alternativa (entidades autónomas) fica em aberto (P-08).
* MH-03 — Assumiu-se documento com produto opcional (documento ao nível da empresa é permitido), coerente com arquitectura §6.2 (`product_id` opcional); confirmação em P-09.

### 6.7. Pontos a validar por humano

* P-07 — Confirmar o conjunto de oito entidades núcleo (6.5) como o modelo mínimo do MVP.
* P-08 — Confirmar que resultado, revisão e pacote de contexto ficam como conceitos associados à execução, e não como entidades autónomas.
* P-09 — Confirmar que um documento pode existir associado apenas à empresa (sem produto) no MVP.
* P-10 — Confirmar a distinção operacional entre função organizacional (conteúdo) e papel de utilizador (acesso), para consistência com F0-B10.
* P-11 — Confirmar que a "revisão periódica de produto" fica fora do MVP (Versão 1), mantendo no MVP apenas o campo de última revisão usado pela visão de atenção.

### 6.8. Critérios de verificação do modelo funcional

* Todas as entidades usadas no fluxo estão definidas no glossário — 6.2 cobre C1–C4, E1–E6 e T1. ✔
* Nenhuma entidade sem uso no fluxo permanece no modelo — resultado, revisão, pacote de contexto e atenção reclassificados (6.5); núcleo reduzido a oito entidades usadas. ✔
* As relações são coerentes com a arquitectura §6.3 ou o desvio está justificado — 6.4 sem relações novas; folds justificados em 6.5. ✔
* As funções organizacionais estão definidas e distinguidas dos papéis de utilizador — 6.3. ✔
* O glossário está em linguagem de negócio, sem esquema físico — 6.2 a 6.5, sem campos nem tipos. ✔

---

## 7. Critérios de verificação deste artefacto

* Cada passo do fluxo tem actor, entrada e saída definidos — secção 2 (C1–C4, E1–E6). ✔
* Nenhuma etapa depende de funcionalidade excluída do MVP — E3 usa IA manual (não ligação automática); auditoria e atenção são do escopo MVP. ✔
* As ambiguidades estão resolvidas ou registadas — resoluções em 2.x e notas; pendências em P-01 a P-06. ✔
* O fluxo suporta integralmente o caso de uso principal — secção 2.2 cobre preparação, execução, registo, validação e actualização (F-04). ✔
* A lista preliminar de limites distingue incluído, excluído, opcional e adiado — secção 3 (3.1 a 3.4). ✔
