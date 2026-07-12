# Requisitos mínimos de segurança do MVP — VentureOps AI

* Fase: F0 — Preparação e alinhamento
* Item tratado: F0-B12 (F0-12)
* Decisão bloqueadora: DB-12
* Estado do artefacto: Confirmado com reservas (DEC-20260712-04); mecanismo de sensibilidade fechado (`export_policy`, DEC-F0-FINAL-08); plataforma de deploy transferida para MVP-20 (DEC-F0-FINAL-02)
* Prompt de origem: F0-P04-PR03 (reexecução); marcador de sensibilidade e transferência do deploy fechados no fecho formal da Fase 0 (2026-07-12)

## 1. Identificação

Artefacto que fixa os controlos de segurança **não adiáveis** do MVP, ao nível
funcional e verificável. Não contém código, configuração, esquema de tabelas,
endpoints, escolha de fornecedor nem infraestrutura. Distingue: **facto**,
**decisão adoptada tacitamente**, **requisito obrigatório**, **recomendação**,
**ponto a validar** e **risco residual**.

## 2. Objectivo

Estabelecer o checklist mínimo de segurança do MVP nos seis domínios da baseline
(isolamento, autorização, protecção documental, auditoria, segredos,
exportação), o nível de auditoria, as operações sujeitas a validação humana, a
política de IA externa e os requisitos de retenção/eliminação/residência —
cada controlo com forma de verificação na Fase 1, sem inventar requisitos legais
nem infraestrutura.

## 3. Factos e fontes

* SF-01 — Requisitos transversais da baseline: RT-01 isolamento; RT-02 rastreabilidade; RT-05 validação humana; RT-07 segurança de conteúdo; RT-08 recuperação (`05_backlog_macro.md`).
* SF-02 — A arquitectura define autenticação/autorização (§7) e segurança (§11): isolamento por empresa, autorização no backend, sanitização de Markdown, objectos privados, minimização de logs, rate limiting, auditoria, protecção contra prompt injection.
* SF-03 — Fluxo e modelo do MVP: uma resposta de IA começa como não validada e não altera automaticamente o estado oficial (artefacto 02, §2.2; arquitectura §2.5).
* SF-04 — Fronteira BD/Markdown e versões imutáveis (artefacto 05): acesso mediado pelo backend; versões recuperáveis.
* SF-05 — Regra de validação humana de resultados de IA: capacidade VAL-010 da matriz global ("nenhuma aplicação sem validação humana").

## 4. Decisões adoptadas tacitamente (dos artefactos 08 e 09)

Tratadas como vigentes para esta execução (governação não bloqueante, DEC-20260712-01); nenhuma incoerência material encontrada.

* DT-01 — MVP com **uma empresa activa** e utilizador único **Owner**; estrutura preparada para multiempresa/memberships (artefacto 08, D-08-01/02/03).
* DT-02 — **Isolamento por empresa obrigatório desde o MVP**; autorização no backend; nunca confiar em `organisation_id` do cliente (artefacto 08, §4 IS-01/IS-02).
* DT-03 — **Django Auth com sessão segura por cookie**; SSO/OIDC/MFA adiados (artefacto 09, §3.1).
* DT-04 — Armazenamento documental: **filesystem** local; **S3 compatível** em ambiente partilhado (artefacto 09, §3.2).
* DT-05 — Ambiente **greenfield**; **plataforma de deploy por identificar** — não inventar (artefacto 09, §1, §3.3).

## 5. Pressupostos

* PS-01 — A stack proposta (React/TS, Django/DRF, PostgreSQL, Markdown versionado) é a base do desenho (artefacto 09, a validar P-02 desse artefacto).
* PS-02 — TLS disponível nos ambientes partilhados/produção; em desenvolvimento local pode não existir, pelo que `Secure` no cookie é condicional ao ambiente com TLS.
* PS-03 — A classificação avançada de sensibilidade documental é de fase posterior; no MVP usa-se um mecanismo simples (marcador não-exportável).

## 6. Modelo de ameaças mínimo

Ameaças que os controlos abaixo devem mitigar:

