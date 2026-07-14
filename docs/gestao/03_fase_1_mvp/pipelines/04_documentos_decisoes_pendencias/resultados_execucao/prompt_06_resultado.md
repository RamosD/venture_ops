---
fase: F1
pipeline: F1-P04
prompt: F1-P04-PR06
modelo: claude-fable-5
inicio: 2026-07-14 09:10
fim: 2026-07-14 10:35
estado_execucao: Concluído
estado_revisao: Não revista
commit: não criado
---

# Resultado — Prompt 06 — Validação integrada e fecho da F1-P04

## 1. Veredicto

**F1-P04 Concluída (6/6).** Documentos versionados, tipos, decisões e pendências
estão integrados e utilizáveis no browser, isolados por empresa, com armazenamento
privado íntegro, concorrência estável, auditoria limpa e migrações sem drift.
Validação integrada ponta a ponta executada ao vivo; regressão completa verde
(**293 backend + 49 frontend + build**); concorrência estável em **3 rondas**;
checksums coincidentes; sem fugas de conteúdo na auditoria. **Nenhum defeito real
encontrado — nenhuma correcção de código de aplicação foi necessária.** Nenhuma
funcionalidade de F1-P05 foi antecipada. **VAL-004, VAL-005 e VAL-006 → Validadas**;
**VAL-002, VAL-012 e VAL-014 permanecem Parciais**.

## 2. Modelos e contratos finais

- **Document** (metadados) + **DocumentVersion** (imutável): tipos fechados
  (`contexto_da_empresa`/`visao_de_produto`/`instrucoes`/`decisao_detalhada`/
  `resultado`), marcadores `is_outdated`/`export_policy`. API `/documents`
  (list/create), `/documents/{id}` (get/patch), `/versions`, `/versions/{n}`,
  `/restore`, `/preview`. Sem DELETE.
- **Decision**: `active`/`superseded`, cadeia `supersedes` (OneToOne, inverso
  `replaced_by`). API `/decisions` (list/create), `/decisions/{id}` (get),
  `/decisions/{id}/supersede`. Sem DELETE/PATCH.
- **WorkItem**: 5 tipos fechados, `priority` low/medium/high, `status`
  open/completed/cancelled, `is_overdue` calculado. API `/work-items`
  (list/create), `/work-items/{id}` (get/patch), `/complete`, `/cancel`. Sem DELETE.

Todos exigem `expected_version` nas operações mutáveis (409 em versão obsoleta);
entrada estrita (rejeita `organisation`/`status`/`version`/chaves de servidor).

## 3. Política BD/Markdown e armazenamento

Fonte de verdade: BD guarda apenas metadados; o **conteúdo Markdown** vive só no
armazenamento privado (`StorageAdapter`), referenciado por `storage_key`.
Coordenação BD↔storage: objecto escrito **antes** da BD; falha de escrita → sem
versão; falha de BD após escrita → remoção controlada do órfão (`storage.failure`
se a remoção falhar). **Verificado nesta validação:** os 4 objectos de versão
existem, o SHA-256 do ficheiro **coincide** com o checksum na BD, `current_version`
nunca aponta para objecto inexistente (0 órfãos), chaves geradas no servidor
(`xx/30hex`), objectos **não públicos** (nenhuma rota serve `/var/storage`), path
traversal rejeitado (teste dedicado). **Limitação residual honesta:** uma falha
abrupta do processo **entre** a escrita do objecto e o commit da BD pode deixar um
objecto órfão (nunca referenciado, inócuo quanto a exposição); a reconciliação/GC
fica como tarefa operacional futura — **não** se declara transacção distribuída
nem fila (inexistentes).

## 4. Versões, recuperação e sanitização

Cada submissão cria versão imutável; a recuperação cria uma **nova** versão
reutilizando o objecto imutável da origem (histórico preservado). A preview usa
**exclusivamente** o endpoint seguro do backend (*escape-first*); revalidada ao
vivo com XSS/HTML/`javascript:`/`data:`/links/código: **0 `<script>`, 0 `<img>`**,
único `<a>` é o https com `rel="nofollow noopener" target="_blank"`, sem
`javascript:`/`data:text/html`, código e listas renderizados.

## 5. Tipos, decisões/cadeia, pendências/transições

