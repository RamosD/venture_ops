---
fase: F1
pipeline: F1-P04
prompt: F1-P04-PR03
modelo: claude-fable-5
inicio: 2026-07-13 22:10
fim: 2026-07-13 23:35
estado_execucao: Concluído
estado_revisao: Não revista
commit: não criado
---

# Resultado — Prompt 03 — Experiência documental no frontend (React/TS)

## 1. Veredicto

**Concluído.** A gestão documental é utilizável no browser, integrada na ficha
do produto: listar, criar, visualizar, editar (com nova versão), pré-visualizar
com segurança, consultar histórico, abrir uma versão exacta, recuperar versões
(com confirmação) e gerir marcadores. A **pré-visualização usa exclusivamente o
endpoint seguro do backend** e nunca executa conteúdo. **39 testes frontend
verdes** (28 anteriores + 11 novos) e **build (tsc + vite) OK**. Demonstração ao
vivo completa, com confirmação dos dados na BD e no armazenamento privado.
Decisões, pendências e execuções permanecem indisponíveis (PR04/PR05). Nada da
API foi reimplementado — só consumido.

## 2. Componentes criados (`src/components/documents/`)

| Componente | Papel |
|---|---|
| `DocumentSection` | Container da área documental na ficha (lista/criação/detalhe/edição/histórico); filtra sempre pelo produto |
| `DocumentList` | Lista de metadados (título, tipo, versão actual, desactualizado, política); sem conteúdo integral |
| `DocumentCreateForm` | Criação (título, tipo dos 5 fechados, Markdown, marcadores); preview seguro |
| `DocumentDetail` | Metadados + conteúdo da versão actual; edição de marcadores com concorrência |
| `DocumentEditor` | Editor simples (textarea); `expected_version`, resumo de alteração, 409 → recarregar |
| `DocumentPreview` | **Único ponto** que insere HTML — e apenas o HTML sanitizado do backend |
| `DocumentHistory` | Histórico (nº, autor, data, checksum, resumo); abrir versão exacta; recuperação confirmada |

Suporte: `src/api/documents.ts` (contratos/tipos) e
`src/components/documents/labels.ts` (rótulos PT dos tipos e políticas).

## 3. Integração na ficha (`ProductDetail`)

Substituiu-se **apenas** a parte de documentos do placeholder "Contexto
relacionado" por `<DocumentSection productId=... />`. A frase de indisponibilidade
foi reduzida a "Decisões, pendências e execuções ainda não estão disponíveis
nesta versão." Sem contagens simuladas.

## 4. Segurança da pré-visualização (SEC-DOC-02)

- O Markdown **nunca** é renderizado no cliente: `DocumentPreview` envia o
  conteúdo ao endpoint `POST /v1/documents/preview` e insere via
  `dangerouslySetInnerHTML` **só** o HTML já sanitizado devolvido pelo backend.
- Verificado ao vivo com conteúdo hostil
  (`<script>`, `<img onerror>`, `[x](javascript:alert(1))`): o HTML inserido não
  continha nenhum `<script>`/`<img>` (escapados para texto), o único `<a>` era o
  link `https` seguro com `rel="nofollow noopener" target="_blank"`, e a string
  `javascript:` não permaneceu no HTML (o link degradou para texto). Blocos de
  código são apresentação (`<pre><code>`), nunca execução. Sem diagramas, HTML,
  JavaScript ou plugins.

## 5. Contratos consumidos (sob /api/v1/)

`GET/POST /documents`, `GET/PATCH /documents/{id}`,
`GET /documents/{id}/versions`, `GET /documents/{id}/versions/{n}`,
`POST /documents/{id}/restore`, `POST /documents/preview`. O cliente central
(`api/client.ts`) trata sessão por cookie, CSRF e 401/403. A listagem consome só
metadados; o conteúdo integral é pedido apenas ao abrir um documento/versão.

## 6. Comportamentos-chave

- **Criação:** título, tipo (só os 5, `<select>` — sem tipos arbitrários),
  Markdown, marcadores; produto derivado da ficha; empresa nunca escolhida.
- **Edição:** textarea simples; envia `expected_version`; exige resumo curto
  quando o conteúdo muda; 409 → aviso + "Recarregar versão actual" (nunca
  sobrescreve o servidor); guarda de submissão duplicada (`busy`).
- **Histórico/recuperação:** lista versões; abre o conteúdo de uma versão exacta;
  "Recuperar" pede confirmação explícita e explica que **cria uma nova versão**
  (nunca apresentada como eliminação); a versão actual é actualizada após sucesso.
