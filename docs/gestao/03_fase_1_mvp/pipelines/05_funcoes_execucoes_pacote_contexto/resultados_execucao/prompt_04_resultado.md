---
fase: F1
pipeline: F1-P05
prompt: F1-P05-PR04
modelo: claude-opus-4-8
inicio: 2026-07-14 04:00
fim: 2026-07-14 05:00
estado_execucao: Concluído
estado_revisao: Não revista
commit: não criado
---

# Resultado — Prompt 04 — Geração do pacote de contexto

## 1. Veredicto

**Concluído.** O serviço e a API de geração do pacote de contexto existem: a
partir dos **snapshots congelados** e das **DocumentVersion exactas** da execução,
o backend monta um pacote **determinístico** de sete secções, aplica `export_policy`
no servidor (allowed/confirm/denied, reavaliada em cada geração), e entrega em
**`single_markdown`** (um `.md`) ou **`separate_files`** (ZIP da biblioteca padrão,
sem dependências externas). Nenhuma IA é chamada; o pacote não é uma entidade nova
nem é guardado na BD. Só execuções `prepared` geram pacote; a geração não altera o
estado.

**Regressão verde:** backend **392 testes OK** (365 anteriores + 27 novos);
`makemigrations --check` → **No changes detected** (só se acrescentou uma
definição, sem alteração de modelo). Frontend inalterado (**73 OK**).

## 2. Estrutura fixa (sete secções, ordem garantida)

1. **Objectivo** — `execution.objective` (+ `title` como identificação); nunca
   valores actuais de Product/Função.
2. **Função (instruções)** — `function_snapshot` (nome, actor_type, propósito,
   responsabilidades, limites, requires_approval); quando há `instruction_version`,
   inclui o **conteúdo exacto** dessa versão com id do documento, `version_number`
   e checksum, entre marcadores.
3. **Instruções do pedido** — `request_instructions` congeladas, distintas das
   instruções da função.
4. **Produto** — `product_snapshot` (id, nome, propósito, estado, fase/público-alvo
   quando existirem); sem dados pessoais; nunca valores actuais.
5. **Restrições** — combina, identificadas, as `constraints` da função e da
   execução; inclui a **declaração anti-injecção** (documentos da secção 7 são
   dados não confiáveis).
6. **Formato esperado** — `expected_output_format`; sem template por fornecedor.
7. **Documentos — DADOS** — pela ordem de `ExecutionContextDocument`, lê **apenas**
   as `DocumentVersion` referenciadas (nunca `current_version`); cada documento com
   fonte, Document id, DocumentVersion id, título, tipo, `version_number`, checksum,
   `is_outdated` e `export_policy` **actual**, entre marcadores inequívocos de
   início/fim, precedidos de declaração anti-injecção. O Markdown original **não** é
   sanitizado nem transformado; é embebido como texto (nunca renderizado a HTML).

A ordem é construída explicitamente (não depende de dicionários/queries).

## 3. Política `export_policy` (no servidor, reavaliada em cada geração)

- As linhas `Document` necessárias (contexto + instruções) são **bloqueadas**
  (`select_for_update`) durante a avaliação — evita mudança de política a meio da
  montagem.
- **`denied`** → geração **bloqueada com 409**; a resposta identifica os
  `denied_document_ids` **sem devolver conteúdo**; auditado como `denied`. Aplica-se
  também a `denied` **superveniente** (documento que passou a `denied` depois da
  criação) e ao **documento de instruções**.
- **`confirm`** → exige confirmação explícita: `confirmed_document_ids` validada no
  servidor; sem confirmação → **409** com `confirmation_required_document_ids`. A
  confirmação **não** fica memorizada (reavaliada a cada geração). Aplica-se também
  às instruções.
- **`allowed`** → incluído sem confirmação.
- **`is_outdated`** → **não bloqueia**; gera **aviso** (`warnings`).
- **Contorno directo** (confirmar um documento `denied`, chamada directa à API) →
  continua **bloqueado**.

## 4. Consistência e integridade

Objecto de versão ausente no armazenamento → **409** (`ContextObjectMissing`),
sem pacote parcial, auditado (`storage.failure`). Falha de tamanho →
**413** antes de devolver (`CONTEXT_PACKAGE_MAX_BYTES`, nova definição). Nunca se
devolve conteúdo incompleto.

