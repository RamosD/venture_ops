# Status das pipelines

Fonte de verdade do progresso das pipelines. Actualizar apenas a linha da
pipeline afectada. As colunas de contagem referem-se a prompts. A coluna
`Revisão` é **informativa e não bloqueante** (guia §10); `Revistos` conta prompts
com revisão humana registada. Os artefactos 01–11 da Fase 0 foram revistos
pelo operador humano; o fecho formal (2026-07-12, DEC-20260712-04) confirmou a
saída da Fase 0 com reservas. **Todas as pipelines da Fase 0 estão concluídas.**

| ID | Fase | Pipeline | Execução | Revisão | Prompts | Concluídos | Revistos | Bloqueios | Próximo |
|---|---|---|---|---|---:|---:|---:|---|---|
| F0-P00 | F0 | Bootstrap da gestão | Em execução | Não revista | 1 | 1 | 0 | 0 | — |
| F0-P01 | F0 | Planeamento da Fase 0 | Concluído | Não revista | 2 | 2 | 0 | 0 | — |
| F0-P02 | F0 | Escopo e caso de uso do MVP | Concluído | Revista | 2 | 2 | 2 | 0 | — |
| F0-P03 | F0 | Modelo funcional do MVP | Concluído | Revista | 3 | 3 | 3 | 0 | — |
| F0-P04 | F0 | Dados, contexto de IA e segurança | Concluído | Revista (PR01–PR02) | 3 | 3 | 2 | 0 | — |
| F0-P05 | F0 | Stack, piloto e fecho da Fase 0 | Concluído | Revista | 5 | 5 | 5 | 0 | — (Fase 0 concluída com reservas) |
| F1-P01 | F1 | Planeamento e decomposição do MVP | Concluído | Não revista | 1 | 1 | 0 | 0 | Geração das pipelines de execução do MVP (F1-P02..P08) |
