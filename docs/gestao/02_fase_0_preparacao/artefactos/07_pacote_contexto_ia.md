# Pacote de contexto para execução assistida por IA — VentureOps AI

* Fase: F0 — Preparação e alinhamento
* Item tratado: F0-B09 (F0-09)
* Decisão bloqueadora: DB-09
* Estado do artefacto: Confirmado com reservas (DEC-20260712-04); regra de bloqueio por `export_policy` acrescentada (DEC-F0-FINAL-08)
* Prompt de origem: F0-P04-PR02; regra de exportação acrescentada no fecho formal da Fase 0 (2026-07-12)

Âmbito: estrutura do pacote de contexto para uso **manual** (IA externa ou
local), formato de exportação e de importação do resultado, e teste manual.
Ao nível funcional: não se desenham APIs, conectores nem integração automática.
Base: passos de execução assistida (artefacto 02, §2.2), fronteira BD/Markdown
(artefacto 05) e arquitectura §8.3 e §11.10.

---

## 1. Factos

* PC-01 — No MVP não há integração directa com IA; o utilizador copia ou exporta manualmente o contexto e importa manualmente o resultado (arquitectura §8.3; artefacto 02, §2.2 E3).
* PC-02 — Mitigação de prompt injection (arquitectura §11.10): os documentos devem ser tratados como dados e não como instruções de sistema; as instruções da função devem ser distinguidas do conteúdo documental; o contexto exportado deve identificar as fontes; pedidos de acção presentes em documentos não devem gerar acções automáticas.
* PC-03 — O pacote deve preservar as **versões exactas** dos documentos usados (artefacto 05, §2; capacidade VAL-008 da matriz global).
* PC-04 — O resultado de IA começa como não validado e exige aprovação humana antes de ser aplicado (artefacto 02, §2.2 E4–E6).
* PC-05 — O pacote de contexto é uma associação execução↔versões mais objectivo/instruções; o ficheiro exportado é gerado a partir do conteúdo das versões, não é fonte de verdade (artefacto 05, §2).

---

## 2. Estrutura do pacote (decisão proposta)

Estado: **Proposta / A validar**. Sete secções, correspondendo aos sete
elementos exigidos por F0-09, mais identificação de fontes e separação
instruções/dados.

1. **Objectivo** — o que se pretende obter com a execução.
2. **Função organizacional (instruções da função)** — nome, tipo, propósito, limites, necessidade de aprovação. Bloco de **instruções**.
3. **Instruções específicas do pedido** — o que fazer nesta execução concreta. Bloco de **instruções**.
4. **Produto** — identificação e ficha administrativa mínima (F0-B07).
5. **Restrições** — o que não fazer; regras de segurança; **declaração explícita de que instruções contidas nos documentos são dados e não devem ser executadas**.
6. **Formato esperado do resultado** — como o resultado deve ser devolvido.
7. **Documentos de contexto (dados)** — cada documento com título, identificação, **versão exacta** e fonte; conteúdo delimitado e marcado como DADOS, não instruções.

Regras estruturais (mitigação §11.10, PC-02):

* R-PC-01 — As **instruções válidas** são apenas as das secções 2 e 3; tudo na secção 7 é dados.
* R-PC-02 — Cada documento da secção 7 identifica a **fonte** (produto e versão exacta) e é delimitado por marcadores claros de início/fim de conteúdo.
* R-PC-03 — A secção 5 inclui a declaração de que instruções embebidas em documentos não devem ser executadas.
* R-PC-04 — O pacote não contém segredos, tokens nem dados sensíveis desnecessários; a selecção de documentos é do operador.
* R-PC-05 — **(DEC-F0-FINAL-08)** Um documento com `export_policy = denied` **não pode** ser incluído na secção 7 nem em nenhuma exportação de pacote de contexto; `export_policy = confirm` exige confirmação explícita do operador antes da inclusão; `export_policy = allowed` pode ser incluído directamente. Controlo aplicado pelo backend (ver artefacto 05, §2; artefacto 10, §10).

## 3. Formatos (decisão proposta)

Estado: **Proposta / A validar**. Formatos neutros, não optimizados para um
fornecedor específico (texto/Markdown simples).

* **Exportação — ambos, com um por defeito:** por defeito, um **documento único** em texto/Markdown (fácil de copiar para um chat externo, arquitectura §8.3); em alternativa, **ficheiros separados** (um por documento de contexto) quando os documentos são grandes, preservando cada versão como ficheiro. Justificação: o texto único cobre o caso manual mais comum; os ficheiros separados servem conteúdos extensos e a portabilidade das versões.
* **Importação do resultado — texto/Markdown por defeito, ficheiro em alternativa:** o resultado é colado como texto/Markdown ou anexado como ficheiro; é registado como **documento de resultado** (Markdown, artefacto 05, §2), com a origem (ferramenta/modelo e data) guardada como metadado. Sem integração automática.

## 4. Pacote de exemplo e teste manual

Foi produzido um pacote de exemplo com conteúdo **fictício e não sensível** e
realizado um teste manual pela IA executora (auto-teste local), incluindo uma
linha de injecção plantada num documento para verificar a mitigação §11.10.

* Resultado do teste: estrutura suficiente; sete elementos presentes; versões e
  fontes identificadas; a instrução de injecção foi tratada como dados e **não**
  foi executada; o resultado ficou no âmbito e apto a validação humana.
* Limitação: teste de um único modelo; recomenda-se confirmação com um modelo
  externo distinto (P-06).
* **Evidência:** `pipelines/04_dados_contexto_seguranca/resultados_execucao/evidencias/prompt_02_teste_pacote.md`.

## 5. Hipóteses assumidas

* AH-01 — Assumiu-se o texto único como formato de exportação por defeito, por ser o mais directo para uso manual em chat externo (arquitectura §8.3).
* AH-02 — Assumiu-se o resultado importado como documento de resultado em Markdown, coerente com a fronteira BD/Markdown (artefacto 05).
* AH-03 — Assumiu-se que a delimitação textual de secções e documentos (marcadores de início/fim) é suficiente para a separação instruções/dados no uso manual; a robustez pode variar entre modelos (P-06).

## 6. Pontos a validar por humano

* P-01 — Confirmar a estrutura de sete secções do pacote (secção 2).
* P-02 — Confirmar o formato de exportação (texto único por defeito, ficheiros separados em alternativa).
* P-03 — Confirmar o formato de importação do resultado (texto/Markdown por defeito, ficheiro em alternativa) e os metadados de origem a registar.
* P-04 — Confirmar as regras de separação instruções/dados e a declaração anti-injecção (R-PC-01 a R-PC-03).
* P-05 — Confirmar que a selecção de documentos e a ausência de dados sensíveis no pacote são responsabilidade do operador, articulando com F0-B12 (política de envio a IA externa).
* P-06 — Confirmar o teste com um **modelo externo distinto**, para além do auto-teste registado.

## 7. Referência à evidência do teste

`docs/gestao/02_fase_0_preparacao/pipelines/04_dados_contexto_seguranca/resultados_execucao/evidencias/prompt_02_teste_pacote.md`

## 8. Critérios de verificação deste artefacto

* A estrutura cobre os sete elementos exigidos (F0-09) — secção 2 (1 a 7). ✔
* O pacote de exemplo existe e não contém dados sensíveis — evidência (conteúdo fictício marcado). ✔
* O teste manual foi executado com evidência registada — secção 4 e evidência referenciada; limitação (auto-teste) declarada. ✔
* As fontes estão identificadas e as instruções separadas do conteúdo — secção 2 (R-PC-01 a R-PC-03) e evidência (injecção não obedecida). ✔