* MA-01 — Acesso a dados de outra empresa (fuga entre tenants).
* MA-02 — Escalada de acesso por confiança em identificadores do cliente.
* MA-03 — XSS/execução via Markdown ou resultado de IA importado.
* MA-04 — Prompt injection através de conteúdo documental no pacote de contexto.
* MA-05 — Exfiltração por exportação indevida ou envio a IA externa.
* MA-06 — Exposição de segredos/dados sensíveis em logs ou objectos públicos.
* MA-07 — Perda ou corrupção de dados/versões sem recuperação.
* MA-08 — Aplicação de resultado de IA como oficial sem validação humana.

## 7. Checklist de controlos

Cada controlo: identificador, domínio, requisito, prioridade, fase, verificação,
evidência esperada, estado de decisão, dependências. Prioridade: **Obrigatório**
(não adiável no MVP) ou **Recomendado**. Fase de implementação: F1 salvo
indicação. Estado de decisão: **Adoptada tacitamente** salvo indicação.

### 7.1. Isolamento (RT-01)

| ID | Requisito | Prioridade | Verificação | Evidência esperada |
|---|---|---|---|---|
| SEC-ISO-01 | Toda a entidade empresarial tem contexto explícito de empresa; nenhuma consulta ou operação confia apenas num `organisation_id` do cliente. | Obrigatório | Teste de integração de isolamento entre empresas | Testes que provam ausência de acesso transversal |
| SEC-ISO-02 | Cada operação valida: utilizador autenticado, associação à empresa, pertença das entidades à mesma empresa, autorização da operação e estado do recurso. | Obrigatório | Teste automatizado por endpoint/serviço | Casos negativos (403/404) cobertos |
| SEC-ISO-03 | Não é possível associar um documento/entidade de uma empresa a um recurso de outra. | Obrigatório | Teste de integridade referencial funcional | Tentativa cruzada rejeitada |

### 7.2. Autorização (RT-01)

| ID | Requisito | Prioridade | Verificação | Evidência esperada |
|---|---|---|---|---|
| SEC-AUT-01 | Autorização aplicada **sempre no backend**; o frontend nunca é a única barreira. | Obrigatório | Revisão de código + teste de API sem UI | Pedido directo à API respeita autorização |
| SEC-AUT-02 | No MVP, o Owner detém as operações críticas (exportar, arquivar, aprovar); a base para restringir por papel fica preparada para V1. | Obrigatório | Demonstração funcional | Operações críticas exigem Owner |
| SEC-AUT-03 | Operações críticas exigem autorização explícita e são auditadas (ver §8). | Obrigatório | Teste + inspecção de auditoria | Evento de auditoria por operação crítica |

### 7.3. Protecção documental (RT-03, RT-07)

| ID | Requisito | Prioridade | Verificação | Evidência esperada |
|---|---|---|---|---|
| SEC-DOC-01 | Leitura/escrita de conteúdo documental mediada pelo backend; a IA não acede directamente ao armazenamento nem à BD. | Obrigatório | Revisão de código + teste | Sem caminho de acesso directo |
| SEC-DOC-02 | Markdown e resultados importados tratados como conteúdo não confiável; sanitização de HTML, scripts desactivados, URLs perigosas bloqueadas, sem execução de código, conteúdo incorporado restringido, protecção XSS. | Obrigatório | Teste de sanitização/XSS | Payloads XSS neutralizados |
| SEC-DOC-03 | Objectos de armazenamento privados; chaves/nomes gerados pelo servidor; acesso via backend ou URLs temporárias; checksum; limites de tamanho; UTF-8; versões imutáveis. | Obrigatório | Inspecção de configuração + teste | Objecto não acessível publicamente; versão não editável |
| SEC-DOC-04 | Nomes de ficheiro sanitizados; caminhos nunca construídos a partir de input não validado. | Obrigatório | Teste de path traversal | Tentativa de traversal rejeitada |

### 7.4. Auditoria (RT-02)

