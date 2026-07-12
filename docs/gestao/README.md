# Gestão da execução assistida por IA — VentureOps AI

## 1. Objectivo desta área

A pasta:

```text
docs/gestao/
```

organiza, controla e audita a execução assistida por IA durante a implementação do VentureOps AI.

Esta área acompanha pipelines executadas por agentes locais ou assistentes de implementação, como:

* Codex;
* Claude;
* agentes locais;
* outros modelos ou ferramentas de implementação assistida.

A sua função é permitir responder, de forma verificável:

* que trabalho foi solicitado;
* que prompts foram executados;
* que alterações foram realizadas;
* que validações foram executadas;
* que decisões foram tomadas;
* que riscos ou bloqueios surgiram;
* que evidências suportam o resultado;
* qual é o estado actual da execução;
* se a fase seguinte pode avançar.

Esta pasta não substitui a documentação funcional, técnica e operacional final do produto.

A documentação actual e permanente da solução reside em:

```text
docs/produto/
```

---

## 2. Princípio de gestão leve

O registo de gestão e auditoria é obrigatório, mas não constitui a actividade principal da execução.

A IA local deve dedicar o mínimo de contexto e escrita necessário para preservar:

* rastreabilidade;
* verificabilidade;
* continuidade;
* controlo de risco;
* capacidade de auditoria.

Deve evitar:

* repetir a mesma descrição em vários documentos;
* copiar conteúdos integrais dos resultados para os documentos globais;
* reproduzir logs extensos;
* reescrever ficheiros globais completos;
* reler toda a pasta `docs/gestao/` em cada prompt;
* actualizar documentos sem alteração real de estado;
* criar relatórios narrativos desnecessariamente longos.

A regra central é:

> O resultado do prompt contém o detalhe. Os documentos globais contêm apenas estado, índices, decisões, riscos e evidências consolidadas.

---

## 3. Fontes de verdade

Cada tipo de informação possui uma fonte oficial.

| Informação                                   | Fonte de verdade                |
| -------------------------------------------- | ------------------------------- |
| Detalhe da execução de um prompt             | `prompt_XX_resultado.md`        |
| Estado e progresso de uma pipeline           | `01_status_pipelines.md`        |
| Estado executivo global                      | `00_painel_execucao_global.md`  |
| Decisões relevantes de execução              | `02_log_decisoes_execucao.md`   |
| Riscos, bloqueios e dívida técnica           | `03_riscos_bloqueios.md`        |
| Estado das validações globais                | `04_matriz_validacao_global.md` |
| Sequência cronológica de execuções           | `05_diario_execucao_ia.md`      |
| Estado funcional e técnico actual do produto | `docs/produto/`                 |
| Baseline aprovada do produto                 | `docs/gestao/01_baseline/`      |

Os documentos globais não devem duplicar o conteúdo detalhado dos ficheiros de resultado.

Devem apontar para o resultado ou evidência correspondente.

---

## 4. Estrutura recomendada

```text
docs/
├── gestao/
│   ├── README.md
│   ├── 00_painel_execucao_global.md
│   ├── 01_status_pipelines.md
│   ├── 02_log_decisoes_execucao.md
│   ├── 03_riscos_bloqueios.md
│   ├── 04_matriz_validacao_global.md
│   ├── 05_diario_execucao_ia.md
│   │
│   ├── _templates/
│   │   └── resultado_prompt.md
│   │
│   ├── 01_baseline/
│   │   ├── 01_benchmarking.md
│   │   ├── 02_visao_do_produto.md
│   │   ├── 03_arquitetura.md
│   │   ├── 04_roadmap_faseado.md
│   │   └── 05_backlog_macro.md
│   │
│   ├── 02_fase_0_preparacao/
│   │   ├── 01_backlog.md
│   │   └── pipelines/
│   │       ├── 01_<identificador_pipeline>/
│   │       │   ├── 01_pipeline.md
│   │       │   └── resultados_execucao/
│   │       │       ├── prompt_01_resultado.md
│   │       │       ├── prompt_02_resultado.md
│   │       │       └── evidencias/
│   │       └── 02_<identificador_pipeline>/
│   │           ├── 01_pipeline.md
│   │           └── resultados_execucao/
│   │
│   ├── 03_fase_1_mvp/
│   │   ├── 01_backlog.md
│   │   └── pipelines/
│   │
│   ├── 04_fase_2_versao_1/
│   │   ├── 01_backlog.md
│   │   └── pipelines/
│   │
│   └── 05_fase_3_evolucao/
│       ├── 01_backlog.md
│       └── pipelines/
│
└── produto/
    └── ...
```

