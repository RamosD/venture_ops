---
fase: F1
pipeline: F1-P04
prompt: F1-P04-PR01
modelo: claude-fable-5
inicio: 2026-07-13 19:10
fim: 2026-07-13 19:55
estado_execucao: Concluído
estado_revisao: Não revista
commit: não criado
---

# Resultado — Prompt 01 — Fundação persistente da gestão documental

## 1. Veredicto

**Concluído.** Os modelos `Document` e `DocumentVersion` existem com a
enumeração fechada de 5 tipos documentais, os marcadores estruturados
(`is_outdated`, `export_policy`) e a migração inicial do módulo `documents`.
O conteúdo Markdown **não** é persistido na BD (só metadados e a referência
`storage_key`); o isolamento estrutural por empresa está aplicado; as versões
são imutáveis. Migrações aplicam em base vazia e na base de desenvolvimento,
com reversibilidade demonstrada e sem drift. **207 testes backend verdes**
(185 anteriores + 22 novos). Nenhuma API, escrita real no armazenamento ou UI
foi antecipada.

## 2. Condição obrigatória (verificação de entrada)

- **F1-P03-PR06 terminou:** `estado_execucao: Concluído` no resultado final;
  F1-P03 **Concluída (6/6)** no status.
- **Aceitação para avanço:** F1-P03 foi **commitada em `main`** (`303d741`,
  working tree limpo) e o seu resultado final recomenda explicitamente gerar
  F1-P04. A coluna `Revisão` está "Não revista", mas é **informativa e não
  bloqueante** (guia §10, nota no cabeçalho de `01_status_pipelines.md`) — o
  mesmo critério com que F1-P03 avançou sobre F1-P02. Nenhum dos estados
  bloqueantes (Em execução, bloqueada, defeito estrutural pendente) se
  verifica. **Sem bloqueio; nenhuma correcção a F1-P03 foi feita.**

## 3. Inspecção inicial (convenções confirmadas)

- **UUID + timestamps:** `UUIDPrimaryKeyModel` (`apps/common/models.py`).
- **Isolamento:** `OrganisationScopedModel` (`organisation` obrigatória,
  `PROTECT`, `editable=False`, derivada do contexto no servidor).
- **StorageAdapter:** `save(content) -> StoredObject(key, checksum, size)`;
  chaves geradas no servidor (formato `xx/30hex`); checksum SHA-256.
- **Product (F1-P03):** concluído, com concorrência optimista por campo
  `version` (PositiveInteger, default 1, constraint `>= 1`) — padrão reutilizado.
- **AuditAction:** lista fechada já contém os eventos documentais 5–7
  (`document.created/updated`, `document.version_created`,
  `document.version_restored`) — nenhuma alteração necessária nesta etapa.
- **Sem alterações inesperadas:** árvore limpa sobre `303d741` antes de começar.

## 4. Modelos criados (`backend/apps/documents/models.py`)

### Enumerações fechadas (novos valores exigem alteração formal)

- **`DocumentType`** (MVP-07.R1): `contexto_da_empresa`, `visao_de_produto`,
  `instrucoes`, `decisao_detalhada`, `resultado`. Sem tipos configuráveis nem
  templates.
- **`ExportPolicy`** (DEC-F0-FINAL-08/CLR-03): `allowed`, `confirm`, `denied`;
  **default `confirm`**.

### `Document` (herda `OrganisationScopedModel`)

| Campo | Definição |
|---|---|
| `id`, `created_at`, `updated_at` | UUIDv4 + carimbos (base comum) |
| `organisation` | obrigatória, `PROTECT`, `editable=False` (RT-01) |
| `title` | obrigatório, não vazio (normalizado com strip) |
| `document_type` | obrigatório, enumeração fechada |
| `product` | opcional, `PROTECT`; tem de pertencer à mesma empresa |
| `current_version` | opcional na criação técnica, `PROTECT`, `editable=False`; tem de apontar para versão do próprio documento; obrigatória após a 1.ª versão (regra do serviço, PR02) |
| `is_outdated` | boolean, default `false` (só na BD; sem cópia no Markdown) |
| `export_policy` | enumeração fechada, default `confirm` (só na BD) |
| `version` | concorrência optimista estrutural (padrão real de `Product`) |

### `DocumentVersion` (imutável; sem `updated_at`)

| Campo | Definição |
|---|---|
| `id` | UUIDv4 |
| `document` | obrigatório, `PROTECT`, `editable=False` |
| `version_number` | sequencial por documento (atribuído pelo serviço em PR02) |
| `storage_key` | gerada no servidor, `editable=False` — nunca vem do cliente |
| `checksum` | SHA-256 hex (64), `editable=False` |
| `byte_size` | `PositiveBigIntegerField`, `editable=False` |
| `author` | FK utilizador, `PROTECT` |
| `change_summary` | curto (255) e opcional |
| `created_at` | `auto_now_add` |

