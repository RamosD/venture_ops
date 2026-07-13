# Decisões técnicas de arranque — VentureOps AI

* Fase: F1 — MVP
* Pipeline: F1-P02 — Fundação, autenticação e isolamento
* Prompt de origem: F1-P02-PR01
* Data: 2026-07-12
* Estado: vigente (decisões estruturais de arranque)
* Base: artefacto 09 (stack e padrões); arquitectura §1, §5, §7, §13; DEC-20260712-05 (CLR-01); DEC-20260712-06 (CustomUser/fundação em PR02/`/api/system/ping`).

Este documento fecha as decisões técnicas indispensáveis **antes da primeira
migração**. Valores concretos são fixados aqui e passam a vigorar para os prompts
seguintes de F1-P02. Não substitui a baseline nem os artefactos da Fase 0.

---

## 1. Estrutura dos módulos e dependências permitidas

Monólito modular Django com módulos de domínio sob `backend/apps/` e o projecto
em `backend/config/`. Módulos (arquitectura §5.1):

`accounts`, `organisations`, `portfolio`, `documents`, `decisions`,
`work_items`, `functions`, `executions`, `audit`, `storage`, `common`.

Regras de fronteira (MVP-01.R1 / CLR-01):

* um módulo depende apenas dos **serviços públicos** (interfaces explícitas) de
  outros módulos, nunca do seu estado interno, modelos ou tabelas directamente;
* as dependências são **explícitas e orientadas numa única direcção**, sem ciclos;
* `common` limita-se a **utilitários genuinamente partilhados** e a endpoints
  técnicos de sistema; não contém regra de negócio nem modelos de domínio;
* **proibido** criar `BaseRepository`, `BaseService`, command bus, event bus,
  sistema de plugins ou qualquer abstracção genérica para evitar as dependências
  normais do monólito modular.

Direcção de dependência prevista (a materializar quando os módulos ganharem
conteúdo): `organisations` é a base de isolamento; os módulos de domínio
(`portfolio`, `documents`, `decisions`, `work_items`, `functions`, `executions`)
dependem de `organisations` e de `accounts`; `audit` e `storage` são serviços
transversais consumidos via interface pública; `common` não depende de módulos
de domínio.

## 2. Modelo de utilizador — CustomUser

Adopta-se um **modelo de utilizador próprio (`CustomUser`)** baseado no sistema
de autenticação do Django (`AbstractBaseUser` + `PermissionsMixin`), **desde a
primeira migração**. Confirmada a decisão de DEC-20260712-06.

**Nesta etapa (PR01):** o módulo `accounts` é criado **vazio**; o modelo **não**
é criado; `AUTH_USER_MODEL` **não** é configurado (não pode apontar para um
modelo inexistente); **não** se executa `makemigrations` nem `migrate`.

**PR02** criará `CustomUser`, activará `AUTH_USER_MODEL = "accounts.CustomUser"`
e gerará a **primeira migração de forma atómica** (User + Organisation +
Membership numa migração inicial coerente).

## 3. Identificador de autenticação — email único

O identificador de autenticação do `CustomUser` é o **email**, **único** e
normalizado. Não há `username` separado. Sem palavra-passe em claro; hashing
robusto do Django. (Implementado em PR02/PR07.)

**Política de normalização (PR12):** o email é normalizado por uma função única
(`apps/accounts/normalization.py`) — **remoção de espaços exteriores + conversão
de todo o endereço para minúsculas** (parte local *e* domínio), tornando a
identidade **case-insensitive**. Aplica-se à criação, autenticação, recuperação e
edição de perfil. A unicidade case-insensitive é garantida também ao nível da BD
por uma constraint funcional `Lower(email)` (migração `accounts/0003`, com
verificação de colisões preexistentes sem fundir/apagar contas).

## 4. Ausência de registo público irrestrito

**Não** existe registo público aberto/auto-serviço no MVP. Nenhum endpoint
permite a criação livre de contas por terceiros. Qualquer criação de conta passa
pelo mecanismo controlado (secção 5).

## 5. Mecanismo controlado de criação da primeira conta

A primeira conta é criada por **comando de gestão de bootstrap** (Django
management command, por exemplo `createinitialuser`), executado por um operador
com acesso ao ambiente — não por endpoint público. O comando cria o utilizador
inicial (email único) de forma auditável. Alternativa equivalente aceite:
`createsuperuser` restrito ao operador. A decisão final de nomenclatura/detalhe
concretiza-se em PR07 (fluxos de autenticação), mantendo a ausência de registo
público. O onboarding da empresa (PR10) associa a empresa e a Membership Owner a
essa conta.

## 6. Convenção de identificadores das entidades de negócio

**Chave primária `UUID` (versão 4)** para todas as entidades de negócio
expostas ou referenciadas por API — `User`, `Organisation`, `Membership` e
entidades empresariais futuras (produtos, documentos, decisões, etc.).

Justificação (curta): identificadores **não sequenciais e não adivinháveis**
reduzem a enumeração e a fuga de informação por ID previsível; são estáveis e
seguros de expor em URLs/relações entre empresas; evitam a necessidade de alterar
o tipo de chave mais tarde. É uma convenção suportada nativamente pelo Django
(`UUIDField(primary_key=True, default=uuid.uuid4, editable=False)`), sem criar um
mecanismo genérico de identificação.