### Justificação da hierarquia

Cada fase possui:

* um backlog próprio;
* uma ou mais pipelines;
* resultados separados por pipeline;
* evidências associadas aos prompts.

Esta estrutura evita que uma fase extensa tenha:

* um único ficheiro de pipeline demasiado grande;
* resultados de pipelines diferentes misturados;
* identificadores ambíguos;
* dificuldade em relacionar o resultado com a pipeline de origem.

---

## 5. Identificadores

Cada fase, pipeline e prompt deve possuir um identificador estável.

Exemplo:

```text
Fase: F1
Pipeline: F1-P03
Prompt: F1-P03-PR02
```

Formato recomendado:

```text
F<fase>-P<pipeline>-PR<prompt>
```

Exemplos:

```text
F0-P01-PR01
F1-P03-PR04
F2-P02-PR07
```

Os identificadores devem ser registados:

* no ficheiro da pipeline;
* no resultado do prompt;
* no estado global;
* nas decisões;
* nos riscos;
* nas evidências de validação.

---

## 6. Escopo da execução

A execução assistida por IA deve implementar o VentureOps AI de acordo com:

* visão de produto aprovada;
* arquitectura aprovada;
* roadmap faseado;
* backlog macro/baseline;
* backlog detalhado da fase activa;
* regras de segurança;
* critérios de validação;
* limites explícitos do MVP.

A execução não deve introduzir funcionalidades de fases posteriores sem decisão formal.

A IA local não deve:

* redefinir unilateralmente a visão do produto;
* alterar a arquitectura estrutural sem revisão;
* antecipar funcionalidades adiadas;
* substituir tecnologia aprovada sem justificação;
* alterar contratos ou modelos de dados críticos sem registo;
* avançar perante bloqueio crítico não resolvido.

---

## 7. Ordem recomendada de execução

A ordem geral é:

1. consultar o backlog da fase;
2. seleccionar a pipeline activa;
3. confirmar os pré-requisitos da pipeline;
4. executar os prompts pela ordem indicada;
5. validar o resultado de cada prompt;
6. registar o resultado;
7. actualizar apenas os documentos globais aplicáveis;
8. resolver bloqueios antes de continuar;
9. executar a validação final da pipeline;
10. actualizar a documentação de produto, quando aplicável;
11. decidir se a pipeline ou fase pode ser encerrada.

A fase seguinte só pode avançar quando os critérios de saída da fase actual forem cumpridos.

---

## 8. Regra de contexto mínimo por prompt

Cada prompt deve indicar explicitamente os ficheiros que a IA precisa de consultar.

Estrutura recomendada:

```markdown
## Contexto obrigatório

- `caminho/do/backlog.md`
- `caminho/do/ficheiro_afectado.py`
- `caminho/do/resultado_anterior.md`

## Contexto opcional

- `caminho/de/documento_adicional.md`

## Ficheiros que não devem ser alterados

- `...`
```

A IA não deve pesquisar ou ler indiscriminadamente:

```text
docs/gestao/
```

Por defeito, deve consultar apenas:

* o prompt actual;
* os ficheiros explicitamente referenciados;
* o resultado anterior directamente necessário;
* decisões ou riscos identificados por ID;
* os ficheiros de código ou documentação afectados.

