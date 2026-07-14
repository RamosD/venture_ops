---
fase: F1
pipeline: F1-P04
prompt: F1-P04-PR04
modelo: claude-fable-5
inicio: 2026-07-13 23:50
fim: 2026-07-14 01:20
estado_execucao: Concluído
estado_revisao: Não revista
commit: não criado
---

# Resultado — Prompt 04 — Gestão de decisões (modelo, API, cadeia e UI)

## 1. Veredicto

**Concluído.** As decisões podem ser registadas, consultadas e substituídas,
preservando a cadeia histórica e as ligações opcionais a `Product` e ao documento
`decisao_detalhada`. A substituição é atómica, cria uma nova decisão `active`,
marca a anterior `superseded` e liga a cadeia — **sem apagar nem reescrever** a
justificação histórica. Isolamento por empresa, auditoria (evento 8) sem conteúdo
integral, concorrência protegida. **263 testes backend** (239 + 24) e **43 testes
frontend** (39 + 4) verdes; **build (tsc+vite) OK**; migração sem drift.
Demonstração ao vivo com confirmação na BD (estados, cadeia, eventos). Sem
workflow de aprovação, sem tipos configuráveis, sem pendências/execuções.

## 2. Modelo `Decision` (`apps/decisions/models.py`)

| Campo | Definição |
|---|---|
| `id`, `created_at`, `updated_at` | UUIDv4 + carimbos (base comum) |
| `organisation` | obrigatória, `PROTECT`, `editable=False` (RT-01) |
| `title` | obrigatório, não vazio |
| `context` | obrigatório (resumo/justificação) |
| `decision_text` | obrigatório (o que foi decidido) |
| `responsible` | FK `CustomUser`, `PROTECT`; Membership activa na mesma empresa |
| `decided_at` | `default=timezone.now`; aceitável do cliente |
| `impact` | opcional (`blank`) |
| `status` | `active`/`superseded`, default `active` |
| `product` | opcional, `PROTECT`, mesma empresa |
| `detail_document` | opcional, `PROTECT`, mesma empresa e **tipo `decisao_detalhada`** |
| `supersedes` | `OneToOne(self)`, `PROTECT`, `editable=False` — direcção única; inverso `replaced_by` |
| `version` | `PositiveInteger` (protege a substituição) |

**Ciclo de vida** (artefacto 03, §2.3): **Activa → Substituída**. A decisão nasce
`active`; nunca é eliminada; a decisão histórica **não** é reescrita. Constraints
de BD: `title`/`context`/`decision_text` não vazios, `status` fechado, `version ≥ 1`.

**Direcção da relação escolhida:** `supersedes` — a nova decisão referencia a que
substitui; a anterior é acessível por `replaced_by`. Sendo `OneToOne`, a cadeia é
linear (cada decisão substitui no máximo uma e é substituída no máximo uma vez),
garantido ao nível da BD.

**Regra de coerência:** se `product` e `detail_document` forem ambos específicos e
o documento pertencer a um produto, tem de ser o mesmo produto.

## 3. Contratos (sob /api/v1/)

| Método | Caminho | Efeito | Códigos |
|---|---|---|---|
| GET | `/decisions` | Lista (filtros `product`/`status`; paginação) | 200, 400, 403 |
| POST | `/decisions` | Cria decisão `active` | 201, 400, 403 |
| GET | `/decisions/{id}` | Detalhe (inclui `supersedes`/`replaced_by`) | 200, 403, 404 |
| POST | `/decisions/{id}/supersede` | Substitui a decisão activa | 201, 400, 403, 404, 409 |

**Sem DELETE e sem PATCH** (a decisão histórica não é reescrita; edição comum não
é permitida pelo modelo funcional — usa-se substituição). Métodos não permitidos →
405. Entrada estrita: `organisation`/`status`/`version`/`supersedes` nunca são
aceites do cliente.

## 4. Substituição (atómica; concorrência)

`supersede_decision` bloqueia a linha da decisão anterior (`select_for_update`),
valida que está `active` e que `version == expected_version`, cria a nova `active`
ligada por `supersedes` e marca a anterior `superseded` (incrementa a versão). Uma
decisão já `superseded` → **409** (`AlreadySuperseded`); versão obsoleta → **409**.
Duas substituições concorrentes não podem ambas vencer: a serialização pela linha
+ a **unicidade de `supersedes`** (OneToOne) garantem cadeia linear — teste real em
PostgreSQL (2 substituições simultâneas): uma vence, a outra recebe conflito;
apenas uma decisão substitui a original.

## 5. Isolamento (RT-01)

Empresa derivada da Membership; sem contexto → 403. Decisão de outra empresa →
**404 indistinguível**, com tentativa cruzada auditada
(`security.cross_org_attempt`, `entity_type=decision`). Responsável/produto/
documento alheios → **400**. Listagem e filtros nunca atravessam empresas.

