# Mapa global das pipelines — Fase 1/MVP

Planeamento **just-in-time**: este mapa controla cobertura e dependências das
pipelines F1-P02 a F1-P08. Apenas a **pipeline imediatamente seguinte** recebe
prompts completos de cada vez; as restantes ficam mapeadas (título, escopo,
fronteiras e títulos previstos dos prompts) e só são detalhadas depois da
execução da pipeline anterior, usando o estado real do repositório.

Base: `01_backlog.md` (MVP-01..23, capacidades, tarefas, RT, VAL); §15 do backlog
(pipelines recomendadas); DEC-20260712-04/05.

**Estado das pipelines de execução:**

| Pipeline | Estado | Prompts |
|---|---|---|
| F1-P02 | **Concluída (11/11)** | Executados (ver `pipelines/02_.../resultados_execucao/`) |
| F1-P03 | **Concluída** | Executados (ver `pipelines/03_.../resultados_execucao/`) |
| F1-P04 | **Concluída (6/6)** | Executados (ver `pipelines/04_.../resultados_execucao/`) |
| F1-P05 | **Concluída (6/6)** | Executados (ver `pipelines/05_.../resultados_execucao/`) |
| F1-P06 | **Concluída (6/6)** | PR01–PR06 executados (`pipelines/06_.../resultados_execucao/`); validação E2E + regressão + M1 atingido |
| F1-P07 a F1-P08 | Mapeadas (sem prompts completos) | A gerar após a pipeline anterior |

Ordem recomendada: F1-P02 → P03 → P04 → P05 → P06 → P07 → P08. MVP-20.T1
(selecção da plataforma) e MVP-18.T1 (isolamento) podem antecipar-se em paralelo.

Marcos: **M1 — ATINGIDO** (fluxo vertical ponta a ponta, fim de F1-P06, 2026-07-14); **M2** segurança e
testes consolidados (F1-P07); **M3** ambiente de piloto (F1-P08); **M4** piloto
concluído; **M5** decisão formal.

---

## F1-P02 — Fundação, autenticação e isolamento

* **Objectivo:** base executável do monólito com identidade, contexto de empresa isolado e auditoria mínima; primeiro percurso vertical técnico (arranca → BD → frontend↔backend → auditoria → autentica → empresa/membership → contexto → acesso cruzado rejeitado → testes/CI).
* **Itens macro cobertos:** MVP-01, MVP-02, MVP-03, MVP-17.T1.
* **Capacidades/tarefas principais:** MVP-01.C1/C2 (T1–T6); MVP-02.C1/C2 (T1–T5); MVP-03.C1/C2 (T1–T4); MVP-17.C1 (T1, base).
* **Pré-requisitos:** backlog da Fase 1 existente; repositório greenfield; nenhuma plataforma de deploy escolhida.
* **Dependências entre pipelines:** nenhuma a montante; é o pré-requisito de todas as seguintes.
* **Resultado esperado:** aplicação local executável (backend+frontend+PostgreSQL), configuração validada, armazenamento filesystem, testes base+CI, auditoria mínima, autenticação funcional, empresa+membership Owner, onboarding, contexto de empresa no servidor, testes iniciais de isolamento.
* **Marco:** contribui para M1 (fundação do percurso vertical).
* **Reservas relacionadas:** RT-08 apenas ao nível de fundação (backup/recuperação completos em F1-P08/MVP-20).
* **Itens paralelizáveis internos:** auditoria (MVP-17.T1) em paralelo com a autenticação; frontend base em paralelo com migrações.
* **Títulos previstos dos prompts:** ver a pipeline detalhada (`pipelines/02_fundacao_autenticacao_isolamento/01_pipeline.md`).
* **Ajuste F1-P01-PR03:** F1-P02 continua com **11 prompts** e o resultado global permanece inalterado. **PR02** passa a criar a **fundação de `CustomUser`, `Organisation` e `Membership`** (identidade própria desde a primeira migração + convenção de isolamento); **PR10** passa a implementar **comportamento e onboarding** sobre essas entidades (deixa de as recriar). PR01 fecha as decisões estruturais de arranque (modelo de utilizador próprio, identificadores, toolchain, fronteira HTTP) e cria o endpoint técnico `/api/system/ping`, consumido por PR03 antes dos health checks de PR05.
* **Só detalhável depois da pipeline anterior:** N/A (é a primeira; já detalhada).

## F1-P03 — Portefólio e ficha do produto

