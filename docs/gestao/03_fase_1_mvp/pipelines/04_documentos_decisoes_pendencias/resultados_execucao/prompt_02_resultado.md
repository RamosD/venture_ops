---
fase: F1
pipeline: F1-P04
prompt: F1-P04-PR02
modelo: claude-fable-5
inicio: 2026-07-13 20:10
fim: 2026-07-13 21:40
estado_execucao: Concluído
estado_revisao: Não revista
commit: não criado
---

# Resultado — Prompt 02 — API documental completa (conteúdo, versões, preview)

## 1. Veredicto

**Concluído.** A API documental existe e funciona sobre os modelos de PR01:
criar, listar, consultar, editar, recuperar e marcar documentos, com o conteúdo
Markdown em ficheiros privados, versões imutáveis, concorrência optimista,
isolamento por empresa, preview sanitizada no backend e auditoria limpa. **239
testes backend verdes** (207 anteriores + 32 novos), sem drift. Nenhuma UI,
exportação, decisão, pendência ou integração com função/execução foi antecipada.

## 2. Pré-requisitos (verificação)

PR01 concluído (modelos + migração); `FilesystemStorageAdapter` funcional
(`get_storage()`, chaves no servidor, checksum SHA-256); `Document`/
`DocumentVersion` existentes; `Product`, contexto empresarial (`require_context`/
`deny_cross_org`) e auditoria (`record_event`, lista fechada) funcionais. Nada de
PR01 foi corrigido silenciosamente.

## 3. Contratos (sob /api/v1/)

| Método | Caminho | Efeito | Códigos |
|---|---|---|---|
| GET | `/documents` | Lista metadados (filtros; paginação; sem conteúdo) | 200, 400, 403 |
| POST | `/documents` | Cria documento + versão 1 + objecto privado | 201, 400, 403, 413 |
| GET | `/documents/{id}` | Detalhe: metadados + conteúdo da versão actual | 200, 403, 404 |
| PATCH | `/documents/{id}` | Edição: nova versão e/ou metadados (concorrência) | 200, 400, 403, 404, 409, 413 |
| GET | `/documents/{id}/versions` | Histórico (metadados imutáveis) | 200, 403, 404 |
| GET | `/documents/{id}/versions/{n}` | Conteúdo de uma versão exacta | 200, 403, 404 |
| POST | `/documents/{id}/restore` | Recupera versão `n` → cria nova versão | 200, 403, 404, 409 |
| POST | `/documents/preview` | HTML sanitizado de Markdown não guardado | 200, 400, 403, 413 |

Sem DELETE (sem eliminação física). Leitura de detalhe inclui `content`,
`checksum` e `current_version_number`. Listagem: `results`, `count`, `page`,
`page_size`, `num_pages` — **nunca** `content`.

### Contratos de entrada (campos aceites; resto rejeitado com 400)

- **criação:** `title`, `document_type`, `content` (obrigatórios); `product`,
  `is_outdated`, `export_policy` (opcionais). **Não** aceita `organisation`,
  `storage_key`, `checksum`, `version_number`, `version`, `id`.
- **edição:** `expected_version` (obrigatório); `content`, `change_summary`,
  `title`, `document_type`, `product`, `is_outdated`, `export_policy` (opcionais).
- **recuperação:** `version_number`, `expected_version` (+ `change_summary`).
- **preview:** apenas `content`.

## 4. Estratégia de coordenação BD↔armazenamento (SEC-STO-01)

Implementada em `apps/documents/service.py`:

1. valida-se UTF-8 e o limite de bytes **antes** de qualquer escrita (413/400);
2. o objecto privado é escrito **antes** de criar a referência oficial na BD
   (`_write_object`);
3. enquanto a transacção de BD não confirmar, nada na aplicação expõe o objecto
   (só é alcançável via `DocumentVersion`, cuja linha ainda não está visível);
4. se a escrita falhar, não se abre transacção — **não** se cria versão nem se
   toca `current_version`;
5. se a transacção falhar **depois** da escrita, o objecto órfão é removido de
   forma controlada (`_discard_object`); se a própria remoção falhar, regista-se
   `storage.failure` (evento aprovado da lista fechada);
