# Estados e transições das entidades do MVP — VentureOps AI

* Fase: F0 — Preparação e alinhamento
* Item tratado: F0-B05 (F0-05)
* Decisão bloqueadora: DB-05
* Estado do artefacto: Confirmado com reservas (DEC-20260712-04); tipos de pendência fechados (DEC-F0-FINAL-07)
* Prompt de origem: F0-P03-PR02; tipos de pendência fechados no fecho formal da Fase 0 (2026-07-12)

Âmbito: estados **mínimos** e transições válidas das entidades com ciclo de
vida, ao nível funcional. Não são máquinas de estado técnicas nem enumerações de
código. Base: o fluxo aprovado e o modelo funcional em
`docs/gestao/02_fase_0_preparacao/artefactos/02_fluxo_e_modelo_funcional.md`
(secções 2 e 6). Estados apenas para funcionalidades do MVP; sinais da visão de
atenção e regras associadas pertencem a F0-B08 e não são estados aqui.

Papéis funcionais usados (mapeamento definitivo para papéis de utilizador em
F0-B10): **Operador** (cria e mantém entidades; corresponde a Editor ou Owner) e
**Revisor/Aprovador** (valida resultados; corresponde a Reviewer ou Owner). No
MVP individual podem ser a mesma pessoa.

---

## 1. Factos

* ST-01 — O fluxo aprovado tem passos de configuração (C1–C4) e um ciclo recorrente (E1–E6), mais auditoria (T1) e visão de atenção (T2) transversais (artefacto 02, §2).
* ST-02 — O modelo funcional propõe oito entidades núcleo e reclassifica resultado, revisão, pacote de contexto e visão de atenção como conceitos associados (artefacto 02, §6.5).
* ST-03 — A arquitectura (§6.2, indicativa) prevê campos de estado (`status`) em produto, documento, decisão, pendência, função e execução, e campos de revisão (revisor, data, decisão) na própria execução.
* ST-04 — A visão de atenção é calculada, não persistida (artefacto 02, §6.5, MF-04); "documento desactualizado" e "decisão pendente" são sinais definidos em F0-B08, não estados desta secção.

---

## 2. Estados e transições por entidade (decisão proposta)

Estado geral: **Proposta / A validar**. Cada transição indica quem a executa e o
passo do fluxo que a origina.

### 2.1. Produto

Estados mínimos: **Activo**, **Arquivado**.

| De | Para | Quem | Origem no fluxo |
|---|---|---|---|
| (criação) | Activo | Operador | C2 |
| Activo | Arquivado | Operador | Gestão de portefólio (arquivo) |
| Arquivado | Activo | Operador | Reactivação |

Nota: a "fase" do produto (por exemplo ideação, desenvolvimento, operação) é um
atributo de classificação distinto do estado administrativo; os seus valores não
são exigidos pelo fluxo e ficam como ponto a validar (P-02). A data de última
revisão usada pela visão de atenção é um campo, não um estado.

### 2.2. Documento

Estados mínimos: **Activo**, **Arquivado**.

| De | Para | Quem | Origem no fluxo |
|---|---|---|---|
| (criação) | Activo | Operador | C3 |
| Activo | Arquivado | Operador | Gestão documental |
| Arquivado | Activo | Operador | Reactivação |

Nota 1: a **versão de documento** é imutável e não tem ciclo de vida próprio;
cada gravação relevante cria uma nova versão e actualiza a versão actual do
documento (E6). Nota 2: a marcação de um documento como "desactualizado" é um
sinal de atenção a definir em F0-B08 (P-03), não um estado de ciclo de vida.

### 2.3. Decisão

Estados mínimos: **Activa**, **Substituída**.

| De | Para | Quem | Origem no fluxo |
|---|---|---|---|
| (registo) | Activa | Operador | E1 |
| Activa | Substituída | Operador | Registo de nova decisão que a substitui |

Nota: o sinal "decisão pendente" da visão de atenção não corresponde
necessariamente a um estado de decisão; a sua interpretação (decisão em rascunho
vs pendência de tipo decisão) é decidida em F0-B08 (P-04). Não se acrescenta um
estado "Proposta" por não ser exigido pelo fluxo.

### 2.4. Pendência

Estados mínimos: **Aberta**, **Concluída**, **Cancelada**.

| De | Para | Quem | Origem no fluxo |
|---|---|---|---|
| (registo) | Aberta | Operador | E1 |
| Aberta | Concluída | Operador | E6 (assunto resolvido) |
| Aberta | Cancelada | Operador | Pendência deixa de ser necessária |

Nota: "pendência vencida" é derivada do prazo com a pendência ainda **Aberta**
(sinal de atenção, F0-B08), não um estado. Um estado intermédio "Em curso" não é
exigido pelo fluxo e fica como opcional a validar (P-05).

**Tipo de pendência (DEC-F0-FINAL-07, resolve INC-02):** o tipo é um atributo
independente do estado, com a enumeração mínima `action`, `review`, `validation`,
`obligation`, `decision_follow_up` (ver artefacto 02, §6.2, glossário de
Pendência). O tipo `decision_follow_up`/`validation` é o que suporta a regra
R-AT-02 (decisão pendente) do artefacto 06.

### 2.5. Função organizacional

Estados mínimos: **Activa**, **Inactiva**.

| De | Para | Quem | Origem no fluxo |
|---|---|---|---|
| (criação) | Activa | Operador (Owner) | C4 |
| Activa | Inactiva | Operador (Owner) | Deixa de estar disponível para novas execuções |
| Inactiva | Activa | Operador (Owner) | Reactivação |

Nota: só funções **Activas** podem ser seleccionadas numa nova execução (E2);
execuções passadas mantêm a referência à função usada.

### 2.6. Execução assistida

