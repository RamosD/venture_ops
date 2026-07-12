---
fase: F0
pipeline: F0-P03
prompt: F0-P03-PR02
modelo: claude-opus-4-8
inicio: 2026-07-11 22:50
fim: 2026-07-11 22:53
estado_execucao: Concluído
estado_validacao: Pendente
commit: não criado
---

# Resultado — Prompt 02 — Estados e transições das entidades

## 1. Resumo

Criado o artefacto `03_estados_e_transicoes.md`, com os estados mínimos e as
transições válidas de produto, documento, decisão, pendência, função, execução e
revisão, ao nível funcional. Cada transição indica o papel funcional que a
executa (Operador ou Revisor/Aprovador) e o passo do fluxo que a origina. Uma
tabela de cobertura confirma que cada passo do fluxo aprovado é suportado e que
nenhum estado fica sem uso. A revisão é tratada como estado de validação do
resultado dentro da execução, coerente com o modelo funcional. Estados
especulativos foram evitados; sinais da visão de atenção remetidos para F0-B08.
Tudo "A validar".

## 2. Alterações

### Ficheiros criados

- `docs/gestao/02_fase_0_preparacao/artefactos/03_estados_e_transicoes.md`
- `docs/gestao/02_fase_0_preparacao/pipelines/03_modelo_funcional/resultados_execucao/prompt_02_resultado.md`

### Ficheiros alterados

- Nenhum (além dos registos globais previstos no fecho).

### Ficheiros removidos

- Nenhum.

## 3. Validações

| Comando ou verificação | Resultado | Evidência |
|---|---|---|
| Estados e transições por entidade | Sucesso | Artefacto §2 (2.1 a 2.7) |
| Cada transição indica quem executa | Sucesso | Coluna "Quem" em todas as tabelas |
| Nenhum passo exige estado inexistente | Sucesso | Artefacto §3 (cobertura completa) |
| Nenhum estado sem uso no fluxo | Sucesso | Artefacto §3 + notas 2.1/2.3/2.4 |

## 4. Problemas e excepções

- Problemas encontrados: Nenhum.
- Limitações da validação: estados propostos, "A validar"; revisão humana pendente (P-01 a P-07). Interpretação dos sinais "documento desactualizado" e "decisão pendente" deliberadamente remetida para F0-B08.
- Trabalho não executado: Nenhum (dentro do âmbito do prompt).

## 5. Decisões relevantes

- Nenhuma fechada. Decisões de desenho propostas: conjunto mínimo de estados por entidade e revisão folded na execução (coerente com F0-P03-PR01). Sem entrada no log global sem aprovação humana.

## 6. Riscos, bloqueios ou dívida técnica

- Nenhum.

## 7. Próximo passo

- Revisão humana dos estados (P-01 a P-07); a seguir, prompt F0-P03-PR03 (ficha administrativa mínima do produto). Não avançar autonomamente.
