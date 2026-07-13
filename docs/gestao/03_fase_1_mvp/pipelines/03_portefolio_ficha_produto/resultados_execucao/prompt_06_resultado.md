---
fase: F1
pipeline: F1-P03
prompt: F1-P03-PR06
modelo: claude-opus-4-8
inicio: 2026-07-13 17:30
fim: 2026-07-13 18:35
estado_execucao: Concluído
estado_revisao: Não revista
commit: não criado
---

# Resultado — Prompt 06 — Validação integrada e fecho da F1-P03

## 1. Veredicto

**F1-P03 Concluída (6/6).** O portefólio e a ficha administrativa estão completos,
isolados por empresa, com concorrência optimista, auditoria e experiência de
utilização funcional no browser. Validação integrada ponta a ponta executada ao
vivo; regressão completa verde; migrações sem drift e reversíveis. **VAL-003 →
Validada**; **VAL-002 e VAL-012 permanecem Parciais** (evidência do módulo Product
acrescentada; consolidação global fica para F1-P07). Um único defeito real foi
corrigido: **lacuna de cobertura** de isolamento nas operações de ciclo de vida
(sem alteração de código de aplicação — só testes). Nenhuma funcionalidade de
F1-P04 foi antecipada.

## 2. Comportamento implementado (consolidado)

Gestão de vários produtos por empresa: criar (só `name`+`purpose`), listar (com
filtros e paginação), consultar, editar a ficha, arquivar/reactivar e marcar como
revisto — tudo com contexto de empresa derivado no servidor, autorização por
Membership activa, concorrência optimista e auditoria. UI React/TS integrada
(cliente HTTP central, sessão por cookie + CSRF), sem store global, router ou
biblioteca de UI dedicados.

## 3. Contratos finais (sob /api/v1/)

| Método | Caminho | Efeito | Códigos |
|---|---|---|---|
| GET | `/products` | Lista (filtros `status`/`responsible`, paginação `page`/`page_size`) | 200, 400, 403 |
| POST | `/products` | Cria (só `name`+`purpose` obrigatórios) | 201, 400, 403 |
| GET | `/products/{id}` | Detalhe (isolado) | 200, 403, 404 |
| PATCH | `/products/{id}` | Edição comum (`expected_version`) | 200, 400, 403, 404, 409 |
| POST | `/products/{id}/archive` | active → archived | 200, 400, 403, 404, 409 |
| POST | `/products/{id}/reactivate` | archived → active | 200, 400, 403, 404, 409 |
| POST | `/products/{id}/mark-reviewed` | actualiza `last_reviewed_at` (só active) | 200, 400, 403, 404, 409 |

Sem DELETE (não há eliminação física). Resposta de listagem: `results`, `count`,
`page`, `page_size`, `num_pages`. Leitura de produto inclui `version`.

## 4. Campos finais de Product

`id` (UUID), `organisation` (FK obrigatória, `PROTECT`, `editable=False`),
`name`, `purpose` (obrigatórios, não vazios), `status` (`active`/`archived`,
default `active`), `responsible` (FK `CustomUser`, `PROTECT`; Membership activa na
mesma empresa), `last_reviewed_at` (inicializada na criação; `default=timezone.now`;
nunca `auto_now`), `target_audience`/`phase`/`notes` (opcionais, `blank`),
`next_review_at` (opcional, `null`), `version` (PositiveInteger, ≥1, defeito 1),
`created_at`/`updated_at`. **`attention_level` não é persistido** (MVP-05.R3).
Constraints de BD: `name`/`purpose` não vazios e `version ≥ 1`.

## 5. Estados e transições (artefacto 03 §2.1)

Estados: **active**, **archived**. Transições: (criação)→active; active→archived
(arquivo); archived→active (reactivação). Nenhum estado adicional; sem eliminação
física; arquivo é transição, não `delete`.

## 6. Política de revisão (CLR-02 / MVP-05.R1)

`last_reviewed_at` é inicializada na criação e **só** é actualizada pela operação
explícita "marcar como revisto" (auditada, apenas em produtos active). Edições
comuns, arquivo e reactivação **não** a alteram. Verificado ao nível do timestamp
(edição: `last_reviewed_at == created_at`, `updated_at` avança; revisão: altera).

## 7. Política de concorrência

Todas as operações mutáveis exigem `expected_version`, bloqueiam a linha
(`select_for_update`), validam a versão e incrementam-na **exactamente uma vez**;
versão obsoleta → 409, sem lost update. Teste real em PostgreSQL (2 escritas com a
mesma versão) **estável em 3 execuções**: uma vence, a outra recebe conflito.

## 8. Isolamento (RT-01)

