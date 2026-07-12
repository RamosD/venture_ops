
# Compilação de pipelines

Pipeline: Escopo e caso de uso do MVP

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


docs\gestao\02_fase_0_preparacao\pipelines\03_modelo_funcional\01_pipeline.md

Pipeline: Modelo funcional do MVP

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


docs\gestao\02_fase_0_preparacao\pipelines\04_dados_contexto_seguranca\01_pipeline.md

Pipeline: Dados, contexto de IA e segurança

* Identificador: F0-P04 (Fase F0).
* Itens do backlog cobertos: F0-B06, F0-B09, F0-B12 (rastreiam F0-06, F0-09, F0-12 da baseline).
* Artefactos produzidos: `artefactos/05_fonte_de_verdade_bd_markdown.md`; `artefactos/07_pacote_contexto_ia.md`; `artefactos/10_requisitos_seguranca_mvp.md`.
* Pré-requisitos: pipeline F0-P02 concluída; modelo funcional (F0-P03-PR01) aprovado. O Prompt 03 exige ainda os artefactos 08 e 09 (pipeline F0-P05, prompts 01 e 02) aprovados.
* Execução: prompts pela ordem indicada; um humano entrega cada prompt e revê o resultado antes do seguinte.

## Prompt 01 (opus) — Definir a fronteira BD/Markdown e o versionamento

```prompt
Iteração 01

Actua como arquitecto de solução e gestor de configuração documental.

Identificadores: Fase F0; Pipeline F0-P04; Prompt F0-P04-PR01.
Itens do backlog tratados: F0-B06 (F0-06). Decisão bloqueadora: DB-06.

Objectivo: definir, para cada tipo de informação do modelo funcional, a fonte oficial (base de dados ou Markdown), a política de versões documentais e as regras de actualização.

Pré-requisito: secção de modelo funcional aprovada (F0-P03-PR01).

Contexto obrigatório:
- docs/gestao/02_fase_0_preparacao/01_backlog.md (item F0-B06)
- docs/gestao/02_fase_0_preparacao/artefactos/02_fluxo_e_modelo_funcional.md (entidades)
- docs/gestao/01_baseline/03_arquitetura.md (secções 2.3, 6.1 e 15.2)

Contexto opcional:
- docs/gestao/01_baseline/02_visao_do_produto.md (secção 12, princípios 5 a 7)

Ficheiros que não devem ser alterados:
- todos os documentos de docs/gestao/01_baseline/

Trabalho a realizar:
1. classificar cada tipo de informação do modelo funcional por fonte oficial: base de dados ou Markdown;
2. identificar os metadados duplicados apenas para identificação e as regras que impedem valores operacionais concorrentes;
3. definir a política de versões documentais: quando se cria versão, imutabilidade e recuperação;
4. definir as regras de actualização: quem actualiza, através de quê, e o que acontece em caso de conflito;
5. registar como ponto a validar as questões que dependem do levantamento técnico (F0-B11), como o mecanismo de armazenamento no piloto.

Artefacto a criar:
- docs/gestao/02_fase_0_preparacao/artefactos/05_fonte_de_verdade_bd_markdown.md

O artefacto deve separar explicitamente, em secções próprias:
- factos, com referência à fonte;
- decisões propostas (matriz de fonte de verdade e políticas), com estado Proposta / A validar;
- hipóteses assumidas;
- pontos a validar por humano.

Critérios de verificação:
- cada tipo de informação do modelo funcional tem exactamente uma fonte oficial;
- a política de versões define quando se cria versão e garante recuperabilidade;
- as regras impedem valores operacionais concorrentes entre BD e Markdown (requisito RT-04 da baseline);
- as dependências do levantamento técnico estão registadas como ponto a validar, não como decisão.

O que não deve ser feito:
- não desenhar esquema de base de dados, chaves ou estruturas de pastas de armazenamento;
- não decidir tecnologia de armazenamento (pertence a F0-B11);
- não deixar tipos de informação sem classificação;
- não reproduzir a baseline.

Fecho e registo obrigatório:

1. cria ou actualiza docs/gestao/02_fase_0_preparacao/pipelines/04_dados_contexto_seguranca/resultados_execucao/prompt_01_resultado.md;
2. actualiza apenas a linha correspondente em docs/gestao/01_status_pipelines.md;
3. acrescenta uma linha curta em docs/gestao/05_diario_execucao_ia.md;
4. actualiza docs/gestao/00_painel_execucao_global.md apenas se mudar o estado, pipeline actual, último prompt, próximo prompt ou bloqueio;
5. actualiza decisões, riscos, validações e docs/produto/ apenas se os critérios definidos em docs/gestao/README.md forem aplicáveis.

Não reescrevas documentos completos, não dupliques detalhes e não copies logs extensos.

Não avances para o prompt seguinte.
```