* **Objectivo:** gerir vários produtos com a ficha administrativa mínima e a operação explícita de revisão.
* **Itens macro cobertos:** MVP-04, MVP-05.
* **Capacidades/tarefas principais:** MVP-04.C1/C2 (T1–T5); MVP-05.C1 (T1–T4, incl. "marcar como revisto").
* **Pré-requisitos:** F1-P02 concluída (empresa, isolamento, auditoria).
* **Dependências:** MVP-04→MVP-03; MVP-05→MVP-04; agregadas da ficha ficam progressivas (documentos/decisões/pendências chegam em F1-P04).
* **Resultado esperado:** portefólio funcional; ficha com defaults e revisão explícita; auditoria de produto.
* **Marco:** M1 (parcial).
* **Reservas relacionadas:** CLR-02 (revisão explícita) — DEC-20260712-05.
* **Itens paralelizáveis:** filtros/paginação (MVP-04.T4) em paralelo com a ficha.
* **Títulos previstos dos prompts (a confirmar no detalhe):** portefólio (entidade+API+isolamento); UI de portefólio; ficha e defaults; operação explícita de revisão; auditoria e filtros.
* **Só detalhável depois de F1-P02:** convenções reais de módulo/serviço e padrão de autorização estabelecidos em F1-P02.

## F1-P04 — Documentos, tipos, decisões e pendências

* **Objectivo:** contexto documental versionado e seguro, com tipos mínimos, decisões e pendências tipificadas.
* **Itens macro cobertos:** MVP-06, MVP-07, MVP-08, MVP-09.
* **Capacidades/tarefas principais:** MVP-06.C1/C2/C3 (T1–T7, incl. `is_outdated`/`export_policy`, versões, sanitização, concorrência); MVP-07 (T1–T3); MVP-08 (T1–T4); MVP-09 (T1–T4).
* **Pré-requisitos:** F1-P03 concluída; adaptador de armazenamento (F1-P02).
* **Dependências:** MVP-06→MVP-03/adaptador; MVP-07→MVP-06; MVP-08/09→MVP-04(+06/08).
* **Resultado esperado:** documentos criáveis/versionáveis/recuperáveis com marcadores; decisões e pendências (5 tipos) funcionais; agregadas da ficha ligadas.
* **Marco:** M1 (parcial).
* **Reservas relacionadas:** CLR-03 (marcador `export_policy` no documento; comportamento completo em F1-P05/P07).
* **Itens paralelizáveis:** decisões e pendências em paralelo após os documentos.
* **Títulos previstos:** documentos+versões; segurança documental+marcadores; tipos documentais; decisões; pendências.
* **Só detalhável depois de F1-P03:** modelo real da ficha e associações de produto.

## F1-P05 — Funções, execuções e pacote de contexto

* **Objectivo:** preparar trabalho de IA rastreável — função prévia com snapshot, execução com versões exactas, pacote de contexto seguro.
* **Itens macro cobertos:** MVP-10, MVP-11, MVP-12.
* **Capacidades/tarefas principais:** MVP-10.C1 (T1–T4); MVP-11.C1/C2 (T1–T5, snapshot+estados); MVP-12.C1/C2 (T1–T5, geração fiel+`export_policy`).
* **Pré-requisitos:** F1-P04 concluída (documentos/versões).
* **Dependências:** MVP-11→MVP-10/06; MVP-12→MVP-11(+06.T5).
* **Resultado esperado:** função configurável; execução com contexto congelado; pacote de contexto fiel às versões com política de exportação aplicada.
* **Marco:** M1 (aproxima o topo do percurso vertical).
* **Reservas relacionadas:** CLR-03 (bloqueio de geração por `denied`); confirmação externa do pacote validada em F1-P08/piloto.
* **Itens paralelizáveis:** função (MVP-10) pode iniciar em paralelo com o fim de F1-P04.
* **Títulos previstos:** funções organizacionais; execução+snapshot+estados; geração do pacote; `export_policy` na geração.
* **Só detalhável depois de F1-P04:** modelo real de documento/versão e marcadores.

## F1-P06 — Resultados, revisão e aplicação controlada

* **Objectivo:** fechar o ciclo de validação humana — tentativas imutáveis, revisão com histórico, aplicação controlada ligada à tentativa aprovada. Atinge **M1** (fluxo vertical ponta a ponta).
* **Itens macro cobertos:** MVP-13, MVP-14, MVP-15.
* **Capacidades/tarefas principais:** MVP-13.C1 (T1–T5, tentativa imutável); MVP-14.C1 (T1–T5, revisão+histórico); MVP-15.C1/C2 (T1–T5, aplicação por tentativa aprovada).
* **Pré-requisitos:** F1-P05 concluída (execução+pacote).
* **Dependências:** MVP-14→MVP-13; MVP-15→MVP-14/06/08/09.
* **Resultado esperado:** ciclo E1–E6 completo; importar≠aprovar≠aplicar comprovado; histórico de tentativas/revisões preservado.
* **Marco:** **M1** atingido.
* **Reservas relacionadas:** CLR-04 (tentativas/revisões) — DEC-20260712-05.
* **Itens paralelizáveis:** poucos (cadeia sequencial 13→14→15); UI em paralelo com a API de cada um.
* **Títulos previstos:** registo de tentativa; revisão e histórico; aplicação controlada; provas negativas de segurança.
* **Só detalhável depois de F1-P05:** modelo real de execução e snapshot.