- **Tipos:** enumeração fechada validada no servidor e filtrável; `denied` é só
  marcador — **não** omite o documento (confirmado ao vivo: o documento "Visão do
  Produto Demo" com exportação recusada continua listado); **não** existe geração
  de pacote/exportação (adiado para F1-P05).
- **Decisões:** cadeia Activa↔Substituída confirmada na ficha e na BD (nova
  `active` com `supersedes`; anterior `superseded` com `replaced_by`); sem edição
  destrutiva do histórico.
- **Pendências:** os 5 tipos com estados corretos; `open→completed`/`open→
  cancelled` finais (estados finais não transitam → 409); `is_overdue` calculado
  ("Renovar licença", prazo 2026-06-02, sinal **(Vencida)**).

## 6. Integração na ficha

`ProductDetail` compõe `DocumentSection` + `DecisionSection` + `WorkItemSection`,
cada uma a derivar os agregados **das associações via API** (por `productId`) —
**sem campos duplicados no Product** nem contagens simuladas. Execuções continua
identificada como indisponível. Confirmado ao vivo: as três áreas apresentam
dados reais em simultâneo.

## 7. Isolamento

Isolamento por empresa validado por testes dedicados de acesso cruzado nos três
módulos (documento/decisão/pendência alheios → **404 indistinguível** de
inexistente, tentativa auditada `security.cross_org_attempt` com o tipo de
entidade; responsável/produto/decisão/documento alheios → 400; coerência
product–decision). Filtros e paginação nunca revelam contagens externas.

## 8. Concorrência

Testes concorrentes reais em PostgreSQL, **estáveis em 3 rondas**: duas edições
documentais na mesma versão (uma vence, sem lost update; órfão da perdedora
removido); duas substituições da mesma decisão (uma vence, cadeia linear por
unicidade OneToOne); duas transições da mesma pendência (uma vence). Sem versões
duplicadas nem cadeias divergentes.

## 9. Auditoria

Eventos 5–7 (documentos), 8 (decisões), 9 (pendências) + acesso cruzado +
`storage.failure`. **Todos** com `correlation_id` (0 sem correlação). Inspecção
das chaves de metadados dos três módulos: só `operation`, `transition`, `version`,
`document_version`, `work_type`, `checksum` (abreviado), `from/to_version`,
`supersedes`, `replaced_by`, `product_id`, `detail_document_id`, `decision_id`,
`fields` — **nenhum** conteúdo Markdown, `context`, `decision_text` ou `notes`.
VAL-012 mantém-se **Parcial** (consulta/linha temporal e consolidação em F1-P07).

## 10. Migrações

`makemigrations --check` → **No changes detected** (drift zero). Aplicam em base
vazia (criação da base de testes) e na base de desenvolvimento existente.
Reversibilidade estrutural demonstrada em **base controlada** (testes de migração,
agora independentes de ordem). **Nota honesta:** reverter as migrações destes
módulos **remove** as respectivas tabelas — **não** preserva conteúdo documental
nem dados do módulo; os dados de **outras** aplicações permanecem intactos.

## 11. Testes e demonstração

- **Regressão:** backend **293 OK**; frontend **49 OK**; `npm run build` OK; health
  `/live` e `/ready` → 200 (db+storage ok); Docker Compose `healthy`.
- **Concorrência:** 4 testes concorrentes × **3 rondas** — todas OK.
- **Demonstração integrada (ao vivo):** ficha do Produto Demo com os três módulos
  reais; documento v1→v2→recuperação v3 e preview XSS neutralizada; cadeia de
  decisão Activa↔Substituída; 5 pendências com conclusão/cancelamento/vencida e
  `decision_follow_up` ligada. Estados e integridade confirmados na BD, no
  armazenamento (checksums) e na auditoria.

## 12. VAL actualizadas

- **VAL-004 → Validada** (documentos: criação, edição, versões, histórico,
  recuperação, marcadores e preview — evidência integrada).
- **VAL-005 → Validada** (decisões: registo, associação e substituição/cadeia).
- **VAL-006 → Validada** (pendências: 5 tipos e transições, vencimento calculado).
- **VAL-002 Parcial** (evidência dos três módulos acrescentada; suite transversal
  em F1-P07/MVP-18).
- **VAL-012 Parcial** (emissores 5–9 auditados; consolidação/consulta em F1-P07).
- **VAL-014 Parcial** (preview revalidada; anti-*prompt injection* e restantes
  controlos em F1-P07).

## 13. Problemas corrigidos e reservas

- **Problemas:** nenhum defeito de aplicação encontrado nesta validação; nenhuma
  correcção de código foi necessária. (O único ajuste técnico da pipeline — a
  independência de ordem dos testes de migração — foi feito em PR05.)
- **Reservas / integrações adiadas:** `instrucoes`↔função (F1-P05); `resultado`↔
  execução/resultado (F1-P05/P06); aplicação efectiva de `export_policy` no pacote
  (F1-P05); atenção por documento/pendência/decisão (F1-P07); pesquisa e
  comparação de versões (V1). Sem desvio estrutural real → **nenhuma decisão
  global criada**.

## 14. Estado final e próximo passo

- **F1-P04 Concluída (6/6).** Estado de revisão: **Não revista** — a execução
  técnica não substitui a revisão humana (guia §10).
- Próximo passo recomendado: efectuar **commit** de F1-P04 e **gerar a pipeline
  F1-P05** (funções, execuções e pacote de contexto) just-in-time. **Não iniciado
  nesta iteração.**
