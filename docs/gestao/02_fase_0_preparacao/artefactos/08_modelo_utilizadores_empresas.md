# Modelo de utilizadores e empresas do MVP — VentureOps AI

* Fase: F0 — Preparação e alinhamento
* Item tratado: F0-B10 (F0-10)
* Decisão bloqueadora: DB-10
* Estado do artefacto: Confirmado com reservas (DEC-20260712-04); acumulação de papéis fechada (DEC-F0-FINAL-05)
* Prompt de origem: F0-P05-PR02; acumulação de papéis fechada no fecho formal da Fase 0 (2026-07-12)

Âmbito: decisões formais sobre empresas por conta, individual vs multiutilizador
e papéis mínimos do MVP, ao nível funcional. Não se desenham tabelas, esquemas
nem modelos de permissões técnicos. Base: segmento e caso de uso (artefacto 01),
arquitectura §7.2 e roadmap §4.2.

---

## 1. Factos

* MU-01 — O segmento inicial proposto é o fundador técnico ou microequipa (1–5 pessoas) que gere **2 ou mais produtos** com uso recorrente de IA (artefacto 01, D-01).
* MU-02 — O caso de uso principal decorre sobre **produtos dentro de uma empresa**; a multiplicidade é de produtos, não necessariamente de empresas (artefacto 01, D-03).
* MU-03 — No MVP individual, operador e revisor/aprovador podem ser a mesma pessoa (artefacto 01, H-03).
* MU-04 — O roadmap prevê para o MVP "uma empresa activa" e admite que a estrutura de dados esteja preparada para várias empresas sem que a experiência do MVP explore essa capacidade (roadmap §4.2).
* MU-05 — A arquitectura propõe quatro papéis — Owner, Editor, Reviewer, Viewer — e indica que, num MVP individual, o utilizador inicial é Owner (arquitectura §7.2).
* MU-06 — Múltiplos utilizadores, convites e permissões avançadas estão fora do MVP (artefacto 02, §3.3; roadmap §4.3).

---

## 2. Decisões propostas

Estado geral: **Proposta / A validar**.

### D-08-01 — Empresas por conta no MVP

**Proposta:** **uma empresa activa por conta** na experiência do MVP, com o
modelo preparado para várias empresas no futuro (ver secção 3).

**Justificação:** a necessidade central do segmento é a visão consolidada de um
**portefólio de produtos dentro de uma empresa** (MU-01, MU-02); gerir várias
empresas por conta é uma capacidade opcional de fase posterior (roadmap, itens
opcionais). Manter uma empresa activa reduz a complexidade de navegação e
permissões no MVP (roadmap §4.2). **A validar.**

### D-08-02 — Individual vs multiutilizador no MVP

**Proposta:** **utilização individual** no MVP — uma conta de utilizador por
empresa, que exerce o papel de Owner —, com a estrutura preparada para
multiutilizador e memberships no futuro (secção 3).

**Justificação:** a tese do MVP valida-se com um único fundador a gerir o
portefólio e a completar o ciclo de execução assistida (MU-03); colaboração,
convites e permissões são explicitamente Versão 1 (MU-06). **Tensão registada:**
o segmento inclui microequipas de 2–5 pessoas; no MVP, uma equipa pode participar
no piloto através de uma conta única do fundador, com a colaboração real adiada
para a Versão 1 (ver P-02).

### D-08-03 — Papéis mínimos no MVP

**Proposta:** no MVP, **um único papel efectivo — Owner** —, que detém todas as
permissões necessárias ao fluxo. O conjunto **Owner, Editor, Reviewer, Viewer**
(arquitectura §7.2) é confirmado como **alvo para a Versão 1**, quando entrar o
multiutilizador, mas não é implementado como diferenciação de permissões no MVP.

**Justificação:** sendo o MVP individual (D-08-02), a diferenciação de papéis não
tem uso no fluxo; definir já o conceito dos quatro papéis prepara a Versão 1 sem
construir permissões nem interface de gestão de membros no MVP (MU-05, MU-06).
**Confirmado com reservas** (DEC-20260712-04).

### D-08-04 — Acumulação controlada de papéis no MVP individual (DEC-F0-FINAL-05)

**Decisão confirmada:** no MVP individual, o mesmo utilizador **pode exercer**
Owner, Operador e Revisor/Aprovador (resolve INC-01, artefacto 12 §7). As
**responsabilidades continuam funcionalmente separadas**, mesmo quando exercidas
pela mesma pessoa:

* **importar** um resultado de IA **não equivale a aprovar**;
* **aprovar não equivale automaticamente a aplicar**;
* a **aprovação** exige uma acção explícita;
* a **aplicação** exige uma operação explícita e auditável;
* actor, acção, data, entidade e resultado são sempre auditados (SEC-AUD-01/02, artefacto 10), independentemente de as três funções recaírem na mesma pessoa;
* a arquitectura e o modelo de dados devem permitir **separar estes papéis no futuro** (Versão 1), sem redesenho estrutural.

**Estado:** Confirmada (DEC-F0-FINAL-05, 2026-07-12).

---

## 3. Preparação para evolução (sem expor no MVP)

Descrição funcional, sem esquema técnico.

* Toda a entidade pertence a **uma empresa**, que é a **unidade de isolamento**; a empresa é o contexto obrigatório de produtos, documentos, decisões, pendências, funções, execuções e auditoria.
* Existe, ao nível conceptual, uma **associação utilizador–empresa–papel** (membership); no MVP essa associação é **única** (o fundador como Owner de uma empresa).
* A experiência do MVP **não expõe**: selector de empresa, criação de várias empresas, convites, gestão de membros nem escolha de papéis.
* A evolução para multiempresa e multiutilizador consiste em permitir mais do que uma associação e em activar a diferenciação de papéis, sem alterar o princípio de isolamento por empresa já presente no MVP.

Esta preparação segue o roadmap §4.2 ("estrutura preparada para várias empresas,
experiência do MVP não necessita de explorar essa capacidade") sem inflacionar o
MVP.

---

## 4. Impacto em isolamento e segurança (para F0-B12)

Entradas para o checklist de segurança (F0-B12):

* IS-01 — **Isolamento por empresa obrigatório desde o MVP**, mesmo com uma única empresa: cada entidade traz o contexto de empresa e toda a autorização deriva da empresa autorizada. Evita retrofitting e o risco de fuga entre empresas quando o multiempresa/multiutilizador chegar.
* IS-02 — **Autorização no backend**: a pertença à empresa é sempre validada no servidor; nunca se confia num identificador de empresa enviado pelo cliente (arquitectura §7.3, a detalhar em F0-B12).
* IS-03 — **Papel Owner como detentor de operações críticas** no MVP: exportação, arquivamento e aprovação de resultados exigem Owner; a base para restringir estas operações por papel fica preparada para a Versão 1.
* IS-04 — **Preparação para revogação e memberships**: o modelo conceptual de membership antecipa a futura revogação de acesso, sem a implementar no MVP.

Estes pontos devem ser consumidos por F0-B12 (isolamento, autorização,
auditoria) e não são aqui transformados em checklist.

---

## 5. Hipóteses assumidas

* UH-01 — Assumiu-se que o segmento gere vários produtos dentro de uma empresa, e não várias empresas, no MVP (MU-02); a necessidade de multiempresa é de fase posterior.
* UH-02 — Assumiu-se que uma microequipa pode participar no piloto através de uma conta única, adiando a colaboração real para a Versão 1 (a validar, P-02).
* UH-03 — Assumiu-se que definir o conceito dos quatro papéis não implica construí-los no MVP (apenas Owner é exercido).

## 6. Pontos a validar por humano

* P-01 — ~~Confirmar "uma empresa activa por conta"~~ — **Resolvido**: confirmado com reservas na saída da Fase 0 (DEC-20260712-04).
* P-02 — ~~Confirmar a utilização individual~~ — **Resolvido**: confirmado; o participante mínimo do piloto (Aldino Ramos) é individual (DEC-F0-FINAL-03).
* P-03 — ~~Confirmar papel único Owner no MVP~~ — **Resolvido**: confirmado, com acumulação controlada de Owner/Operador/Revisor (D-08-04, DEC-F0-FINAL-05).
* P-04 — Confirmar que a preparação para evolução (secção 3) não exige qualquer elemento visível de multiempresa/multiutilizador no MVP. (Mantém-se como recomendação a observar na decomposição da Fase 1.)

## 7. Critérios de verificação deste artefacto

* As três decisões estão propostas com justificação — secção 2 (D-08-01 a D-08-03). ✔
* A coerência com o segmento aprovado está explícita — secção 2 (referências a MU-01/MU-02/MU-03) e secção 5. ✔
* A preparação para evolução está descrita sem inflacionar o MVP — secção 3 (sem selector, convites ou permissões no MVP). ✔
* O impacto em isolamento está identificado para F0-B12 — secção 4 (IS-01 a IS-04). ✔