## 6. Auditoria (RT-02) — evento 8

- criação → `decision.created` (operação, `product_id`, `detail_document_id`);
- substituição → `decision.created` (nova, `supersedes`) + `decision.updated`
  (anterior, `transition: active->superseded`, `replaced_by`).

Metadados só com operação, transição e identificadores — **nunca** `context` nem
`decision_text` integrais (verificado: tokens únicos ausentes dos eventos).

## 7. Frontend (`src/components/decisions/`)

`DecisionSection` (container na ficha), `DecisionList` (título/data/estado/
cadeia), `DecisionForm` (partilhado por criar e substituir; oferece os documentos
`decisao_detalhada` do produto como associação), `DecisionDetail` (campos,
associações e **cadeia navegável** — anterior/seguinte — com "Substituir" só em
decisões activas). Integrado na ficha do produto, ao lado dos documentos;
pendências e execuções permanecem indisponíveis (sem contagens simuladas).

## 8. Testes (28 novos; obrigatórios 1–19 cobertos)

Backend (`test_decision_api.py` 21, `test_decision_concurrency.py` 1,
`test_migration.py` 2):
1. criação empresarial sem Product ✔  2. associada a Product ✔  (+ com documento)
3. responsável alheio → 400 ✔  4. Product alheio → 400 ✔  5. documento alheio →
400 ✔  6. tipo errado → 400 ✔ (+ documento de outro produto)  7. listagem isolada
✔ (+ filtros)  8. detalhe alheio → 404 auditado ✔  9/10/11. substituição cria nova
active, anterior superseded, cadeia navegável ✔  12. superseded não é substituída
de novo → 409 ✔ (+ versão obsoleta → 409; alheia → 404)  13. concorrência não cria
duas substituições ✔ (PostgreSQL real)  14. histórico preservado ✔  15. criação e
substituição auditadas ✔  16. auditoria sem conteúdo integral ✔  (+ sem DELETE/
PATCH → 405; sem contexto → 403).

Frontend (`decisions.test.tsx` 4): estado vazio; **17.** UI cria e consulta;
**18.** UI substitui e mostra a cadeia (navega anterior→substituída, sem
"Substituir"); filtro por estado.

**19.** build + suites: **263 backend**, **43 frontend**, `npm run build` OK,
`makemigrations --check` limpo.

## 9. Demonstração ao vivo (Docker Compose; imagens reconstruídas)

Login → Produto Demo → criar documento `decisao_detalhada` ("Detalhe da decisão
de arquitectura") → criar decisão "Adoptar arquitectura modular" ligada ao produto
**e** ao documento → substituir por "Adoptar arquitectura modular (revista)" →
navegar a cadeia. **Confirmação na BD:** anterior `superseded` (version 2,
`supersedes` nulo, product+doc ligados); nova `active` (version 1, `supersedes`
definido, product ligado). **Auditoria:** `decision.created` (create, com
`product_id`+`detail_document_id`), `decision.created` (supersede_create,
`supersedes`), `decision.updated` (`active->superseded`, `replaced_by`) — sem
conteúdo. Dados de demonstração **mantidos** (prática vigente desde PR03: os dados
de dev não são removidos).

## 10. Ficheiros

- Backend criados: `apps/decisions/models.py`, `service.py`, `serializers.py`,
  `views.py`, `urls.py`, `migrations/0001_initial.py`,
  `tests/test_decision_api.py`, `test_decision_concurrency.py`, `test_migration.py`.
- Frontend criados: `src/api/decisions.ts`; `src/components/decisions/labels.ts`,
  `DecisionList.tsx`, `DecisionForm.tsx`, `DecisionDetail.tsx`,
  `DecisionSection.tsx`, `decisions.test.tsx`.
- Alterados: `config/urls.py`; `ProductDetail.tsx` (integra a secção);
  `portfolio.test.tsx` (mock responde a `/v1/decisions`); governação.
- Artefactos da Fase 0 não alterados.

## 11. Problemas e reservas

- **Problema corrigido:** a constraint `status__in` não podia referenciar a classe
  aninhada `Status` dentro de `Meta` (`NameError`); usaram-se os literais fechados.
  Nenhum outro defeito.
- **Ambiente:** imagens Docker sem bind mount — reconstruídas/recriadas para a
  demo servir o código de PR04; container de BD reiniciado quando necessário.
- **Reservas:** pendências (com ligação opcional a decisão) chegam em F1-P04-PR05;
  a aplicação controlada de resultados a decisões (E6) é de F1-P06. Edição comum de
  decisões permanece **não** suportada por desenho (usa-se substituição).

## 12. Estado e próximo passo

- **F1-P04 Em execução (4/6).**
- Próximo prompt recomendado: **F1-P04-PR05** (pendências mínimas). Não iniciado.