## Prompt 02 (sonnet) — Definir e testar o pacote de contexto para IA

```prompt
Iteração 02

Actua como engenheiro de prompts e analista funcional.

Identificadores: Fase F0; Pipeline F0-P04; Prompt F0-P04-PR02.
Itens do backlog tratados: F0-B09 (F0-09). Decisão bloqueadora: DB-09.

Objectivo: padronizar o pacote de contexto para execução assistida por IA (utilização manual, local ou externa), o formato de importação do resultado, e testar o pacote manualmente.

Pré-requisitos: fluxo aprovado (F0-P02-PR02) e fronteira BD/Markdown aprovada (F0-P04-PR01).

Contexto obrigatório:
- docs/gestao/02_fase_0_preparacao/01_backlog.md (item F0-B09)
- docs/gestao/02_fase_0_preparacao/artefactos/02_fluxo_e_modelo_funcional.md (passos de execução assistida)
- docs/gestao/02_fase_0_preparacao/artefactos/05_fonte_de_verdade_bd_markdown.md
- docs/gestao/01_baseline/03_arquitetura.md (secções 8.3 e 11.10)

Ficheiros que não devem ser alterados:
- todos os documentos de docs/gestao/01_baseline/

Trabalho a realizar:
1. definir a estrutura do pacote de contexto: objectivo, função, instruções, produto, documentos com versões, restrições e formato esperado do resultado;
2. definir o formato de exportação (texto único, ficheiros separados ou ambos) e o formato de importação do resultado (texto, Markdown ou ficheiro), como decisões propostas;
3. garantir que o pacote identifica as fontes e separa instruções da função do conteúdo documental (mitigação de prompt injection, arquitectura secção 11.10);
4. produzir um pacote de exemplo com conteúdo não sensível ou fictício controlado;
5. testar manualmente o pacote numa IA externa ou local: se a IA executora não puder realizar o teste, preparar o procedimento passo a passo para o operador humano, marcar o estado de execução como Parcial e registar o pedido;
6. guardar a evidência do teste em resultados_execucao/evidencias/ e referenciá-la por caminho.

Artefacto a criar:
- docs/gestao/02_fase_0_preparacao/artefactos/07_pacote_contexto_ia.md

O artefacto deve separar explicitamente, em secções próprias:
- factos, com referência à fonte;
- decisões propostas (estrutura e formatos), com estado Proposta / A validar;
- hipóteses assumidas;
- pontos a validar por humano;
- referência à evidência do teste.

Critérios de verificação:
- a estrutura cobre os sete elementos exigidos pela baseline (F0-09);
- o pacote de exemplo existe e não contém dados sensíveis;
- o teste manual foi executado com evidência registada, ou o estado é Parcial com procedimento entregue ao humano;
- as fontes estão identificadas no pacote e as instruções estão separadas do conteúdo documental.

O que não deve ser feito:
- não desenhar APIs, conectores ou integração automática com IA;
- não optimizar o formato para um único modelo ou fornecedor;
- não usar informação sensível no teste;
- não declarar o teste como concluído sem evidência.

Fecho e registo obrigatório:

1. cria ou actualiza docs/gestao/02_fase_0_preparacao/pipelines/04_dados_contexto_seguranca/resultados_execucao/prompt_02_resultado.md;
2. actualiza apenas a linha correspondente em docs/gestao/01_status_pipelines.md;
3. acrescenta uma linha curta em docs/gestao/05_diario_execucao_ia.md;
4. actualiza docs/gestao/00_painel_execucao_global.md apenas se mudar o estado, pipeline actual, último prompt, próximo prompt ou bloqueio;
5. actualiza decisões, riscos, validações e docs/produto/ apenas se os critérios definidos em docs/gestao/README.md forem aplicáveis.

Não reescrevas documentos completos, não dupliques detalhes e não copies logs extensos.

Não avances para o prompt seguinte.
```

