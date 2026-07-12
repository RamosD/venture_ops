# Decisão de saída da Fase 0 — VentureOps AI

* Fase: F0 — Preparação e alinhamento
* Item tratado: F0-B14 (F0-14)
* Decisão bloqueadora: DB-14
* Estado do artefacto: **Confirmado com reservas** (DEC-20260712-04) — Fase 0 concluída com reservas; decomposição controlada da Fase 1/MVP autorizada
* Prompt de origem: F0-P05-PR05; fecho formal aplicado em 2026-07-12 (ver §17)

## 1. Identificação

Revisão cruzada dos artefactos 01–11 da Fase 0, verificação dos critérios de
saída, consolidação do escopo do MVP e proposta fundamentada de decisão de saída.
Não implementa código, não cria o backlog do MVP, não corrige os artefactos nem
altera a baseline. Distingue: **facto**, **decisão adoptada tacitamente**,
**critério cumprido/parcial**, **risco aceite**, **pendência transferida**,
**bloqueio** e **recomendação**.

## 2. Objectivo

Determinar se a Fase 0 reúne condições para habilitar a decomposição segura do
MVP (Fase 1), registando decisões vigentes, pendências materiais e escopo
congelado.

## 3. Fontes analisadas

Artefactos 01–11 (`02_fase_0_preparacao/artefactos/`); backlog F0-B14, §4, §8,
§11; roadmap §11.1; backlog macro (requisitos transversais e controlo de
alterações); painel, status, log de decisões e riscos/bloqueios; guia `README.md`.

## 4. Estado dos artefactos 01–11

| # | Artefacto | Item | Execução | Revisão | Pendência material |
|---|---|---|---|---|---|
| 01 | Segmento e caso de uso | F0-B01/02 | Concluído | Revista | — |
| 02 | Fluxo e modelo funcional | F0-B03/04 | Concluído | Revista | — |
| 03 | Estados e transições | F0-B05 | Concluído | Revista | — |
| 04 | Ficha administrativa | F0-B07 | **Concluído** (teste real 2026-07-12) | Revista | — (resolvida) |
| 05 | Fonte de verdade BD/Markdown | F0-B06 | Concluído | Revista | — |
| 06 | Regras da visão de atenção | F0-B08 | Concluído | Revista | — |
| 07 | Pacote de contexto | F0-B09 | Concluído | Revista | Confirmação com modelo externo (recomendação, não bloqueante) |
| 08 | Modelo de utilizadores/empresas | F0-B10 | Concluído | Revista | — |
| 09 | Stack, repositório e padrões | F0-B11 | Concluído | Revista | Plataforma concreta transferida para MVP-20 (resolvida) |
| 10 | Requisitos de segurança | F0-B12 | Concluído | Não revista | — |
| 11 | Plano do piloto | F0-B13 | Concluído | Revista | Participante mínimo identificado (resolvida); adicionais opcionais |
| 12 | Decisão de saída da Fase 0 | F0-B14 | Concluído | Não revista | — |

Todos os 12 artefactos existem (facto verificado).

## 5. Decisões vigentes DB-01 a DB-13

Todas foram utilizadas como base por trabalho posterior, pelo que vigoram como
**Adoptadas tacitamente** (governação não bloqueante). Pendências materiais
assinaladas não afectam a vigência da decisão, mas continuam por cumprir.

