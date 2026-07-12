# Log de decisões de execução

Registo append-only das decisões relevantes de execução (arquitectura, contratos
de API, modelo de dados, permissões, segurança, comportamento funcional,
integração, deploy, escopo, compatibilidade ou manutenção futura).

Cada decisão segue o template abaixo. Não editar entradas históricas; quando uma
decisão evoluir, registar a nova entrada indicando que substitui a anterior.

```markdown
## DEC-YYYYMMDD-XX — <Título>

- Data:
- Fase:
- Pipeline:
- Prompt:
- Decisão:
- Motivo:
- Alternativas consideradas:
- Impacto:
- Ficheiros ou áreas afectadas:
- Estado: Activa | Substituída | Rever
- Substitui:
- Resultado relacionado:
```

---

## DEC-20260712-01 — Aprovação humana deixa de ser gate da execução documental

- Data: 2026-07-12
- Fase: F0
- Pipeline: Governação (transversal)
- Prompt: —
- Decisão: a revisão ou aprovação humana dos artefactos deixa de ser um gate obrigatório entre prompts, pipelines ou fases. Passam a distinguir-se três eixos: estado de execução, estado de revisão (informativo, não bloqueante) e estado de decisão (Proposta / Adoptada tacitamente / Confirmada / Confirmada com reservas / Rejeitada / Substituída). Uma decisão proposta e usada como base por trabalho posterior vigora como Adoptada tacitamente até ser confirmada, alterada, rejeitada ou substituída. Os pré-requisitos de execução passam a basear-se na existência material de artefactos e dependências, não em aprovação.
- Motivo: o uso de estados de aprovação humana como pré-requisito bloqueou prompts (F0-P04-PR03 e F0-P05-PR05) mesmo quando os artefactos materiais necessários já existiam e tinham sido revistos, sem que os estados documentais tivessem sido actualizados. A mudança preserva a continuidade sem inventar factos.
- Alternativas consideradas: manter a aprovação como gate (rejeitada: causa bloqueios artificiais); tornar a revisão opcional mas sem estado de decisão (rejeitada: perderia rastreabilidade da vigência das decisões).
- Impacto: guia `README.md` (§10 estados, §11 template, §15 fecho, §17 bloqueio, §20 decisões, §14 formatos); template `_templates/resultado_prompt.md`; backlog `02_fase_0_preparacao/01_backlog.md`; pipelines F0-P02 a F0-P05 (pré-requisitos passam a existência material); `01_status_pipelines.md`, `00_painel_execucao_global.md`, `05_diario_execucao_ia.md`. F0-P04-PR03 fica pronto para reexecução (artefactos 08 e 09 existem); F0-P05-PR05 continua dependente apenas da existência do artefacto 10, não de aprovação.
- Distinção governação vs produto: esta decisão aplica-se **apenas** à governação da execução e dos artefactos. **Não** altera a regra funcional do produto VentureOps AI segundo a qual **resultados de IA não podem tornar-se informação oficial nem ser aplicados sem validação humana** (visão §12 princípio 8; arquitectura §2.5; matriz `04_matriz_validacao_global.md`, VAL-010). A validação humana de resultados de IA no produto permanece inalterada.
- Ficheiros ou áreas afectadas: governação documental e pipelines da Fase 0.
- Estado: Confirmada
- Substitui: —
- Resultado relacionado: esta alteração de governação (2026-07-12).

## DEC-20260712-02 — Aceite de revisão dos artefactos da Fase 0 para continuidade

- Data: 2026-07-12
- Fase: F0
- Pipeline: Fase 0 (artefactos)
- Prompt: —
- Decisão: os artefactos 01–09 e 11 da Fase 0, já produzidos, foram revistos pelo operador humano em 2026-07-12 e são aceites para continuidade. As decisões neles propostas passam a vigorar como Adoptadas tacitamente (ou Confirmadas quando o humano o indicar), sem reescrita do conteúdo substantivo dos artefactos.
- Motivo: actualizar o estado de revisão documental que estava por registar, permitindo a continuidade sem bloqueios.
- Alternativas consideradas: manter "Não revista" (rejeitada: não reflecte a revisão ocorrida).
- Impacto: coluna `Revisão` de `01_status_pipelines.md` (F0-P02–F0-P05). Não altera o conteúdo dos artefactos. Não torna cumpridos critérios materiais em falta (ver pendências).
- Distinção: o aceite é documental; pendências materiais (teste da ficha com produto real, participantes do piloto, artefacto 10, fecho da fase) **não** são consideradas cumpridas.
- Ficheiros ou áreas afectadas: `01_status_pipelines.md`.
- Estado: Confirmada
- Substitui: —
- Resultado relacionado: DEC-20260712-01.

