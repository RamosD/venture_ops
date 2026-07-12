# Stack, repositório e padrões — VentureOps AI

* Fase: F0 — Preparação e alinhamento
* Item tratado: F0-B11 (F0-11)
* Decisão bloqueadora: DB-11
* Estado do artefacto: Confirmado com reservas (DEC-20260712-04); plataforma concreta de deploy transferida para MVP-20 (DEC-F0-FINAL-02)
* Prompt de origem: F0-P05-PR01; deploy transferido no fecho formal da Fase 0 (2026-07-12)

Âmbito: levantamento do estado **real** do repositório e confronto com as
decisões assumidas na arquitectura (§1), fechando stack, repositório,
autenticação, armazenamento e deploy. Não se cria estrutura de código,
configuração ou CI/CD, nem se inicializam frameworks. Base:
`docs/gestao/01_baseline/03_arquitetura.md` §1, §2.10, §7.1 e §13.

---

## 1. Factos (levantamento real, com evidência)

Evidência: `ls -la`, `find . -type f` e procura de marcadores de stack na raiz
do repositório (2026-07-11).

* SR-01 — O repositório contém apenas dois directórios de topo: `.git/` e `docs/`. Não existe código de aplicação.
* SR-02 — Todo o conteúdo versionado é **documentação** em Markdown, sob `docs/gestao/` e `docs/produto/`.
* SR-03 — O repositório está inicializado com git (`.git/` presente). O remoto não foi verificado neste levantamento (P-05).
* SR-04 — **Nenhum** marcador de stack, código ou CI/CD foi encontrado: ausentes `package.json`, `pyproject.toml`, `requirements.txt`, `manage.py`, `Dockerfile`, `docker-compose.yml`, `.github/`, `.gitlab-ci.yml`, `Makefile`, `tsconfig.json`, `pom.xml`, `go.mod`, `Cargo.toml`.
* SR-05 — Conclusão factual: o ambiente é **greenfield** para efeitos de implementação — não existe stack, autenticação, armazenamento nem pipeline de deploy pré-existentes a reutilizar. A documentação já usa Markdown, mas não há implementação.

Nota: não se declara qualquer stack ou infraestrutura como existente, por não
existir (cumpre "nenhum facto declara stack que não exista").

---

## 2. Confronto com as decisões assumidas na arquitectura (§1)

Como não existe código, nenhuma decisão pode ser **confirmada empiricamente**
contra uma stack existente; também não há stack que as **contrarie** (sem
desvios). Classificam-se, portanto, como decisões a **adoptar de raiz**, a
confirmar pela equipa. Estado geral: **Proposta / A validar**.

| Decisão assumida (arquitectura §1) | Estado no repositório | Classificação |
|---|---|---|
| Frontend React + TypeScript | Inexistente | Adoptar de raiz — A validar |
| Backend Django + DRF | Inexistente | Adoptar de raiz — A validar |
| PostgreSQL (dados estruturados) | Inexistente | Adoptar de raiz — A validar |
| Markdown em ficheiros (fora da BD) | Inexistente como implementação | Adoptar de raiz — A validar (coerente com a fronteira de F0-B06) |
| Object storage em produção | Inexistente | Adoptar de raiz — A validar (ver §3.2) |
| Sem Redis/Celery/Kafka/Kubernetes por defeito | Nada existe | Confirmado por ausência (nada a remover) |

Não há reutilização possível de stack existente (arquitectura §2.10 não se
aplica: o repositório não usa ainda React, Django, DRF, PostgreSQL, Docker ou
CI/CD).

---

## 3. Decisões propostas

Estado geral: **Proposta / A validar**. Nenhum artefacto de código é criado.

### 3.1. Autenticação

Proposta: como **não existe autenticação a reutilizar** (SR-05), adoptar
**Django Auth** com sessão segura por cookie, conforme a arquitectura §7.1 para o
caso "não existe autenticação". SSO/OIDC ficam para fase posterior.
Justificação: é a via recomendada pela arquitectura na ausência de autenticação
prévia; alinha frontend e backend no mesmo domínio; a futura API para agentes
usará tokens separados, não a sessão web.

### 3.2. Armazenamento documental no piloto

