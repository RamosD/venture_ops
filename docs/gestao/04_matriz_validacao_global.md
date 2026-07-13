# Matriz de validação global

A matriz valida capacidades do VentureOps AI. Aponta para resultados e
evidências; não os reproduz. Actualizar apenas por evidência (nova validação ou
mudança de estado), pelo respectivo ID.

Estados: `Não iniciado` | `Em validação` | `Validado` | `Parcial` | `Falhado` |
`Bloqueado` | `Não aplicável`.

| ID | Capacidade | Fase | Critério | Estado | Evidência | Última validação |
|---|---|---|---|---|---|---|
| VAL-001 | Autenticação | MVP | Acesso autenticado e sessão segura | Validado | Escopo MVP completo (PR07–PR09): login/sessão/logout por cookie (HttpOnly, SameSite=Lax, Secure condicional), CSRF, conta controlada, recuperação por token único/expirável (invalida sessões), rate limiting persistente (PostgreSQL, sem Redis) auditado, perfil mínimo. 78 testes backend + 10 frontend; e2e e demos ao vivo (login/recuperação/rate limit/perfil). Hardening PR12: email case-insensitive (constraint `Lower(email)`), `createinitialuser` sem palavra-passe em CLI, rate limiting atómico (advisory lock) com retenção/limpeza. Ver `prompt_07/08/09/12_resultado.md`. | 2026-07-13 |
| VAL-002 | Isolamento entre empresas | MVP | Nenhum acesso transversal entre tenants | Parcial | Contexto de empresa derivado da Membership no servidor; acesso por id valida pertença (cruzado → 404 auditado; sem Membership → 403); bateria de isolamento com 2 empresas (8 testes) nos endpoints existentes. Módulo `Product` (F1-P03-PR02/PR04/PR06): listagem/detalhe/edição/ciclo de vida só da empresa do contexto; produto alheio → 404 indistinguível de inexistente (inclui archive/reactivate/mark-reviewed); filtros nunca atravessam empresas; tentativa cruzada auditada (`security.cross_org_attempt`, `entity_type=product`). 8 testes dedicados de isolamento cross-org + E2E ao vivo com 2 empresas (PR06). Ver `prompt_10/11_resultado.md` e `03_.../prompt_02/04/06_resultado.md`. **Parcial**: restantes módulos de domínio ainda não existem; suite completa em F1-P07/MVP-18. Hardening PR12: garantia de BD de uma Membership activa por utilizador + onboarding concorrente testado. | 2026-07-13 |
| VAL-003 | Portefólio de produtos | MVP | CRUD e arquivo validados | Validado | Módulo Product completo (F1-P03, PR01–PR06): vários produtos geríveis; criação com ficha mínima (só `name`+`purpose`, defaults no servidor); consulta e edição; arquivo/reactivação (active↔archived, sem eliminação física); filtros (estado/responsável), paginação e ordenação; revisão explícita ("marcar como revisto" é a única fonte de `last_reviewed_at`); isolamento por empresa (produto alheio → 404 auditado; ciclo de vida alheio falha); concorrência optimista (409, sem lost update, estável em 3 rondas); UI React/TS funcional. Fecho (PR06): E2E ao vivo dos 21 passos + isolamento com 2 empresas; regressão 185 testes backend + 28 frontend + build; migração sem drift e reversível com dados preservados; health/Docker OK. 69 testes backend do módulo + 16 de componente. Ver `prompt_01–06_resultado.md`. **Fora do âmbito** (não validados aqui): agregados reais (documentos/decisões/pendências/execuções), nível de atenção e pesquisa. | 2026-07-13 |
| VAL-004 | Documentos e versões | MVP | Versões criadas e recuperáveis | Não iniciado | — | — |
| VAL-005 | Decisões | MVP | Registo e associação a produto | Não iniciado | — | — |
| VAL-006 | Pendências administrativas | MVP | Estados e prazos validados | Não iniciado | — | — |
| VAL-007 | Funções organizacionais | MVP | Função utilizável numa execução | Não iniciado | — | — |
| VAL-008 | Pacote de contexto | MVP | Versões exactas preservadas | Não iniciado | — | — |
| VAL-009 | Resultados de IA | MVP | Resultado associado à execução correcta | Não iniciado | — | — |
| VAL-010 | Revisão e aprovação | MVP | Nenhuma aplicação sem validação humana | Não iniciado | — | — |
| VAL-011 | Visão de atenção | MVP | Alertas explicáveis e coerentes | Não iniciado | — | — |
| VAL-012 | Auditoria | MVP | Operações críticas rastreáveis | Parcial | `AuditEvent` append-only + serviço (correlação, conteúdo proibido rejeitado). Emissores integrados: autenticação/falhas (PR07/09), empresa criação/alteração (PR10), acesso cruzado (PR11), produto criação/edição/ciclo de vida (F1-P03-PR02/PR04: `product.created`/`product.updated`/`product.archived` com apenas operação, transições e nomes de campos — reactivação e revisão usam `product.updated` com a operação nos metadados; sem `purpose`/`notes` integrais). Fecho PR06: E2E confirma criação/edição/arquivo/reactivação/revisão/tentativa cruzada auditadas, com `correlation_id` e 0 fugas de conteúdo. Ver `prompt_06/07/09/10/11_resultado.md` e `03_.../prompt_02/04/06_resultado.md`. **Parcial**: consulta/linha temporal e restantes emissores em F1-P07. | 2026-07-13 |
| VAL-013 | Exportação | MVP | Dados e Markdown exportáveis | Não iniciado | — | — |
| VAL-014 | Segurança de Markdown | MVP | Conteúdo renderizado sem XSS | Não iniciado | — | — |
| VAL-015 | Backup e recuperação | MVP | Recuperação validada | Não iniciado | — | — |
| VAL-016 | Deploy e rollback | MVP | Deploy e reversão executáveis | Parcial | Fundação apenas: health checks `/health/live` e `/health/ready` + CI mínimo build/testes (`.github/workflows/ci.yml`); ver `03_fase_1_mvp/pipelines/02_.../resultados_execucao/prompt_05_resultado.md`. **Deploy e rollback NÃO validados** (MVP-20/F1-P08). | 2026-07-12 |
