# Pipeline: Modelo funcional do MVP

* Identificador: F0-P03 (Fase F0).
* Itens do backlog cobertos: F0-B04, F0-B05, F0-B07 (rastreiam F0-04, F0-05, F0-07 da baseline).
* Artefactos produzidos: `artefactos/02_fluxo_e_modelo_funcional.md` (secção de modelo funcional); `artefactos/03_estados_e_transicoes.md`; `artefactos/04_ficha_administrativa_produto.md`.
* Pré-requisitos: pipeline F0-P02 concluída e artefactos revistos por humano.
* Execução: prompts pela ordem indicada; um humano entrega cada prompt e revê o resultado antes do seguinte.

## Prompt 01 (opus) — Fechar glossário, entidades, relações e funções organizacionais

```prompt
Iteração 01

Actua como analista funcional e arquitecto de solução.

Identificadores: Fase F0; Pipeline F0-P03; Prompt F0-P03-PR01.
Itens do backlog tratados: F0-B04 (F0-04). Decisão bloqueadora: DB-04.

Objectivo: confirmar as entidades mínimas do MVP, as suas relações de alto nível e o glossário funcional, incluindo as funções organizacionais (humanas, de IA e híbridas).

Contexto obrigatório:
- docs/gestao/02_fase_0_preparacao/01_backlog.md (item F0-B04)
- docs/gestao/02_fase_0_preparacao/artefactos/02_fluxo_e_modelo_funcional.md (fluxo aprovado)
- docs/gestao/01_baseline/03_arquitetura.md (secções 6.2 e 6.3, como referência indicativa)
- docs/gestao/01_baseline/04_roadmap_faseado.md (secção 3.2, lista de entidades)

Ficheiros que não devem ser alterados:
- todos os documentos de docs/gestao/01_baseline/

Trabalho a realizar:
1. validar cada entidade proposta (empresa, produto, documento, decisão, pendência, função, execução, resultado, revisão, auditoria) contra o fluxo aprovado;
2. produzir um glossário funcional: definição de cada entidade em linguagem de negócio, sem campos técnicos;
3. definir as funções organizacionais como conceito funcional: tipos (humana, IA, híbrida), propósito, responsabilidades, limites e necessidade de aprovação; sem confundir com papéis de utilizador (tratados em F0-B10);
4. confirmar as relações de alto nível entre entidades;
5. identificar entidades dispensáveis no MVP e registar a exclusão como decisão proposta.

Artefacto a actualizar:
- docs/gestao/02_fase_0_preparacao/artefactos/02_fluxo_e_modelo_funcional.md (acrescentar a secção de modelo funcional; não reescrever as secções de fluxo e limites)

O artefacto deve separar explicitamente, em secções próprias:
- factos, com referência à fonte;
- decisões propostas, com estado Proposta / A validar;
- hipóteses assumidas;
- pontos a validar por humano.

Critérios de verificação:
- todas as entidades usadas no fluxo estão definidas no glossário;
- nenhuma entidade sem uso no fluxo do MVP permanece no modelo;
- as relações são coerentes com a arquitectura (secção 6.3) ou o desvio está justificado;
- as funções organizacionais estão definidas e distinguidas dos papéis de utilizador;
- o glossário está em linguagem de negócio, sem esquema físico.

O que não deve ser feito:
- não definir campos, tipos de dados, chaves ou migrações;
- não alterar as secções de fluxo e limites já aprovadas;
- não antecipar estados e transições (pertencem ao prompt seguinte);
- não reproduzir a baseline; referenciar por caminho e secção.

Fecho e registo obrigatório:

1. cria ou actualiza docs/gestao/02_fase_0_preparacao/pipelines/03_modelo_funcional/resultados_execucao/prompt_01_resultado.md;
2. actualiza apenas a linha correspondente em docs/gestao/01_status_pipelines.md;
3. acrescenta uma linha curta em docs/gestao/05_diario_execucao_ia.md;
4. actualiza docs/gestao/00_painel_execucao_global.md apenas se mudar o estado, pipeline actual, último prompt, próximo prompt ou bloqueio;
5. actualiza decisões, riscos, validações e docs/produto/ apenas se os critérios definidos em docs/gestao/README.md forem aplicáveis.

Não reescrevas documentos completos, não dupliques detalhes e não copies logs extensos.

Não avances para o prompt seguinte.
```

## Prompt 02 (sonnet) — Definir estados e transições das entidades