## Prompt 03 (opus) — Definir os requisitos mínimos de segurança do MVP

```prompt
Iteração 03

Actua como analista de segurança e arquitecto de solução.

Identificadores: Fase F0; Pipeline F0-P04; Prompt F0-P04-PR03.
Itens do backlog tratados: F0-B12 (F0-12). Decisão bloqueadora: DB-12.

Objectivo: estabelecer o checklist de controlos de segurança não adiáveis do MVP, incluindo o nível de auditoria e as regras de validação humana.

Pré-requisitos: artefactos 08_modelo_utilizadores_empresas.md e 09_stack_repositorio_padroes.md aprovados (pipeline F0-P05, prompts 01 e 02). Não executar este prompt antes dessa aprovação.

Contexto obrigatório:
- docs/gestao/02_fase_0_preparacao/01_backlog.md (item F0-B12)
- docs/gestao/02_fase_0_preparacao/artefactos/08_modelo_utilizadores_empresas.md
- docs/gestao/02_fase_0_preparacao/artefactos/09_stack_repositorio_padroes.md
- docs/gestao/01_baseline/03_arquitetura.md (secções 7 e 11)
- docs/gestao/01_baseline/05_backlog_macro.md (requisitos RT-01, RT-02, RT-05, RT-07 e RT-08)

Ficheiros que não devem ser alterados:
- todos os documentos de docs/gestao/01_baseline/

Trabalho a realizar:
1. derivar o checklist mínimo nos seis domínios da baseline: isolamento, autorização, protecção documental, auditoria, segredos e exportação;
2. definir o nível de auditoria do MVP: lista fechada de eventos auditáveis;
3. definir as regras de validação humana: que operações exigem aprovação explícita e por quem;
4. definir a política de envio de informação para serviços externos de IA;
5. registar requisitos de retenção, eliminação e residência de dados conhecidos, marcando os dependentes de mercado como A validar;
6. garantir que cada controlo é verificável na Fase 1 (teste, demonstração ou inspecção).

Artefacto a criar:
- docs/gestao/02_fase_0_preparacao/artefactos/10_requisitos_seguranca_mvp.md

O artefacto deve separar explicitamente, em secções próprias:
- factos, com referência à fonte;
- decisões propostas (checklist e políticas), com estado Proposta / A validar;
- hipóteses assumidas;
- pontos a validar por humano.

Critérios de verificação:
- o checklist cobre os seis domínios exigidos pela baseline (F0-12);
- cada controlo indica como será verificado na Fase 1;
- a lista de eventos auditáveis está fechada;
- a política de envio de dados a IA externa está definida;
- nenhum controlo declarado não adiável pela baseline foi adiado.

O que não deve ser feito:
- não escrever configuração, código ou políticas técnicas de infraestrutura;
- não produzir um checklist genérico sem critério de verificação;
- não decidir requisitos legais de mercado sem base; marcar como A validar;
- não reproduzir a baseline.

Fecho e registo obrigatório:

1. cria ou actualiza docs/gestao/02_fase_0_preparacao/pipelines/04_dados_contexto_seguranca/resultados_execucao/prompt_03_resultado.md;
2. actualiza apenas a linha correspondente em docs/gestao/01_status_pipelines.md;
3. acrescenta uma linha curta em docs/gestao/05_diario_execucao_ia.md;
4. actualiza docs/gestao/00_painel_execucao_global.md apenas se mudar o estado, pipeline actual, último prompt, próximo prompt ou bloqueio;
5. actualiza decisões, riscos, validações e docs/produto/ apenas se os critérios definidos em docs/gestao/README.md forem aplicáveis.

Não reescrevas documentos completos, não dupliques detalhes e não copies logs extensos.

Não avances para o prompt seguinte.
```


