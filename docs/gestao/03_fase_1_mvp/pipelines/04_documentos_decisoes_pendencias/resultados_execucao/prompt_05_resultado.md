---
fase: F1
pipeline: F1-P04
prompt: F1-P04-PR05
modelo: claude-fable-5
inicio: 2026-07-14 01:40
fim: 2026-07-14 03:20
estado_execucao: Concluído
estado_revisao: Não revista
commit: não criado
---

# Resultado — Prompt 05 — Gestão mínima de pendências (WorkItem)

## 1. Veredicto

**Concluído.** As pendências são acompanháveis até conclusão ou cancelamento,
com os **cinco tipos fechados**, um único ciclo de vida (`open → completed |
cancelled`, finais imutáveis), vencimento **calculado** (nunca persistido),
associações isoladas por empresa (produto obrigatório, decisão opcional, com
coerência) e auditoria (evento 9) sem conteúdo integral. **Não** há gestor de
projectos disfarçado (sem sprints, kanban, bugs, histórias ou dependências).
**293 testes backend** (263 + 30) e **49 frontend** (43 + 6) verdes; **build
OK**; migração sem drift. Demonstração ao vivo dos cinco tipos com conclusão,
cancelamento e vencida, confirmada na BD e na auditoria.

## 2. Modelo `WorkItem` (`apps/work_items/models.py`)

| Campo | Definição |
|---|---|
| `id`, `created_at`, `updated_at` | UUIDv4 + carimbos |
| `organisation` | obrigatória, `PROTECT`, `editable=False` (RT-01) |
| `product` | **obrigatório**, `PROTECT`, mesma empresa (R-AT-02/03 pressupõem produto) |
| `decision` | opcional, `PROTECT`, mesma empresa; coerente com o produto |
| `title` | obrigatório, não vazio |
| `work_type` | enum fechada: `action`/`review`/`validation`/`obligation`/`decision_follow_up` |
| `responsible` | FK `CustomUser`, `PROTECT`; Membership activa na mesma empresa |
| `priority` | enum mínima fechada `low`/`medium`/`high`, default `medium` |
| `due_at` | prazo opcional (nullable) |
| `notes` | opcional (`blank`) |
| `status` | `open`/`completed`/`cancelled`, default `open` |
| `completed_at`/`cancelled_at` | carimbos das transições (nullable) |
| `version` | `PositiveInteger` (concorrência optimista) |

**`is_overdue`** é uma **property calculada** (prazo definido e passado com a
pendência ainda `open`) — nunca persistida (artefacto 03, §2.4; R-AT-03).
Constraints de BD: `title` não vazio; `work_type`/`priority`/`status` fechados;
`version ≥ 1`. Tipo é **atributo** (não estado); um único ciclo de vida para
todos os tipos.

**Decisões de âmbito:** produto obrigatório (o artefacto de atenção não prevê
pendência empresarial). Enumeração de prioridade não existe nos artefactos F0 —
adoptada aqui a mínima fechada `low`/`medium`/`high`.

## 3. Transições

`(registo) → open`; `open → completed` (define `completed_at`); `open →
cancelled` (define `cancelled_at`). `completed` e `cancelled` são **finais** —
não se reabre no MVP; não há eliminação física. A edição só é permitida enquanto
`open`.

## 4. Contratos (sob /api/v1/)

| Método | Caminho | Efeito | Códigos |
|---|---|---|---|
| GET | `/work-items` | Lista (filtros; paginação) | 200, 400, 403 |
| POST | `/work-items` | Cria (`open`) | 201, 400, 403 |
| GET | `/work-items/{id}` | Detalhe | 200, 403, 404 |
| PATCH | `/work-items/{id}` | Edição (só `open`) | 200, 400, 403, 404, 409 |
| POST | `/work-items/{id}/complete` | open → completed | 200, 403, 404, 409 |
| POST | `/work-items/{id}/cancel` | open → cancelled | 200, 403, 404, 409 |

Sem DELETE (405). Filtros: `product`, `status`, `work_type`, `responsible`,
`overdue`. Ordenação determinística (`-created_at`, `id`). Todas as operações
mutáveis exigem `expected_version` → **409** em versão obsoleta ou estado final;
**404** para acesso cruzado. Entrada estrita (rejeita `organisation`/`status`/
`version`/timestamps).

## 5. Isolamento (RT-01)

Empresa derivada da Membership; sem contexto → 403. Pendência de outra empresa →
**404 indistinguível**, tentativa cruzada auditada (`security.cross_org_attempt`,
`entity_type=work_item`). Responsável/produto/decisão alheios → **400**;
decisão incoerente com o produto → **400**. Filtros e paginação nunca atravessam
empresas.

## 6. Auditoria (RT-02) — evento 9

- criação → `work_item.created` (operação, `work_type`, `product_id`, `decision_id`);
- edição/conclusão/cancelamento → `work_item.updated` (operação e transição).

Metadados sem `notes` integrais (verificado: token único ausente dos eventos).

## 7. Frontend (`src/components/workitems/`)