- **Marcadores:** `is_outdated` (checkbox) e `export_policy` (allowed/confirm/
  denied); `denied` mostra aviso de que o documento não poderá ser seleccionado
  para pacote de contexto — **sem** omitir o documento da lista; exportação não
  implementada (F1-P05 aplicará o bloqueio de selecção/geração — CLR-03).

## 7. Testes (11 novos; obrigatórios 1–19 cobertos)

`src/components/documents/documents.test.tsx`:

1. estado vazio ✔
2/3/4. criação; exactamente 5 tipos; sem tipo arbitrário (é `<select>`) ✔
5/6/7. preview via backend; sem `<script>` vivo; `javascript:` ausente do HTML ✔
8. edição cria nova versão (versão actual → 2) ✔
9. conflito 409 permite recarregar ✔
10/11. histórico lista versões; abre versão exacta ✔
12/13. recuperação exige confirmação; cria nova versão (→ 3) ✔
14. `is_outdated` alterado ✔
15/16. `export_policy` alterada; `denied` apresenta aviso ✔
17. listagem não recebe conteúdo integral (sentinela no mock) ✔
18. regressão: autenticação/empresa/portefólio verdes (suite completa) ✔
19. **build e testes passam** — `npm test` → 39 OK; `npm run build` (tsc+vite) OK ✔

Ajuste necessário: o mock do teste de portefólio passou a responder à área
documental (lista vazia), porque `ProductDetail` agora compõe `DocumentSection`.

## 8. Demonstração ao vivo (Docker Compose; imagens reconstruídas)

Autenticar (`demo@ventureops.cv`) → onboarding (Empresa Demo P04) → criar
Produto Demo → abrir a ficha (área **Documentos** real; decisões/pendências/
execuções indisponíveis) → criar documento `visao_de_produto` com Markdown
(títulos, lista, link, bloco de código) **e** XSS controlado → **pré-visualizar**
(sanitizado: sem script/img, link seguro com `rel`/`target`, `javascript:`
removido, código como texto) → criar (v1) → editar (v2, com resumo) → abrir
histórico (v2, v1 com checksum/resumo) → abrir v1 (conteúdo exacto) → recuperar
v1 com confirmação (v3) → marcar desactualizado → `export_policy=denied` (aviso).

**Confirmação no backend (BD):** `Visão do Produto Demo`, `visao_de_produto`,
`is_outdated=t`, `export_policy=denied`, `version=4`; três versões (v1: 236 B /
`870e8f0241dc`; v2: 120 B / `1821e3303cc5`; v3: **reutiliza** `storage_key` e
checksum da v1, "Recuperado da versão 1"). **Armazenamento privado:** os três
objectos existem em `/var/storage` e o **SHA-256 do ficheiro coincide** com o
checksum na BD. **Auditoria:** `document.created` (1), `document.version_created`
(2), `document.updated` (2: conteúdo e marcadores), `document.version_restored`
(1) — metadados só com operação, versão, checksum abreviado e nomes de campos;
**zero conteúdo Markdown**.

## 9. Ficheiros

- Criados: `src/api/documents.ts`; `src/components/documents/labels.ts`,
  `DocumentSection.tsx`, `DocumentList.tsx`, `DocumentCreateForm.tsx`,
  `DocumentDetail.tsx`, `DocumentEditor.tsx`, `DocumentPreview.tsx`,
  `DocumentHistory.tsx`, `documents.test.tsx`; este relatório.
- Alterados: `src/components/portfolio/ProductDetail.tsx` (integra a secção);
  `src/components/portfolio/portfolio.test.tsx` (mock responde à área
  documental); governação (status/painel/diário/matriz).
- Sem alterações no backend. Artefactos da Fase 0 não alterados.

## 10. Problemas e pendências

- **Problema corrigido:** integrar `DocumentSection` na ficha fez os testes de
  portefólio dispararem um pedido `/v1/documents` não coberto pelo mock (alerta
  de erro extra). Resolvido acrescentando ao mock do portefólio uma resposta de
  lista vazia — sem alterar o comportamento testado. Nenhum defeito de código.
- **Nota de ambiente:** as imagens Docker copiam o código em build-time (sem bind
  mount); foi necessário `docker compose up -d --build` e `--force-recreate` do
  backend para a demo servir o código de PR02/PR03.
- **Pendências:** editor rich-text, comparação lado a lado, pesquisa, upload,
  exportação e integração com IA continuam fora do âmbito; VAL-004/VAL-014
  permanecem **Parciais** até à validação integrada (F1-P04-PR06).

## 11. Estado e próximo passo

- **F1-P04 Em execução (3/6).**
- Próximo prompt recomendado: **F1-P04-PR04** (decisões, ligadas a
  `decisao_detalhada`). Não iniciado.
