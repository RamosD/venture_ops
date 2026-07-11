# Backlog detalhado — Fase 0: Preparação e alinhamento

## 1. Identificação e objectivo da fase

**Fase:** F0 — Preparação e alinhamento
**Baseline de referência:** `docs/gestao/01_baseline/05_backlog_macro.md` (itens F0-01 a F0-14)
**Estado da fase:** Pendente

**Objectivo:** fechar as decisões que bloqueiam a implementação segura do MVP,
produzindo uma especificação funcional e técnica mínima que permita gerar o
backlog do MVP sem reabrir decisões estruturais. A fase produz análise e
decisões, não código.

Esta fase deve reduzir ambiguidade, não produzir documentação excessiva
(roadmap, §3.1).

## 2. Escopo incluído

* fecho do segmento inicial e do caso de uso principal;
* fecho do fluxo funcional ponta a ponta do MVP;
* confirmação do modelo funcional mínimo (entidades e relações);
* definição de estados e transições das entidades;
* definição da fronteira entre base de dados e Markdown;
* definição da ficha administrativa mínima do produto;
* definição das regras da visão de atenção;
* definição e teste manual do pacote de contexto;
* decisão do modelo de utilizadores e empresas do MVP;
* levantamento e confirmação de stack, repositório e padrões;
* definição dos requisitos mínimos de segurança;
* preparação do plano de piloto;
* congelamento formal do escopo do MVP.

## 3. Escopo excluído

* implementação de frontend, backend ou infraestrutura;
* inicialização de frameworks, repositórios de código ou CI/CD;
* backlog técnico detalhado do MVP (pertence à Fase 1);
* modelos de dados ao nível de migração ou esquema físico;
* protótipos funcionais além de esboços de fluxo, se necessários;
* integrações com IA local, Git ou ferramentas externas;
* decisões de fases posteriores (V1-*, EV-*);
* alteração da visão, arquitectura ou roadmap aprovados.

## 4. Decisões bloqueadoras

Decisões que têm de ser fechadas nesta fase (fontes: roadmap §3.3; arquitectura
§17). Todas estão por fechar — estado **A validar**.

| # | Decisão | Item que a trata | Estado |
|---|---|---|---|
| DB-01 | Segmento inicial exacto (dimensão da equipa, n.º de produtos) | F0-B01 | A validar |
| DB-02 | Caso de uso principal do MVP | F0-B02 | A validar |
| DB-03 | Fluxo funcional ponta a ponta | F0-B03 | A validar |
| DB-04 | Entidades mínimas e relações | F0-B04 | A validar |
| DB-05 | Estados oficiais de produto, documento, decisão, pendência, função, execução e revisão | F0-B05 | A validar |
| DB-06 | Fronteira BD/Markdown, política de versões e regras de actualização | F0-B06 | A validar |
| DB-07 | Campos obrigatórios da ficha administrativa do produto | F0-B07 | A validar |
| DB-08 | Regras determinísticas da visão de atenção | F0-B08 | A validar |
| DB-09 | Formato do pacote de contexto e formato de importação de resultados | F0-B09 | A validar |
| DB-10 | Uma ou várias empresas por conta; individual ou multiutilizador; papéis mínimos | F0-B10 | A validar |
| DB-11 | Stack efectiva, reutilização de autenticação, armazenamento de ficheiros no piloto, plataforma de deploy | F0-B11 | A validar |
| DB-12 | Nível de auditoria e controlos de segurança não adiáveis | F0-B12 | A validar |
| DB-13 | Utilizadores piloto, dados e critérios de sucesso | F0-B13 | A validar |
| DB-14 | Lista final de escopo congelado do MVP | F0-B14 | A validar |

## 5. Itens detalhados da Fase 0

Convenções comuns a todos os itens (não repetidas item a item):

* **Estado inicial:** Pendente.
* **Validação humana:** obrigatória — todos os itens fecham decisões e o
  respectivo artefacto só é considerado aprovado após revisão humana registada.
