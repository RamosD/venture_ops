# Regras da visão de atenção — VentureOps AI

* Fase: F0 — Preparação e alinhamento
* Item tratado: F0-B08 (F0-08)
* Decisão bloqueadora: DB-08
* Estado do artefacto: Confirmado com reservas (DEC-20260712-04); R-AT-02 e R-AT-05 fechadas (DEC-F0-FINAL-07/08)
* Prompt de origem: F0-P05-PR03; R-AT-02/R-AT-05 fechadas no fecho formal da Fase 0 (2026-07-12)

Âmbito: regras **determinísticas e explicáveis** para a visão de atenção do MVP,
uma por sinal, ao nível funcional. Não se definem queries, algoritmos nem
detalhes de implementação. Base: estados (artefacto 03), ficha do produto
(artefacto 04), roadmap §3.2 e arquitectura §15.7.

---

## 1. Factos

* AT-01 — O roadmap (§3.2) define a visão de atenção com cinco sinais: produto sem revisão, decisão pendente, pendência vencida, resultado a aguardar validação e documento marcado como desactualizado.
* AT-02 — A arquitectura recomenda calcular a atenção por consulta simples, sem persistir indicadores (arquitectura §15.7; confirmado no artefacto 02, §6.5).
* AT-03 — Dados disponíveis: estados de produto (Activo/Arquivado), decisão (Activa/Substituída), pendência (Aberta/Concluída/Cancelada) com prazo, execução (inclui "Resultado por validar") e documento (Activo/Arquivado) (artefacto 03); campos da ficha do produto, incluindo Data da última revisão (artefacto 04).
* AT-04 — O artefacto 03 remeteu para F0-B08 a definição de dois elementos: a interpretação de "decisão pendente" (§2.3, nota) e o marcador "documento desactualizado" (§2.2, nota 2). Este artefacto fecha essa definição.

---

## 2. Regras (decisão proposta)

Estado geral: **Proposta / A validar**. Cada regra é determinística (comparações
de data, igualdade de estado ou marcador booleano), com motivo apresentável ao
utilizador. Aplicam-se apenas a entidades não arquivadas.

### R-AT-01 — Produto sem revisão recente

* Condição objectiva: produto **Activo** cuja **Data da última revisão** é anterior a (hoje − prazo de revisão), ou que não tem data de última revisão.
* Motivo apresentável: "Este produto não é revisto há mais de [prazo] dias."
* Parâmetros: prazo de revisão — valor inicial **30 dias**.
* Dados usados: estado de produto (F0-B05) e campo Data da última revisão (F0-B07).

### R-AT-02 — Decisão pendente

* Condição objectiva: existe uma **pendência Aberta cujo tipo é `decision_follow_up`** associada ao produto (tipo confirmado em DEC-F0-FINAL-07).
* Motivo apresentável: "Há uma decisão por tomar, registar ou dar seguimento neste produto."
* Parâmetros: nenhum (binário); depende do tipo de pendência.
* Dados usados: estado de pendência (Aberta) e tipo de pendência `decision_follow_up` (artefacto 02 §6.2; artefacto 03 §2.4).
* **Resolvido (DEC-F0-FINAL-07, fecha INC-02):** a entidade Decisão mantém apenas os estados Activa/Substituída (artefacto 03), sem estado "pendente"; a interpretação via pendência de tipo `decision_follow_up` é a leitura formal adoptada, sem alterar os estados da Decisão.

### R-AT-03 — Pendência vencida

* Condição objectiva: pendência **Aberta** cujo **prazo** é anterior a hoje.
* Motivo apresentável: "Esta pendência passou o prazo."
* Parâmetros: nenhum por defeito (usa o prazo da própria pendência). Opcional, não incluído por defeito: sinalizar "a vencer" nos próximos [X] dias (P-02).
* Dados usados: estado de pendência (Aberta) e prazo (F0-B05).

### R-AT-04 — Resultado por validar

* Condição objectiva: existe uma **execução no estado "Resultado por validar"** associada ao produto.
* Motivo apresentável: "Há um resultado de IA à espera de validação."
* Parâmetros: nenhum por defeito. Opcional, não incluído: destacar se está por validar há mais de [Y] dias (P-03).
* Dados usados: estado de execução (F0-B05).

### R-AT-05 — Documento sinalizado como desactualizado