`WorkItemSection` (container na ficha), `WorkItemList` (lista curta: título,
tipo, prioridade, prazo, estado, com sinal **(Vencida)** calculado no servidor),
`WorkItemForm` (criar/editar; tipos e prioridades fechados; ligação opcional à
decisão do produto), `WorkItemDetail` (acções: Editar/Concluir enquanto `open`;
Cancelar **com confirmação**; estados finais imutáveis). Filtros mínimos (estado,
tipo, apenas vencidas). Sem quadro kanban, sprint, backlog, bug, história ou
dependência. Integrado na ficha ao lado de documentos e decisões; execuções
permanecem indisponíveis.

## 8. Testes (36 novos; obrigatórios 1–24 cobertos)

Backend (`test_work_item_api.py` 27, `test_work_item_concurrency.py` 1,
`test_migration.py` 2):
1. criação com cada um dos 5 tipos ✔  2. tipo inválido → 400 ✔  3. estado inicial
`open` ✔  4. prioridade inválida → 400 ✔  5. prazo persistido ✔  6. vencimento
calculado (open) ✔  7. completed não vencida ✔  8. cancelada não vencida ✔  9.
conclusão ✔  10. cancelamento ✔  11. transição de estado final → 409 ✔  12. edição
de estado final → 409 ✔  13. responsável alheio → 400 ✔  14. produto alheio → 400
✔  15. decisão alheia → 400 ✔  16. Product–Decision incoerente → 400 ✔  17. filtros/
paginação isolados ✔ (+ filtro por vencimento)  18. concorrência sem dupla
transição ✔ (PostgreSQL real)  19. operações auditadas ✔  20. auditoria sem
conteúdo ✔  (+ sem DELETE → 405; versão obsoleta → 409; sem contexto → 403).

Frontend (`workitems.test.tsx` 6): estado vazio; **21.** UI cria/conclui/cancela
(com confirmação); **22.** UI apresenta vencimento; filtro por estado. **23.** sem
conceitos de gestão de projectos (só campos administrativos). **24.** suites +
build: **293 backend**, **49 frontend**, `npm run build` OK, `--check` limpo.

## 9. Demonstração ao vivo (Docker Compose; imagens reconstruídas)

Produto Demo → criadas as **cinco** tipologias: `action` "Preparar reunião"
(**concluída**), `review` "Rever documentação" (**cancelada** com confirmação),
`validation` "Validar requisitos" (aberta), `obligation` "Renovar licença" com
prazo 2026-06-02 (**Vencida**, aberta), `decision_follow_up` "Seguir decisão"
(aberta, **ligada** à decisão activa "Adoptar arquitectura modular (revista)").
**Confirmação na BD:** os cinco `work_type`, `action=completed`
(`completed_at`), `review=cancelled` (`cancelled_at`), `obligation` com `due_at`
(vencida por cálculo), `decision_follow_up` com `decision_id`. **Auditoria:**
`work_item.created`×5 + `work_item.updated`×2 (conclusão/cancelamento), só com
operação/transição/tipo/identificadores — **sem notas**. Dados de demonstração
mantidos (prática vigente desde PR03).

## 10. Ficheiros

- Backend criados: `apps/work_items/models.py`, `service.py`, `serializers.py`,
  `views.py`, `urls.py`, `migrations/0001_initial.py`, `tests/*` (3).
- Frontend criados: `src/api/workItems.ts`; `src/components/workitems/labels.ts`,
  `WorkItemList.tsx`, `WorkItemForm.tsx`, `WorkItemDetail.tsx`,
  `WorkItemSection.tsx`, `workitems.test.tsx`.
- Alterados: `config/urls.py`; `ProductDetail.tsx` (integra a secção);
  `portfolio.test.tsx` (mock responde a `/v1/work-items`); governação. Testes de
  migração (`portfolio`/`documents`/`decisions`/`work_items`) endurecidos (ver
  §11).
- Artefactos da Fase 0 não alterados.

## 11. Problemas e reservas

- **Problema corrigido (infra de testes):** ao acrescentar `work_items` (nova app
  dependente de `portfolio` e `decisions`), a suite completa passou a falhar de
  forma dependente da ordem — os `TransactionTestCase` de migração que revertem
  uma app base para zero **cascatam** e removem as tabelas das apps dependentes,
  reaplicando só a base e deixando dependentes sem tabela para testes seguintes.
  Corrigido tornando os quatro testes de migração **independentes de ordem**:
  restauram o esquema completo (`migrate`) no `setUp`/`tearDown`. Sem alteração de
  código de aplicação. Suite completa estável (293) confirmada.
- **Ambiente:** imagens Docker sem bind mount — reconstruídas/recriadas para a
  demo; container de BD reiniciado quando necessário.
- **Reservas:** o painel/visão de atenção (R-AT-02/03) **não** é implementado
  aqui — `decision_follow_up` e o prazo apenas alimentarão essas regras em fase
  posterior (F1-P07). Reabertura de pendências fora do âmbito (final é imutável).

## 12. Estado e próximo passo

- **F1-P04 Em execução (5/6).**
- Próximo prompt recomendado: **F1-P04-PR06** (validação integrada e fecho da
  F1-P04). Não iniciado.
