---
fase: F1
pipeline: F1-P06
prompt: F1-P06-PR02
modelo: claude-opus-4-8
inicio: 2026-07-14 09:40
fim: 2026-07-14 10:20
estado_execucao: Concluído
estado_revisao: Não revista
commit: não criado
---

# Resultado — Prompt 02 — Interface de importação e histórico de resultados

## 1. Veredicto

**Concluído.** O detalhe da execução ganha um **`ResultAttemptsPanel`** que permite
importar manualmente um resultado (texto colado **ou** ficheiro), consultar a
tentativa exacta e ver o histórico preservado — **sem aprovar nem aplicar**. A
importação só aparece em `prepared`; após importar, o estado passa a **Resultado
por validar** e a tentativa criada é aberta. O conteúdo (não confiável) é
apresentado com segurança: texto original como texto e pré-visualização **via o
endpoint de sanitização do backend** (nunca Markdown renderizado no browser). Não
há acções de revisão nem de aplicação nesta etapa.

**Regressão verde:** frontend **105 testes OK** (91 anteriores + 14 novos) +
`npm run build` OK (86 módulos). Backend inalterado (PR02 é só frontend).

## 2. Componentes e contratos

- **`ResultAttemptsPanel`** (novo) em `ExecutionDetail` — orquestra por estado:
  `prepared` → formulário de importação (+ histórico se houver); `result_pending_
  validation` → tentativa actual + **indicação de revisão pendente**; `approved`/
  `rejected`/`completed` → histórico em modo leitura. `ExecutionDetail` mantém uma
  cópia local da execução e recarrega-a (`getExecution`) após a importação.
- **`ResultImportForm`** (novo) — escolha explícita Colar/Carregar (exclusiva),
  campos `source_tool` (obrigatório)/`source_model`/`source_notes`, limite
  informativo, confirmação e guarda contra submissão duplicada.
- **`ResultAttemptView`** (novo) — vista só-leitura da tentativa: texto original
  (`<pre>`) e pré-visualização segura (reutiliza `DocumentPreview`).
- **`api/executions.ts`** — tipos `ResultAttempt`/`ResultAttemptDetail`, e
  `listResultAttempts`/`getResultAttempt`/`importResult` (desfecho tipado
  ok/conflict/too_large/invalid/error).
- **`api/client.ts`** — **um** auxiliar mínimo `apiPostFormWithStatus` para
  multipart/form-data (não define `Content-Type` — o browser gera o boundary),
  mantendo sessão + CSRF e o tratamento uniforme de erros. **Não** se criou um
  segundo cliente HTTP.

## 3. Formulário de importação

Escolha explícita entre **Colar resultado** (textarea) e **Carregar ficheiro**
(`accept` textual: `.md`/`.markdown`/`.txt`); só a origem do modo activo é enviada
— **nunca `content` e `file` juntos**. `source_tool` obrigatório; `source_model` e
`source_notes` opcionais; envia o `expected_version` **actual** da execução; mostra
o limite de tamanho (autoridade é o servidor). **Confirmação** obrigatória antes de
importar, que explica: importar **regista uma tentativa**, **não aprova**, **não
aplica alterações**, e a tentativa **fica imutável**. Submissão duplicada evitada
(estado `busy` + botão desactivado). O ficheiro mostra **apenas o nome local**
antes de submeter; não se usa `FileReader`, não se persiste nome/caminho no
browser.

## 4. Depois da importação

O detalhe é actualizado (recarga da execução → **Resultado por validar**); a
tentativa criada é aberta; nada é apresentado como oficial; documentos, decisões e
pendências **não** são alterados na UI (a importação só toca em
`result-attempts`/`executions`/`documents/preview` — testado).

## 5. Histórico e tentativa

Lista **crescente** por `attempt_number` com data, origem (`source_tool`), modo,
modelo (quando exista), checksum e versão documental; a **tentativa actual**
(número mais alto) é identificada; qualquer tentativa é abrível. A vista da
tentativa usa **sempre** o conteúdo da **versão exacta** devolvido pelo backend
(`getResultAttempt`) — nunca o `current_version` do documento. **Não** há editar,
eliminar, recuperar versões de resultado, aprovar nem aplicar; reserva-se apenas a
indicação de revisão pendente (sem a implementar).

## 6. Apresentação segura do conteúdo não confiável

Duas vistas: **texto original** em `<pre>` (não executável) e **pré-visualização
segura** que envia o conteúdo ao endpoint `documents/preview` e insere **apenas** o
HTML sanitizado devolvido (via `DocumentPreview`). O Markdown **nunca** é
renderizado no cliente; scripts/handlers/URLs perigosas não executam (testado com
`<script>` hostil — aparece como texto no original e nenhum `<script>` é injectado
na pré-visualização). A pré-visualização não altera o conteúdo guardado.

## 7. Conflitos e erros

- **413** → mensagem clara ("excede o limite (413)").
- **409** (estado/versão) → recarrega a execução e apresenta o estado actual com
  **aviso** (`import-conflict`); **não** repete a importação automaticamente; o
  conteúdo local do formulário só se perde deliberadamente/com aviso.
- **400** → mensagem do servidor. Todos os desfechos são decididos pelo estado do
  servidor, não localmente.

## 8. Testes (14 entradas, 23 casos do guião)

`result-attempts.test.tsx`: formulário só em `prepared`; importação por texto e por
ficheiro (multipart); `source_tool` obrigatório; origem única de cada vez;
confirmação explica importar≠aprovar≠aplicar+imutável; submissão duplicada evitada
(um só POST); erro 413; erro 409 recarrega o estado; após importar →
`result_pending_validation`; tentativa actual apresentada; histórico com várias
tentativas e actual identificada; tentativa histórica com conteúdo exacto; sem
editar/eliminar/aprovar/aplicar; pré-visualização usa o backend; hostil não
executa; texto como texto; importar só toca em resultados/execução/preview.
Regressão de execuções e pacote verde (mocks actualizados com lista de tentativas
vazia). **Regressão:** frontend 105 OK; build OK.

**Nota honesta (demonstração):** o fluxo ponta a ponta é exercido pelos testes de
componente (importar por texto → tentativa 1 + `result_pending_validation` →
pré-visualização segura + texto original; sem aprovar/aplicar). Uma execução no
browser real contra o Compose exigiria reconstruir as imagens (não efectuado); a
imutabilidade/estados são garantidos e testados no backend (F1-P06-PR01).

## 9. VAL e reservas

- **VAL-009 → Parcial** (resultado importável no browser, tentativa e histórico
  consultáveis; validação integrada e revisão em prompts seguintes de F1-P06).
- **VAL-014 → Parcial** (conteúdo não confiável apresentado com segurança — texto
  não executável + preview sanitizada do backend; suites de conteúdo/injecção
  consolidam-se em F1-P07).
- Sem desvio estrutural → **nenhuma decisão global criada**.

## 10. Estado final e próximo passo

- **F1-P06 Em execução (2/6).** Estado de revisão: **Não revista**.
- **Próximo prompt recomendado: F1-P06-PR03.** **Não iniciado nesta iteração.**
