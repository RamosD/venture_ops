# Ficha administrativa mínima do produto — VentureOps AI

* Fase: F0 — Preparação e alinhamento
* Item tratado: F0-B07 (F0-07)
* Decisão bloqueadora: DB-07
* Estado do artefacto: Campos confirmados (DEC-F0-FINAL-04); teste real concluído
* Estado do teste: **Concluído** — testado com o produto real VentureOps AI em 2026-07-12 (ver secção 7.1); exemplo ilustrativo original preservado (secção 7.2)
* Prompt de origem: F0-P03-PR03 (teste real concluído em reexecução — ver `prompt_03_resultado.md`)

Âmbito: campos **mínimos** da ficha administrativa do produto, ao nível
funcional. Não se definem tipos de dados, validações técnicas nem layout de
interface. Base: caso de uso principal (artefacto 01), entidade produto
(artefacto 02, §6.2) e estados de produto (artefacto 03, §2.1).

---

## 1. Factos

* FA-01 — A visão lista, para a ficha administrativa, propósito, descrição, público-alvo, estado, riscos, decisões, documentos, pendências e notas relevantes (visão §8.1).
* FA-02 — O backlog (F0-B07) exige distinguir campos obrigatórios, opcionais e adiados, e justificar os obrigatórios pelo caso de uso principal ou pelas regras de atenção.
* FA-03 — O caso de uso principal é o ciclo de execução assistida sobre um produto, que exige identificar o produto, aceder ao seu contexto e responsável e manter o estado administrativo actualizado (artefacto 01, D-03).
* FA-04 — Os estados do produto no MVP são **Activo** e **Arquivado** (artefacto 03, §2.1); a data de última revisão é um campo usado pela visão de atenção (regra "produto sem revisão", a fechar em F0-B08).
* FA-05 — No modelo funcional, documentos, decisões e pendências relacionam-se com o produto por associação (artefacto 02, §6.4); não são campos de entrada manual da ficha, mas vistas agregadas.

---

## 2. Campos da ficha (decisão proposta)

Estado geral: **Proposta / A validar**.

### 2.1. Campos obrigatórios

Conjunto mínimo fechado, com justificação. Cada campo é justificado pelo caso de
uso principal (CU) ou por uma regra de atenção prevista (AT).

| Campo | Descrição funcional | Justificação |
|---|---|---|
| Nome do produto | Identificação legível do produto | CU: é necessário identificar e seleccionar o produto no fluxo (C2, E2) |
| Propósito | Uma a três linhas sobre o que o produto é e para que serve | CU: contexto mínimo para compreender o produto e preparar execuções |
| Estado administrativo | Activo ou Arquivado (artefacto 03, §2.1) | CU/AT: distingue produtos activos dos arquivados na visão de portefólio e de atenção |
| Responsável | Pessoa responsável pelo produto (owner) | CU/AT: atribui responsabilidade e alimenta sinais de atenção sobre falta de acompanhamento |
| Data da última revisão | Momento da última revisão administrativa do produto | AT: base da regra "produto sem revisão recente" (F0-B08) |

### 2.2. Campos opcionais

Preenchimento não exigido; podem ficar vazios sem bloquear o fluxo.

* Resumo/descrição alargada — quando útil; conteúdo extenso deve preferencialmente residir num documento associado, não na ficha.
* Público-alvo do produto.
* Fase do produto (por exemplo ideação, desenvolvimento, operação) — atributo de classificação, não estado (artefacto 03, §2.1, nota; P-02 desse artefacto).
* Próxima revisão — data alvo; pode ser derivada da última revisão mais um intervalo, em vez de preenchida.
* Notas relevantes.

### 2.3. Vistas agregadas (não são campos de entrada)

Apresentadas na ficha por associação, não preenchidas manualmente: documentos,
decisões, pendências e execuções relacionadas com o produto (FA-05). O nível de
atenção do produto é **calculado**, não um campo (artefacto 02, §6.5).

### 2.4. Campos adiados (fases posteriores)

Não entram no MVP: classificação de sensibilidade do produto (Versão 1);
múltiplos responsáveis/equipa (Versão 1 multiutilizador); indicadores de saúde do
produto persistidos (Versão 1/analytics); atributos de monetização ou financeiros
(fases posteriores). Fonte: visão §15.2 e §15.4.

---

## 3. Coerência com os estados (F0-B05)

O campo "Estado administrativo" usa exactamente os estados de produto definidos
em `03_estados_e_transicoes.md` (§2.1): **Activo** e **Arquivado**. Nenhum campo
introduz um estado novo. A data de última revisão é um campo temporal, não um
estado, coerente com a nota do artefacto 03.

---

## 4. Avaliação do esforço de preenchimento