6. `current_version` só é definida dentro da transacção, para uma versão do
   próprio documento — **nunca** aponta para objecto inexistente.

**Recuperação:** reutiliza o `storage_key`/`checksum` da versão de origem
(conteúdo imutável e idêntico) — cria uma nova versão sem reescrever nem gerar
órfãos.

**Limitação residual (documentada):** uma falha abrupta do processo **entre** a
escrita do objecto e o commit da BD pode deixar um objecto órfão (nunca
referenciado, portanto inócuo quanto a exposição). A reconciliação/garbage
collection fica como tarefa operacional futura — **sem** introduzir fila nem
transacção distribuída no MVP.

## 5. Concorrência optimista

Padrão real de `Product`: cada mutação bloqueia a linha do `Document`
(`select_for_update`), valida `Document.version` contra `expected_version` e
incrementa-a exactamente uma vez; versão obsoleta → **409** sem sobrescrita
silenciosa. Aplica-se a edição de conteúdo, edição só de metadados e recuperação.
Teste real em PostgreSQL (2 edições concorrentes com a mesma versão): uma vence
(cria v2), a outra recebe conflito; `Document.version` termina em 2 (sem lost
update) e o objecto da perdedora é removido.

## 6. Versões e conteúdo

Cada submissão de conteúdo cria uma **nova** `DocumentVersion` imutável; a
anterior permanece intacta (modelo bloqueia update/delete). `version_number` é
sequencial por documento (atribuído no servidor, com a linha bloqueada; unicidade
garantida por constraint). O conteúdo vive só no armazenamento; a BD nunca o
guarda (verificado por introspecção e por SQL directo às duas tabelas).

## 7. Preview e sanitização (SEC-DOC-02 / MVP-06.R3)

`apps/documents/markdown.py` — renderizador autocontido (sem dependências
externas), estratégia *escape-first*:

- todo o texto é escapado **antes** de qualquer transformação → HTML bruto,
  `<script>`, atributos e *event handlers* tornam-se texto inerte;
- só se emite um subconjunto fixo e seguro de marcas (`h1`–`h6`, `p`, `strong`,
  `em`, `code`, `pre`, `ul`/`ol`/`li`, `blockquote`, `a`, `img`, `hr`, `br`);
- `href`/`src` só aceitam esquemas seguros (`http`, `https`, `mailto`, âncoras e
  caminhos relativos); `javascript:`, `data:` e ofuscações com caracteres de
  controlo são removidos (o elemento degrada para texto); links seguros levam
  `rel="nofollow noopener"`;
- código é apresentado como texto, nunca executado.

O preview aplica o mesmo limite de tamanho e **não** guarda o conteúdo.

## 8. Marcadores e tipos

`is_outdated` (booleano) e `export_policy` (`allowed`/`confirm`/`denied`)
persistem só na BD e são editáveis por PATCH com concorrência coerente.
`export_policy=denied` é **apenas** um marcador: **não** oculta nem elimina o
documento na aplicação. Listagem filtra por `document_type`, `product`,
`is_outdated` e `export_policy`, sempre dentro da empresa do contexto.
**Reserva registada:** o **bloqueio de selecção e de geração** de pacote/
exportação por `denied` é de F1-P05 (CLR-03); esta pipeline não implementa
exportação.

## 9. Isolamento (RT-01)

Empresa derivada da Membership activa; sem contexto → 403. Documento/produto de
outra empresa → **404 indistinguível** de inexistente; a tentativa cruzada é
auditada (`security.cross_org_attempt`, `entity_type=document`). Filtros e
histórico nunca atravessam empresas.

## 10. Auditoria (RT-02) — eventos 5–7

- criação → `document.created` + `document.version_created`;
- edição → `document.updated` (+ `document.version_created` se houve conteúdo);
- recuperação → `document.version_restored`.

