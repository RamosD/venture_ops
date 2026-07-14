---
fase: F1
pipeline: F1-P05
prompt: F1-P05-PR05
modelo: claude-opus-4-8
inicio: 2026-07-14 05:15
fim: 2026-07-14 06:05
estado_execucao: Concluído
estado_revisao: Não revista
commit: não criado
---

# Resultado — Prompt 05 — Interface do pacote e handoff manual

## 1. Veredicto

**Concluído.** O detalhe da execução ganha um **`ContextPackagePanel`** que permite
preparar e transferir manualmente o pacote de uma execução `prepared`: escolher
formato, ver a **análise de política** por documento, confirmar explicitamente os
documentos `confirm`, **gerar a pré-visualização**, **copiar** o Markdown ou
**descarregar** `.md`/`.zip`. Nenhuma IA é chamada, nenhum resultado é criado e o
**estado permanece `prepared`**. O painel só aparece em `prepared`; nos restantes
estados apresenta uma explicação sem tentar gerar. Snapshots e lista de versões
mantêm-se.

**Regressão verde:** frontend **91 testes OK** (73 anteriores + 18 novos) +
`npm run build` OK (83 módulos). Backend inalterado (**392 OK** — PR05 é só
frontend).

## 2. Componentes e contratos

- **`ContextPackagePanel`** (novo) integrado em `ExecutionDetail` (só em
  `prepared`; caso contrário `package-unavailable`).
- **`api/executions.ts`**: tipos do pacote (`ContextPackageFormat`, manifesto,
  `ContextPackagePreview`, `ContextPackageBlocked`) e funções `previewContextPackage`
  (desfecho tipado ok/blocked/too_large/error) e `downloadContextPackage` (blob).
- **`api/client.ts`**: dois auxiliares mínimos — `apiPostWithStatus` (não lança em
  409/413; devolve estado+corpo, essencial para a análise de política que vem no
  corpo do 409) e `apiPostBlob` (descarga binária; lê `Content-Disposition` e
  `X-Package-Checksum`). Reutilizam sessão + CSRF do cliente central.

## 3. Análise de política (não contornável, fonte no servidor)

- **`allowed`** → indicação simples (sem confirmação).
- **`confirm`** → checkbox individual, **inicialmente desmarcada**; a inclusão só
  ocorre se confirmada. **"Confirmar todos…"** exige mostrar a contagem/lista e uma
  **confirmação adicional** deliberada antes de marcar todas.
- **`denied`** → estado **bloqueado**, **sem botão de contorno**.
- **`is_outdated`** → aviso visível (não bloqueia).
- O **documento de instruções da função** aparece na mesma análise (sinalizado
  pela resposta do backend).
- A UI **não confia apenas no estado local**: a geração chama sempre o backend; um
  **409** apresenta o motivo e **recarrega a análise** com as listas frescas
  (`denied`/`confirmation_required`), cobrindo a mudança de política **superveniente**
  (allowed→denied) detectada no servidor. As confirmações vivem **só em memória**
  (nunca `localStorage`) e são **reavaliadas a cada geração**.

## 4. Confirmação, aviso e modos

Texto explícito de que o conteúdo **poderá sair da aplicação**. Aviso por modo:
**`manual_external`** → partilha com serviço externo (confirmar ausência de dados
sensíveis); **`manual_local`** → o pacote deve permanecer no ambiente autorizado.

## 5. Preview, cópia e descarga

- **Preview**: mostra o conteúdo como **texto não executável** num `<pre>` —
  **nunca** `dangerouslySetInnerHTML`, nunca renderização de HTML documental (HTML
  embebido aparece como texto literal; nenhum `<script>` é injectado); documentos
  DADOS delimitados; **checksum** e **manifesto** (identificadores e versões, sem
  comparação de documentos) apresentados; avisos listados.
- **Cópia** (só `single_markdown`): **Clipboard API** com tratamento de falha
  (mensagem de fallback); reavalia no servidor (operação `copy`, auditada) antes de
  copiar; confirmação visual após copiar; nada é guardado no browser.