* Condição objectiva: documento **Activo** com o campo **`is_outdated = true`**.
* Motivo apresentável: "Este documento foi marcado como desactualizado."
* Parâmetros: nenhum (marcador booleano manual).
* Dados usados: estado de documento (Activo) e o campo `is_outdated`.
* **Resolvido (DEC-F0-FINAL-08, fecha INC-03):** `is_outdated` é um campo estruturado do documento — fonte oficial **base de dados**; valor inicial `false`; actualizado manualmente no MVP (sem detecção automática); alimenta esta regra; **sem valor concorrente no Markdown** (coerente com a fronteira BD/Markdown, artefacto 05).

### Marcador complementar — `export_policy` (DEC-F0-FINAL-08)

Não alimenta uma regra de atenção, mas é registado aqui por decorrer da mesma
decisão de fecho dos marcadores documentais: campo estruturado do documento,
fonte oficial **base de dados**, valores `allowed | confirm | denied`, valor
inicial `confirm`. `denied` impede a inclusão do documento num pacote de
contexto ou exportação para IA externa (aplicado pelo backend; ver artefacto 07
e artefacto 10, §10). Detalhado no artefacto 05, §2 e no artefacto 10, §10.

---

## 3. Parâmetros (valores iniciais propostos)

Estado: **Proposta / A validar**.

| Parâmetro | Regra | Valor inicial | Observação |
|---|---|---|---|
| Prazo de revisão de produto | R-AT-01 | 30 dias | A calibrar no piloto (F0-B13) |
| Janela "a vencer" (opcional) | R-AT-03 | não activa | Sinal adicional só se aprovado (P-02) |
| Antiguidade "por validar" (opcional) | R-AT-04 | não activa | Destaque só se aprovado (P-03) |

Não há outros parâmetros; R-AT-02 e R-AT-05 são binários.

---

## 4. Abordagem de cálculo

Estado: **Proposta / A validar**. As cinco regras são **calculadas por consulta**
sobre os dados existentes (estados, datas e marcador), **sem persistir**
indicadores nem um "nível de atenção" (arquitectura §15.7; artefacto 02, §6.5).
Cada item da visão de atenção apresenta o produto/entidade afectado e o motivo
correspondente à regra que o sinalizou. As regras são independentes; um mesmo
produto pode surgir por mais do que um motivo.

---

## 5. Hipóteses assumidas

* ATH-01 — Assumiu-se o prazo de revisão de 30 dias como valor inicial razoável para o segmento, a calibrar no piloto (P-05).
* ATH-02 — Assumiu-se a interpretação de "decisão pendente" via pendência de tipo "decisão", por ser a leitura determinística possível sem alterar os estados da Decisão (R-AT-02, P-01).
* ATH-03 — Assumiu-se o "documento desactualizado" como marcador manual booleano, e não como estado nem como detecção automática (que seria fase posterior).

## 6. Pontos a validar por humano

* P-01 — ~~Confirmar a interpretação de "decisão pendente"~~ — **Resolvido**: pendência de tipo `decision_follow_up` (DEC-F0-FINAL-07).
* P-02 — Confirmar se se inclui, além de "vencida", o sinal opcional "a vencer em ≤ X dias" (R-AT-03). (Mantém-se aberto; não bloqueante.)
* P-03 — Confirmar se "resultado por validar" deve destacar antiguidade (R-AT-04). (Mantém-se aberto; não bloqueante.)
* P-04 — ~~Confirmar a introdução do marcador "desactualizado"~~ — **Resolvido**: campo `is_outdated` no documento, fonte BD (DEC-F0-FINAL-08).
* P-05 — Confirmar/calibrar o prazo de revisão (30 dias) com base no piloto (F0-B13). (Mantém-se aberto; a calibrar durante o piloto.)

## 7. Critérios de verificação deste artefacto

* Cada regra tem condição objectiva e motivo apresentável — secção 2 (R-AT-01 a R-AT-05). ✔
* Cada regra depende apenas de dados de F0-B05 e F0-B07 — secção 2 (campo "Dados usados"); os dois elementos que F0-B05 remeteu para F0-B08 (interpretação de decisão pendente e marcador desactualizado) estão **fechados** (DEC-F0-FINAL-07/08). ✔
* Os parâmetros têm valores iniciais propostos — secção 3. ✔
* Não existem regras com heurísticas não explicáveis — todas são comparações de data, igualdade de estado ou marcador booleano; sem pontuações. ✔
