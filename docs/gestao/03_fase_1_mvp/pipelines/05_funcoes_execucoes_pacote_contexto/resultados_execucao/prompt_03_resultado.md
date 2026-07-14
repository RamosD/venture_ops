---
fase: F1
pipeline: F1-P05
prompt: F1-P05-PR03
modelo: claude-opus-4-8
inicio: 2026-07-14 03:00
fim: 2026-07-14 03:45
estado_execucao: Concluído
estado_revisao: Não revista
commit: não criado
---

# Resultado — Prompt 03 — Interface de preparação da execução

## 1. Veredicto

**Concluído.** A ficha do produto passa a ter uma secção **Execuções** real: é
possível **preparar** uma execução no browser (escolhendo função `active`, modo
manual e versões documentais exactas — empresariais ou do produto), **listar** as
execuções do produto e **consultar** o contexto congelado (snapshots de função e
produto, `instruction_version`, documentos ordenados com versão e checksum). A
indicação "Execuções indisponíveis" foi substituída; `DocumentSection`,
`DecisionSection` e `WorkItemSection` mantêm-se. Sem edição, eliminação,
transições de estado, chamadas a IA nem resultados simulados.

**Regressão verde:** frontend **73 testes OK** (57 anteriores + 16 novos) +
`npm run build` OK; backend **365 OK** (inalterado; documentos revalidados com as
duas adições de leitura). Sem drift.

## 2. Componentes

- **`ExecutionSection`** — container da ficha (lista/criação/detalhe; sem store/
  router); filtra sempre pelo produto actual; resolve nomes de função (inclui
  inactivas, para execuções passadas).
- **`ExecutionList`** — título, função, modo, estado e data; sem estados/
  resultados fictícios.
- **`ExecutionCreateForm`** — campos do pedido (`title`, `objective`,
  `request_instructions`, `constraints?`, `expected_output_format`,
  `execution_mode`), selecção de função `active` e do contexto; evita submissão
  duplicada (`busy` + `disabled`); trata 400/403/404/409.
- **`ContextDocumentSelector`** — candidatos = documentos empresariais + do
  produto actual; escolha de versão exacta (histórico); ordenação Subir/Descer;
  `purpose` opcional por documento.
- **`FunctionSnapshotView`** — apresenta o snapshot imutável da função.
- **`ExecutionDetail`** — metadados + snapshots + `instruction_version` + contexto
  ordenado; distingue snapshot (congelado) de marcadores actuais.
- **`api/executions.ts`** + **`labels.ts`** — contratos e rótulos.

## 3. Contratos e adições mínimas de leitura (autorizadas pelo prompt)

A UI consome os endpoints existentes de PR02 (`/api/v1/executions`),
`/api/v1/functions` (PR01) e `/api/v1/documents` (F1-P04). Foram necessárias duas
**adições de leitura mínimas, aditivas e retrocompatíveis** ao módulo documental
(o prompt autoriza "acrescenta apenas filtro de leitura mínimo"):

1. **`empresarial=true|false`** no `GET /api/v1/documents` — filtra documentos ao
   nível da empresa (`product` NULL), necessário para listar candidatos
   empresariais sem expor documentos de outros produtos.
2. **`id` (UUID da versão)** exposto em `DocumentVersionSerializer` — a selecção de
   contexto precisa do identificador exacto e imutável da `DocumentVersion` para o
   enviar ao serviço de execução (que referencia versões, não números). Campo
   apenas de leitura; nenhum teste existente assume um conjunto de chaves fechado
   (suite documental **54 OK**).

Nenhuma outra alteração a módulos anteriores; nenhuma correcção silenciosa.

## 4. Selecção de contexto (regras reflectidas na UI)

- **Candidatos:** só documentos **empresariais** e do **produto actual** — nunca de
  outros produtos.
- **`export_policy=denied`** → candidato **desactivado**, sem botão de selecção
  (aviso "Não seleccionável — exportação recusada").
- **`export_policy=confirm`** → seleccionável, com aviso "Exigirá confirmação antes
  da geração" (na selecção e no contexto escolhido).