## F1-P07 — Atenção, auditoria, segurança e exportação

* **Objectivo:** sinais explicáveis, rastreabilidade consolidada, segurança verificada e portabilidade. Atinge **M2**.
* **Itens macro cobertos:** MVP-16, MVP-17 (consolidação), MVP-18, MVP-19.
* **Capacidades/tarefas principais:** MVP-16.C1 (T1–T4); MVP-17.C1/C2 (integração dos emissores, consulta); MVP-18.C1/C2 (suites de isolamento/autorização/conteúdo/segredos/injecção); MVP-19.C1/C2 (exportação+manifesto).
* **Pré-requisitos:** F1-P06 concluída (fluxo vertical completo para gerar sinais e dados a exportar/auditar).
* **Dependências:** MVP-16→emissores de 04/06/09/11–14; MVP-18 transversal; MVP-19→04/06/08/09.
* **Resultado esperado:** painel de atenção com as 5 regras; auditoria integrada em todos os módulos; suites de segurança verdes (VAL-002/014); exportação de portabilidade com manifesto.
* **Marco:** **M2** atingido.
* **Reservas relacionadas:** RR-07 (controlos de segurança — comprovados aqui); CLR-03 (exclusões no manifesto).
* **Itens paralelizáveis:** MVP-16 e MVP-19 em paralelo; MVP-18 progressivo desde F1-P02.
* **Títulos previstos:** cálculo das regras de atenção; consolidação de auditoria; suites de isolamento/autorização; suites de conteúdo/injecção; exportação e manifesto.
* **Só detalhável depois de F1-P06:** conjunto real de estados/eventos emitidos.

## F1-P08 — Operação, testes críticos, piloto e avaliação

* **Objectivo:** ambiente estável (com selecção da plataforma), suite E2E, condução do piloto e decisão formal. Atinge **M3–M5**.
* **Itens macro cobertos:** MVP-20, MVP-21, MVP-22, MVP-23.
* **Capacidades/tarefas principais:** MVP-20.C1/C2/C3 (T1 selecção da plataforma + T2–T7); MVP-21.C1/C2 (E2E+consolidação); MVP-22.C1/C2 (preparação+condução); MVP-23.C1 (relatório+decisão).
* **Pré-requisitos:** F1-P07 concluída (M2); **MVP-20.T1 pode e deve anteceder-se** (selecção da plataforma antes da implementação operacional).
* **Dependências:** MVP-20→01/17/18; MVP-21→01..19; MVP-22→01..21+artefacto 11; MVP-23→22.
* **Resultado esperado:** plataforma seleccionada e registada; ambiente de piloto recuperável e observável; E2E verde em CI; piloto concluído com dados; matriz VAL actualizada; decisão formal sobre a Versão 1.
* **Marco:** **M3** (operação) → **M4** (piloto) → **M5** (decisão).
* **Reservas relacionadas:** DEC-F0-FINAL-02 (plataforma em MVP-20.T1); RR-06 (execução do piloto); confirmação externa do pacote (naturalmente cumprida no piloto).
* **Itens paralelizáveis:** MVP-20.T1 muito cedo; instrumentos do piloto (MVP-22.T1) em paralelo com testes.
* **Títulos previstos:** selecção e registo da plataforma; observabilidade e continuidade; suite E2E; preparação do piloto; condução; avaliação e decisão.
* **Só detalhável depois de F1-P07:** estado real de segurança/operação e evidências acumuladas.

---

## Cobertura e rastreabilidade

* **Itens macro:** F1-P02 (01,02,03,17.T1) · P03 (04,05) · P04 (06,07,08,09) · P05 (10,11,12) · P06 (13,14,15) · P07 (16,17,18,19) · P08 (20,21,22,23). Cobertura 23/23, sem sobreposição de escopo (MVP-17 aparece em F1-P02 como base — T1 — e em F1-P07 como consolidação, por desenho).
* **RT:** RT-01/02/08/09/10 desde F1-P02; RT-03/04/07 em F1-P04/P05; RT-05 em F1-P06; RT-06 em F1-P07; RT-08 completo em F1-P08.
* **VAL:** VAL-001/002/012/016 parciais em F1-P02; 003 (P03); 004/005/006/007/008/009 (P04–P06); 010/011 (P06/P07); 013/014 (P07); 015/016 completos (P08).
* **Reservas transferidas:** plataforma → F1-P08/MVP-20.T1; piloto → F1-P08/MVP-22; controlos de segurança → F1-P07/MVP-18 (+P08/MVP-21); confirmação externa do pacote → F1-P08/piloto.

## Regra de detalhe just-in-time

Após concluir cada pipeline, gerar os prompts completos da seguinte usando o
**estado real do repositório** (decisões técnicas de arranque, convenções de
módulo, padrões de autorização e de teste efectivamente adoptados). Não gerar
prompts completos com antecedência para pipelines cujo pré-requisito ainda não
foi executado.