docs\gestao\02_fase_0_preparacao\pipelines\05_stack_piloto_e_fecho\01_pipeline.md

Pipeline: Stack, piloto e fecho da Fase 0

* Identificador: F0-P05 (Fase F0).
* Itens do backlog cobertos: F0-B08, F0-B10, F0-B11, F0-B13, F0-B14 (rastreiam F0-08, F0-10, F0-11, F0-13, F0-14 da baseline).
* Artefactos produzidos: `artefactos/09_stack_repositorio_padroes.md`; `artefactos/08_modelo_utilizadores_empresas.md`; `artefactos/06_regras_visao_atencao.md`; `artefactos/11_plano_piloto.md`; `artefactos/12_decisao_saida_fase_0.md`.
* Pré-requisitos: os Prompts 01 e 02 dependem apenas do backlog e da pipeline F0-P02 (Prompt 02); o Prompt 03 exige os artefactos 03 e 04 aprovados (pipeline F0-P03); o Prompt 05 exige todos os artefactos 01 a 11 aprovados.
* Ordem entre pipelines: os Prompts 01 e 02 devem ser executados antes do Prompt 03 da pipeline F0-P04 (segurança), que deles depende.
* Execução: prompts pela ordem indicada; um humano entrega cada prompt e revê o resultado antes do seguinte.

## Prompt 01 (sonnet) — Levantar e confirmar stack, repositório e padrões

```prompt
Iteração 01

Actua como arquitecto de solução e engenheiro responsável pelo levantamento técnico.

Identificadores: Fase F0; Pipeline F0-P05; Prompt F0-P05-PR01.
Itens do backlog tratados: F0-B11 (F0-11). Decisão bloqueadora: DB-11.

Objectivo: levantar o estado real do ambiente de desenvolvimento e confrontá-lo com as decisões assumidas na arquitectura, fechando as questões de stack, repositório, autenticação, armazenamento e deploy.

Contexto obrigatório:
- docs/gestao/02_fase_0_preparacao/01_backlog.md (item F0-B11)
- docs/gestao/01_baseline/03_arquitetura.md (secções 1, 2.10, 7.1 e 13)
- a raiz do repositório actual (listar a estrutura existente; não ler documentos da baseline para este fim)

Ficheiros que não devem ser alterados:
- todos os documentos de docs/gestao/01_baseline/

Trabalho a realizar:
1. levantar o que existe realmente no repositório: estrutura, código, configuração, CI/CD; registar como facto que o repositório contém apenas documentação, se for o caso, sem inventar stack;
2. confrontar cada decisão assumida da arquitectura (secção 1: React/TypeScript, Django/DRF, PostgreSQL, Markdown em ficheiros, object storage, sem Redis/Celery/Kafka/Kubernetes) com o ambiente real: confirmar, marcar desvio ou marcar A validar;
3. propor decisão sobre autenticação: reutilizar existente ou Django Auth;
4. propor decisão sobre armazenamento documental no piloto: filesystem ou S3 compatível;
5. identificar a plataforma de deploy disponível ou registar a ausência como ponto a validar;
6. registar convenções e padrões a adoptar (estrutura de repositório, testes, CI/CD) como propostas, sem os criar.

Artefacto a criar:
- docs/gestao/02_fase_0_preparacao/artefactos/09_stack_repositorio_padroes.md

O artefacto deve separar explicitamente, em secções próprias:
- factos (o que existe realmente), com evidência;
- decisões propostas, com estado Proposta / A validar;
- hipóteses assumidas;
- pontos a validar por humano.

Critérios de verificação:
- cada decisão assumida da arquitectura está confirmada, com desvio justificado ou marcada A validar;
- a decisão de autenticação está proposta com justificação;
- a decisão de armazenamento do piloto está proposta;
- a plataforma de deploy está identificada ou o ponto está registado como A validar;
- nenhum facto declara stack ou infraestrutura que não exista.

O que não deve ser feito:
- não criar estrutura de repositório, código, configuração ou CI/CD;
- não inicializar frameworks nem instalar dependências;
- não assumir infraestrutura inexistente como disponível;
- não reproduzir a baseline.

Fecho e registo obrigatório:

1. cria ou actualiza docs/gestao/02_fase_0_preparacao/pipelines/05_stack_piloto_e_fecho/resultados_execucao/prompt_01_resultado.md;
2. actualiza apenas a linha correspondente em docs/gestao/01_status_pipelines.md;
3. acrescenta uma linha curta em docs/gestao/05_diario_execucao_ia.md;
4. actualiza docs/gestao/00_painel_execucao_global.md apenas se mudar o estado, pipeline actual, último prompt, próximo prompt ou bloqueio;
5. actualiza decisões, riscos, validações e docs/produto/ apenas se os critérios definidos em docs/gestao/README.md forem aplicáveis.

Não reescrevas documentos completos, não dupliques detalhes e não copies logs extensos.

Não avances para o prompt seguinte.
```