| Decisão | Artefacto | Conteúdo adoptado | Vigência | Pendência | Impacto no backlog MVP |
|---|---|---|---|---|---|
| DB-01 | 01 | Segmento: fundador técnico/microequipa (1–5), 2+ produtos, IA recorrente | **Confirmada** | — | Define público do MVP |
| DB-02 | 01 | Caso de uso principal: ciclo de execução assistida com validação | **Confirmada** | — | Fluxo central do MVP |
| DB-03 | 02 | Fluxo ponta a ponta (C1–C4, E1–E6, T1–T2); C4 configuração prévia (DEC-F0-FINAL-06) | **Confirmada** | — (INC-04 resolvida) | Estrutura os módulos |
| DB-04 | 02 | 8 entidades núcleo; resultado/revisão/pacote folded; tipos de pendência fechados | **Confirmada** (DEC-F0-FINAL-07) | — (INC-02 resolvida) | Modelo de domínio |
| DB-05 | 03 | Estados mínimos por entidade; tipo de pendência associado | **Confirmada** | — | Ciclos de vida |
| DB-06 | 05 | Fonte de verdade única; versões imutáveis; `is_outdated`/`export_policy` | **Confirmada** (DEC-F0-FINAL-08) | — (INC-03 resolvida) | Persistência |
| DB-07 | 04 | 5 campos obrigatórios da ficha; **testados com VentureOps AI** | **Confirmada** (DEC-F0-FINAL-04) | — (resolvida) | Ficha do produto |
| DB-08 | 06 | 5 regras determinísticas de atenção; R-AT-02/05 fechadas | **Confirmada** (DEC-F0-FINAL-07/08) | Confirmação externa do pacote (recomendação) | Visão de atenção |
| DB-09 | 07 | Estrutura do pacote + formatos; regra `export_policy` | **Confirmada** | Teste externo (recomendação, não bloqueante) | Execução assistida |
| DB-10 | 08 | Uma empresa, individual, Owner; acumulação controlada de papéis | **Confirmada** (DEC-F0-FINAL-05) | — (resolvida) | Auth/isolamento |
| DB-11 | 09 | Stack greenfield; Django Auth; filesystem/S3; requisitos mínimos de deploy | **Confirmada** | Plataforma concreta em MVP-20 (DEC-F0-FINAL-02, não bloqueante) | Fundação/operação |
| DB-12 | 10 | Checklist de segurança mínima; `export_policy` | **Confirmada** | — (resolvida) | Segurança/auditoria |
| DB-13 | 11 | Plano do piloto; participante mínimo Aldino Ramos | **Confirmada** (DEC-F0-FINAL-03) | Participantes adicionais opcionais; 2º produto real a seleccionar antes do arranque | Validação do MVP |

Nenhuma decisão permanece meramente "A validar" nem apenas "Adoptada
tacitamente": DB-01 a DB-13 estão **Confirmadas** (com reservas quando aplicável)
pelo fecho formal da Fase 0 (2026-07-12). DB-14 (escopo congelado) é a decisão
deste artefacto (§11), **Confirmada** com a saída da fase (§17).

## 6. Revisão cruzada

Coerência verificada entre: segmento↔caso de uso; fluxo↔modelo funcional;
entidades↔estados; ficha↔regras de atenção; estados↔regras de atenção; fonte de
verdade↔modelo funcional; pacote de contexto↔segurança; modelo de
utilizadores↔isolamento; stack↔segurança; piloto↔tese do MVP; critérios do
piloto↔métricas; limites funcionais↔escopo. A cadeia é globalmente coerente
(os artefactos foram construídos em encadeamento). Incoerências residuais em §7.

## 7. Incoerências

Todas de severidade baixa/média, **não bloqueantes**, e **resolvidas** pelo
fecho formal da Fase 0 (2026-07-12).

| ID | Artefactos | Descrição | Impacto | Severidade | Resolução | Estado |
|---|---|---|---|---|---|---|
| INC-01 | 03, 08 | O papel "Revisor/Aprovador" das transições (03) e o MVP individual só-Owner (08): o Owner acumula os papéis funcionais no MVP | Nenhum funcional; clarificação | Baixa | **DEC-F0-FINAL-05**: acumulação controlada de Owner/Operador/Revisor confirmada, com responsabilidades funcionalmente separadas e auditadas (artefacto 08, §2 D-08-04) | **Resolvida** |
| INC-02 | 06, 03 | R-AT-02 ("decisão pendente") depende de pendência de tipo "decisão", mas os valores de "tipo de pendência" não foram enumerados em F0-B05 | Regra de atenção sem tipo formal | Média | **DEC-F0-FINAL-07**: enumeração mínima de 5 tipos de pendência adoptada (`action`, `review`, `validation`, `obligation`, `decision_follow_up`); R-AT-02 usa `decision_follow_up` (artefacto 02 §6.2; artefacto 03 §2.4; artefacto 06 §2) | **Resolvida** |
| INC-03 | 06, 10, 02, 05 | Marcadores "desactualizado" (06) e "não-exportável" (10) são atributos do documento não presentes no modelo funcional (02/03) nem na fronteira (05) | Completude do modelo de dados | Média | **DEC-F0-FINAL-08**: campos estruturados `is_outdated` (boolean) e `export_policy` (`allowed`\|`confirm`\|`denied`) adoptados, fonte oficial BD, incorporados na fronteira BD/Markdown (artefacto 05 §2), nas regras de atenção (artefacto 06) e no pacote de contexto (artefacto 07, R-PC-05) | **Resolvida** |
| INC-04 | 02 | Colocação do passo C4 "definir função" (config única vs por execução) em aberto | Detalhe de fluxo | Baixa | **DEC-F0-FINAL-06**: função configurada previamente (configuração inicial/manutenção); execução referencia função existente com snapshot das instruções; não faz parte do ciclo recorrente (artefacto 02, C4 e E2) | **Resolvida** |