- **`is_outdated`** → aviso "Documento desactualizado", mas **permanece
  seleccionável**.
- **Versão exacta / histórica:** ao escolher um documento carrega-se o histórico de
  versões (`/documents/{id}/versions`); a versão actual (número mais alto) é o
  defeito, mas qualquer versão anterior é seleccionável.
- **Documento de instruções da função:** apresentado **à parte** (nota) e excluído
  dos candidatos de dados — não pode ser duplicado.
- **Ordenação:** controlos **Subir/Descer** (sem drag-and-drop nem biblioteca
  adicional); a `order` enviada corresponde à ordem visível.
- **Pelo menos um** documento é exigido antes de submeter.

## 5. Funções no formulário

Apresenta apenas funções `active` (filtro `status=active` no servidor); mostra
`actor_type`, propósito e `requires_approval` da função escolhida. **Não** permite
criar/editar funções dentro do formulário — o catálogo continua na área
**Funções** (PR01).

## 6. Detalhe congelado

Após criar, abre o detalhe com: **estado Preparada**; **snapshot da função**
(retrato no momento da criação, com aviso explícito); **snapshot do produto**;
**`instruction_version`** (versão exacta ou "sem documento de instruções");
**documentos de contexto** por ordem, com `version_number` e checksum abreviado. O
detalhe distingue claramente o **snapshot congelado** dos **marcadores actuais**
dos documentos (que podem ter mudado). Como a apresentação lê o detalhe imutável
do servidor, alterações posteriores à função ou aos documentos **não** mudam o que
é apresentado (imutabilidade garantida e testada no backend em PR02).

## 7. Regras respeitadas

Sem edição/eliminação da execução; sem transições de estado; sem chamadas a IA;
sem resultado simulado; cliente HTTP central reutilizado (sessão + CSRF); 400/403/
404/409 tratados; submissão duplicada evitada.

## 8. Testes (16 entradas, 22 casos do guião)

`executions.test.tsx`: estado vazio; listagem; só funções `active`; `denied`
indisponível; `confirm` com aviso; `is_outdated` com aviso seleccionável; versão
exacta; versão histórica; ordenação Subir/Descer; exigência de ≥1 documento;
criação em `manual_local` **e** `manual_external`; detalhe mostra estado
`prepared`, `function_snapshot`, `product_snapshot`, `instruction_version` e
ordem/versão/checksum; submissão duplicada evitada (uma só criação); erro 400
tratado; ausência de transições/resultados/IA no detalhe. Regressão de portefólio/
documentos/decisões/pendências verde (o teste de portefólio foi actualizado para a
secção real de execuções). Backend documental **54 OK** (adições revalidadas).

**Nota honesta sobre a demonstração:** o fluxo ponta a ponta foi exercido pelos
testes de componente (drivam criação → detalhe → snapshots → versões exactas) e
pelo `build`. A imutabilidade perante alterações posteriores à função/documento é
garantida e testada ao nível do backend (PR02). Uma demonstração no browser contra
o stack em execução exigiria reconstruir as imagens Docker (não efectuado nesta
iteração); os testes automáticos cobrem o comportamento exigido.

## 9. VAL e reservas

- **VAL-007 → Parcial** (função agora seleccionável e usada na preparação de
  execução via UI; ciclo completo com resultados em F1-P06).
- **VAL-008 → Parcial** (contexto por versões exactas preparável e consultável na
  UI; **geração** fiel do pacote e `export_policy` efectiva em F1-P05-PR04).
- **VAL-002/VAL-012** reforçadas (Parciais).
- Reservas: geração do pacote (PR04); comandos funcionais e transições (F1-P06).
  Sem desvio estrutural → **nenhuma decisão global criada**.

## 10. Estado final e próximo passo

- **F1-P05 Em execução (3/6).** Estado de revisão: **Não revista**.
- **Próximo prompt recomendado: F1-P05-PR04** (geração do pacote de contexto com
  políticas efectivas). **Não iniciado nesta iteração.**