Dos cinco campos obrigatórios, três podem ser pré-preenchidos ou derivados:
"Estado administrativo" tem valor por defeito **Activo** na criação; "Responsável"
assume por defeito o operador no MVP individual; "Data da última revisão" é
registada automaticamente na criação e em cada revisão. Restam **dois campos que
exigem escrita** — Nome e Propósito (uma a três linhas). O preenchimento inicial
obrigatório é, portanto, **curto** e coerente com os princípios de simplicidade e
de "o fundador não deve servir a ferramenta" (visão §12, princípios 11 e 15).
Avaliação: **aprovada como curta**, a confirmar no piloto (F0-B13).

---

## 5. Hipóteses assumidas

* AH-01 — Assumiu-se, no MVP individual, o "Responsável" com valor por defeito igual ao operador; em contexto multiutilizador (F0-B10) poderá exigir selecção.
* AH-02 — Assumiu-se "Data da última revisão" como preenchida automaticamente; a definição do que conta como "revisão" liga-se a F0-B08.
* AH-03 — Assumiu-se que descrições extensas residem em documentos associados, mantendo a ficha curta (coerente com a fronteira BD/Markdown, a fechar em F0-B06).

## 6. Pontos a validar por humano

* P-01 — Confirmar o conjunto de cinco campos obrigatórios (2.1).
* P-02 — Confirmar a classificação de "Público-alvo" e "Fase" como opcionais.
* P-03 — Confirmar se "Próxima revisão" é campo preenchido ou valor derivado.
* P-04 — Confirmar que documentos/decisões/pendências são vistas agregadas e não campos de entrada (2.3).
* P-05 — ~~Fornecer um produto real para completar o teste da ficha~~ — **Resolvido**: produto real fornecido pelo operador (DEC-F0-FINAL-04); teste concluído em 7.1.

---

## 7. Evidência do teste (ficha preenchida)

### 7.1. Teste real — VentureOps AI (2026-07-12)

Produto real definido pelo operador (DEC-F0-FINAL-04): **VentureOps AI**, o
próprio produto em preparação.

| Campo | Valor |
|---|---|
| Nome do produto | VentureOps AI |
| Propósito | Centralizar o estado administrativo, o contexto, as decisões, os documentos e as execuções assistidas por IA de uma empresa com múltiplos produtos digitais |
| Estado administrativo | Activo |
| Responsável | Aldino Ramos |
| Data da última revisão | 2026-07-12 |
| (Opcionais deixados vazios) | público-alvo, fase, próxima revisão, notas |

**Avaliação do teste:**

* Suficiência: os cinco campos obrigatórios bastaram para identificar e
  descrever o produto de forma compreensível; nenhum campo obrigatório em falta
  se revelou necessário.
* Esforço de preenchimento: curto — apenas Nome e Propósito exigiram escrita
  (Estado, Responsável e Data seguem os valores por defeito descritos na secção
  4); confirma a avaliação prévia.
* Redundância: nenhum dos cinco campos se revelou redundante.
* Campo adicional indispensável: nenhum identificado; o caso de uso principal
  (execução assistida) é servido pelos cinco campos mais as vistas agregadas
  (2.3).
* Suporte às regras de atenção: "Estado administrativo" e "Data da última
  revisão" alimentam directamente R-AT-01 (produto sem revisão), confirmando a
  coerência com o artefacto 06.

**Resultado:** teste concluído sem lacuna material; **F0-B07 concluído**.
Nenhum campo foi acrescentado, removido ou alterado em resultado deste teste.

### 7.2. Exemplo ilustrativo original (histórico, preservado)

Registo original da execução anterior (2026-07-11), mantido para
rastreabilidade e não usado como evidência de conclusão:

Ficha — EXEMPLO ILUSTRATIVO (dados fictícios, não é um produto real):

* Nome do produto: [EXEMPLO] Agendador de publicações para redes sociais
* Propósito: [EXEMPLO] Permitir a um criador agendar e rever publicações em várias redes a partir de um único painel, com pré-visualização antes de publicar.
* Estado administrativo: Activo
* Responsável: Fundador (Owner) — [EXEMPLO]
* Data da última revisão: [EXEMPLO] preenchida automaticamente na criação/edição
* (Opcionais deixados vazios: público-alvo, fase, próxima revisão, notas)

Observação original: os cinco campos obrigatórios mostraram-se suficientes;
esta observação foi reconfirmada com o produto real em 7.1.

---

## 8. Critérios de verificação deste artefacto

* A lista de campos obrigatórios está fechada e justificada — secção 2.1 (cinco campos, cada um com justificação CU/AT). ✔
* A ficha foi preenchida com um produto real — secção 7.1 (VentureOps AI, 2026-07-12). ✔
* O preenchimento da ficha obrigatória é curto (avaliação registada e reconfirmada) — secção 4 e 7.1. ✔
* Os campos são coerentes com os estados definidos em F0-B05 — secção 3. ✔