Nenhuma incoerência era estrutural; todas foram fechadas por decisão explícita do operador.

## 8. Avaliação dos critérios de saída

| # | Critério | Estado | Evidência | Lacuna / acção | Bloqueante |
|---|---|---|---|---|---|
| 1 | Caso de uso principal | Cumprido | 01 (D-03) | — | — |
| 2 | Fluxo funcional fechado | Cumprido | 02 (§2) | — | — |
| 3 | Entidades e estados | Cumprido | 02 (§6), 03 | INC-02/03 resolvidas | — |
| 4 | Divisão BD/Markdown | Cumprido | 05 | — | — |
| 5 | Ficha mínima fechada **e testada** | **Cumprido** | 04 (§7.1, teste real com VentureOps AI, 2026-07-12) | — (resolvida, DEC-F0-FINAL-04) | — |
| 6 | Regras de atenção | Cumprido | 06 | INC-02/03 resolvidas | — |
| 7 | Pacote de contexto testado | Cumprido | 07 (auto-teste com evidência) | Confirmação externa (recomendação, não bloqueante) | Não |
| 8 | Modelo de utilizadores/empresas | Cumprido | 08 | — | — |
| 9 | Stack e padrões | **Cumprido** (requisitos mínimos) | 09 (levantamento feito; requisitos mínimos de deploy vigentes) | Plataforma concreta transferida para MVP-20 (DEC-F0-FINAL-02, não bloqueante) | — |
| 10 | Requisitos mínimos de segurança | Cumprido | 10 | — | — |
| 11 | Piloto preparado **com participantes identificados** | **Cumprido** (mínimo) | 11 (§2.1, Aldino Ramos confirmado, DEC-F0-FINAL-03) | Participantes adicionais (perfis B/C) permanecem opcionais | — |
| 12 | Escopo do MVP congelado | **Cumprido** | §11 (Confirmado, DB-14) | — | — |
| 13 | Backlog do MVP escrevível sem decisões estruturais em aberto | **Cumprido** | Decisões DB-01..14 Confirmadas | Nenhuma decisão estrutural em aberto | — |

Todos os 13 critérios estão **Cumpridos**. Nenhum foi declarado cumprido sem
evidência. Reservas remanescentes (não bloqueantes, listadas em §9): confirmação
do pacote com modelo externo, plataforma concreta de deploy (MVP-20), execução
efectiva do piloto.

## 9. Pendências materiais

Três pendências identificadas em F0-P05-PR05 foram fechadas no fecho formal da
Fase 0 (2026-07-12). Registo preservado para rastreabilidade; permanecem apenas
as reservas de §9.4.

### 9.1. Teste da ficha com produto real (critério 5) — Resolvida
- Produto real fornecido pelo operador: **VentureOps AI** (DEC-F0-FINAL-04).
- Teste executado e registado em `04_ficha_administrativa_produto.md`, §7.1; sem lacuna material.
- **F0-B07 concluído.**

### 9.2. Participantes do piloto (critério 11) — Resolvida (mínimo)
- Participante mínimo confirmado: **Aldino Ramos**, fundador técnico e operador principal (DEC-F0-FINAL-03), registado em `11_plano_piloto.md`, §2.1.
- Participantes adicionais (perfis B/C) **permanecem opcionais**, não inventados; o piloto pode arrancar com um único participante.
- Pendência residual (não bloqueante): segundo produto real a seleccionar antes do arranque efectivo do piloto.