Estados mínimos: **Preparada**, **Resultado por validar**, **Aprovada**,
**Rejeitada**, **Concluída**.

| De | Para | Quem | Origem no fluxo |
|---|---|---|---|
| (criação e geração de contexto) | Preparada | Operador | E2 |
| Preparada | Resultado por validar | Operador | E4 (registo do resultado; E3 é uso externo manual) |
| Resultado por validar | Aprovada | Revisor/Aprovador | E5 (aprovar) |
| Resultado por validar | Rejeitada | Revisor/Aprovador | E5 (rejeitar) |
| Resultado por validar | Preparada | Revisor/Aprovador | E5 (pedir correcção; nova tentativa) |
| Aprovada | Concluída | Operador | E6 (aplicação controlada da alteração) |

Nota 1: **Rejeitada** é terminal — a execução fecha sem actualização do estado
administrativo; uma nova necessidade origina nova execução. Nota 2: o passo E3
(uso da IA) é manual e externo; a execução permanece **Preparada** até ao registo
do resultado. Nota 3: reexecuções seguem a regra do guia global (mesmo resultado,
sem ficheiros vN).

### 2.7. Revisão / validação do resultado

Conforme o modelo funcional (artefacto 02, §6.5), a revisão é o **acto e o estado
de validação do resultado dentro da execução**, e não uma entidade autónoma no
MVP. Os seus estados são, portanto, os do resultado de uma execução:

Estados de validação do resultado: **Por validar**, **Aprovado**, **Rejeitado**;
com o desfecho adicional **Correcção pedida** (que devolve a execução a
Preparada).

| De | Para | Quem | Origem no fluxo |
|---|---|---|---|
| (registo do resultado) | Por validar | Operador | E4 |
| Por validar | Aprovado | Revisor/Aprovador | E5 |
| Por validar | Rejeitado | Revisor/Aprovador | E5 |
| Por validar | Correcção pedida | Revisor/Aprovador | E5 |

Estes estados de validação são a face de "revisão" dos estados da execução
(2.6): "Aprovado" corresponde a execução **Aprovada**, "Rejeitado" a **Rejeitada**
e "Correcção pedida" ao regresso a **Preparada**. Se, na revisão humana, se
preferir tratar a revisão como entidade autónoma, ver P-06.

### 2.8. Empresa (nota, fora do conjunto pedido)

A empresa não consta da lista de entidades deste prompt. Para o MVP, o seu ciclo
de vida é trivial (**Activa**, com eventual **Arquivada**) e a sua definição fica
associada ao modelo de utilizadores e empresas (F0-B10). Registada aqui apenas
para completude; não é aprofundada.

---

## 3. Cobertura do fluxo (verificação estado a estado)

| Passo | Entidade e estado resultante |
|---|---|
| C1 | Empresa Activa (nota 2.8) |
| C2 | Produto Activo (2.1) |
| C3 | Documento Activo, versão 1 (2.2) |
| C4 | Função Activa (2.5) |
| E1 | Decisão Activa (2.3) ou Pendência Aberta (2.4) |
| E2 | Execução Preparada (2.6) |
| E3 | Execução mantém-se Preparada (uso externo manual) |
| E4 | Execução Resultado por validar; resultado Por validar (2.6, 2.7) |
| E5 | Execução Aprovada / Rejeitada; resultado Aprovado / Rejeitado / Correcção pedida (2.6, 2.7) |
| E6 | Execução Concluída; nova versão de documento e/ou Pendência Concluída (2.2, 2.4, 2.6) |
| T1 | Auditoria (transversal; sem ciclo de vida) |
| T2 | Visão de atenção (derivada dos estados acima; regras em F0-B08) |

Nenhum passo do fluxo exige um estado não definido; nenhum estado definido fica
sem uso no fluxo.

---

## 4. Hipóteses assumidas

* SH-01 — Assumiu-se a reactivação (Arquivado→Activo, Inactiva→Activa) como transição de baixo custo e útil; se indesejada no MVP, remover (P-07).
* SH-02 — Assumiu-se que "pedir correcção" na revisão devolve a execução a Preparada para nova tentativa, em vez de criar um estado próprio.
* SH-03 — Assumiu-se que a conclusão de uma pendência (Aberta→Concluída) pode ocorrer em E6 ou de forma independente, quando o assunto é resolvido.
* SH-04 — Assumiu-se, seguindo o modelo funcional, que a revisão não é entidade autónoma; os seus estados vivem no resultado da execução.

## 5. Pontos a validar por humano

* P-01 — Confirmar o conjunto mínimo de estados por entidade (secção 2).
* P-02 — Confirmar se a "fase" do produto entra no MVP e, em caso afirmativo, com que valores (atributo, não estado).
* P-03 — Confirmar como se representa "documento desactualizado" (marcador vs estado); interpretação final em F0-B08.
* P-04 — Confirmar a interpretação de "decisão pendente" na visão de atenção; interpretação final em F0-B08.
* P-05 — Confirmar se a pendência precisa de um estado intermédio "Em curso" no MVP.
* P-06 — Confirmar que a revisão permanece folded na execução (2.7) e não como entidade autónoma.
* P-07 — Confirmar se as reactivações (produto e função) são permitidas no MVP.

## 6. Critérios de verificação deste artefacto

* Cada entidade tem estados enumerados e transições explícitas — secção 2 (2.1 a 2.7). ✔
* Cada transição indica quem a pode executar — coluna "Quem" em todas as tabelas. ✔
* Nenhum passo do fluxo exige um estado inexistente — secção 3 (cobertura completa). ✔
* Não existem estados sem uso no fluxo do piloto — secção 3 confirma uso de todos os estados; estados especulativos evitados (notas em 2.1, 2.3, 2.4). ✔
