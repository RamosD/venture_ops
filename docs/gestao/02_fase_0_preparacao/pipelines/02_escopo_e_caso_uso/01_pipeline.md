# Pipeline: Escopo e caso de uso do MVP

* Identificador: F0-P02 (Fase F0).
* Itens do backlog cobertos: F0-B01, F0-B02, F0-B03 (rastreiam F0-01, F0-02, F0-03 da baseline).
* Artefactos produzidos: `artefactos/01_segmento_e_caso_uso.md`; `artefactos/02_fluxo_e_modelo_funcional.md` (secções de fluxo e limites funcionais).
* Pré-requisitos: backlog da Fase 0 (`01_backlog.md`) revisto por humano.
* Execução: prompts pela ordem indicada; um humano entrega cada prompt e revê o resultado antes do seguinte.

## Prompt 01 (opus) — Definir segmento inicial e caso de uso principal

```prompt
Iteração 01

Actua como Product Owner sénior e analista funcional.

Identificadores: Fase F0; Pipeline F0-P02; Prompt F0-P02-PR01.
Itens do backlog tratados: F0-B01 (F0-01) e F0-B02 (F0-02). Decisões bloqueadoras: DB-01 e DB-02.

Objectivo: fixar o segmento inicial do VentureOps AI, identificar o problema prioritário desse segmento e seleccionar o caso de uso principal que o MVP deve demonstrar.

Contexto obrigatório:
- docs/gestao/02_fase_0_preparacao/01_backlog.md (itens F0-B01 e F0-B02)
- docs/gestao/01_baseline/02_visao_do_produto.md (secções 2, 3, 7 e 15.1)

Contexto opcional:
- docs/gestao/01_baseline/01_benchmarking.md (apenas se necessário para delimitar o segmento)

Ficheiros que não devem ser alterados:
- todos os documentos de docs/gestao/01_baseline/

Trabalho a realizar:
1. caracterizar o segmento inicial: dimensão da equipa, número de produtos, maturidade técnica e utilização de IA;
2. delimitar explicitamente o que fica fora do segmento inicial;
3. identificar o problema prioritário do segmento a partir da visão;
4. avaliar os casos de uso da visão (secção 7) contra a tese do MVP (secção 15.1) e seleccionar um único caso de uso principal, com justificação;
5. descrever o caso de uso com: situação inicial, actor, necessidade, execução, resultado e valor esperado;
6. identificar dois a três perfis reais candidatos a piloto, sem incluir dados pessoais.

Artefacto a criar:
- docs/gestao/02_fase_0_preparacao/artefactos/01_segmento_e_caso_uso.md

O artefacto deve separar explicitamente, em secções próprias:
- factos, com referência à fonte (documento e secção);
- decisões propostas, cada uma com justificação e estado Proposta / A validar;
- hipóteses assumidas;
- pontos a validar por humano.

Critérios de verificação:
- o perfil do segmento cobre dimensão de equipa, número de produtos, maturidade técnica e uso de IA;
- as exclusões do segmento estão explícitas;
- existe um único caso de uso principal com justificação da escolha;
- a descrição do caso de uso cobre os seis elementos exigidos;
- a relação com a tese do MVP está explícita;
- pelo menos um perfil real candidato a piloto está identificado.

O que não deve ser feito:
- não fechar decisões como aprovadas; tudo fica A validar até revisão humana;
- não redefinir a visão do produto nem alargar o público-alvo;
- não copiar integralmente secções da baseline; referenciar por caminho e secção;
- não criar outros artefactos, código ou estrutura técnica.

Fecho e registo obrigatório:

1. cria ou actualiza docs/gestao/02_fase_0_preparacao/pipelines/02_escopo_e_caso_uso/resultados_execucao/prompt_01_resultado.md;
2. actualiza apenas a linha correspondente em docs/gestao/01_status_pipelines.md;
3. acrescenta uma linha curta em docs/gestao/05_diario_execucao_ia.md;
4. actualiza docs/gestao/00_painel_execucao_global.md apenas se mudar o estado, pipeline actual, último prompt, próximo prompt ou bloqueio;
5. actualiza decisões, riscos, validações e docs/produto/ apenas se os critérios definidos em docs/gestao/README.md forem aplicáveis.

Não reescrevas documentos completos, não dupliques detalhes e não copies logs extensos.

Não avances para o prompt seguinte.
```