Proposta: **filesystem local** em desenvolvimento/piloto simples e
**armazenamento compatível com S3** quando existir ambiente partilhado, conforme
a arquitectura §13.1 e §15.3. Justificação: o filesystem reduz dependências no
piloto local; o object storage garante escalabilidade, backups e objectos
privados quando houver ambiente partilhado. A escolha exacta liga-se à fronteira
BD/Markdown (F0-B06, ponto P-04 desse artefacto) e à plataforma de deploy (§3.3).

### 3.3. Plataforma de deploy

Não identificável a partir do repositório (SR-04: sem CI/CD nem configuração de
deploy). **Requisitos mínimos vigentes** (arquitectura §13.5; artefacto 10,
§11-A): execução em containers; PostgreSQL; armazenamento persistente; TLS;
gestão segura de segredos; backups; health checks; migrações controladas;
rollback; logs estruturados. Alvo de referência: uma instância backend ou poucas
réplicas, frontend estático, PostgreSQL gerido ou dedicado, armazenamento S3
compatível, reverse proxy; Kubernetes só se já existir plataforma operacional
(não há evidência de que exista).

**Decisão (DEC-F0-FINAL-02):** a selecção da **plataforma concreta** é
**transferida para `MVP-20 — Operação mínima do MVP`**, a decidir antes da
implementação e validação operacional desse item. A ausência de escolha da
plataforma concreta **deixa de impedir** o fecho da Fase 0.

### 3.4. Convenções e padrões a adoptar (propostas, não criados)

* Estrutura de repositório: monólito modular com um directório de backend
  (módulos de domínio) e um de frontend, mantendo `docs/` como está.
  Proposta a criar apenas na Fase 1.
* Estratégia de testes: unitários, integração, isolamento por empresa,
  permissões, versões documentais, transições de execução, API e segurança
  básica (arquitectura §13.3). A adoptar na Fase 1.
* CI/CD: pipeline mínimo (build, testes, backup quando aplicável, migrações
  compatíveis, deploy, health check) — arquitectura §13.7. A criar na Fase 1.

Estas convenções são registadas como propostas; não são criadas nesta fase
(sem `frontend/`, `backend/`, `infra/`, código ou CI/CD).

---

## 4. Hipóteses assumidas

* TH-01 — Assumiu-se que a stack assumida na arquitectura (§1) é a stack pretendida para o desenvolvimento greenfield, na ausência de decisão contrária (a confirmar, P-02).
* TH-02 — Assumiu-se que a documentação em Markdown já existente não constitui, por si, uma implementação da fronteira BD/Markdown (é apenas conteúdo documental de gestão).
* TH-03 — Assumiu-se que a ausência de marcadores na raiz reflecte a ausência real de código, e não código fora do repositório (a confirmar, P-03).

## 5. Pontos a validar por humano

* P-01 — ~~Indicar a plataforma de deploy disponível~~ — **Transferido**: selecção concreta remetida para `MVP-20` (DEC-F0-FINAL-02); requisitos mínimos vigentes (§3.3).
* P-02 — Confirmar a adopção da stack da arquitectura (React/TS, Django/DRF, PostgreSQL, object storage) para o desenvolvimento greenfield.
* P-03 — Confirmar que não existe código relevante fora deste repositório a considerar.
* P-04 — Confirmar a decisão de autenticação (Django Auth com sessão por cookie).
* P-05 — Confirmar o remoto do repositório e a política de branches (não verificados neste levantamento).
* P-06 — Confirmar o armazenamento do piloto (filesystem vs S3 compatível), em articulação com F0-B06.

## 6. Critérios de verificação deste artefacto

* Cada decisão assumida da arquitectura está confirmada, com desvio justificado ou marcada A validar — secção 2 (todas classificadas; sem stack existente). ✔
* A decisão de autenticação está proposta com justificação — secção 3.1. ✔
* A decisão de armazenamento do piloto está proposta — secção 3.2. ✔
* A plataforma de deploy está identificada ou registada como A validar — requisitos mínimos vigentes; selecção concreta transferida para MVP-20 (secção 3.3, DEC-F0-FINAL-02). ✔
* Nenhum facto declara stack ou infraestrutura que não exista — secção 1 (levantamento com evidência; ambiente greenfield). ✔
