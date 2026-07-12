# Riscos e bloqueios

Registo de riscos, bloqueios e dívida técnica com impacto superior ao prompt
actual. Não criar nova entrada para o mesmo risco; quando o risco evoluir,
actualizar a entrada existente pelo respectivo ID.

Cada registo segue o template abaixo.

```markdown
## RB-YYYYMMDD-XX — <Título>

- Data de abertura:
- Última actualização:
- Fase:
- Pipeline:
- Prompt:
- Tipo: Risco | Bloqueio | Dívida técnica
- Severidade: Baixa | Média | Alta | Crítica
- Descrição:
- Impacto:
- Acção recomendada:
- Responsável:
- Estado: Aberto | Em mitigação | Resolvido | Aceite | Adiado
- Evidência ou resultado relacionado:
```

---

## RB-20260711-01 — Artefacto 10 (segurança, F0-B12) inexistente

- Data de abertura: 2026-07-11
- Última actualização: 2026-07-12
- Fase: F0
- Pipeline: F0-P04
- Prompt: F0-P04-PR03
- Tipo: Bloqueio
- Severidade: Baixa
- Descrição: o artefacto 10 (requisitos mínimos de segurança, F0-B12) ainda não existe. É produzido pela reexecução de F0-P04-PR03, cujos pré-requisitos materiais (artefactos 08 e 09) já existem.
- Impacto: sem o artefacto 10, o fecho da Fase 0 (F0-P05-PR05) não pode ser executado, por exigir a existência de todos os artefactos 01–11. Não afecta a reexecução de F0-P04-PR03.
- Acção recomendada: reexecutar F0-P04-PR03 (produz o artefacto 10); em seguida executar F0-P05-PR05 (fecho, que pode propor avanço com reservas).
- Responsável: operador da pipeline.
- Estado: Resolvido
- Data de resolução: 2026-07-12
- Actualização 2026-07-11 23:13: os artefactos 09 (F0-P05-PR01) e 08 (F0-P05-PR02) foram criados; ambos os pré-requisitos materiais passam a existir.
- Actualização 2026-07-12: sob a governação não bloqueante (DEC-20260712-01), a falta de aprovação humana deixou de ser causa deste bloqueio, permanecendo apenas a inexistência material do artefacto 10.
- Resolução 2026-07-12: F0-P04-PR03 foi reexecutado e produziu `10_requisitos_seguranca_mvp.md`. Os artefactos 08 e 09 existiam e foram utilizados; a alteração de governação removeu o gate de aprovação. O artefacto 10 passa a existir e o bloqueio está resolvido.
- Evidência ou resultado relacionado: `02_fase_0_preparacao/artefactos/10_requisitos_seguranca_mvp.md`; `02_fase_0_preparacao/pipelines/04_dados_contexto_seguranca/resultados_execucao/prompt_03_resultado.md` (secção Reexecução — 2026-07-12).

---

## RB-20260712-02 — Riscos de transição da Fase 0 formalmente aceites

- Data de abertura: 2026-07-12
- Última actualização: 2026-07-12
- Fase: F0 (transição para F1)
- Pipeline: F0-P05 (fecho formal)
- Prompt: F0-P05-PR05 (fecho formal)
- Tipo: Risco
- Severidade: Baixa
- Descrição: no fecho formal da Fase 0 (DEC-20260712-04), foram formalmente aceites os riscos residuais RR-03 (plataforma de deploy/TLS/backup concretos por seleccionar em `MVP-20`), RR-05 (robustez da separação instruções/dados varia entre modelos de IA), RR-06 (piloto ainda não executado) e RR-07 (controlos de segurança do artefacto 10 ainda não implementados, apenas especificados). Nenhum é crítico nem estrutural.
- Impacto: nenhuma reserva impede a decomposição controlada da Fase 1/MVP. A selecção da plataforma de deploy é pré-condição apenas de `MVP-20`; a execução do piloto e a implementação dos controlos de segurança são actividades próprias da Fase 1.
- Acção recomendada: seleccionar a plataforma de deploy antes de `MVP-20`; executar o piloto com o participante mínimo confirmado; implementar e verificar os controlos de `10_requisitos_seguranca_mvp.md` na Fase 1; recomenda-se (não obrigatório) confirmar o pacote de contexto com um modelo de IA externo.
- Responsável: operador/equipa da Fase 1.
- Estado: Aceite
- Evidência ou resultado relacionado: `02_fase_0_preparacao/artefactos/12_decisao_saida_fase_0.md` (§10, §17); `docs/gestao/02_log_decisoes_execucao.md` (DEC-20260712-04).
