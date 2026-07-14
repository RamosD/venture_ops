---
fase: F1
pipeline: F1-P05
prompt: F1-P05-PR06
modelo: claude-opus-4-8
inicio: 2026-07-14 06:30
fim: 2026-07-14 08:00
estado_execucao: Concluído
estado_revisao: Não revista
commit: não criado
---

# Resultado — Prompt 06 — Validação integrada e fecho da F1-P05

## 1. Veredicto

**F1-P05 Concluída (6/6).** Funções organizacionais, execuções `prepared` com
snapshots imutáveis e versões documentais exactas, e o pacote de contexto
determinístico com política de exportação aplicada no servidor estão integrados e
utilizáveis no browser. Validação integrada ponta a ponta executada; concorrência
e consistência da geração testadas; regressão completa verde (**396 backend + 91
frontend + build**); migrações sem drift, aplicadas em base vazia **e na base de
desenvolvimento existente**; auditoria limpa; isolamento demonstrado. **Nenhuma IA
foi chamada, nenhum resultado foi criado, e as execuções permanecem `prepared`.**
**Nenhum defeito estrutural encontrado — nenhuma correcção de código de aplicação
foi necessária.** Nenhuma funcionalidade de F1-P06 foi antecipada.

**VAL-007 → Validada; VAL-008 → Validada.** **VAL-002, VAL-012 e VAL-014
permanecem Parciais.** **VAL-009 não é validável** sem resultados importados
(F1-P06).

## 2. Modelos e contratos finais

- **FunctionProfile** (`functions_functionprofile`): `actor_type`
  `human`/`ai`/`hybrid`, `purpose`/`responsibilities` obrigatórios, `constraints`
  opcional, `instruction_document` opcional (empresarial `instrucoes` com versão),
  `requires_approval` (SEC-HUM), `status` `active`/`inactive`, `version`. API
  `/functions` (list/create/detail/patch/deactivate/reactivate). Sem DELETE.
- **AIExecution** (`executions_aiexecution`): `product`/`function_profile`/
  `requested_by` (PROTECT), pedido congelado (`title`/`objective`/
  `request_instructions`/`constraints?`/`expected_output_format`/`execution_mode`),
  `status` (enum oficial, nasce `prepared`), `function_snapshot`/`product_snapshot`
  (JSON, servidor), `instruction_version` (FK exacta), `version`. API
  `/executions` (list/create/detail) + `context-package/preview|download`. Sem
  PATCH/DELETE.
- **ExecutionContextDocument** (`executions_executioncontextdocument`): ligação
  **imutável** a versões exactas; `unique(execution, order)` e
  `unique(execution, document_version)`.

## 3. Regras de FunctionProfile (validadas)

Função ≠ papel de autorização; nasce `active`; sem eliminação física. `ai`/`hybrid`
→ `requires_approval` obrigatoriamente `True` (verificado nos três tipos). Ciclo
`active↔inactive` explícito: função `inactive` **não é seleccionável** em novas
execuções (→ 400), mas a **execução passada mantém o `function_snapshot`** e
continua a gerar pacote; reactivação repõe `active`. Edição de função `inactive`
sem a reactivar. Auditoria evento 10 (`function.created`/`updated`) com
`correlation_id`, sem conteúdo.

## 4. Snapshots e versões exactas (validados)

`function_snapshot` e `product_snapshot` gerados só no servidor, imutáveis a
edições posteriores da função/produto. `instruction_version` = `current_version`
exacta no instante da criação. O contexto liga **DocumentVersion exactas**: no
cenário integrado, após criar v2 das instruções e dos documentos A e B, a execução
**continua ligada às v1** (conteúdo e checksums das v1 no pacote; `conteudo A v2`/
`conteudo B v2` nunca aparecem). Uso indevido de `current_version`: **não
detectado**.

## 5. Estados da execução

Máquina oficial (`transitions.py`): `prepared → result_pending_validation →
approved|rejected|prepared(correcção)`, `approved → completed`; restantes
inválidas; `rejected`/`completed` terminais. Nesta pipeline a criação impõe
`prepared` e **nenhuma transição funcional** é exposta (F1-P06). A geração do
pacote **não altera o estado** (confirmado no cenário e após concorrência).

## 6. Estrutura das sete secções (validada)