Metadados mínimos: operação, número de versão, **checksum abreviado** (12 hex),
nomes de campos alterados, versão de concorrência. **Nunca** o conteúdo
Markdown integral (verificado: token único do conteúdo não aparece em nenhum
evento). Falhas de armazenamento usam `storage.failure`.

## 11. Testes (32 novos; obrigatórios 1–24 cobertos)

`test_document_api.py` (24), `test_markdown_preview.py` (7),
`test_storage_coordination.py` (2), `test_document_concurrency.py` (1) + os de
PR01 (modelo/migração):

1. criação gera v1 e ficheiro privado ✔
2. edição gera v2 e preserva v1 ✔
3. conteúdo não aparece na BD ✔ (SQL directo às 2 tabelas)
4. checksum corresponde ao ficheiro ✔ (SHA-256 recalculado)
5. conteúdo acima do limite → 413 ✔ (`DOCUMENT_MAX_BYTES` reduzido)
6. UTF-8 inválido rejeitado ✔ (corpo com bytes inválidos → 400; + unidade
   `encode_content` recusa surrogate isolado)
7. Product alheio rejeitado ✔ (+ mesma-empresa aceite)
8. documento alheio → 404 auditado ✔ (+ inexistente → 404)
9. conflito de versão → 409 ✔
10. duas edições concorrentes sem lost update ✔ (PostgreSQL real)
11. histórico mantém todas as versões ✔
12. recuperação cria nova versão ✔
13. versão recuperada corresponde ao conteúdo histórico ✔ (+ 404/409 na recuperação)
14. marcadores persistem na BD ✔ (+ edição de marcadores; política inválida → 400)
15/16/17. filtros por tipo/produto/política ✔ (+ listagem sem conteúdo; isolada)
18. preview neutraliza XSS ✔
19. URLs perigosas removidas ✔ (`javascript:`, `data:`; ofuscação com controlo)
20. falha de armazenamento não cria versão ✔
21. falha de BD tenta limpar objecto órfão ✔
22. auditoria sem conteúdo integral ✔
23. migrações sem drift ✔ (`makemigrations --check`)
24. suite anterior verde ✔ — **`manage.py test` → 239 OK** (207 + 32)

## 12. Ficheiros

- Criados: `apps/documents/markdown.py`, `serializers.py`, `service.py`,
  `views.py`, `urls.py`, `tests/test_document_api.py`,
  `tests/test_markdown_preview.py`, `tests/test_storage_coordination.py`,
  `tests/test_document_concurrency.py`; este relatório.
- Alterados: `config/urls.py` (monta `apps.documents.urls`),
  `config/settings.py` (`DOCUMENT_MAX_BYTES`); governação
  (`01_status_pipelines.md`, `00_painel_execucao_global.md`,
  `05_diario_execucao_ia.md`, `04_matriz_validacao_global.md`).
- **Sem migrações novas** (modelos inalterados desde PR01). Artefactos da Fase 0
  não alterados.

## 13. Problemas e reservas

- **Problemas corrigidos durante a execução:** dois testes iniciais precisaram
  de ajuste (não o código): (a) o cliente de teste DRF não serializa um surrogate
  isolado para JSON — o UTF-8 inválido passou a ser exercido com bytes crus no
  corpo (400) e por teste unitário do serviço; (b) a asserção do esquema
  ofuscado foi corrigida para um caracter de controlo não-espaço que forma o
  link mas é removido antes da verificação (prova a degradação para texto).
  Nenhum defeito de aplicação encontrado.
- **Reservas:** `export_policy=denied` só bloqueia selecção/geração em F1-P05
  (CLR-03); limitação residual de falha abrupta entre sistemas (órfão inócuo,
  GC operacional futura); VAL-004/VAL-014 permanecem **Parciais** até existir UI
  e validação integrada.

## 14. Fora do âmbito (confirmado não implementado)

UI/editor, comparação visual de versões, pesquisa, exportação/pacote de contexto,
integração com função ou execução, decisões e pendências.

## 15. Estado e próximo passo

- **F1-P04 Em execução (2/6).**
- Próximo prompt recomendado: **F1-P04-PR03** (editor + pré-visualização
  sanitizada no frontend). Não iniciado.