* **Inputs comuns:** `02_visao_do_produto.md`, `03_arquitetura.md`,
  `04_roadmap_faseado.md`, `05_backlog_macro.md` (referenciados por secção em
  cada item; não reler integralmente).

---

### F0-B01 — Definir o segmento inicial

* **Rastreia:** F0-01.
* **Objectivo:** fixar o primeiro perfil de cliente e utilizador do MVP.
* **Problema/decisão:** DB-01 — a visão deixa **A validar** a dimensão exacta da equipa e o número mínimo de produtos (visão §3.1).
* **Inputs:** visão §2–§3 (problema, públicos), §6.3 (diferenciais por validar).
* **Actividades:** caracterizar o segmento prioritário; delimitar o que fica explicitamente fora do segmento inicial; identificar 2–3 perfis reais candidatos a piloto.
* **Resultado esperado:** segmento inicial documentado e distinguido dos públicos futuros.
* **Artefacto:** `artefactos/01_segmento_e_caso_uso.md` (secção de segmento).
* **Critérios de aceitação:** perfil descreve dimensão de equipa, n.º de produtos, maturidade técnica e uso de IA; exclusões explícitas; pelo menos um perfil real identificável para o piloto.
* **Dependências:** visão de produto aprovada (existe).
* **Riscos:** segmento demasiado amplo diluir o MVP.

### F0-B02 — Definir o caso de uso principal

* **Rastreia:** F0-02.
* **Objectivo:** seleccionar o fluxo que demonstrará valor no MVP.
* **Problema/decisão:** DB-02 — a visão lista 10 casos de uso (visão §7) sem eleger o principal; o parecer da visão exige fechar "o fluxo central que gera valor na primeira semana".
* **Inputs:** visão §7, §15.1 (tese do MVP); F0-B01.
* **Actividades:** avaliar os casos de uso da visão contra a tese do MVP; seleccionar e descrever o caso de uso principal (situação, actor, necessidade, execução, resultado, valor esperado).
* **Resultado esperado:** caso de uso completo, utilizável como referência de validação do piloto.
* **Artefacto:** `artefactos/01_segmento_e_caso_uso.md` (secção de caso de uso).
* **Critérios de aceitação:** um único caso de uso principal eleito com justificação; descrição cobre os seis elementos exigidos pela baseline (F0-02); relação explícita com a tese do MVP.
* **Dependências:** F0-B01.
* **Riscos:** escolher um caso de uso que dependa de integração automática com IA (fora do MVP).

### F0-B03 — Fechar o fluxo funcional do MVP

* **Rastreia:** F0-03.
* **Objectivo:** definir o ciclo ponta a ponta do utilizador no MVP.
* **Problema/decisão:** DB-03 — o fluxo de nove passos do roadmap (§3.2) precisa de ser confirmado passo a passo sem etapas críticas em aberto.
* **Inputs:** roadmap §3.2 (fluxo proposto); arquitectura §1 (fluxo geral); F0-B02.
* **Actividades:** percorrer o fluxo proposto passo a passo; identificar pontos ambíguos ou etapas em falta; confirmar entradas, saídas e actor de cada passo.
* **Resultado esperado:** fluxo aprovado, sem etapas críticas em aberto.
* **Artefacto:** `artefactos/02_fluxo_e_modelo_funcional.md` (secção de fluxo).
* **Critérios de aceitação:** cada passo tem actor, entrada e saída definidos; nenhuma etapa depende de funcionalidade excluída do MVP; ambiguidades resolvidas ou registadas como decisão.
* **Dependências:** F0-B02.
* **Riscos:** fluxo crescer para além do ciclo mínimo de validação.

### F0-B04 — Fechar o modelo funcional mínimo