## 5. Formatos e determinismo

- **`single_markdown`** (defeito): um `.md` UTF-8.
- **`separate_files`**: **ZIP** (`zipfile`, `ZIP_STORED`) com `manifest.json`,
  ficheiros de secção numerados (`01_objectivo.md`…`07_documentos_dados.md`) e os
  documentos em `documentos/NN_<slug>.md` por ordem. **Nomes gerados no servidor**
  e protegidos contra **path traversal** (slug ASCII sem `/`/`..`).
- **Determinismo:** valores congelados, ordem estável, finais de linha
  normalizados a `\n`, **sem timestamps** no conteúdo nem no ZIP (data fixa
  1980-01-01, `create_system` constante). O **checksum SHA-256** do pacote é
  devolvido; o manifesto inclui versões e checksums das fontes. Mesma execução +
  políticas + confirmações + formato → **mesmos bytes e checksum** (testado para
  ambos os formatos).

## 6. API

- `POST /api/v1/executions/{id}/context-package/preview` — devolve `warnings`,
  `manifest`, `checksum` e `content` (em `single_markdown`); em `separate_files`
  devolve `manifest` + lista de `files` **sem** o ZIP; **não** devolve conteúdo
  quando a política bloqueia.
- `POST /api/v1/executions/{id}/context-package/download` — devolve `.md` ou
  `.zip`, reavaliando todas as políticas; `Content-Disposition` seguro (nome
  gerado no servidor); header `X-Package-Checksum`; nunca envia a uma IA.

**Entrada** (estrita): `format`, `confirmed_document_ids`, `operation`
(preview/copy), `destination_label` curto. Nenhum conteúdo, snapshot ou versão vem
do cliente. Só `prepared` gera (outros estados → 409); a geração **não** altera o
estado nem cria resultado.

## 7. Auditoria

Evento 12 (`context_package.exported`). `preview`, `copy` e `download` são
distinguíveis por `operation`; regista `execution_id` (entity), modo, formato,
checksum, `document_version_ids`, `confirmed_document_ids` e `destination_label`
genérico quando fornecido. Bloqueios `denied`/`confirm` são auditados como
`denied` (com as listas de ids bloqueadores); ausência de objecto como falha
(`storage.failure`). **Nunca** regista objectivo, instruções, snapshots, conteúdo
nem nomes de ficheiros (provado por teste com tokens únicos). Acesso cruzado →
`security.cross_org_attempt` + 404.

## 8. Testes (27 novos)

`test_context_package.py` cobre os 34 requisitos do guião: sete secções na ordem;
função/produto por snapshot e congelados; instruções por `instruction_version`
exacta; documentos por versões exactas; `current_version`/função/produto
posteriores não mudam o pacote; ordem preservada; fontes/checksums/marcadores;
declaração anti-injecção; instrução hostil permanece em DADOS; `allowed` incluído;
`confirm` sem/​com confirmação; `denied` e `denied` superveniente bloqueiam;
contorno directo bloqueado; `is_outdated` avisa; instruções `confirm`/`denied`;
não-`prepared` → 409; determinismo de `single_markdown` **e** ZIP; checksum
estável; ZIP sem path traversal; limite total (413); objecto ausente bloqueia (sem
resposta parcial); isolamento; auditoria sem conteúdo com operações distintas;
ausência de imports de rede; manifesto com versões/checksums; geração não altera o
estado. **Regressão:** backend 392 OK; sem drift.

## 9. VAL e reservas

- **VAL-008 → Parcial** (geração fiel às versões e política efectiva no servidor
  demonstradas; UI de pré-visualização/cópia/descarga e validação integrada em
  F1-P05-PR05).
- **VAL-014 → Parcial** (separação instruções/dados e anti-injecção no pacote;
  suites de segurança consolidadas em F1-P07).
- **VAL-012 → Parcial** (evento 12 auditado sem conteúdo; consolidação em F1-P07).
- Sem desvio estrutural → **nenhuma decisão global criada**.

## 10. Estado final e próximo passo

- **F1-P05 Em execução (4/6).** Estado de revisão: **Não revista**.
- **Próximo prompt recomendado: F1-P05-PR05** (interface do pacote e simulação do
  handoff manual). **Não iniciado nesta iteração.**