| ID | Requisito | Prioridade | Verificação | Evidência esperada |
|---|---|---|---|---|
| SEC-AUD-01 | Registo append-only dos eventos da lista fechada (§8), com os campos definidos e sem conteúdo proibido. | Obrigatório | Teste + inspecção | Eventos gerados; ausência de segredos |
| SEC-AUD-02 | Tentativas de acesso entre empresas e falhas repetidas de autenticação são auditadas. | Obrigatório | Teste de segurança | Evento registado no cenário negativo |

### 7.5. Segredos (RT-07)

| ID | Requisito | Prioridade | Verificação | Evidência esperada |
|---|---|---|---|---|
| SEC-SEC-01 | Segredos, tokens e chaves fora do código, em variáveis de ambiente ou gestor de segredos; validação de configuração no arranque. | Obrigatório | Inspecção de configuração | Sem segredos no repositório |
| SEC-SEC-02 | TLS obrigatório em ambientes partilhados/produção; cifragem em trânsito; cifragem no armazenamento quando a infraestrutura a disponibilizar. | Obrigatório (TLS) / Recomendado (at-rest) | Inspecção de ambiente | TLS activo; nota sobre at-rest |
| SEC-SEC-03 | Logs sem palavras-passe, tokens, chaves, prompts/documentos/resultados completos nem dados sensíveis desnecessários. | Obrigatório | Revisão de logs | Amostra de logs sem dados sensíveis |

### 7.6. Exportação (RT-06)

| ID | Requisito | Prioridade | Verificação | Evidência esperada |
|---|---|---|---|---|
| SEC-EXP-01 | Exportação de dados/documentos restrita ao Owner e auditada; escopo validado. | Obrigatório | Teste de autorização + auditoria | Export não-Owner rejeitado; evento gerado |
| SEC-EXP-02 | Exportação preserva as versões documentais e não expõe objectos publicamente. | Obrigatório | Demonstração funcional | Pacote exportado sem URLs públicas permanentes |

### 7.7. Secções complementares

| ID | Domínio | Requisito | Prioridade | Verificação |
|---|---|---|---|---|
| SEC-AUTH-01 | Autenticação/sessão | Django Auth; cookie `HttpOnly`, `Secure` (com TLS), `SameSite`; CSRF; recuperação por token temporário; invalidação de sessão após mudanças críticas; sem credenciais no frontend. | Obrigatório | Inspecção + teste de sessão/CSRF |
| SEC-AUTH-02 | Rate limiting | Rate limiting em login, recuperação de palavra-passe, exportação, upload e geração de pacotes; aplicável no reverse proxy ou backend. | Obrigatório | Teste de rate limiting |
| SEC-IA-01 | IA externa | Ver política em §10. | Obrigatório | Demonstração + inspecção |
| SEC-STO-01 | Armazenamento | Consistência coordenada BD↔ficheiro pelo backend; objectos privados; fallback filesystem apenas em desenvolvimento/piloto. | Obrigatório | Teste de consistência |
| SEC-BAK-01 | Backup/recuperação | Ver §11-A (backup e recuperação). | Obrigatório | Teste de restauro |
| SEC-RET-01 | Retenção/eliminação | Ver §11-B. | Obrigatório (capacidade) | Demonstração de arquivamento/exportação |
| SEC-INJ-01 | Prompt injection | Instruções da função separadas do conteúdo documental; documentos tratados como dados; pedidos de acção em documentos não geram acções automáticas (coerente com artefacto 07). | Obrigatório | Teste com injecção plantada |
| SEC-AGT-01 | Agentes (futuro) | Tokens de agente com escopo, expiração, rotação e revogação; nenhuma credencial partilhada entre empresas. | Recomendado (V1) | Inspecção quando aplicável |

## 8. Eventos auditáveis do MVP (lista fechada)

Eventos que geram auditoria funcional:

1. autenticação relevante (login/logout);
2. falhas repetidas de autenticação;
3. criação e alteração de empresa;
4. criação, edição e arquivo de produto;
5. criação e alteração documental;
6. criação de versão documental;
7. recuperação/restauração de versão;
8. criação e alteração de decisão;
9. criação e alteração de pendência;
10. criação e alteração de função organizacional;
11. criação de execução;
12. geração/exportação de pacote de contexto;
13. importação de resultado de IA;
14. aprovação de resultado;
15. rejeição de resultado;
16. pedido de correcção;
17. aplicação manual de alteração aprovada;
18. exportação de dados;
19. alteração futura de membros ou papéis (quando existir);
20. tentativa de acesso entre empresas;
21. falha de armazenamento relevante.

**Campos por evento:** actor; empresa; acção; entidade; data; resultado;
correlação; metadados permitidos.

**Nunca registar:** palavras-passe; tokens; chaves; prompts completos;
documentos completos; resultados completos; dados sensíveis sem necessidade.

## 9. Operações sujeitas a validação humana no produto (obrigatório)

Regra funcional **inalterada** pela governação documental (SF-03, SF-05). Um
resultado de IA não é decisão oficial, documento actualizado, pendência
concluída nem alteração aplicada, e não se torna oficial só por ter sido
importado. Exigem acção explícita de utilizador autorizado:

* SEC-HUM-01 — aprovação ou rejeição de resultado de IA;
* SEC-HUM-02 — aplicação de alterações propostas por IA (operação controlada e auditável; sem aplicação automática);
* SEC-HUM-03 — criação de nova versão documental a partir de resultado de IA;
* SEC-HUM-04 — actualização de decisões ou pendências com base em resultado de IA;
* SEC-HUM-05 — exportação de contexto potencialmente sensível;
* SEC-HUM-06 — futuras operações de agentes.

Verificação (F1): teste que prova que nenhuma alteração oficial ocorre sem a
acção de validação; evidência de auditoria da aprovação. Prioridade: Obrigatório.

## 10. Política de utilização de IA externa

Controlos mínimos (SEC-IA-01):

* selecção explícita do contexto pelo operador;
* minimização dos dados incluídos;
* proibição de envio automático (só manual no MVP);
* identificação do destino (ferramenta/modelo);
* aviso ao utilizador antes do envio;
* confirmação/classificação de sensibilidade;
* não envio de segredos;
* registo da origem e do modo de execução;
* responsabilidade do operador registada;
* resultados tratados como não confiáveis (sanitizados na importação);
* possibilidade de **bloquear documentos marcados como não-exportáveis**.

Mecanismo mínimo de sensibilidade no MVP **(resolvido — DEC-F0-FINAL-08, fecha
P-03):** o campo estruturado **`export_policy`** ao nível do documento, com
três valores — `allowed` (incluído directamente), `confirm` (exige confirmação
explícita do operador; valor inicial), `denied` (bloqueia a inclusão em
exportações e no pacote de contexto) — fonte oficial na base de dados,
verificável, sem antecipar um sistema avançado de classificação. Verificação
(F1): teste que impede o envio de documento com `export_policy = denied` e que
exige confirmação para `confirm`.

## 11. Retenção, eliminação e residência

Separação obrigatória entre requisito mínimo do produto e decisões dependentes
de mercado/ambiente (não inventar prazos nem jurisdições).

### 11-A. Backup e recuperação (RT-08)

* backup da base de dados; backup/versionamento do armazenamento documental;
* consistência entre metadados e ficheiros;
* recuperação de versões documentais;
* procedimento de restauro documentado;
* teste periódico de recuperação;
* protecção contra migrações destrutivas (duas fases; backup antes de migração crítica);
* rollback da aplicação disponível.
* Verificação (F1): teste de restauro; sem assumir ferramenta/fornecedor específico.

### 11-B. Retenção, eliminação e residência

Capacidades mínimas que o produto deve permitir:

* arquivamento em vez de eliminação física quando houver histórico;
* eliminação controlada e auditada;
* exportação antes da eliminação;
* retenção configurável (futura);
* registo de quem solicitou e executou;
* tratamento coerente de documentos e versões;
* preparação para requisitos futuros de residência.

Dependentes de mercado/ambiente (**A validar**, não decididos aqui): prazos
legais de retenção; jurisdição/residência dos dados; requisitos regulatórios
específicos.