Quando precisar de contexto adicional, deve justificar essa necessidade no resultado.

---

## 9. Como executar uma pipeline

Cada pipeline contém um ficheiro:

```text
01_pipeline.md
```

Um humano é responsável por:

1. seleccionar o próximo prompt;
2. entregar o prompt à IA local;
3. confirmar que a IA está no repositório e branch correctos;
4. acompanhar bloqueios ou pedidos de decisão;
5. rever o resultado;
6. decidir se o próximo prompt pode avançar.

A IA local deve executar apenas o prompt fornecido.

Não deve avançar autonomamente para o prompt seguinte.

---

## 10. Estados

Para evitar ambiguidade, distinguem-se três eixos independentes: **estado de
execução**, **estado de revisão** (informativo, não bloqueante) e **estado de
decisão** (vigência). A ausência de revisão ou de aprovação humana **não**
bloqueia, por si só, a continuidade da execução (ver 10.4).

Nota de âmbito: esta governação aplica-se à execução e aos artefactos. **Não**
altera a regra funcional do produto segundo a qual resultados de IA não podem
tornar-se informação oficial nem ser aplicados sem validação humana (ver §19 e a
matriz `04_matriz_validacao_global.md`, que trata a validação de capacidades do
produto, distinta da revisão documental aqui descrita).

### 10.1. Estado de execução

Usar um dos seguintes:

```text
Pendente
Em execução
Concluído
Parcial
Bloqueado
Falhado
Adiado
Fora do escopo
```

| Estado           | Significado                                        |
| ---------------- | -------------------------------------------------- |
| `Pendente`       | Ainda não iniciado                                 |
| `Em execução`    | Trabalho actualmente em curso                      |
| `Concluído`      | Escopo do prompt executado                         |
| `Parcial`        | Parte do escopo executada, com pendências          |
| `Bloqueado`      | Não pode prosseguir sem resolver um impedimento    |
| `Falhado`        | Execução realizada sem produzir o resultado mínimo |
| `Adiado`         | Execução suspensa por decisão                      |
| `Fora do escopo` | Item não pertence à fase ou pipeline               |

### 10.2. Estado de revisão

Informativo e **não bloqueante**. Regista se houve revisão humana, sem a exigir
para avançar.

```text
Não revista
Revista
Revista com reservas
Não aplicável
```

| Estado                | Significado                                              |
| --------------------- | -------------------------------------------------------- |
| `Não revista`         | Ainda não revista por humano (não impede a continuidade) |
| `Revista`             | Revista pelo operador humano, sem reservas               |
| `Revista com reservas`| Revista, com observações registadas a tratar             |
| `Não aplicável`       | Não há revisão humana prevista para este resultado       |

### 10.3. Estado de decisão

Vigência de uma decisão proposta num artefacto ou resultado.

```text
Proposta
Adoptada tacitamente
Confirmada
Confirmada com reservas
Rejeitada
Substituída
```

| Estado                   | Significado                                                                 |
| ------------------------ | --------------------------------------------------------------------------- |
| `Proposta`               | Registada, ainda não utilizada como base nem confirmada                     |
| `Adoptada tacitamente`   | Usada como base por prompt/artefacto/pipeline/fase posterior sem confirmação explícita |
| `Confirmada`             | Confirmada explicitamente pelo humano                                       |
| `Confirmada com reservas`| Confirmada com observações registadas                                       |
| `Rejeitada`              | Recusada; não vigora                                                         |
| `Substituída`            | Substituída por decisão posterior                                           |

Uma decisão passa de `Proposta` a `Adoptada tacitamente` quando é utilizada como
base por trabalho posterior sem confirmação humana explícita. A adopção tácita é
rastreável (o resultado que a usa referencia-a) e reversível (pode ser
confirmada, alterada, rejeitada ou substituída).