### 9.3. Plataforma de deploy (critério 9 / F0-B11) — Resolvida (transferida)
- Requisitos mínimos definidos e vigentes (09 §3.3; 10 §11-A): containers, PostgreSQL, armazenamento persistente, TLS, gestão segura de segredos, backups, health checks, migrações controladas, rollback, logs estruturados.
- **Selecção da plataforma concreta transferida para `MVP-20 — Operação mínima do MVP`** (DEC-F0-FINAL-02), a decidir antes da implementação e validação operacional desse item.
- Não considerada identificada; não inventada.

### 9.4. Reservas remanescentes (não bloqueantes)

1. Confirmação do pacote de contexto com um **modelo de IA externo** distinto do auto-teste (artefacto 07, P-06) — recomendação, não obrigação de fecho.
2. **Execução efectiva do piloto** com o participante mínimo confirmado — actividade da Fase 1/preparação, não desta fase.
3. **Implementação e validação dos controlos** de segurança (artefacto 10) — verificação na Fase 1, por desenho (os controlos são requisitos, não código).
4. **Selecção da plataforma concreta de deploy** antes de `MVP-20` (9.3).

Nenhuma destas reservas impede a decomposição segura do MVP.

## 10. Riscos residuais

RR-01, RR-02 e RR-04 foram fechados pelas resoluções de §7 e §9. Permanecem,
**formalmente aceites** por DEC-20260712-04:

| ID | Risco | Origem | Tratamento |
|---|---|---|---|
| RR-03 | Plataforma de deploy/TLS/backup concretos por seleccionar em MVP-20 | 09/10 | **Aceite formalmente**; requisitos mínimos vigentes; selecção antes de MVP-20 (9.3) |
| RR-05 | Robustez anti-injecção varia entre modelos de IA | 07/10 | Mitigado; validação humana obrigatória (SEC-HUM-01..06); confirmação com modelo externo recomendada |
| RR-06 | Execução do piloto ainda não realizada | 11 | **Aceite formalmente**; actividade de preparação/Fase 1, com participante mínimo já confirmado |
| RR-07 | Controlos de segurança são requisitos, ainda não implementados | 10 | **Aceite formalmente**; eficácia verificável apenas na Fase 1, por desenho da Fase 0 (análise, não implementação) |

Histórico (resolvidos): ~~RR-01~~ (usabilidade da ficha — 9.1); ~~RR-02~~
(participantes — 9.2); ~~RR-04~~ (completude do modelo de dados — INC-02/03).

Nenhum risco é crítico nem estrutural.

## 11. Escopo congelado do MVP (DB-14)

Estado: **Confirmado** (DEC-20260712-04). Consolida os limites preliminares (02
§3) e as decisões Confirmadas (§5). Inclui os fechos de INC-02/03 (tipos de
pendência; campos `is_outdated`/`export_policy`).

### 11.1. Incluído
Uma empresa; utilizador individual (Owner); vários produtos; ficha administrativa
(5 campos); documentos Markdown versionados; decisões; pendências mínimas; funções
organizacionais; execuções assistidas manuais; pacote de contexto; registo e
validação humana de resultados; visão de atenção (5 regras); auditoria (21
eventos); exportação; isolamento por empresa; segurança mínima (checklist F0-B12).

### 11.2. Excluído do MVP (fase posterior — adiado)
Multiutilizador e convites; permissões avançadas; ligação **automática** a IA
local/externa; sincronização Git; pesquisa (textual/semântica); notificações;
templates; revisões periódicas; histórico consolidado e comparação de versões;
classificação avançada de documentos; API controlada; indicadores de portefólio.

### 11.3. Opcional no MVP
IA local **manual** e limitada; importação inicial de Markdown; referência
externa por URL. (Entram só se não comprometerem prazo, segurança ou foco.)

### 11.4. Descartado do núcleo
Gestão completa de projectos; ERP; CRM; agentes autónomos e multiagente;
marketplace; alojamento de modelos; construtor de workflows; chat genérico;
avatares/personalidades; app móvel nativa; automações sem aprovação.

### 11.5. Confirmação de exclusões obrigatórias
**Não** entram no MVP: agentes autónomos; integração directa obrigatória com IA;
Git bidireccional; pesquisa semântica; gestão completa de projectos;
multiutilizador avançado; ERP; CRM; microserviços; filas; Kafka; Kubernetes
dedicado. ✔

## 12. Controlo de alterações