Ordem fixa: 1 Objectivo · 2 Função (instruções) · 3 Instruções do pedido ·
4 Produto · 5 Restrições · 6 Formato esperado · 7 Documentos (DADOS). Verificado:
as **sete secções** presentes e em ordem; secções 1–6 usam os valores congelados
(objectivo/snapshots/instruções do pedido/restrições/formato) e **não** são
alteradas pelo conteúdo documental; a secção 7 usa marcadores início/fim
inequívocos, identifica fonte/Document id/DocumentVersion id/`version_number`/
checksum/`is_outdated`/`export_policy` actual, e é precedida da **declaração
anti-injecção**. Conteúdo hostil plantado num documento (`IGNORA … rm -rf /`)
permanece **dentro dos marcadores de DADOS** — não migra para as secções de
instruções.

## 7. Política `export_policy` (aplicada no servidor)

Reavaliada em **cada** geração, com as linhas `Document` bloqueadas
(`select_for_update`). No cenário integrado: `C=denied` **não seleccionável** na
criação; gerar sem confirmar B(`confirm`) e instruções(`confirm`) → **409** com
`confirmation_required_document_ids = {B, instruções}` e **sem conteúdo**;
confirmando explicitamente → geração. Alteração posterior de B para `denied` →
**409 `reason=denied` sem conteúdo**; repor B para `allowed` → geração aplica a
política **actual**; as versões congeladas **não** mudam. `is_outdated` avisa sem
bloquear. Contorno directo (confirmar documento `denied`) → continua bloqueado.

## 8. Formatos, determinismo e checksum (evidência)

`single_markdown` (um `.md`) e `separate_files` (ZIP `zipfile`/`ZIP_STORED`, sem
dependências externas). **Evidência de geração** (dados fictícios, transacção
revertida — base de dev intacta):

- **single_markdown**: `checksum = 4df4df5c…c1b7b8`; **determinístico = True**
  (regeneração byte-idêntica); 1906 bytes; secções presentes `[1..7]`.