### 10.4. Regra de avanço (governação não bloqueante)

Um prompt, pipeline ou fase **pode avançar** quando: os artefactos materiais
necessários existem; as dependências técnicas necessárias existem; o trabalho
pode ser executado sem inventar factos ou decisões; os riscos críticos estão
mitigados ou formalmente aceites; e não existe falha material que impeça o
objectivo.

**Não** bloquear apenas porque: o estado de revisão é `Não revista`; uma decisão
permanece `Adoptada tacitamente`; não existe assinatura ou aprovação humana
formal; ou existem pontos de revisão por responder que não impedem materialmente
o trabalho.

Um prompt pode estar, por exemplo, `Execução: Concluído` / `Revisão: Não revista`
— e o trabalho posterior pode prosseguir. Critérios materiais não executados
continuam pendências reais e **não** podem ser declarados cumpridos sem
evidência. Uma pipeline não é considerada validada só porque todos os prompts
estão concluídos.

---

## 11. Registo obrigatório por prompt

Após cada execução, a IA local deve criar ou actualizar:

```text
docs/gestao/<fase>/pipelines/<pipeline>/resultados_execucao/prompt_XX_resultado.md
```

O ficheiro é a fonte de verdade detalhada da execução.

### Template recomendado

```markdown
---
fase: F1
pipeline: F1-P03
prompt: F1-P03-PR02
modelo: <modelo>
inicio: YYYY-MM-DD HH:mm
fim: YYYY-MM-DD HH:mm
estado_execucao: Concluído
estado_revisao: Não revista
commit: <hash ou "não criado">
---

# Resultado — Prompt XX — <Título>

## 1. Resumo

<Resumo objectivo, normalmente entre três e oito linhas.>

## 2. Alterações

### Ficheiros criados

- `caminho/do/ficheiro`

### Ficheiros alterados

- `caminho/do/ficheiro`

### Ficheiros removidos

- Nenhum.

## 3. Validações

| Comando ou verificação | Resultado | Evidência |
|---|---|---|
| `comando` | Sucesso | Saída resumida ou caminho da evidência |

## 4. Problemas e excepções

- Problemas encontrados: Nenhum.
- Limitações da validação: Nenhuma.
- Trabalho não executado: Nenhum.

## 5. Decisões relevantes e vigência

- Nenhuma. (Quando existirem: indicar a decisão e o estado — `Proposta`, `Adoptada tacitamente`, `Confirmada`, etc.)

## 6. Pendências materiais

- Nenhuma. (Trabalho material por executar que continua pendência real, não critério cumprido.)

## 7. Riscos, bloqueios ou dívida técnica

- Nenhum.

## 8. Riscos aceites

- Nenhum. (Riscos assumidos para permitir avanço com reservas.)

## 9. Próximo passo

- <Próxima acção concreta.>
```

### Regras do resultado

* não incluir conteúdos extensos que já existam nos ficheiros alterados;
* não copiar diffs completos;
* não copiar logs extensos;
* indicar explicitamente `Nenhum` quando uma secção não tiver ocorrências;
* manter o resumo objectivo;
* referenciar evidências por caminho;
* distinguir claramente trabalho executado de trabalho não revisto;
* não declarar sucesso quando a validação material não foi executada;
* a ausência de revisão humana não impede o avanço, mas não pode ser apresentada como revisão feita.

---

## 12. Reexecuções

Quando um prompt for reexecutado, deve ser actualizado o mesmo ficheiro.

Adicionar no final:

```markdown
## Reexecução — YYYY-MM-DD HH:mm

- Motivo:
- Alterações adicionais:
- Validações executadas:
- Resultado:
- Estado de execução:
- Estado de validação:
- Riscos ou pendências:
```

Não criar ficheiros como:

```text
prompt_01_resultado_v2.md
prompt_01_resultado_final.md
prompt_01_resultado_final_final.md
```

---

