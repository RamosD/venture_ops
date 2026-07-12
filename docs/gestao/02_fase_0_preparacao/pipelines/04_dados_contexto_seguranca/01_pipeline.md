# Pipeline: Dados, contexto de IA e segurança

* Identificador: F0-P04 (Fase F0).
* Itens do backlog cobertos: F0-B06, F0-B09, F0-B12 (rastreiam F0-06, F0-09, F0-12 da baseline).
* Artefactos produzidos: `artefactos/05_fonte_de_verdade_bd_markdown.md`; `artefactos/07_pacote_contexto_ia.md`; `artefactos/10_requisitos_seguranca_mvp.md`.
* Pré-requisitos (existência material, não aprovação): fluxo (F0-P02) e modelo funcional (F0-P03-PR01) existentes. O Prompt 03 exige ainda a existência dos artefactos 08 e 09 (pipeline F0-P05, prompts 01 e 02).
* Execução: prompts pela ordem indicada; um humano entrega cada prompt e revê o resultado antes do seguinte.

## Prompt 01 (opus) — Definir a fronteira BD/Markdown e o versionamento

```prompt
Iteração 01

Actua como arquitecto de solução e gestor de configuração documental.

Identificadores: Fase F0; Pipeline F0-P04; Prompt F0-P04-PR01.
Itens do backlog tratados: F0-B06 (F0-06). Decisão bloqueadora: DB-06.

Objectivo: definir, para cada tipo de informação do modelo funcional, a fonte oficial (base de dados ou Markdown), a política de versões documentais e as regras de actualização.

Pré-requisito: secção de modelo funcional existente (F0-P03-PR01). A revisão humana não é exigida para avançar.

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

Pré-requisitos: artefactos de fluxo (F0-P02-PR02) e de fronteira BD/Markdown (F0-P04-PR01) existentes. A revisão humana não é exigida para avançar.

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

Pré-requisitos (existência material, não aprovação): os artefactos 08_modelo_utilizadores_empresas.md e 09_stack_repositorio_padroes.md devem **existir** (pipeline F0-P05, prompts 01 e 02). Não executar este prompt sem esses artefactos; a revisão ou aprovação humana **não** é exigida para avançar.

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