**Imutabilidade:** `save()` de instância existente, `delete()` e
`update()`/`delete()` de queryset lançam `DocumentVersionImmutableError`
(padrão append-only do `AuditEvent`). **Não existe campo de conteúdo** — o
corpo vive exclusivamente no armazenamento privado (artefacto 05, R-02).

## 5. Constraints de BD (defesa em profundidade)

- `documents_document_title_not_blank`;
- `documents_document_type_closed` (`document_type IN` 5 valores);
- `documents_document_export_policy_closed` (`IN allowed|confirm|denied`);
- `documents_document_version_positive` (`version >= 1`);
- `uniq_documentversion_document_number` (**document + version_number únicos**);
- `documents_documentversion_number_positive` (`version_number >= 1`);
- `documents_documentversion_storage_key_not_blank`;
- `documents_documentversion_checksum_not_blank`.

## 6. Migrações

- **`documents/0001_initial`** criada (2 tabelas, FK circular
  `current_version` resolvida por `AddField` posterior; depende de
  `organisations`, `portfolio` e do utilizador).
- **Base vazia:** aplica na base de testes criada de raiz (toda a cadeia). OK.
- **Base de desenvolvimento existente:** `migrate documents` → OK, dados
  anteriores intactos.
- **Reversibilidade estrutural:** demonstrada em **base controlada** (base de
  testes): reverter `documents` para zero remove as duas tabelas e reaplicar
  recria-as, sem tocar migrações históricas (teste dedicado). A base de
  desenvolvimento **não** foi revertida.
- **Drift:** `makemigrations --check --dry-run` → *No changes detected* (na
  base de dev e como teste permanente).

## 7. Testes (22 novos; obrigatórios 1–16 cobertos)

`apps/documents/tests/test_document_model.py` (20) e `test_migration.py` (2):

1. organisation obrigatória ✔ (nível BD)
2. title obrigatório ✔ (+ constraint de BD para título vazio)
3. tipo inválido rejeitado ✔ (+ enumeração exactamente fechada)
4. export_policy inválida rejeitada ✔ (+ enumeração exactamente fechada)
5. defaults `is_outdated=false`, `export_policy=confirm` (+ `version=1`,
   `current_version=NULL`) ✔
6. Product de outra empresa rejeitado ✔ (+ mesmo-empresa aceite)
7. documento empresarial sem Product aceite ✔
8. DocumentVersion exige Document ✔
9. version_number único por documento ✔ (+ repetível entre documentos)
10. `storage_key` não editável pelo cliente ✔ (também `checksum`, `byte_size`,
    `document`)
11. DocumentVersion sem campo de conteúdo ✔
12. DocumentVersion inalterável ✔ (save/update/delete de instância e queryset)
13. `current_version` de outro documento rejeitada ✔ (+ do próprio aceite)
14. conteúdo não existe na BD ✔ (introspecção das colunas das duas tabelas)
15. migrações aplicam sem drift ✔ (aplica/reverte/reaplica + `--check`)
16. suite anterior verde ✔ — **`manage.py test` → 207 OK** (185 + 22).

## 8. Fora do âmbito (confirmado não implementado)

API, escrita real no armazenamento, editor, preview, histórico, recuperação,
decisões, pendências, exportação/pacote de contexto, eliminação física,
pesquisa, comparação de versões, classificação avançada, ligação
`decisao_detalhada`→decisão (PR04) e ligações a funções/execuções (F1-P05).

## 9. Ficheiros alterados

- Criados: `backend/apps/documents/models.py`, `exceptions.py`,
  `migrations/0001_initial.py`, `tests/test_document_model.py`,
  `tests/test_migration.py` (+ `__init__.py` de migrations/tests); este
  relatório.
- Alterados (governação): `01_status_pipelines.md`,
  `00_painel_execucao_global.md`, `05_diario_execucao_ia.md`.
- Sem alterações a código de outros módulos nem a artefactos da Fase 0.

## 10. Problemas e pendências

- **Problemas:** nenhum defeito encontrado; nenhum desvio estrutural — **não**
  foi criada decisão global.
- **Nota de execução:** os testes correram no host (venv do backend contra o
  PostgreSQL do Compose, porta 5434) porque a imagem do backend não monta o
  código-fonte; o contentor só verá o módulo novo no próximo rebuild — sem
  impacto, o serviço em execução não usa ainda estes modelos.
- **Pendências para os próximos prompts:** obrigatoriedade de
  `current_version` após a 1.ª versão e atribuição de `version_number` são
  regras do serviço (PR02, com a escrita coordenada BD↔armazenamento);
  auditoria documental (eventos 5–7) entra com a API; VAL-004/VAL-014 ficam
  **preparadas** (fundação persistente), não validadas.

## 11. Estado e próximo passo

- **F1-P04 Em execução (1/6).**
- Próximo prompt recomendado: **F1-P04-PR02** (API documental com criação de
  versões e escrita coordenada com o armazenamento privado). Não iniciado.