## 13. Política de actualização dos documentos globais

A IA local não deve actualizar todos os documentos globais em cada prompt.

Deve aplicar a seguinte matriz.

| Documento                       | Actualização                    | Condição                                                                  |
| ------------------------------- | ------------------------------- | ------------------------------------------------------------------------- |
| Resultado do prompt             | Sempre                          | Após qualquer execução ou reexecução                                      |
| `01_status_pipelines.md`        | Sempre                          | Actualizar apenas a linha da pipeline afectada                            |
| `05_diario_execucao_ia.md`      | Sempre                          | Acrescentar apenas uma linha curta                                        |
| `00_painel_execucao_global.md`  | Quando houver mudança           | Pipeline actual, último prompt, próximo prompt, estado global ou bloqueio |
| `02_log_decisoes_execucao.md`   | Apenas por evento               | Nova decisão relevante ou alteração de decisão                            |
| `03_riscos_bloqueios.md`        | Apenas por evento               | Novo risco, bloqueio, dívida ou mudança de estado                         |
| `04_matriz_validacao_global.md` | Apenas por evidência            | Nova validação ou mudança de estado                                       |
| `docs/produto/`                 | Apenas por alteração permanente | Mudança aceite no comportamento ou desenho da solução                     |

### Regra de edição

A IA deve:

* actualizar apenas a linha ou secção afectada;
* evitar reformatar o documento completo;
* manter a ordenação existente;
* não reescrever entradas históricas;
* não duplicar decisões ou riscos já registados;
* actualizar pelo ID quando o registo já existir.

---

## 14. Documentos globais

### 14.1. `00_painel_execucao_global.md`

Resumo executivo curto.

Deve conter apenas:

```text
- estado global;
- fase actual;
- pipeline actual;
- último prompt executado;
- próximo prompt recomendado;
- bloqueios críticos activos;
- decisões críticas recentes;
- progresso resumido;
- data da última actualização.
```

O painel não deve repetir detalhes dos resultados.

Exemplo:

```markdown
# Painel de execução global

- Estado global: Em execução
- Fase actual: F1 — MVP
- Pipeline actual: F1-P03 — Gestão documental
- Último prompt: F1-P03-PR04 — Concluído / Revista
- Próximo prompt: F1-P03-PR05
- Bloqueios críticos: Nenhum
- Última actualização: YYYY-MM-DD HH:mm
```

---

### 14.2. `01_status_pipelines.md`

Fonte de verdade do progresso das pipelines.

Formato recomendado:

```markdown
| ID | Fase | Pipeline | Execução | Revisão | Prompts | Concluídos | Revistos | Bloqueios | Próximo |
|---|---|---|---|---|---:|---:|---:|---|---|
| F1-P03 | F1 | Gestão documental | Em execução | Não revista | 8 | 4 | 0 | 0 | PR05 |
```

A coluna `Revisão` é informativa (não bloqueante); `Revistos` conta prompts com
revisão humana registada. A IA deve actualizar apenas a linha correspondente à
pipeline executada.

---

### 14.3. `02_log_decisoes_execucao.md`

Registo append-only das decisões relevantes.

Uma decisão deve ser registada quando afecta:

* arquitectura;
* contratos de API;
* modelo de dados;
* permissões;
* segurança;
* comportamento funcional;
* integração;
* deploy;
* escopo;
* compatibilidade;
* manutenção futura.

Template:

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

Decisões pequenas e locais, sem impacto futuro, permanecem apenas no resultado do prompt.

---

### 14.4. `03_riscos_bloqueios.md`

Registo de riscos, bloqueios e dívida técnica com impacto superior ao prompt actual.

Template:

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

Não criar nova entrada para o mesmo risco.

Quando o risco evoluir, actualizar a entrada existente.

---

### 14.5. `04_matriz_validacao_global.md`

A matriz deve validar capacidades do VentureOps AI, e não componentes herdados de outros projectos.

