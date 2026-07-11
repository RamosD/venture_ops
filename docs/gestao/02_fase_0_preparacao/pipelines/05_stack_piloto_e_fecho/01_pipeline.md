# Pipeline: Stack, piloto e fecho da Fase 0

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
