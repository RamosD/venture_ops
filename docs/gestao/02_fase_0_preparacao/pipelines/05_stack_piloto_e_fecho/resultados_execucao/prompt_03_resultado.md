---
fase: F0
pipeline: F0-P05
prompt: F0-P05-PR03
modelo: claude-opus-4-8
inicio: 2026-07-11 23:14
fim: 2026-07-11 23:20
estado_execucao: Concluído
estado_validacao: Pendente
commit: não criado
---

# Resultado — Prompt 03 — Regras da visão de atenção

## 1. Resumo

Criado o artefacto `06_regras_visao_atencao.md`, com uma regra determinística por
cada um dos cinco sinais: produto sem revisão (R-AT-01), decisão pendente
(R-AT-02), pendência vencida (R-AT-03), resultado por validar (R-AT-04) e
documento desactualizado (R-AT-05). Cada regra tem condição objectiva, motivo
apresentável ao utilizador, parâmetros com valores iniciais e os dados que usa
(apenas de F0-B05 e F0-B07). Fecharam-se os dois elementos que F0-B05 tinha
remetido para F0-B08: a interpretação de "decisão pendente" (via pendência de
tipo decisão) e o marcador manual "documento desactualizado". Confirmou-se o
cálculo simples sem persistência de indicadores. Tudo "A validar".

## 2. Alterações

### Ficheiros criados

- `docs/gestao/02_fase_0_preparacao/artefactos/06_regras_visao_atencao.md`
- `docs/gestao/02_fase_0_preparacao/pipelines/05_stack_piloto_e_fecho/resultados_execucao/prompt_03_resultado.md`

### Ficheiros alterados

- Nenhum (além dos registos globais previstos no fecho).

### Ficheiros removidos

- Nenhum.

## 3. Validações

| Comando ou verificação | Resultado | Evidência |
|---|---|---|
| Cada regra com condição objectiva e motivo | Sucesso | Artefacto §2 (R-AT-01 a R-AT-05) |
| Cada regra depende só de F0-B05 e F0-B07 | Sucesso | Artefacto §2 (campo "Dados usados") |
| Parâmetros com valores iniciais | Sucesso | Artefacto §3 |
| Sem heurísticas não explicáveis | Sucesso | Artefacto §7 (comparações e marcador booleano) |

## 4. Problemas e excepções

- Problemas encontrados: Nenhum.
- Limitações da validação: regras propostas, "A validar" (P-01 a P-05). Dois elementos (interpretação de decisão pendente e marcador desactualizado) fechados aqui exigem confirmação e, se aprovados de forma alternativa, poderão exigir ajuste em F0-B05.
- Trabalho não executado: Nenhum. Não se definiram queries nem algoritmos, por instrução.

## 5. Decisões relevantes

- Nenhuma fechada. Regras e parâmetros propostos. Resolução (proposta) de dois pontos deixados por F0-B05. Sem entrada no log global sem aprovação humana.

## 6. Riscos, bloqueios ou dívida técnica

- Nenhum novo. RB-20260711-01 mantém-se Em mitigação (independente deste prompt).

## 7. Próximo passo

- Revisão humana das regras (P-01 a P-05). A seguir, F0-P05-PR04 (plano do piloto). Não avançar autonomamente.