- **Descarga**: `.md` (single) ou `.zip` (separate_files); nome de ficheiro
  **fornecido pelo backend** (`Content-Disposition`); cria uma URL temporária,
  aciona a descarga e **revoga** a URL (`URL.revokeObjectURL`); **sem biblioteca
  externa**. Um 409 na descarga reavalia a análise e avisa que a política mudou.

## 6. Integração na ficha

A lista de execuções mantém-se; abrir uma execução permite preparar o pacote. Sem
novo separador global. As execuções são agora uma **área real** (deixaram de
aparecer como indisponíveis, desde PR03).

## 7. Simulação do handoff manual

O handoff manual foi **simulado pelos testes de componente** (não por chamada a
qualquer modelo): geração da pré-visualização, confirmação explícita de documento
`confirm`, **cópia** via Clipboard API e **descarga** de `.md` e `.zip` (com
revogação da URL temporária), em execuções `manual_local` **e** `manual_external`.
Verificou-se: as **sete secções** presentes no conteúdo; o **checksum** e o
**manifesto** (secções, documentos, versões) apresentados; os ficheiros do ZIP
listados (`manifest.json`, secções numeradas, documentos). **Nenhum pacote foi
enviado a um serviço real; nenhuma resposta foi importada; as execuções
permanecem `prepared`.**

- **Formato `single_markdown`** — verificação: 7 secções + checksum + manifesto
  apresentados; cópia e descarga `.md` funcionais. **Resultado: OK.**
- **Formato `separate_files`** — verificação: manifesto + lista de ficheiros;
  descarga `.zip` funcional. **Resultado: OK.**
- **Determinismo/checksums**: o checksum SHA-256 é gerado no servidor e é
  **determinístico** (provado nos testes de backend de F1-P05-PR04 —
  `test_single_markdown_deterministic`, `test_separate_files_deterministic`,
  `test_checksum` estável); a UI apresenta-o mas não o recalcula.

**Nota honesta:** tal como em PR03, uma execução no **browser real** contra o stack
em contentor exigiria reconstruir as imagens Docker (não efectuado); os testes de
componente cobrem o comportamento exigido. **A confirmação com um modelo externo
real fica para F1-P08/piloto** (não declarada aqui).

## 8. Testes (18 entradas, 24 casos do guião)

`context-package.test.tsx`: painel só em `prepared` (e estado permanece
`prepared`); sete secções visíveis; `allowed` sem confirmação; `confirm` com
checkbox; `denied` bloqueia sem contorno; `denied` superveniente após 409;
`is_outdated` avisa; instruções na análise após 409; avisos `manual_external`/
`manual_local`; preview como texto não executável (sem `<script>` injectado);
cópia via Clipboard API; falha de clipboard tratada; descarga `.md`; descarga
`.zip`; URL temporária revogada; checksum e manifesto; confirmação não persistida
(`localStorage` intacto); nova geração reavalia após confirmação; só endpoints do
pacote (sem IA/resultado/transições, tudo `POST`); "Confirmar todos" com lista +
confirmação adicional. **Regressão** de funções/documentos/portefólio verde
(91 frontend). Build OK.

## 9. VAL e reservas

- **VAL-008 → Parcial** (o pacote pode ser revisto, confirmado, copiado e
  descarregado na UI; a validação integrada e o fecho de F1-P05 ficam para PR06).
- **VAL-012 → Parcial** (as operações preview/copy/download são auditadas no
  backend — evento 12 — sem conteúdo; consolidação em F1-P07).
- **VAL-014 → Parcial** (conteúdo apresentado como texto não executável, sem
  `dangerouslySetInnerHTML`; anti-*injection* consolidado em F1-P07).
- Sem desvio estrutural → **nenhuma decisão global criada**.

## 10. Estado final e próximo passo

- **F1-P05 Em execução (5/6).** Estado de revisão: **Não revista**.
- **Próximo prompt recomendado: F1-P05-PR06** (validação integrada e fecho de
  F1-P05). **Não iniciado nesta iteração.**