Empresa derivada da Membership activa; sem contexto → 403. Listagem/detalhe/edição
/ciclo de vida só operam na empresa do contexto; produto de outra empresa →
**404 indistinguível** de inexistente. Confirmado ao vivo com duas empresas: GET,
PATCH, archive, reactivate e mark-reviewed alheios → 404; lista de B não inclui
produtos de A; **todas as tentativas cruzadas auditadas** (`security.cross_org_attempt`,
`entity_type=product`, empresa do contexto, `correlation_id`). **VAL-002 mantém-se
Parcial** (restantes módulos de domínio ainda não existem; suite completa em
F1-P07/MVP-18).

## 9. Auditoria (RT-02)

Eventos da lista fechada: `product.created`, `product.updated` (edição comum,
reactivação e revisão, com a operação nos metadados), `product.archived`,
`security.cross_org_attempt`. Metadados mínimos (operação, transições, nomes de
campos); **nunca** `purpose`/`notes` integrais (verificado: 0 eventos com conteúdo
integral). Todos com `correlation_id`. **VAL-012 mantém-se Parcial** (consolidação
e consulta em F1-P07).

## 10. Migrações

`makemigrations --check --dry-run` → No changes detected. `portfolio/0001_initial`
aplica em base vazia (base de testes) e na base de desenvolvimento existente;
**reverte para zero e reaplica** com os dados fora do módulo intactos
(users=2, orgs=1, eventos de auditoria preservados). Não altera migrações
históricas.

## 11. Testes

- **Backend: 185 testes OK** (inclui 8 novos de isolamento cross-org do módulo
  Product; 69 no módulo portfolio: modelo/migração, API, ciclo de vida,
  concorrência, isolamento). Concorrência estável em 3 rondas isoladas.
- **Frontend: 28 testes OK** + `npm run build` (tsc + vite) OK.

## 12. Demonstração ponta a ponta (ao vivo)

Cenário integrado (HTTP, base de desenvolvimento): conta inicial segura → login →
onboarding → criar Produto A (só name+purpose; defaults status=active, version=1,
responsável, `last_reviewed_at` definida) → criar Produto B → listar (2) → editar A
(`last_reviewed_at` inalterada) → marcar A revisto (`last_reviewed_at` muda) →
conflito com versão obsoleta (409, nome intacto) → arquivar B (edição bloqueada,
409) → filtrar arquivados (B) → reactivar B → paginação (`page_size=1`,
`num_pages=2`) → inspecção dos eventos de auditoria. Isolamento com 2 empresas
confirmado. (UI do ciclo completo já demonstrada no browser em PR05.)

Health `/live` e `/ready` → 200 (db+storage ok). Docker Compose: db, backend e
frontend `healthy`.

## 13. VAL actualizadas

- **VAL-003 → Validada** — vários produtos geríveis, ficha mínima, consulta/edição,
  arquivo/reactivação, filtros/paginação, revisão explícita, isolamento,
  concorrência, UI funcional, testes e demonstração. Agregados reais, atenção e
  pesquisa **não** validados (fora do âmbito).
- **VAL-002 → Parcial** (evidência do módulo Product acrescentada).
- **VAL-012 → Parcial** (evidência do módulo Product acrescentada).

## 14. Ficheiros alterados

- Criados: `backend/apps/portfolio/tests/test_product_isolation.py` (8 testes);
  este relatório.
- Alterados (governação): `docs/gestao/01_status_pipelines.md`,
  `00_painel_execucao_global.md`, `05_diario_execucao_ia.md`,
  `04_matriz_validacao_global.md`.
- **Sem alterações de código de aplicação** (nenhum defeito de comportamento
  encontrado). Sem novas migrações. Artefactos da Fase 0 não alterados.

## 15. Problemas corrigidos

- **Cobertura insuficiente de isolamento** nas operações de ciclo de vida:
  faltava provar que archive/reactivate/mark-reviewed alheios falham **e são
  auditados**, e que a lista não mistura empresas. Adicionados 8 testes
  (`test_product_isolation.py`). Nenhuma correcção de código foi necessária — o
  comportamento já era correcto.

## 16. Reservas

- Vistas agregadas reais (documentos/decisões/pendências/execuções) e nível de
  atenção — F1-P04+/F1-P07 (a ficha reserva área informativa, sem dados simulados).
- Consolidação global de auditoria e suite completa de segurança (MVP-18) — F1-P07.
- VAL-002/VAL-012 só ficarão completas quando os restantes módulos existirem.

## 17. Estado final da pipeline

- **F1-P03 Concluída (6/6).** Portefólio e ficha administrativa prontos e
  utilizáveis no browser; sem antecipar F1-P04.

## 18. Próximo passo recomendado

- Efectuar **commit** de F1-P03 e **gerar a pipeline F1-P04** (documentos, tipos,
  decisões e pendências) just-in-time. Não iniciado nesta iteração.
