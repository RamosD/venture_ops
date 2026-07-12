---
fase: F0
pipeline: F0-P04
prompt: F0-P04-PR02
modelo: claude-opus-4-8
inicio: 2026-07-11 23:00
fim: 2026-07-11 23:03
estado_execucao: Concluído
estado_validacao: Pendente
commit: não criado
---

# Resultado — Prompt 02 — Pacote de contexto para IA

## 1. Resumo

Criado o artefacto `07_pacote_contexto_ia.md`, que padroniza o pacote de contexto
em sete secções (objectivo, função, instruções, produto, restrições, formato
esperado, documentos com versões), com identificação de fontes e separação
explícita entre instruções e conteúdo documental (mitigação §11.10). Propôs-se o
formato de exportação (texto único por defeito; ficheiros separados em
alternativa) e de importação do resultado (texto/Markdown por defeito; ficheiro
em alternativa), neutros face a fornecedores. Foi produzido um pacote de exemplo
fictício e realizado um teste manual pela IA executora, com uma linha de injecção
plantada: a estrutura mostrou-se suficiente e a injecção não foi obedecida.
Evidência guardada. Tudo "A validar".

## 2. Alterações

### Ficheiros criados

- `docs/gestao/02_fase_0_preparacao/artefactos/07_pacote_contexto_ia.md`
- `docs/gestao/02_fase_0_preparacao/pipelines/04_dados_contexto_seguranca/resultados_execucao/evidencias/prompt_02_teste_pacote.md`
- `docs/gestao/02_fase_0_preparacao/pipelines/04_dados_contexto_seguranca/resultados_execucao/prompt_02_resultado.md`

### Ficheiros alterados

- Nenhum (além dos registos globais previstos no fecho).

### Ficheiros removidos

- Nenhum.

## 3. Validações

| Comando ou verificação | Resultado | Evidência |
|---|---|---|
| Estrutura cobre os sete elementos (F0-09) | Sucesso | Artefacto §2 (1 a 7) |
| Pacote de exemplo existe, sem dados sensíveis | Sucesso | `evidencias/prompt_02_teste_pacote.md` (conteúdo fictício) |
| Teste manual executado com evidência | Sucesso | `evidencias/prompt_02_teste_pacote.md` (injecção não obedecida) |
| Fontes identificadas e instruções separadas | Sucesso | Artefacto §2 (R-PC-01 a R-PC-03); evidência §3 |

## 4. Problemas e excepções

- Problemas encontrados: Nenhum.
- Limitações da validação: teste realizado por um único modelo (auto-teste da IA executora); confirmação com modelo externo recomendada (P-06). Estrutura e formatos "A validar".
- Trabalho não executado: Nenhum (dentro do âmbito do prompt).

## 5. Decisões relevantes

- Nenhuma fechada. Estrutura do pacote e formatos de exportação/importação propostos. Sem entrada no log global sem aprovação humana.

## 6. Riscos, bloqueios ou dívida técnica

- Nenhum. Nota (não risco): a robustez da separação instruções/dados pode variar entre modelos; mitigada pela declaração anti-injecção e a confirmar em P-06.

## 7. Próximo passo

- Revisão humana da estrutura e formatos (P-01 a P-06), incluindo teste com modelo externo. Conforme a ordem planeada, o prompt seguinte desta pipeline (F0-P04-PR03, segurança) depende de F0-P05-PR01/PR02, ainda não executados. Não avançar autonomamente.