Estrutura recomendada:

```markdown
| ID | Capacidade | Fase | Critério | Estado | Evidência | Última validação |
|---|---|---|---|---|---|---|
| VAL-001 | Autenticação | MVP | Acesso autenticado e sessão segura | Pendente | — | — |
| VAL-002 | Isolamento entre empresas | MVP | Nenhum acesso transversal entre tenants | Pendente | — | — |
| VAL-003 | Portefólio de produtos | MVP | CRUD e arquivo validados | Pendente | — | — |
| VAL-004 | Documentos e versões | MVP | Versões criadas e recuperáveis | Pendente | — | — |
| VAL-005 | Decisões | MVP | Registo e associação a produto | Pendente | — | — |
| VAL-006 | Pendências administrativas | MVP | Estados e prazos validados | Pendente | — | — |
| VAL-007 | Funções organizacionais | MVP | Função utilizável numa execução | Pendente | — | — |
| VAL-008 | Pacote de contexto | MVP | Versões exactas preservadas | Pendente | — | — |
| VAL-009 | Resultados de IA | MVP | Resultado associado à execução correcta | Pendente | — | — |
| VAL-010 | Revisão e aprovação | MVP | Nenhuma aplicação sem validação humana | Pendente | — | — |
| VAL-011 | Visão de atenção | MVP | Alertas explicáveis e coerentes | Pendente | — | — |
| VAL-012 | Auditoria | MVP | Operações críticas rastreáveis | Pendente | — | — |
| VAL-013 | Exportação | MVP | Dados e Markdown exportáveis | Pendente | — | — |
| VAL-014 | Segurança de Markdown | MVP | Conteúdo renderizado sem XSS | Pendente | — | — |
| VAL-015 | Backup e recuperação | MVP | Recuperação validada | Pendente | — | — |
| VAL-016 | Deploy e rollback | MVP | Deploy e reversão executáveis | Pendente | — | — |
```

Estados recomendados:

```text
Não iniciado
Em validação
Validado
Parcial
Falhado
Bloqueado
Não aplicável
```

A matriz deve apontar para resultados e evidências, não reproduzi-los.

---

### 14.6. `05_diario_execucao_ia.md`

O diário é um índice cronológico compacto, não um segundo relatório de execução.

Formato recomendado:

```markdown
| Data/hora | Fase/Pipeline | Prompt | Execução | Revisão | Resumo | Resultado |
|---|---|---|---|---|---|---|
| YYYY-MM-DD HH:mm | F1 / F1-P03 | PR04 | Concluído | Não revista | Versionamento documental concluído | `resultados_execucao/prompt_04_resultado.md` |
```

Cada execução ou reexecução acrescenta apenas uma linha.

Não devem ser copiados:

* ficheiros alterados;
* comandos;
* logs;
* decisões completas;
* riscos completos.

Esses detalhes pertencem ao resultado do prompt e aos respectivos registos especializados.

---

## 15. Bloco obrigatório no fim de cada prompt

Para reduzir tokens, cada prompt deve terminar com um bloco curto.

```text
## Fecho e registo obrigatório

No final:

1. cria ou actualiza:
   `docs/gestao/<fase>/pipelines/<pipeline>/resultados_execucao/prompt_XX_resultado.md`;

2. actualiza apenas a linha correspondente em:
   `docs/gestao/01_status_pipelines.md`;

3. acrescenta uma linha curta em:
   `docs/gestao/05_diario_execucao_ia.md`;

4. actualiza `00_painel_execucao_global.md` apenas se mudar o estado, pipeline actual, último prompt, próximo prompt ou bloqueio;

5. actualiza decisões, riscos, validações e `docs/produto/` apenas se os critérios definidos em `docs/gestao/README.md` forem aplicáveis.

Não reescrevas documentos completos, não dupliques detalhes e não copies logs extensos.

Não avances para o prompt seguinte.
```