* **Rastreia:** F0-04.
* **Objectivo:** confirmar as entidades necessárias ao MVP e as suas relações de alto nível.
* **Problema/decisão:** DB-04 — as dez entidades do roadmap (§3.2) e o modelo de dados indicativo da arquitectura (§6.2–6.3) precisam de confirmação funcional (sem esquema físico).
* **Inputs:** roadmap §3.2; arquitectura §6.2–§6.3; F0-B03.
* **Actividades:** validar cada entidade contra o fluxo fechado; produzir glossário funcional; confirmar relações de alto nível; identificar entidades dispensáveis no MVP.
* **Resultado esperado:** glossário funcional e relações de alto nível aprovados.
* **Artefacto:** `artefactos/02_fluxo_e_modelo_funcional.md` (secção de modelo funcional).
* **Critérios de aceitação:** todas as entidades usadas no fluxo estão definidas no glossário; nenhuma entidade sem uso no fluxo do MVP; relações coerentes com a arquitectura §6.3.
* **Dependências:** F0-B03.
* **Riscos:** detalhar o modelo ao nível de campos de implementação (pertence à Fase 1).

### F0-B05 — Definir estados e transições

* **Rastreia:** F0-05.
* **Objectivo:** remover ambiguidade do ciclo de vida das entidades.
* **Problema/decisão:** DB-05 — estados oficiais por entidade estão em aberto (arquitectura §17, questões 4–5).
* **Inputs:** F0-B04; arquitectura §6.2 (campos `status` indicativos).
* **Actividades:** definir estados mínimos por entidade (produto, documento, decisão, pendência, função, execução, revisão); definir transições válidas e quem as pode executar; verificar cobertura pelo fluxo.
* **Resultado esperado:** matriz de estados e transições válidas aprovada.
* **Artefacto:** `artefactos/03_estados_e_transicoes.md`.
* **Critérios de aceitação:** cada entidade tem estados enumerados e transições explícitas; nenhum passo do fluxo exige um estado inexistente; estados mínimos (sem estados especulativos).
* **Dependências:** F0-B04.
* **Riscos:** máquinas de estados demasiado detalhadas (risco identificado no roadmap §3.6).

### F0-B06 — Definir a fronteira entre BD e Markdown

* **Rastreia:** F0-06.
* **Objectivo:** eliminar dupla fonte de verdade entre dados estruturados e documentos.
* **Problema/decisão:** DB-06 — divisão oficial BD/Markdown, política de versões e regras de actualização em aberto (visão §14.4; arquitectura §17, questões 10–11).
* **Inputs:** arquitectura §2.3, §6.1, §15.2; princípios de produto 5–7 (visão §12).
* **Actividades:** classificar cada tipo de informação por fonte oficial; definir metadados duplicados apenas para identificação; definir política de versões documentais e regras de actualização.
* **Resultado esperado:** matriz de fonte de verdade aprovada para cada tipo de informação.
* **Artefacto:** `artefactos/05_fonte_de_verdade_bd_markdown.md`.
* **Critérios de aceitação:** cada tipo de informação do modelo funcional tem exactamente uma fonte oficial; regras de versão definidas (quando se cria versão); nenhum valor operacional concorrente entre BD e Markdown (RT-04).
* **Dependências:** F0-B04.
* **Riscos:** deixar tipos de informação sem classificação, reabrindo a decisão durante o MVP.

### F0-B07 — Definir a ficha administrativa mínima do produto

* **Rastreia:** F0-07.
* **Objectivo:** limitar os dados obrigatórios de cada produto.
* **Problema/decisão:** DB-07 — campos obrigatórios da ficha em aberto (parecer da visão, questão 2; arquitectura §17, questão 6).
* **Inputs:** visão §8.1 (ficha administrativa); arquitectura §6.2 (Product); F0-B02, F0-B04.
* **Actividades:** distinguir campos obrigatórios, opcionais e adiados; validar a ficha preenchendo-a com um produto real; confirmar que a ficha suporta o caso de uso principal.
* **Resultado esperado:** ficha mínima aprovada e testada num produto real.
* **Artefacto:** `artefactos/04_ficha_administrativa_produto.md`.
* **Critérios de aceitação:** lista fechada de campos obrigatórios; ficha preenchida com pelo menos um produto real como evidência; esforço de preenchimento compatível com o princípio 15 da visão ("o fundador não deve servir a ferramenta").
* **Dependências:** F0-B02, F0-B04.
* **Riscos:** ficha demasiado extensa desencorajar manutenção.

