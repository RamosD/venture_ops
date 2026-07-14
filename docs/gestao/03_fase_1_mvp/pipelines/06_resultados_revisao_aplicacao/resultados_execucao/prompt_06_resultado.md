# F1-P06-PR06 — Validação de fecho e marco M1

- **Fase:** F1 — MVP · **Pipeline:** F1-P06 — Resultados, revisão e aplicação controlada
- **Prompt:** F1-P06-PR06 · **Itens:** MVP-13, MVP-14, MVP-15
- **Validações principais:** VAL-009, VAL-010 · **Reforçadas:** VAL-002/004/005/006/012/014
- **Marco:** **M1 — fluxo vertical ponta a ponta**
- **Estado:** Concluído / Não revista · **F1-P06:** **Concluída 6/6**

## Veredicto

**F1-P06 está Concluída (6/6).** O ciclo vertical completo — preparar execução →
gerar pacote → importar tentativa → rever → pedir correcção → importar nova tentativa
→ aprovar → aplicar alteração controlada → concluir — funciona, é imutável no
histórico, exige revisão humana e aprovação para qualquer aplicação, e produz **no
máximo uma** aplicação por execução. **VAL-009 e VAL-010 estão Validadas.** **M1 está
atingido.** Regressão completa verde; sem drift; migrações reversíveis; stack Docker
saudável. Corrigidos apenas 2 defeitos de expectativa de teste (não de produto) e
acrescentado um hasher rápido só-em-testes. Nenhuma IA foi chamada.

## Modelos e contratos finais

- **`ResultAttempt`** (append-only; `unique(execution, attempt_number)`), conteúdo só
  no armazenamento privado via `DocumentVersion` exacta; `AIExecution.current_result_attempt`.
- **`ResultReview`** (append-only; `unique(result_attempt)`; `decision` fechada
  {approved, rejected, correction_requested}; observações obrigatórias na rejeição/correcção).
- **`ResultApplication`** (append-only; `OneToOne(execution)` = uma por execução;
  `application_type` fechado {document, decision, work_item, no_change};
  `request_fingerprint` SHA-256; ligações PROTECT; constraints de coerência por tipo;
  sem GenericForeignKey nem FK circular — a ligação oficial é `created_document_version`).
- **Endpoints:** `POST .../result-attempts` (+GET lista/detalhe);
  `POST .../result-attempts/{n}/approve|reject|request-correction`, `GET .../reviews`;
  `POST .../apply/document|apply/decision|apply/work-item|close-without-application`,
  `GET .../application`.

## Política de tentativas

Múltiplas tentativas numeradas e **preservadas**; cada uma referencia a
`DocumentVersion` **exacta** (nunca `Document.current_version`); `current_result_attempt`
coerente; append-only; a correcção e a rejeição **não** eliminam histórico; a aprovação
identifica a tentativa exacta. (Verificado no E2E.)

## Política de revisões

**Uma revisão por tentativa** (defesa final de unicidade); a decisão vive num campo
fechado próprio (nunca campo genérico de estado); só Owner activo revê; `reviewer`
deriva da sessão; append-only. Tentativa histórica já revista não é re-revista.

## Aplicação e idempotência

Quatro caminhos, **um** por execução. `request_fingerprint` canónico → repetição
idêntica devolve a aplicação existente (200); diferente → 409. Unicidade por execução
é a defesa final; segundo caminho (mesmo de outro tipo, mesmo por outro endpoint) → 409.

## Estados e transições

`prepared → result_pending_validation` (importar); `result_pending_validation →
prepared` (correcção) / `→ approved` (aprovar) / `→ rejected` (rejeitar);
`approved → completed` (apply/close). `rejected` e `completed` terminais; restantes
transições inválidas (política central; testes de transições verdes).

## Provas importar ≠ aprovar ≠ aplicar

Por contagens/checksums antes e depois (E2E):
- **Após importar:** Product/documentos/decisões/pendências inalterados; sem
  `ResultApplication`; estado só `result_pending_validation`.
- **Após aprovar:** as mesmas entidades continuam inalteradas; sem aplicação; estado só
  `approved`.
- **Depois de aplicar:** exactamente o alvo escolhido muda; existe `ResultApplication`;
  execução `completed`; nenhum alvo não seleccionado muda.

## Aplicação a documento

Versão anterior preservada; nova versão ligada pela aplicação
(`base_document_version`/`created_document_version`); checksum correcto; versão obsoleta
(doc ou execução) → 409; falha de storage não deixa estado parcial (execução fica
`approved`, 503 + `storage.failure`); repetição idêntica idempotente.

## Aplicação a decisão

Usa `supersede_decision`: cadeia linear, anterior `superseded`, nova `active`, aplicação
liga ambas (`target_decision`/`created_decision`); nenhuma edição destrutiva. Alvo de
outro Product/superseded → 422; alheio → 404.

## Aplicação a pendência

Usa `complete_work_item`: `open → completed`, restantes campos preservados, transição
final válida, aplicação liga (`target_work_item`). Alvo final/de outro Product → 422;
alheio → 404.

## Fecho no_change

Rationale obrigatório; nenhuma entidade oficial alterada; a aplicação de fecho existe;
execução `completed`; auditado como fecho explícito.

## Isolamento

Duas empresas: tentativa/revisão alheias não são lidas nem executadas (404); aplicação
alheia e alvos de outra empresa rejeitados (404); tentativas cruzadas auditadas
(`security.cross_org_attempt`); listagens não revelam contagens externas.