O caminho do resultado deve aparecer apenas uma vez.

O estado de revisão é registado quando aplicável, mas **não** é pré-requisito de
avanço. As decisões propostas por um prompt podem vigorar como `Adoptada
tacitamente` para o prompt seguinte, sem confirmação humana explícita.

---

## 16. Convenção de evidências

As evidências devem ser proporcionais ao risco e à importância da validação.

### Evidências pequenas

Podem ser incluídas no resultado:

* comando executado;
* resumo da saída;
* código de retorno;
* contagem de testes;
* resultado observado.

### Evidências extensas

Devem ser guardadas em:

```text
resultados_execucao/evidencias/
```

Exemplos:

```text
prompt_03_testes_backend.txt
prompt_03_resumo_cobertura.txt
prompt_05_migracao_output.txt
prompt_07_response_api.json
```

O resultado deve referenciar o caminho.

### Regras

* não copiar logs completos para Markdown;
* guardar apenas a parte relevante;
* não guardar segredos;
* remover tokens, passwords e dados sensíveis;
* preferir links para pipelines CI/CD quando disponíveis;
* não guardar artefactos gerados que possam ser reproduzidos facilmente, salvo necessidade de auditoria.

---

## 17. Critérios de bloqueio

Um prompt ou pipeline deve ser marcado como `Bloqueado` quando existir:

* risco de perda ou corrupção de dados;
* vulnerabilidade crítica;
* fuga de dados entre empresas;
* migração irreversível não validada;
* testes críticos a falhar;
* dependência externa obrigatória indisponível;
* credencial ou configuração necessária em falta;
* incompatibilidade com arquitectura aprovada;
* ambiguidade funcional que possa causar implementação incorrecta;
* fonte de verdade indefinida;
* alteração que ultrapasse o escopo autorizado;
* impossibilidade de produzir evidência mínima.

A **ausência de revisão ou de aprovação humana não é, por si só, critério de
bloqueio**. Uma decisão arquitectural que beneficiaria de confirmação humana não
bloqueia: vigora como `Adoptada tacitamente` (ou `Confirmada com reservas`) e é
sinalizada, salvo se existir uma falha material das listadas acima.

Um risco crítico não resolvido bloqueia a continuação da pipeline, excepto quando o próximo prompt tem explicitamente como objectivo resolver esse bloqueio.

---

## 18. Critérios de validação global

A execução global só pode ser considerada concluída quando:

* todos os itens obrigatórios da fase estão concluídos;
* os fluxos core foram validados;
* os testes obrigatórios passaram;
* não existem bloqueios críticos activos;
* riscos altos possuem mitigação ou aceitação formal;
* decisões relevantes estão registadas;
* documentos de produto estão actualizados;
* migrações foram validadas;
* deploy e rollback mínimos foram testados;
* backups e recuperação foram verificados, quando aplicável;
* a matriz de validação possui evidências;
* o estado global está coerente com os resultados das pipelines;
* a fase cumpre os respectivos critérios de saída.

`Concluído` não equivale automaticamente a `Validado`.

---

## 19. Relação com `docs/produto/`

A pasta:

```text
docs/gestao/
```

regista como a solução foi executada.

A pasta:

```text
docs/produto/
```

descreve como a solução funciona actualmente.

A IA local deve actualizar `docs/produto/` quando uma alteração aceite afectar:

* arquitectura;
* modelo de dados;
* APIs e contratos;
* autenticação;
* autorização;
* regras de negócio;
* comportamento funcional;
* configuração;
* deploy;
* variáveis de ambiente;
* operação;
* segurança;
* recuperação;
* integrações;
* procedimentos de utilização;
* limitações conhecidas.

Não é necessário actualizar `docs/produto/` quando houver apenas:

* refactor sem alteração de comportamento;
* correcção interna sem impacto documental;
* alteração temporária;
* investigação sem decisão;
* teste adicional;
* formatação;
* alteração rejeitada ou não aplicada.