### F0-B08 — Definir as regras da visão de atenção

* **Rastreia:** F0-08.
* **Objectivo:** determinar como identificar assuntos que exigem intervenção.
* **Problema/decisão:** DB-08 — regras de atenção em aberto (parecer do roadmap, ajuste 3; arquitectura §17, questão 7).
* **Inputs:** roadmap §3.2 (exemplos de regras); visão §7.10; F0-B05, F0-B07.
* **Actividades:** definir regras determinísticas e explicáveis por sinal (produto sem revisão, decisão pendente, pendência vencida, resultado por validar, documento sinalizado); definir parâmetros (ex.: prazo de revisão); confirmar cálculo simples (arquitectura §15.7: calculadas, não persistidas).
* **Resultado esperado:** regras determinísticas, explicáveis e aprovadas.
* **Artefacto:** `artefactos/06_regras_visao_atencao.md`.
* **Critérios de aceitação:** cada regra tem condição objectiva e motivo apresentável ao utilizador; regras dependem apenas de dados definidos em F0-B05/F0-B07; parâmetros com valores iniciais decididos.
* **Dependências:** F0-B05, F0-B07.
* **Riscos:** regras arbitrárias gerarem ruído e descredibilizarem o painel.

### F0-B09 — Definir o pacote de contexto

* **Rastreia:** F0-09.
* **Objectivo:** padronizar a preparação de trabalho para IA e a importação de resultados.
* **Problema/decisão:** DB-09 — formato do pacote e do resultado em aberto (arquitectura §17, questões 12–14).
* **Inputs:** visão §7.6–§7.7; arquitectura §8.3 (fluxo manual), §11.10 (prompt injection); F0-B03, F0-B06.
* **Actividades:** definir a estrutura do pacote (objectivo, função, instruções, produto, documentos, restrições, formato esperado); definir formato de exportação e de importação do resultado; **testar manualmente** o pacote com uma IA externa ou local num cenário real.
* **Resultado esperado:** modelo de pacote produzido e testado manualmente.
* **Artefacto:** `artefactos/07_pacote_contexto_ia.md`.
* **Critérios de aceitação:** estrutura cobre os sete elementos da baseline (F0-09); um teste manual executado com evidência registada (pacote usado e resultado obtido); fontes identificadas no pacote (arquitectura §11.10).
* **Dependências:** F0-B03, F0-B06.
* **Riscos:** formato optimizado para um único modelo de IA; exposição de dados sensíveis no teste.

### F0-B10 — Definir o modelo de utilizadores e empresas

* **Rastreia:** F0-10.
* **Objectivo:** fechar o nível de colaboração do MVP.
* **Problema/decisão:** DB-10 — uma ou várias empresas por conta, individual vs multiutilizador, papéis mínimos (arquitectura §17, questões 1–3; roadmap §3.3).
* **Inputs:** arquitectura §7.2 (papéis propostos); roadmap §4.2 (uma empresa activa); visão §3.5–§3.6; F0-B01.
* **Actividades:** decidir empresas por conta no MVP; decidir individual vs multiutilizador; confirmar papéis mínimos e preparação de memberships futuras.
* **Resultado esperado:** decisão formal registada.
* **Artefacto:** `artefactos/08_modelo_utilizadores_empresas.md`.
* **Critérios de aceitação:** as três decisões fechadas com justificação; coerência com o segmento (F0-B01) e com a estrutura preparada para multiempresa (roadmap §4.2); impacto em isolamento identificado para F0-B12.
* **Dependências:** F0-B01.
* **Riscos:** decidir por excesso (multiutilizador completo) e inflacionar o MVP.

### F0-B11 — Confirmar stack, repositório e padrões