## DEC-20260712-03 — Proposta de saída da Fase 0: avançar com reservas

- Data: 2026-07-12
- Fase: F0
- Pipeline: F0-P05
- Prompt: F0-P05-PR05
- Decisão: propõe-se avançar para a Fase 1 **com riscos formalmente aceites** (Opção B), com base na revisão cruzada dos artefactos 01–11 e na consolidação do escopo do MVP (artefacto 12). As decisões DB-01 a DB-13 vigoram como Adoptadas tacitamente. A Fase 0 **não** é declarada concluída: fica "pronta para transição com reservas".
- Motivo: não há incoerência estrutural nem risco crítico; as pendências materiais são não estruturais e transferíveis, não comprometendo a arquitectura nem a decomposição do MVP.
- Alternativas consideradas: Opção A (rejeitada: há critérios materiais parciais); Opção C (rejeitada: atrasaria a decomposição sem necessidade estrutural); Opção D (rejeitada: sem incoerência estrutural).
- Critérios materiais cumpridos: 1, 2, 3, 4, 6, 7, 8, 10, 12; 13 com reservas.
- Critérios materiais pendentes: 5 (teste da ficha com produto real); 9 (plataforma de deploy); 11 (participantes do piloto).
- Reservas / riscos aceites: RR-01 (usabilidade da ficha), RR-02 (participantes por confirmar), RR-03 (deploy/TLS/backup por definir) — cada um com destino identificado (piloto / ambiente).
- Condições: reclassificar F0-B11 (deploy) como requisitos mínimos + plataforma A validar; transferir o teste da ficha e a identificação dos participantes para o arranque do piloto (F0-B13); manter a validação humana de resultados de IA no produto.
- Impacto: habilita a preparação da decomposição do MVP (Fase 1), não iniciada nesta iteração; escopo congelado (DB-14) em `12_decisao_saida_fase_0.md`.
- Ficheiros ou áreas afectadas: `02_fase_0_preparacao/artefactos/12_decisao_saida_fase_0.md`.
- Estado: Proposta (aguarda decisão do operador; pode vigorar como Adoptada tacitamente se a decomposição do MVP arrancar com este escopo)
- Substitui: —
- Resultado relacionado: `02_fase_0_preparacao/pipelines/05_stack_piloto_e_fecho/resultados_execucao/prompt_05_resultado.md` (Reexecução — 2026-07-12).

## DEC-20260712-04 — Confirmação com reservas da saída da Fase 0 e fecho das decisões residuais