## Prompt 02 (sonnet) — Decidir o modelo de utilizadores e empresas

```prompt
Iteração 02

Actua como Product Owner e arquitecto de solução.

Identificadores: Fase F0; Pipeline F0-P05; Prompt F0-P05-PR02.
Itens do backlog tratados: F0-B10 (F0-10). Decisão bloqueadora: DB-10.

Objectivo: propor as decisões formais sobre o modelo de utilizadores e empresas do MVP: empresas por conta, individual ou multiutilizador, e papéis mínimos.

Pré-requisito: artefacto 01_segmento_e_caso_uso.md aprovado (F0-P02-PR01).

Contexto obrigatório:
- docs/gestao/02_fase_0_preparacao/01_backlog.md (item F0-B10)
- docs/gestao/02_fase_0_preparacao/artefactos/01_segmento_e_caso_uso.md
- docs/gestao/01_baseline/03_arquitetura.md (secção 7.2)
- docs/gestao/01_baseline/04_roadmap_faseado.md (secção 4.2, acesso e empresa)

Ficheiros que não devem ser alterados:
- todos os documentos de docs/gestao/01_baseline/

Trabalho a realizar:
1. propor a decisão: uma ou várias empresas por conta no MVP, com justificação assente no segmento aprovado;
2. propor a decisão: utilização individual ou multiutilizador no MVP;
3. confirmar os papéis mínimos (proposta da arquitectura: Owner, Editor, Reviewer, Viewer) ou propor um subconjunto para o MVP;
4. indicar como a estrutura fica preparada para multiempresa e memberships futuras sem as expor na experiência do MVP;
5. identificar o impacto das decisões em isolamento e segurança, para consumo do item F0-B12.

Artefacto a criar:
- docs/gestao/02_fase_0_preparacao/artefactos/08_modelo_utilizadores_empresas.md

O artefacto deve separar explicitamente, em secções próprias:
- factos, com referência à fonte;
- decisões propostas (as três decisões), com estado Proposta / A validar;
- hipóteses assumidas;
- pontos a validar por humano.

Critérios de verificação:
- as três decisões estão propostas com justificação;
- a coerência com o segmento aprovado está explícita;
- a preparação para evolução futura está descrita sem inflacionar o MVP;
- o impacto em isolamento está identificado para F0-B12.

O que não deve ser feito:
- não desenhar tabelas, esquemas ou modelos de permissões técnicos;
- não incluir convites, notificações ou permissões avançadas no MVP;
- não fechar as decisões como aprovadas; ficam A validar;
- não reproduzir a baseline.

Fecho e registo obrigatório:

1. cria ou actualiza docs/gestao/02_fase_0_preparacao/pipelines/05_stack_piloto_e_fecho/resultados_execucao/prompt_02_resultado.md;
2. actualiza apenas a linha correspondente em docs/gestao/01_status_pipelines.md;
3. acrescenta uma linha curta em docs/gestao/05_diario_execucao_ia.md;
4. actualiza docs/gestao/00_painel_execucao_global.md apenas se mudar o estado, pipeline actual, último prompt, próximo prompt ou bloqueio;
5. actualiza decisões, riscos, validações e docs/produto/ apenas se os critérios definidos em docs/gestao/README.md forem aplicáveis.

Não reescrevas documentos completos, não dupliques detalhes e não copies logs extensos.

Não avances para o prompt seguinte.
```