* **Rastreia:** F0-11.
* **Objectivo:** garantir alinhamento com o ambiente real de desenvolvimento.
* **Problema/decisão:** DB-11 — stack e convenções efectivas do repositório, reutilização de autenticação, armazenamento no piloto e plataforma de deploy (arquitectura §17, questões 16–17, 24–25).
* **Inputs:** arquitectura §1 (decisões assumidas), §2.10, §7.1, §13.
* **Actividades:** levantar o estado real do ambiente (repositório, stack existente, autenticação, CI/CD, armazenamento, deploy); confrontar com as decisões assumidas na arquitectura; registar desvios e confirmações.
* **Resultado esperado:** levantamento técnico aprovado, sem pressupostos críticos pendentes.
* **Artefacto:** `artefactos/09_stack_repositorio_padroes.md`.
* **Critérios de aceitação:** cada decisão assumida da arquitectura (§1) confirmada ou marcada com desvio justificado; decisão sobre autenticação (reutilizar vs Django Auth) fechada; armazenamento do piloto (filesystem vs S3) decidido; plataforma de deploy identificada.
* **Dependências:** arquitectura aprovada (existe). Independente dos itens funcionais — pode decorrer em paralelo.
* **Riscos:** assumir infraestrutura que não existe; nota: o repositório actual contém apenas documentação, o levantamento deve reflectir isso sem inventar stack.

### F0-B12 — Definir requisitos mínimos de segurança

* **Rastreia:** F0-12.
* **Objectivo:** estabelecer os controlos de segurança não adiáveis do MVP.
* **Problema/decisão:** DB-12 — nível de auditoria e checklist mínimo (roadmap §3.3; arquitectura §11, §17 questões 19–23).
* **Inputs:** arquitectura §11 (segurança), §7 (auth/autorização); requisitos transversais RT-01, RT-02, RT-05, RT-07, RT-08; F0-B10, F0-B11.
* **Actividades:** derivar o checklist mínimo (isolamento, autorização, protecção documental, auditoria, segredos, exportação); definir nível de auditoria do MVP; definir que informação pode ser enviada a serviços externos de IA; registar requisitos de retenção/eliminação conhecidos e marcar os restantes como A validar por mercado.
* **Resultado esperado:** checklist de segurança mínima aprovado.
* **Artefacto:** `artefactos/10_requisitos_seguranca_mvp.md`.
* **Critérios de aceitação:** checklist cobre os seis domínios da baseline (F0-12); cada controlo é verificável na Fase 1; lista de eventos auditáveis fechada; política de envio de dados a IA externa definida.
* **Dependências:** F0-B10, F0-B11.
* **Riscos:** checklist genérico e não verificável; adiar controlos que a baseline declara não adiáveis.

### F0-B13 — Preparar o piloto

* **Rastreia:** F0-13.
* **Objectivo:** definir como o MVP será validado com utilizadores e produtos reais.
* **Problema/decisão:** DB-13 — utilizadores piloto, dados, actividades, feedback e critérios de sucesso (roadmap §3.2 e §3.3; visão §11 — metas "A definir após piloto").
* **Inputs:** visão §11 (métricas), §15.1 (tese); roadmap §4.7 (validações do piloto); F0-B01, F0-B02.
* **Actividades:** identificar participantes concretos; definir produtos reais a registar; definir actividades e duração; definir critérios de sucesso e de feedback mensuráveis; delimitar o que fica fora do piloto.
* **Resultado esperado:** plano de piloto aprovado e participantes identificados.
* **Artefacto:** `artefactos/11_plano_piloto.md`.
* **Critérios de aceitação:** pelo menos um utilizador piloto identificado nominalmente; produtos reais listados; critérios de sucesso ligados à tese do MVP e mensuráveis; validações do roadmap §4.7 mapeadas para actividades do piloto.
* **Dependências:** F0-B01, F0-B02.
* **Riscos:** critérios de sucesso vagos que impeçam a decisão de fecho do MVP.

### F0-B14 — Congelar o escopo do MVP

