# Evidência — Cobertura dos itens da Fase 0 pelas pipelines (F0-P01-PR02)

| Item baseline | Backlog | Pipeline | Prompt | Artefacto produzido | Dependências |
|---|---|---|---|---|---|
| F0-01 | F0-B01 | F0-P02 | PR01 | `01_segmento_e_caso_uso.md` | Baseline aprovada |
| F0-02 | F0-B02 | F0-P02 | PR01 | `01_segmento_e_caso_uso.md` | F0-B01 (mesmo prompt) |
| F0-03 | F0-B03 | F0-P02 | PR02 | `02_fluxo_e_modelo_funcional.md` (fluxo e limites) | F0-P02-PR01 |
| F0-04 | F0-B04 | F0-P03 | PR01 | `02_fluxo_e_modelo_funcional.md` (modelo funcional) | F0-P02-PR02 |
| F0-05 | F0-B05 | F0-P03 | PR02 | `03_estados_e_transicoes.md` | F0-P03-PR01 |
| F0-07 | F0-B07 | F0-P03 | PR03 | `04_ficha_administrativa_produto.md` | F0-P03-PR01, PR02; F0-P02-PR01 |
| F0-06 | F0-B06 | F0-P04 | PR01 | `05_fonte_de_verdade_bd_markdown.md` | F0-P03-PR01 |
| F0-09 | F0-B09 | F0-P04 | PR02 | `07_pacote_contexto_ia.md` | F0-P02-PR02; F0-P04-PR01 |
| F0-12 | F0-B12 | F0-P04 | PR03 | `10_requisitos_seguranca_mvp.md` | F0-P05-PR01, PR02 |
| F0-11 | F0-B11 | F0-P05 | PR01 | `09_stack_repositorio_padroes.md` | Arquitectura aprovada |
| F0-10 | F0-B10 | F0-P05 | PR02 | `08_modelo_utilizadores_empresas.md` | F0-P02-PR01 |
| F0-08 | F0-B08 | F0-P05 | PR03 | `06_regras_visao_atencao.md` | F0-P03-PR02, PR03 |
| F0-13 | F0-B13 | F0-P05 | PR04 | `11_plano_piloto.md` | F0-P02-PR01 |
| F0-14 | F0-B14 | F0-P05 | PR05 | `12_decisao_saida_fase_0.md` | Todos os artefactos 01–11 |

Cobertura: 14/14 itens (F0-01 a F0-14). 12/12 artefactos previstos no backlog. Nenhum prompt de implementação do MVP.

Ordem de execução recomendada entre pipelines:
F0-P02 (PR01→PR02) → F0-P03 (PR01→PR02→PR03) → F0-P05 (PR01, PR02) → F0-P04 (PR01→PR02) → F0-P05 (PR03) → F0-P04 (PR03) → F0-P05 (PR04→PR05).