## Prompt 03 (sonnet) — Definir as regras da visão de atenção

```prompt
Iteração 03

Actua como Product Owner e analista funcional.

Identificadores: Fase F0; Pipeline F0-P05; Prompt F0-P05-PR03.
Itens do backlog tratados: F0-B08 (F0-08). Decisão bloqueadora: DB-08.

Objectivo: definir regras determinísticas e explicáveis para a visão de atenção do MVP.

Pré-requisitos: artefactos 03_estados_e_transicoes.md e 04_ficha_administrativa_produto.md aprovados (pipeline F0-P03). Não executar este prompt antes dessa aprovação.

Contexto obrigatório:
- docs/gestao/02_fase_0_preparacao/01_backlog.md (item F0-B08)
- docs/gestao/02_fase_0_preparacao/artefactos/03_estados_e_transicoes.md
- docs/gestao/02_fase_0_preparacao/artefactos/04_ficha_administrativa_produto.md
- docs/gestao/01_baseline/04_roadmap_faseado.md (secção 3.2, definição da visão de atenção)

Contexto opcional:
- docs/gestao/01_baseline/03_arquitetura.md (secção 15.7, regras calculadas vs persistidas)

Ficheiros que não devem ser alterados:
- todos os documentos de docs/gestao/01_baseline/

Trabalho a realizar:
1. definir uma regra determinística por sinal: produto sem revisão, decisão pendente, pendência vencida, resultado por validar, documento sinalizado como desactualizado;
2. para cada regra, definir a condição objectiva, o motivo apresentável ao utilizador e os parâmetros com valores iniciais propostos (por exemplo, prazo de revisão);
3. confirmar que cada regra depende apenas de dados definidos nos estados (F0-B05) e na ficha do produto (F0-B07);
4. confirmar a abordagem de cálculo simples, sem persistência de indicadores, conforme a arquitectura.

Artefacto a criar:
- docs/gestao/02_fase_0_preparacao/artefactos/06_regras_visao_atencao.md

O artefacto deve separar explicitamente, em secções próprias:
- factos, com referência à fonte;
- decisões propostas (regras e parâmetros), com estado Proposta / A validar;
- hipóteses assumidas;
- pontos a validar por humano.

Critérios de verificação:
- cada regra tem condição objectiva e motivo apresentável ao utilizador;
- cada regra depende apenas de dados definidos em F0-B05 e F0-B07;
- os parâmetros têm valores iniciais propostos;
- não existem regras baseadas em heurísticas não explicáveis.

O que não deve ser feito:
- não definir queries, algoritmos ou detalhes de implementação;
- não criar regras dependentes de funcionalidades fora do MVP;
- não multiplicar sinais para além dos cinco previstos sem justificação;
- não reproduzir a baseline.

Fecho e registo obrigatório:

1. cria ou actualiza docs/gestao/02_fase_0_preparacao/pipelines/05_stack_piloto_e_fecho/resultados_execucao/prompt_03_resultado.md;
2. actualiza apenas a linha correspondente em docs/gestao/01_status_pipelines.md;
3. acrescenta uma linha curta em docs/gestao/05_diario_execucao_ia.md;
4. actualiza docs/gestao/00_painel_execucao_global.md apenas se mudar o estado, pipeline actual, último prompt, próximo prompt ou bloqueio;
5. actualiza decisões, riscos, validações e docs/produto/ apenas se os critérios definidos em docs/gestao/README.md forem aplicáveis.

Não reescrevas documentos completos, não dupliques detalhes e não copies logs extensos.

Não avances para o prompt seguinte.
```