* **Rastreia:** F0-14.
* **Objectivo:** impedir entrada de funcionalidades não essenciais e fechar a Fase 0.
* **Problema/decisão:** DB-14 — lista final de itens incluídos, excluídos, opcionais e adiados; decisão formal de saída da fase.
* **Inputs:** todos os artefactos anteriores; visão §9, §15; roadmap §4.3; baseline OUT-01 a OUT-16.
* **Actividades:** consolidar decisões dos itens F0-B01 a F0-B13; produzir a lista final de escopo (incluído/excluído/opcional/adiado); verificar os critérios de saída da Fase 0; registar a decisão formal de avanço (ou não) para a Fase 1.
* **Resultado esperado:** baseline do MVP aprovada e sujeita a controlo de mudança.
* **Artefacto:** `artefactos/12_decisao_saida_fase_0.md`.
* **Critérios de aceitação:** todos os critérios de saída da Fase 0 (secção 8) verificados com referência ao artefacto que os evidencia; lista de escopo congelada sem itens "A validar" pendentes; decisão de saída registada no log de decisões (`docs/gestao/02_log_decisoes_execucao.md`).
* **Dependências:** F0-B01 a F0-B13 (todos).
* **Riscos:** congelar escopo com decisões ainda abertas, transferindo ambiguidade para o MVP.

## 6. Dependências

### Externas à fase

* baseline aprovada (visão, arquitectura, roadmap, backlog macro) — existe;
* disponibilidade de um responsável funcional para validar decisões — A validar;
* disponibilidade de pelo menos um cenário real de utilização — A validar;
* acesso ao ambiente/repositório real para o levantamento de F0-B11 — A validar.

### Internas (grafo resumido)

```text
F0-B01 ─► F0-B02 ─► F0-B03 ─► F0-B04 ─► F0-B05 ─┐
   │                             │              ├─► F0-B08
   │                             ├─► F0-B06 ─┐  │
   │                             └─► F0-B07 ─┼──┘
   │        (F0-B03, F0-B06) ────────────────┴─► F0-B09
   ├─► F0-B10 ─┐
   └─► F0-B13  ├─► F0-B12
F0-B11 (paralelo) ─┘
Todos ─► F0-B14
```

## 7. Riscos da fase

| ID | Risco | Mitigação | Origem |
|---|---|---|---|
| R-01 | Análise prolongada sem avançar para validação prática | Limitar a fase às 14 decisões bloqueadoras; nenhum artefacto novo fora dos 12 previstos | Roadmap §3.6 |
| R-02 | Escopo reabrir continuamente | Lista formal de itens fora do MVP em F0-B14, sujeita a controlo de mudança | Roadmap §3.6 |
| R-03 | Estados e entidades demasiado detalhados | Manter apenas campos e estados necessários ao fluxo piloto | Roadmap §3.6 |
| R-04 | Decisões tomadas sem validação humana registada | Todos os itens exigem validação humana antes de "Validado" | Guia de gestão |
| R-05 | Levantamento técnico (F0-B11) assumir stack inexistente | Levantar apenas o que existe; desvios face à arquitectura registados como decisão | Arquitectura §2.10 |
| R-06 | Teste do pacote de contexto (F0-B09) expor informação sensível | Usar conteúdo não sensível ou fictício controlado no teste manual | Arquitectura §11.10 |

## 8. Critérios de saída da Fase 0

A fase termina quando (baseline + roadmap §3.7):

1. o caso de uso principal está aprovado (F0-B02);
2. o fluxo funcional está fechado (F0-B03);
3. as entidades e estados estão definidos (F0-B04, F0-B05);
4. a divisão BD/Markdown está aprovada (F0-B06);
5. a ficha mínima de produto está fechada e testada (F0-B07);
6. as regras de atenção estão definidas (F0-B08);
7. o pacote de contexto está testado manualmente (F0-B09);
8. o modelo de utilizadores e empresas está decidido (F0-B10);
9. a stack e os padrões estão confirmados (F0-B11);
10. o checklist de segurança mínima está aprovado (F0-B12);
11. o piloto está preparado com participantes identificados (F0-B13);
12. o escopo do MVP está formalmente congelado (F0-B14);
13. o backlog do MVP pode ser escrito sem decisões estruturais em aberto (roadmap §11.1).