## Autorização

Utilizador autenticado sem Owner não revê nem aplica (403); `reviewer`/`applied_by`
derivam da sessão (nunca do cliente); entrada estrita rejeita `reviewer`/`applied_by`/
`decision`/`application_type`/`status`/versão criada/internos.

## Concorrência

Suites dedicadas (TransactionTestCase, PostgreSQL real): duas importações → uma tentativa;
duas revisões → uma revisão; duas aplicações documentais idênticas → uma versão; dois
tipos de aplicação concorrentes → exactamente um vencedor. Sem duplicados; sem duas
`ResultApplication`; sem `completed` sem aplicação.

## Storage e segurança de conteúdo

Coordenação BD↔storage (objecto antes da BD; órfão limpo em falha; sem estado parcial).
Resultado **não confiável**: texto e preview não executam HTML/JS (componentes testados);
a aplicação documental usa **apenas** conteúdo explicitamente confirmado; nenhum parsing
automático; auditoria sem resultado/conteúdo. **VAL-014 permanece Parcial** até
consolidação F1-P07.

## Auditoria

Evento 13 (importação), 14–16 (revisão), 17 (aplicação, distingue os quatro tipos),
eventos de segurança e `storage.failure`; todos com `correlation_id`; nenhum contém
resultado, observações, conteúdo aplicado, snapshots, pacote, prompts nem segredos.
**VAL-012 permanece Parcial** até consulta consolidada F1-P07.

## Migrações

`makemigrations --check` **sem drift**; forward em base vazia (0001–0005) OK; aplicadas
na base existente do contentor (`[X]`); **reversibilidade estrutural** verificada em base
controlada — reverter `executions → 0001` remove `ResultAttempt`/`ResultReview`/
`ResultApplication` e `current_result_attempt`, preservando as migrações de outras apps;
forward de novo OK. (Reverter remove tentativas, revisões e aplicações; outras aplicações
preservadas.)

## Testes

- **Backend completo: 502 testes OK** (todas as apps). Executions: 178 (inclui E2E,
  paths, concorrência).
- **Frontend: 124 OK** + `tsc` + `vite build`.
- Novo `test_pipeline_e2e.py` (10 testes): cenário principal E1–E6, cenários A–E, provas
  negativas, isolamento, autorização.
- **Correcções (defeitos de teste, não de produto):**
  `test_approval_creates_no_application` verifica agora a ausência de **instância**
  `ResultApplication` (o modelo existe desde PR04); a prova negativa E2E conta as versões
  do documento **alvo** (não o total global). Estas duas expectativas estavam
  desactualizadas e provocavam um cascade de erros de isolamento no run completo, que
  desapareceu após a correcção.
- **Infra de testes:** hasher MD5 só quando `'test' in sys.argv` (settings) — sem impacto
  em produção; a suite passou de ~30 min para ~90 s.

## Demonstração

Stack Docker **reconstruída** (imagens backend+frontend) e **saudável**: `health/live`=200,
`health/ready`=200, ping=200; os quatro endpoints de aplicação e os de revisão roteados
(403 sem sessão); frontend serve o bundle «VentureOps AI»; migrações 0001–0005 aplicadas
na base do contentor. O fluxo vertical foi **demonstrado na imagem reconstruída** correndo
o E2E dentro do contentor `ventureops-backend-1` (10 testes, 4.8 s). **Reserva:** a
demonstração **visual** no browser não foi possível por indisponibilidade temporária da
ferramenta de browser (classificador offline no momento do fecho); o fluxo fica, ainda
assim, demonstrado pelos endpoints reais do stack ao vivo e pelos 124 testes de componente
que exercem as UIs de revisão (`ValidationPanel`) e aplicação (`ApplicationPanel`).

## VAL actualizadas

- **VAL-009 — Validada** (resultado associado à execução correcta, preservado, apresentado
  com segurança).
- **VAL-010 — Validada** (nenhuma aplicação sem revisão humana; todos os comandos exigem
  aprovação; uma aplicação por execução).
- **VAL-004/005/006 — Validadas**, com evidência de nova versão / substituição de decisão /
  conclusão de pendência aplicadas.
- **VAL-002/012/014 — Parciais** (consolidação transversal em F1-P07).
- **VAL-011 — inalterada** (pertence a F1-P07).

## Marco M1

**Atingido.** Fluxo vertical ponta a ponta demonstrado (E2E na imagem reconstruída + stack
ao vivo). Registado como atingido em 2026-07-14.

## Problemas corrigidos

- Dois defeitos de expectativa de teste (ver Testes) — sem alteração de código de produto.
- Ambiente: contentores parados por inactividade foram reiniciados; um run de regressão foi
  corrompido por terminação manual de sessões do test DB durante a execução (artefacto de
  operação, não defeito); resolvido correndo as suites de forma isolada.

## Reservas

- Demonstração visual no browser pendente (bloqueio temporário da ferramenta) — o fluxo
  está demonstrado pelos endpoints reais + componentes testados.
- VAL-002/012/014 permanecem Parciais até F1-P07; VAL-011 fora desta pipeline.

## Estado final e próximo passo

**F1-P06 Concluída (6/6); VAL-009 e VAL-010 Validadas; M1 atingido.** Próximo passo
recomendado: **efectuar commit de F1-P06** e gerar **F1-P07** just-in-time. **Não** iniciar
F1-P07 nesta iteração.