## Prompt 04 (sonnet) — Preparar o plano do piloto

```prompt
Iteração 04

Actua como Product Owner e gestor de execução.

Identificadores: Fase F0; Pipeline F0-P05; Prompt F0-P05-PR04.
Itens do backlog tratados: F0-B13 (F0-13). Decisão bloqueadora: DB-13.

Objectivo: definir como o MVP será validado: participantes, produtos reais, actividades, recolha de feedback e critérios de sucesso.

Pré-requisito: artefacto 01_segmento_e_caso_uso.md aprovado (F0-P02-PR01).

Contexto obrigatório:
- docs/gestao/02_fase_0_preparacao/01_backlog.md (item F0-B13)
- docs/gestao/02_fase_0_preparacao/artefactos/01_segmento_e_caso_uso.md (perfis candidatos a piloto)
- docs/gestao/01_baseline/04_roadmap_faseado.md (secção 4.7, validações necessárias)
- docs/gestao/01_baseline/02_visao_do_produto.md (secções 11 e 15.1)

Ficheiros que não devem ser alterados:
- todos os documentos de docs/gestao/01_baseline/

Trabalho a realizar:
1. propor os participantes do piloto a partir dos perfis candidatos; a identificação nominal é do operador humano e deve ficar como ponto a validar se não for fornecida;
2. definir os produtos reais a registar no piloto e os dados a utilizar;
3. definir as actividades do piloto e a duração proposta;
4. mapear as validações do roadmap (secção 4.7) para actividades concretas do piloto;
5. definir critérios de sucesso mensuráveis, ligados à tese do MVP, e o método de recolha de feedback;
6. delimitar o que fica fora do piloto.

Artefacto a criar:
- docs/gestao/02_fase_0_preparacao/artefactos/11_plano_piloto.md

O artefacto deve separar explicitamente, em secções próprias:
- factos, com referência à fonte;
- decisões propostas (plano), com estado Proposta / A validar;
- hipóteses assumidas;
- pontos a validar por humano (incluindo a identificação nominal dos participantes, se em falta).

Critérios de verificação:
- os participantes estão identificados ou o pedido de identificação está registado como ponto a validar;
- os produtos reais e os dados do piloto estão definidos;
- cada validação do roadmap (secção 4.7) está mapeada para uma actividade;
- os critérios de sucesso são mensuráveis e ligados à tese do MVP;
- os limites do piloto estão explícitos.

O que não deve ser feito:
- não definir metas quantitativas sem base; propô-las como hipóteses;
- não incluir actividades que dependam de funcionalidades fora do MVP;
- não inventar participantes nem dados pessoais;
- não reproduzir a baseline.

Fecho e registo obrigatório:

1. cria ou actualiza docs/gestao/02_fase_0_preparacao/pipelines/05_stack_piloto_e_fecho/resultados_execucao/prompt_04_resultado.md;
2. actualiza apenas a linha correspondente em docs/gestao/01_status_pipelines.md;
3. acrescenta uma linha curta em docs/gestao/05_diario_execucao_ia.md;
4. actualiza docs/gestao/00_painel_execucao_global.md apenas se mudar o estado, pipeline actual, último prompt, próximo prompt ou bloqueio;
5. actualiza decisões, riscos, validações e docs/produto/ apenas se os critérios definidos em docs/gestao/README.md forem aplicáveis.

Não reescrevas documentos completos, não dupliques detalhes e não copies logs extensos.

Não avances para o prompt seguinte.
```

## Prompt 05 (opus) — Rever a fase e propor a decisão de saída