## 9. Artefactos esperados

A criar em `docs/gestao/02_fase_0_preparacao/artefactos/` (previstos, ainda não
criados):

| Artefacto | Itens que o produzem |
|---|---|
| `01_segmento_e_caso_uso.md` | F0-B01, F0-B02 |
| `02_fluxo_e_modelo_funcional.md` | F0-B03, F0-B04 |
| `03_estados_e_transicoes.md` | F0-B05 |
| `04_ficha_administrativa_produto.md` | F0-B07 |
| `05_fonte_de_verdade_bd_markdown.md` | F0-B06 |
| `06_regras_visao_atencao.md` | F0-B08 |
| `07_pacote_contexto_ia.md` | F0-B09 |
| `08_modelo_utilizadores_empresas.md` | F0-B10 |
| `09_stack_repositorio_padroes.md` | F0-B11 |
| `10_requisitos_seguranca_mvp.md` | F0-B12 |
| `11_plano_piloto.md` | F0-B13 |
| `12_decisao_saida_fase_0.md` | F0-B14 |

## 10. Ordem recomendada de execução

1. **F0-B01** → **F0-B02** (segmento e caso de uso — abrem a cadeia funcional);
2. **F0-B11** em paralelo desde o início (levantamento técnico, sem dependências funcionais);
3. **F0-B03** → **F0-B04** (fluxo e modelo funcional);
4. **F0-B05** e **F0-B06** em paralelo (estados; fronteira BD/Markdown);
5. **F0-B07** (ficha do produto) e **F0-B10** (modelo de utilizadores — só depende de F0-B01, pode ser antecipado);
6. **F0-B08** (regras de atenção) e **F0-B09** (pacote de contexto, inclui teste manual);
7. **F0-B12** (segurança — consolida F0-B10 e F0-B11);
8. **F0-B13** (plano de piloto — pode iniciar após F0-B02 e fechar aqui);
9. **F0-B14** (congelamento e decisão de saída — último, exige todos).

## 11. Matriz de rastreabilidade

| Item baseline | Item deste backlog | Artefacto | Evidência de conclusão (baseline) |
|---|---|---|---|
| F0-01 | F0-B01 | `01_segmento_e_caso_uso.md` | Segmento documentado, aprovado e distinguido dos públicos futuros |
| F0-02 | F0-B02 | `01_segmento_e_caso_uso.md` | Caso de uso completo, utilizável como referência de validação |
| F0-03 | F0-B03 | `02_fluxo_e_modelo_funcional.md` | Fluxo aprovado sem etapas críticas em aberto |
| F0-04 | F0-B04 | `02_fluxo_e_modelo_funcional.md` | Glossário funcional e relações aprovados |
| F0-05 | F0-B05 | `03_estados_e_transicoes.md` | Matriz de estados e transições aprovada |
| F0-06 | F0-B06 | `05_fonte_de_verdade_bd_markdown.md` | Matriz de fonte de verdade aprovada |
| F0-07 | F0-B07 | `04_ficha_administrativa_produto.md` | Ficha mínima aprovada e testada num produto real |
| F0-08 | F0-B08 | `06_regras_visao_atencao.md` | Regras determinísticas, explicáveis e aprovadas |
| F0-09 | F0-B09 | `07_pacote_contexto_ia.md` | Modelo de pacote produzido e testado manualmente |
| F0-10 | F0-B10 | `08_modelo_utilizadores_empresas.md` | Decisão formal registada |
| F0-11 | F0-B11 | `09_stack_repositorio_padroes.md` | Levantamento técnico aprovado |
| F0-12 | F0-B12 | `10_requisitos_seguranca_mvp.md` | Checklist de segurança mínima aprovado |
| F0-13 | F0-B13 | `11_plano_piloto.md` | Plano de piloto aprovado e participantes identificados |
| F0-14 | F0-B14 | `12_decisao_saida_fase_0.md` | Baseline do MVP aprovada e sujeita a controlo de mudança |