Excepção deliberada: tabelas técnicas internas de sequência estrita (por exemplo,
ordenação append-only da auditoria) podem usar uma chave inteira monotónica
adicional **a par** do UUID, se PR06 o justificar; a chave exposta permanece o
UUID. `DEFAULT_AUTO_FIELD` mantém-se `BigAutoField` apenas para tabelas internas
do Django/terceiros, não para entidades de negócio.

## 7. Versões suportadas (Python, Django, DRF, Node)

| Componente | Versão suportada | Validado nesta máquina |
|---|---|---|
| Python | 3.13.x | 3.13.2 |
| Django | 5.2.x (LTS) | 5.2.16 |
| Django REST Framework | 3.16.x | 3.16.1 |
| django-cors-headers | 4.9.x | 4.9.0 |
| Node.js | 22.x (LTS) | 22.14.0 |
| npm | 10.x | 10.9.2 |

Base de dados-alvo: PostgreSQL (introduzido em PR02). Versões fixadas em
`backend/requirements.txt`; actualização deliberada.

## 8. Gestores de dependências

* **Backend (Python):** `pip` + `venv` com `backend/requirements.txt` (versões
  fixadas). Sem Poetry/Pipenv nesta etapa (simplicidade; dentro da stack).
* **Frontend:** `npm` (Node 22 LTS), a inicializar em PR03 com `package.json`.

## 9. Comandos oficiais

Backend (a partir de `backend/`, com o ambiente virtual activo):

| Objectivo | Comando |
|---|---|
| Instalação | `python -m venv .venv` + activar + `pip install -r requirements.txt` |
| Arranque | `python manage.py runserver` |
| Verificação | `python manage.py check` |
| Testes | `python manage.py test` |
| Build | Sem passo de build dedicado do backend nesta etapa (imagem/artefacto em PR04/MVP-20) |

Frontend: definidos em PR03 (instalação `npm install`; arranque `npm run dev`;
testes/build `npm run test` / `npm run build`).

## 10. Prefixo da API e estratégia HTTP local

* **Endpoints de domínio versionados** sob `/api/v1/...` (arquitectura §9).
* **Endpoints técnicos de sistema** sob `/api/system/...` (não versionados);
  inclui `GET /api/system/ping`.
* **Estratégia local preferida:** **mesma origem** via **proxy de
  desenvolvimento** do frontend (Vite) a encaminhar `/api` para o backend,
  evitando CORS em desenvolvimento. Configurado em PR03.

## 11. Política restritiva de CORS

CORS **restritivo por defeito**: nenhuma origem cruzada é permitida enquanto a
allowlist estiver vazia. Implementado com `django-cors-headers`:
`CORS_ALLOW_ALL_ORIGINS = False` e `CORS_ALLOWED_ORIGINS` alimentado por
`DJANGO_CORS_ALLOWED_ORIGINS` (vazio por defeito). Nunca abrir CORS de forma
indiscriminada; a mesma origem/proxy (secção 10) é preferida ao CORS aberto.

## 12. Estratégia futura de CSRF para o frontend

Autenticação por **sessão com cookie** (PR07): cookie de sessão `HttpOnly`,
`SameSite=Lax` (ou `Strict`), `Secure` condicional a TLS. Para pedidos mutáveis,
o frontend obtém o **token CSRF** por cookie (`csrftoken`) e reenvia-o no
cabeçalho `X-CSRFToken`. Com a estratégia de mesma origem/proxy, o cookie de
sessão e o CSRF funcionam sem CORS. Middleware de sessão/CSRF é introduzido em
PR07 — não está activo nesta etapa (endpoints técnicos públicos apenas).

## 13. Email local de desenvolvimento

`EMAIL_BACKEND = django.core.mail.backends.console.EmailBackend` — os emails
(por exemplo, recuperação de acesso em PR09) são escritos na consola/logs, **sem
fornecedor externo**. A preparação de email real fica para o piloto/produção
(MVP-20), não é exigida em desenvolvimento.

## 14. Contrato mínimo previsto para o adaptador de armazenamento

O módulo `storage` exporá, quando implementado (PR04), um adaptador com contrato
mínimo e uma única interface para os chamadores:

* `save(key, content) -> chave/checksum`;
* `open(key) -> conteúdo`;
* `exists(key) -> bool`;
* `delete(key)`;
* `checksum(key)`.

Regras: **chaves geradas no servidor**; objectos **privados** (não acessíveis
publicamente); implementação **filesystem** em desenvolvimento com **ponto de
extensão para S3** sem alterar os chamadores. Nenhum código de armazenamento é
criado nesta etapa (contrato apenas previsto).

---

## Estado e âmbito

Decisões estruturais **1–4, 6–14** fechadas nesta etapa. A decisão 5 (mecanismo
de conta) fica com a nomenclatura final a concretizar em PR07, mantendo já a
ausência de registo público. A criação efectiva de `CustomUser`,
`AUTH_USER_MODEL` e da primeira migração pertence a **PR02**. Registo de
governação relacionado: DEC-20260712-06.