```prompt
Iteração 05

Actua como revisor de consistência, Product Owner sénior e gestor de execução.

Identificadores: Fase F0; Pipeline F0-P05; Prompt F0-P05-PR05.
Itens do backlog tratados: F0-B14 (F0-14). Decisão bloqueadora: DB-14.

Objectivo: realizar a revisão cruzada dos artefactos da Fase 0, consolidar o congelamento do escopo do MVP e propor a decisão formal de saída da fase.

Pré-requisito: todos os artefactos 01 a 11 de docs/gestao/02_fase_0_preparacao/artefactos/ criados e aprovados por humano. Não executar este prompt com artefactos em falta ou por aprovar.

Contexto obrigatório:
- docs/gestao/02_fase_0_preparacao/01_backlog.md (item F0-B14 e secção 8, critérios de saída)
- todos os artefactos de docs/gestao/02_fase_0_preparacao/artefactos/ (01 a 11)

Contexto opcional:
- docs/gestao/01_baseline/04_roadmap_faseado.md (secção 11.1, critérios de avanço)

Ficheiros que não devem ser alterados:
- todos os documentos de docs/gestao/01_baseline/
- os artefactos 01 a 11 (incoerências são registadas, não corrigidas silenciosamente)

Trabalho a realizar:
1. revisão cruzada: verificar coerência entre artefactos (fluxo vs entidades vs estados vs ficha vs regras de atenção vs fonte de verdade vs pacote de contexto vs utilizadores vs stack vs segurança vs piloto); registar cada incoerência encontrada com referência aos artefactos afectados;
2. verificar cada critério de saída da Fase 0 (backlog, secção 8) e indicar o artefacto que o evidencia;
3. consolidar a lista final de escopo do MVP: incluído, excluído, opcional e adiado, a partir dos limites preliminares e das decisões aprovadas;
4. verificar que nenhuma decisão bloqueadora (DB-01 a DB-13) permanece em aberto; se alguma permanecer, marcar a fase como Bloqueado e identificar o que falta;
5. propor a decisão formal de saída: avançar para a Fase 1, corrigir itens específicos, ou não avançar, com justificação;
6. indicar que, após aprovação humana, a decisão de saída deve ser registada em docs/gestao/02_log_decisoes_execucao.md com o template DEC definido em docs/gestao/README.md.

Artefacto a criar:
- docs/gestao/02_fase_0_preparacao/artefactos/12_decisao_saida_fase_0.md

O artefacto deve separar explicitamente, em secções próprias:
- factos (estado de cada critério de saída, com evidência);
- incoerências encontradas na revisão cruzada;
- decisões propostas (escopo congelado e decisão de saída), com estado Proposta / A validar;
- hipóteses assumidas;
- pontos a validar por humano.

Critérios de verificação:
- todos os critérios de saída da secção 8 do backlog estão verificados com referência ao artefacto que os evidencia;
- a lista de escopo congelado não contém itens A validar pendentes, ou a fase está marcada como Bloqueado;
- todas as incoerências encontradas estão registadas com os artefactos afectados;
- a decisão de saída está proposta com justificação e aguarda aprovação humana.

O que não deve ser feito:
- não aprovar a saída da fase; a aprovação é humana;
- não corrigir artefactos para eliminar incoerências sem as registar;
- não iniciar a decomposição do backlog do MVP;
- não declarar critérios cumpridos sem evidência.

Fecho e registo obrigatório:

1. cria ou actualiza docs/gestao/02_fase_0_preparacao/pipelines/05_stack_piloto_e_fecho/resultados_execucao/prompt_05_resultado.md;
2. actualiza apenas a linha correspondente em docs/gestao/01_status_pipelines.md;
3. acrescenta uma linha curta em docs/gestao/05_diario_execucao_ia.md;
4. actualiza docs/gestao/00_painel_execucao_global.md apenas se mudar o estado, pipeline actual, último prompt, próximo prompt ou bloqueio;
5. actualiza decisões, riscos, validações e docs/produto/ apenas se os critérios definidos em docs/gestao/README.md forem aplicáveis.

Não reescrevas documentos completos, não dupliques detalhes e não copies logs extensos.

Não avances para o prompt seguinte.
```