Qualquer alteração a este escopo congelado segue o controlo de alterações da
baseline (`05_backlog_macro.md`): motivo, benefício, impacto, dependências, risco,
fase afectada, itens substituídos/adicionados e decisão. Alterações estruturais
exigem decisão registada em `02_log_decisoes_execucao.md`.

## 13. Decisão de saída (confirmada)

**Opção B — Avançar para a Fase 1 com riscos formalmente aceites (com
reservas), CONFIRMADA** por DEC-F0-FINAL-01 / DEC-20260712-04 (2026-07-12):

> A Fase 0 está concluída com reservas e fica autorizada a decomposição
> controlada da Fase 1/MVP.

Justificação: não existe incoerência estrutural nem risco crítico; as decisões
bloqueadoras DB-01 a DB-13 estão **Confirmadas**; as pendências materiais
identificadas em F0-P05-PR05 foram resolvidas ou transferidas para destino
identificado (§9); o escopo do MVP está congelado (DB-14, §11); as reservas
restantes (§9.4) não comprometem a arquitectura nem a decomposição do MVP.

- **Critérios cumpridos:** 1 a 13 (todos — §8).
- **Riscos formalmente aceites:** RR-03, RR-05, RR-06, RR-07 (§10).
- **Estado da decisão:** **Confirmada** (DEC-20260712-04), substituindo a proposta em DEC-20260712-03.

## 14. Condições da decisão (cumpridas)

1. ~~Reclassificar F0-B11 (deploy)~~ — **Cumprida**: requisitos mínimos definidos; plataforma concreta transferida para `MVP-20` (DEC-F0-FINAL-02).
2. ~~Transferir/executar o teste da ficha (F0-B07)~~ — **Cumprida**: executado com VentureOps AI (DEC-F0-FINAL-04).
3. ~~Transferir a identificação nominal dos participantes~~ — **Cumprida**: participante mínimo confirmado (DEC-F0-FINAL-03).
4. A Fase 0 está **concluída com reservas** (não "pronta para transição" — estado final).
5. A regra funcional de validação humana de resultados de IA no produto **mantém-se obrigatória**, inalterada por esta decisão.

## 15. Próximo passo

- Decomposição controlada do backlog do MVP (Fase 1), usando o escopo congelado (§11) — **não iniciada nesta iteração**.
- Antes da implementação e validação operacional de `MVP-20`: seleccionar a plataforma concreta de deploy.
- Antes ou durante a preparação do piloto: seleccionar um segundo produto real; executar o piloto.

## 16. Parecer final

A Fase 0 está **concluída com reservas**. Todas as decisões bloqueadoras
(DB-01 a DB-14) estão confirmadas; todas as incoerências identificadas (INC-01 a
INC-04) foram resolvidas; todos os 13 critérios de saída estão cumpridos. As
reservas remanescentes (§9.4) são de implementação e operação, próprias da Fase
1, não estruturais. A pipeline F0-P05 está concluída; **a Fase 0 está
formalmente encerrada com reservas**, e a decomposição controlada da Fase
1/MVP fica autorizada.

## 17. Fecho formal aplicado (2026-07-12)

Esta secção regista a aplicação das decisões do operador que fecham a Fase 0,
sem reabrir as secções 1–16 (preservadas com as marcações de resolução acima).

* **DEC-F0-FINAL-01** — Fase 0 concluída com reservas; decomposição da Fase 1/MVP autorizada.
* **DEC-F0-FINAL-02** — Plataforma concreta de deploy transferida para `MVP-20`; requisitos mínimos vigentes.
* **DEC-F0-FINAL-03** — Participante mínimo do piloto: Aldino Ramos.
* **DEC-F0-FINAL-04** — Produto real do teste da ficha: VentureOps AI.
* **DEC-F0-FINAL-05** — Acumulação controlada de papéis (Owner/Operador/Revisor) no MVP individual; resolve INC-01.
* **DEC-F0-FINAL-06** — Função organizacional configurada previamente; execução referencia função existente; resolve INC-04.
* **DEC-F0-FINAL-07** — Tipos mínimos de pendência (`action`, `review`, `validation`, `obligation`, `decision_follow_up`); resolve INC-02.
* **DEC-F0-FINAL-08** — Marcadores documentais estruturados `is_outdated` e `export_policy`, fonte BD; resolve INC-03.

Registo formal em `docs/gestao/02_log_decisoes_execucao.md` (DEC-20260712-04).