```prompt
Iteração 02

Actua como analista funcional.

Identificadores: Fase F0; Pipeline F0-P03; Prompt F0-P03-PR02.
Itens do backlog tratados: F0-B05 (F0-05). Decisão bloqueadora: DB-05.

Objectivo: definir os estados mínimos e as transições válidas de produto, documento, decisão, pendência, função, execução e revisão.

Pré-requisito: secção de modelo funcional aprovada (F0-P03-PR01).

Contexto obrigatório:
- docs/gestao/02_fase_0_preparacao/01_backlog.md (item F0-B05)
- docs/gestao/02_fase_0_preparacao/artefactos/02_fluxo_e_modelo_funcional.md

Contexto opcional:
- docs/gestao/01_baseline/03_arquitetura.md (secção 6.2, campos status indicativos)

Ficheiros que não devem ser alterados:
- todos os documentos de docs/gestao/01_baseline/

Trabalho a realizar:
1. para cada entidade com ciclo de vida, enumerar os estados mínimos necessários ao fluxo aprovado;
2. definir as transições válidas entre estados e quem as pode executar (por papel funcional, sem detalhe técnico);
3. verificar que cada passo do fluxo é suportado pelos estados definidos;
4. eliminar estados especulativos que não sejam exigidos pelo fluxo do piloto.

Artefacto a criar:
- docs/gestao/02_fase_0_preparacao/artefactos/03_estados_e_transicoes.md

O artefacto deve separar explicitamente, em secções próprias:
- factos, com referência à fonte;
- decisões propostas (estados e transições), com estado Proposta / A validar;
- hipóteses assumidas;
- pontos a validar por humano.

Critérios de verificação:
- cada entidade tem estados enumerados e transições explícitas;
- cada transição indica quem a pode executar;
- nenhum passo do fluxo exige um estado inexistente;
- não existem estados sem uso no fluxo do piloto.

O que não deve ser feito:
- não modelar máquinas de estado técnicas nem enumerações de código;
- não acrescentar estados para funcionalidades de fases posteriores;
- não redefinir entidades (pertence a F0-B04);
- não reproduzir a baseline.

Fecho e registo obrigatório:

1. cria ou actualiza docs/gestao/02_fase_0_preparacao/pipelines/03_modelo_funcional/resultados_execucao/prompt_02_resultado.md;
2. actualiza apenas a linha correspondente em docs/gestao/01_status_pipelines.md;
3. acrescenta uma linha curta em docs/gestao/05_diario_execucao_ia.md;
4. actualiza docs/gestao/00_painel_execucao_global.md apenas se mudar o estado, pipeline actual, último prompt, próximo prompt ou bloqueio;
5. actualiza decisões, riscos, validações e docs/produto/ apenas se os critérios definidos em docs/gestao/README.md forem aplicáveis.

Não reescrevas documentos completos, não dupliques detalhes e não copies logs extensos.

Não avances para o prompt seguinte.
```

## Prompt 03 (sonnet) — Definir e testar a ficha administrativa mínima do produto

```prompt
Iteração 03

Actua como Product Owner e analista funcional.

Identificadores: Fase F0; Pipeline F0-P03; Prompt F0-P03-PR03.
Itens do backlog tratados: F0-B07 (F0-07). Decisão bloqueadora: DB-07.

Objectivo: fechar os campos mínimos da ficha administrativa do produto e testá-la com um produto real.

Pré-requisitos: modelo funcional (F0-P03-PR01) e estados (F0-P03-PR02) aprovados.

Contexto obrigatório:
- docs/gestao/02_fase_0_preparacao/01_backlog.md (item F0-B07)
- docs/gestao/02_fase_0_preparacao/artefactos/01_segmento_e_caso_uso.md (caso de uso principal)
- docs/gestao/02_fase_0_preparacao/artefactos/02_fluxo_e_modelo_funcional.md (entidade produto)
- docs/gestao/02_fase_0_preparacao/artefactos/03_estados_e_transicoes.md (estados de produto)

Contexto opcional:
- docs/gestao/01_baseline/02_visao_do_produto.md (secção 8.1, ficha administrativa)

Ficheiros que não devem ser alterados:
- todos os documentos de docs/gestao/01_baseline/

Trabalho a realizar:
1. distinguir campos obrigatórios, opcionais e adiados da ficha administrativa;
2. justificar cada campo obrigatório pelo caso de uso principal ou pelas regras de atenção previstas;
3. testar a ficha preenchendo-a com um produto real: usar um produto real indicado pelo operador humano; se nenhum for fornecido no contexto, preencher com um exemplo plausível claramente marcado como exemplo e registar como ponto a validar e estado de execução Parcial;
4. avaliar o esforço de preenchimento face ao princípio de que o fundador não deve servir a ferramenta.

Artefacto a criar:
- docs/gestao/02_fase_0_preparacao/artefactos/04_ficha_administrativa_produto.md

O artefacto deve separar explicitamente, em secções próprias:
- factos, com referência à fonte;
- decisões propostas (lista de campos), com estado Proposta / A validar;
- hipóteses assumidas;
- pontos a validar por humano;
- evidência do teste (ficha preenchida).

Critérios de verificação:
- a lista de campos obrigatórios está fechada e justificada;
- a ficha foi preenchida com um produto real ou o teste está marcado como Parcial com pedido explícito ao humano;
- o preenchimento da ficha obrigatória é curto (avaliação registada);
- os campos são coerentes com os estados definidos em F0-B05.

O que não deve ser feito:
- não definir tipos de dados, validações técnicas ou layout de interface;
- não acrescentar campos para funcionalidades de fases posteriores;
- não declarar o teste como feito se a ficha não tiver sido preenchida;
- não reproduzir a baseline.

Fecho e registo obrigatório:

1. cria ou actualiza docs/gestao/02_fase_0_preparacao/pipelines/03_modelo_funcional/resultados_execucao/prompt_03_resultado.md;
2. actualiza apenas a linha correspondente em docs/gestao/01_status_pipelines.md;
3. acrescenta uma linha curta em docs/gestao/05_diario_execucao_ia.md;
4. actualiza docs/gestao/00_painel_execucao_global.md apenas se mudar o estado, pipeline actual, último prompt, próximo prompt ou bloqueio;
5. actualiza decisões, riscos, validações e docs/produto/ apenas se os critérios definidos em docs/gestao/README.md forem aplicáveis.

Não reescrevas documentos completos, não dupliques detalhes e não copies logs extensos.

Não avances para o prompt seguinte.
```