## 12. Matriz de verificação para a Fase 1

| Domínio | Controlos | Forma de verificação predominante |
|---|---|---|
| Isolamento | SEC-ISO-01..03 | Testes de integração de isolamento |
| Autorização | SEC-AUT-01..03 | Testes de API + revisão de código |
| Protecção documental | SEC-DOC-01..04, SEC-INJ-01 | Testes de sanitização/XSS/traversal/injecção |
| Auditoria | SEC-AUD-01..02 | Inspecção de eventos + testes negativos |
| Segredos | SEC-SEC-01..03 | Inspecção de configuração + revisão de logs |
| Exportação | SEC-EXP-01..02 | Testes de autorização + auditoria |
| Autenticação/sessão | SEC-AUTH-01..02 | Testes de sessão/CSRF/rate limiting |
| IA externa | SEC-IA-01, SEC-HUM-05 | Demonstração + teste de bloqueio |
| Validação humana | SEC-HUM-01..06 | Testes de fluxo de aprovação |
| Armazenamento | SEC-STO-01 | Teste de consistência |
| Backup/recuperação | SEC-BAK-01 / 11-A | Teste de restauro |
| Retenção/eliminação | SEC-RET-01 / 11-B | Demonstração de arquivamento/exportação |

## 13. Pontos a validar

* P-01 — Confirmar o conjunto de controlos obrigatórios (§7) e a sua prioridade.
* P-02 — Confirmar a lista fechada de eventos auditáveis (§8).
* P-03 — ~~Confirmar o mecanismo mínimo de sensibilidade~~ — **Resolvido**: `export_policy` de três valores (DEC-F0-FINAL-08).
* P-04 — Confirmar cifragem at-rest como obrigatória ou dependente da infraestrutura (SEC-SEC-02). (Depende da plataforma de deploy — ver P-06.)
* P-05 — **A validar por mercado/ambiente:** prazos de retenção, residência de dados e requisitos legais (§11-B).
* P-06 — Plataforma de deploy: requisitos mínimos já vigentes (containers, PostgreSQL, armazenamento persistente, TLS, gestão segura de segredos, backups, health checks, migrações controladas, rollback, logs estruturados). **A selecção da plataforma concreta foi transferida para `MVP-20`** (DEC-F0-FINAL-02), a decidir antes da implementação e validação operacional desse item; deixa de bloquear o fecho da Fase 0.

## 14. Riscos residuais

* RR-01 — Ambiente greenfield: os controlos são requisitos, ainda não implementados; a eficácia só é comprovável na Fase 1.
* RR-02 — Plataforma de deploy concreta por seleccionar em `MVP-20` (DEC-F0-FINAL-02): TLS, cifragem at-rest e backup concretos ficam dependentes até essa selecção; requisitos mínimos já vigentes (P-06).
* RR-03 — Requisitos legais de retenção/residência por definir (P-05); mitigado por preparar capacidades sem fixar prazos.
* RR-04 — Robustez da separação instruções/dados varia entre modelos de IA (SEC-INJ-01); mitigada por declaração anti-injecção e revisão obrigatória.

## 15. Critérios de conclusão de F0-B12

* checklist cobre os seis domínios da baseline — §7.1 a §7.6. ✔
* cada controlo indica forma de verificação na Fase 1 — §7 e §12. ✔
* lista de eventos auditáveis fechada — §8. ✔
* política de envio a IA externa definida — §10. ✔
* validação humana de resultados de IA mantida como obrigatória — §9. ✔
* nenhum controlo não adiável foi adiado; requisitos legais não inventados — §11-B (A validar). ✔

## 16. Parecer final

Requisitos mínimos de segurança do MVP definidos e verificáveis, cobrindo os seis
domínios obrigatórios e as secções complementares, com a regra funcional de
validação humana de resultados de IA preservada como controlo obrigatório. As
dependências de mercado e de ambiente ficam explicitamente A validar, sem
invenção de requisitos legais nem de infraestrutura. F0-B12 pode considerar-se
cumprido ao nível de análise; a eficácia dos controlos é verificada na Fase 1.