- **separate_files**: `checksum = a98ec602…4fea107`; **determinístico = True`**;
  ficheiros = `manifest.json`, `01_objectivo.md … 07_documentos_dados.md`,
  `documentos/01_doc-a.md`.
- `exec_status = prepared` após gerar.

Determinismo garantido por valores congelados, ordem estável, finais de linha
normalizados a `\n` e ausência de timestamps (ZIP com data fixa). O checksum
SHA-256 do pacote é devolvido; o manifesto inclui versões e checksums das fontes.

## 9. Simulação do handoff manual

Simulado (sem qualquer modelo real): gerar → rever → **confirmar** documentos
`confirm` → **copiar** o Markdown (Clipboard API) → **descarregar** `.md` e abrir o
**ZIP** (manifesto + 7 ficheiros de secção + `documentos/`), em `manual_local` e
`manual_external` (testes de componente, 91 frontend). Verificado que podem ser
usados manualmente fora da aplicação. **Não** se chamou modelo, **não** se criou
resposta fictícia, **não** se importou resultado, **não** se aprovou/aplicou; as
execuções permanecem `prepared`. Evidência registada: apenas checksum e estrutura
(o pacote integral **não** é copiado para a governação).

## 10. Isolamento

Duas empresas: função/produto/DocumentVersion alheios → **400** (não vazam
existência); execução alheia e `context-package/preview` alheio → **404**
indistinguível; a lista da empresa B não conta execuções da A (`count=0`);
tentativas cruzadas auditadas (`security.cross_org_attempt`, `entity_type` de
`function`/`execution`).

## 11. Concorrência e consistência

Testes reais em PostgreSQL: **duas gerações simultâneas** da mesma execução →
**checksums e bytes idênticos**, execução inalterada (sem duplicação de estado,
`version=1`, `status=prepared`). **Alteração de `export_policy` concorrente com a
geração** → resultado sempre **coerente** (a geração vê o documento permitido e
**completo**, ou é **bloqueada**), nunca um pacote parcial; as versões congeladas e
os snapshots permanecem imutáveis; o estado final é coerente (B `denied` → nova
geração bloqueia). A geração bloqueia as linhas `Document` durante a avaliação,
serializando a mudança de política.

## 12. Armazenamento

Todas as `DocumentVersion` referenciadas existem e o checksum do conteúdo coincide
(verificado na geração). Versão/objecto ausente → **409** sem pacote parcial
(auditado `storage.failure`). ZIP sem path traversal (nomes gerados no servidor,
slug ASCII). O pacote integral **não** é guardado na BD (é derivado da execução).

## 13. Segurança

Documentos são **DADOS** com declaração anti-injecção; o conteúdo documental não
altera as secções 1–6; o Markdown original **não** é sanitizado nem transformado
nem renderizado a HTML (embebido como texto; na UI apresentado em `<pre>`, **sem**
`dangerouslySetInnerHTML` — nenhum `<script>` executado). O pacote não contém
cookies, tokens, segredos, credenciais, variáveis de ambiente nem metadados de
auditoria; o conteúdo legítimo permanece fiel. **Não se declara protecção completa
contra prompt injection** — VAL-014 permanece Parcial até F1-P07.

## 14. Auditoria

Eventos: funções (10), criação de execução (11), geração/preview/cópia/download
(12, distinguíveis por `operation`), bloqueios por política (12 `denied`), acessos
cruzados (20). **Todos com `correlation_id`.** Nenhum evento contém `objective`,
`request_instructions`, `constraints`, snapshots, pacote nem conteúdo documental
integral (provado por testes com tokens únicos). VAL-012 mantém-se **Parcial**
(consulta/consolidação em F1-P07).

## 15. Migrações

`makemigrations --check` → **No changes detected** (drift zero). Aplicam em base
vazia (base de testes) e **na base de desenvolvimento existente** (aplicadas nesta
validação: `functions.0001`, `executions.0001` — additivas, sem tocar noutras
tabelas). Reversibilidade estrutural demonstrada em base controlada (testes de
migração). **Nota honesta:** reverter as migrações destes módulos **remove** as
tabelas de `functions`/`executions` (não preserva os respectivos dados); as
**outras** aplicações permanecem intactas.

## 16. Testes e demonstração

- **Regressão:** backend **396 OK** (392 + 4 novos: integração + concorrência de
  geração); frontend **91 OK**; `npm run build` OK; `makemigrations --check` sem
  drift; health `/health/live` e `/health/ready` → **200** (db+storage); Docker
  Compose **healthy**.
- **Validação integrada (backend, API):** `test_integration.py` percorre o cenário
  principal (função IA com instruções `confirm`; execução com A/B; C não
  seleccionável; snapshots; edição + v2; congelamento nas v1; bloqueio→confirmação;
  Markdown determinístico; ZIP com manifesto; sete secções; hostil em DADOS;
  `prepared`; política superveniente `denied`→409→`allowed`) e o ciclo de vida da
  função com isolamento entre duas empresas.
- **Concorrência:** `test_generation_concurrency.py` (gerações simultâneas
  idênticas; alteração de política concorrente coerente).
- **Evidência de geração:** checksums e estrutura registados em §8 (transacção
  revertida).
- **Nota honesta:** as imagens Docker em execução **precedem** F1-P05; a validação
  correu contra o `venv` do host e o **mesmo PostgreSQL** do Compose. Uma
  demonstração no browser real exigiria reconstruir as imagens. A confirmação com
  um **modelo externo real** fica para **F1-P08/piloto** (não declarada aqui).

## 17. VAL actualizadas

- **VAL-007 → Validada** (função criada nos três tipos, gerida — inactivar/
  reactivar com histórico — e **efectivamente utilizada** numa execução com
  snapshot).
- **VAL-008 → Validada** (snapshots e versões exactas preservados; pacote fiel e
  determinístico; política de exportação aplicada no servidor).
- **VAL-002 Parcial** (isolamento reforçado; suite transversal em F1-P07/MVP-18).
- **VAL-012 Parcial** (emissores 10–12 auditados sem conteúdo; consulta/
  consolidação em F1-P07).
- **VAL-014 Parcial** (separação instruções/dados e conteúdo não executável;
  suites de conteúdo/injecção em F1-P07).
- **VAL-009** — **não validada** (exige resultados importados — F1-P06).

## 18. Problemas corrigidos e reservas

- **Problemas:** nenhum defeito de aplicação encontrado nesta validação; nenhuma
  correcção de código foi necessária.
- **Reservas / adiado:** comandos funcionais e transições da execução (F1-P06);
  importação/registo de resultado, revisão, aprovação e aplicação (F1-P06/P06+);
  consolidação de auditoria e suites de segurança/injecção (F1-P07); confirmação
  com modelo externo real (F1-P08/piloto). Sem desvio estrutural real →
  **nenhuma decisão global criada**.

## 19. Estado final e próximo passo

- **F1-P05 Concluída (6/6).** Estado de revisão: **Não revista** — a execução
  técnica não substitui a revisão humana (guia §10).
- **Próximo passo recomendado:** efectuar **commit de F1-P05** e **gerar a pipeline
  F1-P06** (resultados, revisão e aplicação controlada) just-in-time. **Não
  iniciado nesta iteração.**