A documentação final deve representar apenas o estado aceite da solução, não o histórico completo das tentativas.

---

## 20. Regra sobre decisões técnicas

A IA local pode tomar decisões pequenas de implementação quando:

* respeitam a arquitectura;
* não alteram contratos externos;
* não criam dependências relevantes;
* não alteram segurança;
* não aumentam o escopo;
* são reversíveis;
* seguem padrões existentes.

Essas decisões podem permanecer apenas no resultado do prompt.

A decisão deve entrar em `02_log_decisoes_execucao.md` quando afectar:

* arquitectura;
* tecnologia ou dependência principal;
* esquema de dados;
* migração;
* API;
* autenticação;
* autorização;
* segurança;
* estratégia de armazenamento;
* deploy;
* compatibilidade;
* fonte de verdade;
* comportamento visível;
* escopo futuro;
* operação ou manutenção significativa.

Decisões com impacto arquitectural que beneficiariam de confirmação humana **não
bloqueiam** a execução: vigoram como `Adoptada tacitamente` (ou `Confirmada com
reservas`) e são sinalizadas no resultado e, quando aplicável, no log de
decisões. Só se marca `Bloqueado` quando existir uma falha material dos critérios
de §17 (por exemplo, ambiguidade que cause implementação incorrecta ou alteração
fora do escopo autorizado).

---

## 21. Regras obrigatórias para a IA local

A IA local deve:

1. executar apenas o prompt actual;

2. respeitar o escopo da fase;

3. consultar apenas o contexto necessário;

4. não alterar ficheiros fora do escopo sem justificação;

5. validar as alterações realizadas;

6. declarar limitações de validação;

7. não inventar resultados de testes;

8. não declarar validação sem evidência;

9. não esconder erros ou bloqueios;

10. actualizar o resultado do prompt;

11. actualizar os documentos globais de forma selectiva;

12. preservar histórico;

13. evitar copiar conteúdos extensos;

14. proteger segredos e dados sensíveis;

15. actualizar `docs/produto/` apenas quando aplicável;

16. não avançar autonomamente para o próximo prompt;

17. não efectuar commits, pushes ou deploys sem autorização explícita, salvo instrução contrária da pipeline;

18. não introduzir dependências novas sem necessidade justificada;

19. não antecipar funcionalidades de fases posteriores;

20. manter as alterações pequenas, verificáveis e reversíveis.

---

## 22. Critérios de eficiência documental

Para evitar consumo desnecessário de tokens e crescimento artificial da documentação:

* o resumo de execução deve ser curto;
* o diário deve conter uma linha por execução;
* os logs globais devem conter apenas eventos relevantes;
* os resultados devem referenciar ficheiros, não copiar o seu conteúdo;
* os prompts devem referenciar artefactos existentes por caminho;
* baseline e arquitectura não devem ser reproduzidas dentro das pipelines;
* apenas o contexto necessário deve ser carregado;
* alterações globais devem ser feitas por patch localizado;
* resultados antigos não devem ser relidos sem necessidade;
* o último resultado relevante deve ser preferido a todo o histórico;
* decisões e riscos devem ser consultados por ID;
* outputs extensos devem ser guardados como evidência externa.

---

## 23. Resultado esperado desta área

No final de cada fase, esta pasta deve permitir responder claramente:

```text
- que pipelines foram planeadas;
- que prompts foram executados;
- qual foi o estado de cada execução;
- que ficheiros foram alterados;
- que testes e validações foram realizados;
- que evidências existem;
- que decisões foram tomadas;
- que riscos e bloqueios permanecem;
- que documentação final foi actualizada;
- se a fase cumpre os critérios de saída;
- se a próxima fase pode avançar.
```

A pasta `docs/gestao/` deve funcionar como um registo de controlo e auditoria leve, e não como uma segunda documentação completa do produto.