- Data: 2026-07-12
- Fase: F0
- Pipeline: F0-P05 (fecho formal, transversal)
- Prompt: F0-P05-PR05 (fecho formal)
- Decisão: **confirma-se com reservas** a Opção B proposta em DEC-20260712-03. A Fase 0 está **concluída com reservas** e fica **autorizada a decomposição controlada da Fase 1/MVP**. Confirmam-se explicitamente as decisões residuais:
  - **DEC-F0-FINAL-01** — saída da Fase 0 confirmada com reservas; decomposição da Fase 1/MVP autorizada;
  - **DEC-F0-FINAL-02** — a selecção da plataforma concreta de deploy é transferida para `MVP-20 — Operação mínima do MVP`, a decidir antes da implementação e validação operacional desse item; requisitos mínimos (containers, PostgreSQL, armazenamento persistente, TLS, gestão segura de segredos, backups, health checks, migrações controladas, rollback, logs estruturados) já vigentes; a ausência de escolha concreta deixa de impedir o fecho da Fase 0;
  - **DEC-F0-FINAL-03** — participante mínimo do piloto: Aldino Ramos, fundador técnico e operador principal; outros participantes permanecem opcionais;
  - **DEC-F0-FINAL-04** — produto real para o teste da ficha administrativa: VentureOps AI;
  - **DEC-F0-FINAL-05** — no MVP individual, o mesmo utilizador pode exercer Owner, Operador e Revisor/Aprovador, com responsabilidades funcionalmente separadas (importar ≠ aprovar; aprovar ≠ aplicar automaticamente; aprovação e aplicação exigem acção explícita e auditável; arquitectura preparada para separar os papéis no futuro);
  - **DEC-F0-FINAL-06** — a função organizacional é criada e configurada previamente; cada execução assistida referencia uma função activa existente, preserva um snapshot das instruções utilizadas e não exige recriar/redefinir a função; "definir função" pertence à configuração inicial/manutenção, não ao ciclo recorrente;
  - **DEC-F0-FINAL-07** — enumeração funcional mínima de tipos de pendência: `action`, `review`, `validation`, `obligation`, `decision_follow_up`; sem sprint/história/bug/tarefa técnica; novos tipos exigem necessidade funcional demonstrada;
  - **DEC-F0-FINAL-08** — marcadores documentais estruturados `is_outdated` (boolean, fonte BD, valor inicial `false`, alimenta a visão de atenção, sem valor concorrente no Markdown) e `export_policy` (`allowed`\|`confirm`\|`denied`, fonte BD, valor inicial `confirm`, `denied` bloqueia exportação/pacote de contexto, aplicado pelo backend).
- Motivo: o operador reviu a proposta de saída, forneceu os dados em falta (produto real, participante mínimo) e resolveu as quatro incoerências não bloqueantes identificadas na revisão cruzada, permitindo o fecho formal sem inventar factos.
- Alternativas consideradas: manter a Fase 0 apenas "pronta para transição" sem confirmação formal (rejeitada: o operador forneceu decisão explícita, que deve ser registada como Confirmada, não apenas Adoptada tacitamente).
- Critérios materiais cumpridos: 1 a 13 (todos — ver `12_decisao_saida_fase_0.md`, §8).
- Riscos formalmente aceites: RR-03 (deploy/TLS/backup concretos), RR-05 (robustez anti-injecção entre modelos), RR-06 (piloto ainda não executado), RR-07 (controlos de segurança ainda não implementados) — nenhum crítico nem estrutural.
- Condições: nenhuma pendente; as condições da decisão anterior (DEC-20260712-03) foram cumpridas (ver `12_decisao_saida_fase_0.md`, §14).
- Impacto: habilita a preparação e o início da decomposição do backlog do MVP (Fase 1), **não iniciada nesta iteração**; escopo do MVP congelado e confirmado (DB-14).
- Ficheiros ou áreas afectadas: `02_fase_0_preparacao/artefactos/12_decisao_saida_fase_0.md` (§4, §5, §7, §8, §9, §10, §11, §13–§17); `02_fase_0_preparacao/artefactos/02_fluxo_e_modelo_funcional.md`; `03_estados_e_transicoes.md`; `04_ficha_administrativa_produto.md`; `05_fonte_de_verdade_bd_markdown.md`; `06_regras_visao_atencao.md`; `07_pacote_contexto_ia.md`; `08_modelo_utilizadores_empresas.md`; `09_stack_repositorio_padroes.md`; `10_requisitos_seguranca_mvp.md`; `11_plano_piloto.md`; `pipelines/03_modelo_funcional/resultados_execucao/prompt_03_resultado.md`; `pipelines/05_stack_piloto_e_fecho/resultados_execucao/prompt_05_resultado.md`; `01_status_pipelines.md`; `00_painel_execucao_global.md`; `05_diario_execucao_ia.md`.
- Estado: Activa
- Substitui: DEC-20260712-03 (preservada no histórico, não apagada nem editada)
- Resultado relacionado: `02_fase_0_preparacao/pipelines/05_stack_piloto_e_fecho/resultados_execucao/prompt_05_resultado.md` (Fecho formal — 2026-07-12 15:20); `02_fase_0_preparacao/artefactos/12_decisao_saida_fase_0.md` (§17).
