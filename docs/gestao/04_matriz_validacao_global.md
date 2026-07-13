# Matriz de validação global

A matriz valida capacidades do VentureOps AI. Aponta para resultados e
evidências; não os reproduz. Actualizar apenas por evidência (nova validação ou
mudança de estado), pelo respectivo ID.

Estados: `Não iniciado` | `Em validação` | `Validado` | `Parcial` | `Falhado` |
`Bloqueado` | `Não aplicável`.

| ID | Capacidade | Fase | Critério | Estado | Evidência | Última validação |
|---|---|---|---|---|---|---|
| VAL-001 | Autenticação | MVP | Acesso autenticado e sessão segura | Validado | Escopo MVP completo (PR07–PR09): login/sessão/logout por cookie (HttpOnly, SameSite=Lax, Secure condicional), CSRF, conta controlada, recuperação por token único/expirável (invalida sessões), rate limiting persistente (PostgreSQL, sem Redis) auditado, perfil mínimo. 78 testes backend + 10 frontend; e2e e demos ao vivo (login/recuperação/rate limit/perfil). Hardening PR12: email case-insensitive (constraint `Lower(email)`), `createinitialuser` sem palavra-passe em CLI, rate limiting atómico (advisory lock) com retenção/limpeza. Ver `prompt_07/08/09/12_resultado.md`. | 2026-07-13 |
| VAL-002 | Isolamento entre empresas | MVP | Nenhum acesso transversal entre tenants | Parcial | Contexto de empresa derivado da Membership no servidor; acesso por id valida pertença (cruzado → 404 auditado; sem Membership → 403); bateria de isolamento com 2 empresas (8 testes) nos endpoints existentes. Ver `prompt_10/11_resultado.md`. **Parcial**: módulos de domínio (produtos, documentos…) ainda não existem; suite completa em F1-P07/MVP-18. Hardening PR12: garantia de BD de uma Membership activa por utilizador + onboarding concorrente testado. | 2026-07-13 |
| VAL-003 | Portefólio de produtos | MVP | CRUD e arquivo validados | Não iniciado | — | — |
| VAL-004 | Documentos e versões | MVP | Versões criadas e recuperáveis | Não iniciado | — | — |
| VAL-005 | Decisões | MVP | Registo e associação a produto | Não iniciado | — | — |
| VAL-006 | Pendências administrativas | MVP | Estados e prazos validados | Não iniciado | — | — |
| VAL-007 | Funções organizacionais | MVP | Função utilizável numa execução | Não iniciado | — | — |
| VAL-008 | Pacote de contexto | MVP | Versões exactas preservadas | Não iniciado | — | — |
| VAL-009 | Resultados de IA | MVP | Resultado associado à execução correcta | Não iniciado | — | — |
| VAL-010 | Revisão e aprovação | MVP | Nenhuma aplicação sem validação humana | Não iniciado | — | — |
| VAL-011 | Visão de atenção | MVP | Alertas explicáveis e coerentes | Não iniciado | — | — |
| VAL-012 | Auditoria | MVP | Operações críticas rastreáveis | Parcial | `AuditEvent` append-only + serviço (correlação, conteúdo proibido rejeitado). Emissores integrados: autenticação/falhas (PR07/09), empresa criação/alteração (PR10), acesso cruzado (PR11). Ver `prompt_06/07/09/10/11_resultado.md`. **Parcial**: consulta/linha temporal e restantes emissores em F1-P07. | 2026-07-13 |
| VAL-013 | Exportação | MVP | Dados e Markdown exportáveis | Não iniciado | — | — |
| VAL-014 | Segurança de Markdown | MVP | Conteúdo renderizado sem XSS | Não iniciado | — | — |
| VAL-015 | Backup e recuperação | MVP | Recuperação validada | Não iniciado | — | — |
| VAL-016 | Deploy e rollback | MVP | Deploy e reversão executáveis | Parcial | Fundação apenas: health checks `/health/live` e `/health/ready` + CI mínimo build/testes (`.github/workflows/ci.yml`); ver `03_fase_1_mvp/pipelines/02_.../resultados_execucao/prompt_05_resultado.md`. **Deploy e rollback NÃO validados** (MVP-20/F1-P08). | 2026-07-12 |