## Prompt 02 (opus) — Fechar o fluxo funcional e os limites do MVP

```prompt
Iteração 02

Actua como Product Owner técnico e analista funcional.

Identificadores: Fase F0; Pipeline F0-P02; Prompt F0-P02-PR02.
Itens do backlog tratados: F0-B03 (F0-03). Decisão bloqueadora: DB-03. Prepara também a lista preliminar de limites para F0-B14.

Objectivo: fechar o fluxo funcional ponta a ponta do MVP e confirmar os limites funcionais, incluindo a lista preliminar do que fica fora do MVP.

Pré-requisito: artefacto 01_segmento_e_caso_uso.md criado e revisto por humano (F0-P02-PR01).

Contexto obrigatório:
- docs/gestao/02_fase_0_preparacao/01_backlog.md (item F0-B03)
- docs/gestao/02_fase_0_preparacao/artefactos/01_segmento_e_caso_uso.md
- docs/gestao/01_baseline/04_roadmap_faseado.md (secções 3.2 e 4.3)
- docs/gestao/01_baseline/03_arquitetura.md (secção 1, apenas o fluxo geral)

Contexto opcional:
- docs/gestao/01_baseline/02_visao_do_produto.md (secção 9, para os limites)

Ficheiros que não devem ser alterados:
- todos os documentos de docs/gestao/01_baseline/

Trabalho a realizar:
1. percorrer o fluxo de nove passos proposto no roadmap (secção 3.2), passo a passo;
2. confirmar, para cada passo: actor, entrada, saída e estado resultante;
3. identificar etapas ambíguas, em falta ou dependentes de funcionalidades excluídas do MVP, e resolvê-las ou registá-las como ponto a validar;
4. alinhar o fluxo com o caso de uso principal aprovado;
5. consolidar a lista preliminar de limites funcionais do MVP: incluído, excluído, opcional e adiado (a lista final é congelada em F0-B14).

Artefacto a criar:
- docs/gestao/02_fase_0_preparacao/artefactos/02_fluxo_e_modelo_funcional.md (secções de fluxo e de limites funcionais; a secção de modelo funcional será acrescentada pela pipeline F0-P03)

O artefacto deve separar explicitamente, em secções próprias:
- factos, com referência à fonte;
- decisões propostas, com estado Proposta / A validar;
- hipóteses assumidas;
- pontos a validar por humano.

Critérios de verificação:
- cada passo do fluxo tem actor, entrada e saída definidos;
- nenhuma etapa depende de funcionalidade excluída do MVP;
- as ambiguidades estão resolvidas ou registadas como ponto a validar;
- o fluxo suporta integralmente o caso de uso principal;
- a lista preliminar de limites distingue incluído, excluído, opcional e adiado.

O que não deve ser feito:
- não acrescentar passos que exijam integração automática com IA, Git ou notificações;
- não detalhar ecrãs, APIs ou modelos de dados;
- não congelar formalmente o escopo (pertence a F0-B14);
- não reproduzir a baseline; referenciar por caminho e secção.

Fecho e registo obrigatório:

1. cria ou actualiza docs/gestao/02_fase_0_preparacao/pipelines/02_escopo_e_caso_uso/resultados_execucao/prompt_02_resultado.md;
2. actualiza apenas a linha correspondente em docs/gestao/01_status_pipelines.md;
3. acrescenta uma linha curta em docs/gestao/05_diario_execucao_ia.md;
4. actualiza docs/gestao/00_painel_execucao_global.md apenas se mudar o estado, pipeline actual, último prompt, próximo prompt ou bloqueio;
5. actualiza decisões, riscos, validações e docs/produto/ apenas se os critérios definidos em docs/gestao/README.md forem aplicáveis.

Não reescrevas documentos completos, não dupliques detalhes e não copies logs extensos.

Não avances para o prompt seguinte.
```
