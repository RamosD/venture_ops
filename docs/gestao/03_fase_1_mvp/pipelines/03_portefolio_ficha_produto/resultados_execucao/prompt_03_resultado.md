---
fase: F1
pipeline: F1-P03
prompt: F1-P03-PR03
modelo: claude-opus-4-8
inicio: 2026-07-13 14:00
fim: 2026-07-13 14:45
estado_execucao: Concluído
estado_revisao: Não revista
commit: não criado
---

# Resultado — Prompt 03 — Interface inicial do portefólio

## 1. Resumo

Implementada a **interface inicial do portefólio** (React/TS) sobre os contratos
da API de PR02, integrada com o cliente HTTP central, o `AuthContext` e o
`OrganisationGate` existentes. Depois do onboarding empresarial, o utilizador pode
**listar**, **criar** (escrevendo apenas Nome e Propósito), **consultar** a ficha e
**editar** a ficha básica; os defaults são aplicados pelo backend e apresentados na
ficha; conflitos de edição (**409**) são tratados sem sobrescrita silenciosa
(aviso + recarregar). Sem router novo, sem store global e sem outro cliente HTTP.
**8 testes de componente** novos + 12 anteriores = **20 testes frontend verdes**;
`npm run build` (tsc + vite) **OK**. **Validação ao vivo** no browser confirmou
criação com dois campos, defaults na ficha, edição com incremento de `version` e
`last_reviewed_at` **inalterada** (verificado ao nível do timestamp no backend).
Funcionalidades futuras (arquivar/reactivar, filtros, paginação, marcar como
revisto, agregados, atenção) **não** foram antecipadas. **F1-P03 fica 3/6.**

## 2. Componentes (todos em `src/components/portfolio/`)

| Componente | Papel |
|---|---|
| `PortfolioWorkspace` | Container: estado de vista (lista/criação/ficha/edição), carregamento/vazio/erro; monta-se após o onboarding (dentro do `OrganisationGate`). |
| `ProductList` | Tabela: nome (selecção), estado, responsável, última revisão e versão (discreta). Estado vazio explícito. |
| `ProductCreateForm` | Só Nome e Propósito exigidos; opcionais numa área recolhida (`<details>`); evita submissão duplicada. |
| `ProductDetail` | Ficha de visão geral (só leitura); acções Editar / Voltar. Sem agregados nem atenção. |
| `ProductEditForm` | Edita nome, propósito e opcionais; envia `expected_version`; trata 409 (aviso + recarregar). |
| `api/products.ts` | Contratos: `listProducts`, `getProduct`, `createProduct`, `updateProduct` (sobre o cliente central). |
| `format.ts` | Apresentação: data (AAAA-MM-DD), estado em PT, responsável (email do próprio utilizador quando corresponde). |

## 3. Integração

- **Cliente HTTP central** reutilizado (`api/client.ts`): sessão por cookie + CSRF;
  nenhum novo cliente, nenhuma store global, nenhum router dedicado.
- A área de portefólio é montada em `OrganisationGate` **apenas quando existe
  empresa** (depois do onboarding), preservando a experiência de perfil e empresa.
- Caminhos: `/v1/products` e `/v1/products/{id}` (base `/api` via proxy de dev).

## 4. Comportamento por requisito

- **Listagem:** nome, estado, responsável, última revisão; versão como controlo
  técnico discreto (`v.`); selecção por botão do nome; sem métricas nem atenção.
- **Criação:** exige visualmente só Nome e Propósito; opcionais recolhidos;
  submissão duplicada evitada (botão desactivado + guarda `busy`); após sucesso,
  a lista é actualizada e a ficha criada é aberta (mostra os defaults do servidor).
- **Edição:** edita nome/propósito/opcionais; envia a `version` actual; **409** →
  aviso "o produto foi alterado" + botão **Recarregar dados** (nunca sobrescreve o
  servidor); a edição comum não é apresentada como "revisão".

## 5. Testes (8 de componente; 20 no total do frontend)

`src/components/portfolio/portfolio.test.tsx`:

| # | Verificação obrigatória | Resultado |
|---|---|---|
| 1 | estado vazio do portefólio | OK |
| 2 | listagem de produtos | OK |
| 3 | criação com name e purpose | OK |
| 4 | defaults apresentados após a criação | OK |
| 5 | selecção e detalhe | OK |
| 6 | edição válida (nova versão reflectida) | OK |
| 7 | conflito 409 apresentado sem sobrescrita (+ recarregar) | OK |
| 8 | erro da API tratado (listagem falha + tentar novamente) | OK |
| 9 | submissão duplicada evitada | OK |
| 10 | autenticação/perfil/empresa continuam funcionais | OK (suites existentes, 12) |
| 11 | build e testes frontend passam | OK (`npm run build`, `vitest`) |

`organisation-gate.test.tsx` foi actualizado para envolver o `OrganisationGate` em
`AuthProvider` (a área de portefólio, agora montada quando há empresa, consome o
`AuthContext`) — mantém as mesmas asserções de empresa.

## 6. Validação ao vivo (browser, contentores reconstruídos)

`docker compose up -d --build frontend` (+ backend de PR02); conta `demo@x.pt`:
autenticar → onboarding ("Empresa Demo") → **criar** "Produto Demo" só com Nome +
Propósito → a ficha abre com os defaults (**Estado: Activo**, **Responsável:
demo@x.pt**, **Última revisão: 2026-07-13**, **Versão 1**, opcionais "—") →
**Editar** o propósito → **Versão 2**; **última revisão inalterada**. Confirmação
ao nível do timestamp no backend: `last_reviewed_at == created_at` (revisão
intacta) e `updated_at > created_at` (a edição ocorreu). Dados de demo removidos
no fim (base repõe users=2, products=0).

## 7. Ficheiros

### Criados
- `frontend/src/api/products.ts`
- `frontend/src/components/portfolio/PortfolioWorkspace.tsx`
- `frontend/src/components/portfolio/ProductList.tsx`
- `frontend/src/components/portfolio/ProductCreateForm.tsx`
- `frontend/src/components/portfolio/ProductEditForm.tsx`
- `frontend/src/components/portfolio/ProductDetail.tsx`
- `frontend/src/components/portfolio/format.ts`
- `frontend/src/components/portfolio/portfolio.test.tsx`
- `docs/gestao/03_fase_1_mvp/pipelines/03_portefolio_ficha_produto/resultados_execucao/prompt_03_resultado.md`

### Alterados
- `frontend/src/components/OrganisationGate.tsx` (monta `PortfolioWorkspace` quando há empresa)
- `frontend/src/components/organisation-gate.test.tsx` (envolve em `AuthProvider`)
- `docs/gestao/01_status_pipelines.md`, `00_painel_execucao_global.md`,
  `05_diario_execucao_ia.md`, `04_matriz_validacao_global.md` (VAL-003, evidência de UI)

## 8. Comandos e evidências

- `npm run test` → **20 testes OK** (12 anteriores + 8); portfolio estável em 3 rondas.
- `npm run build` → tsc `--noEmit` + `vite build` OK (49 módulos).
- Live: fluxo completo no browser (§6) + verificação de timestamp no backend.

## 9. Problemas encontrados

- Teste de edição instável na forma `expect(await findByText(...)).toBe...`
  (rejeição precoce intermitente); estabilizado separando o `await findByText`
  da asserção `getByText` (8/8 verdes em 3 rondas). Sem alteração de
  comportamento da aplicação.

## 10. Decisões

Sem decisão global. Locais: (a) portefólio montado dentro do `OrganisationGate`
(após onboarding) em vez de novo router — evita infra-estrutura desnecessária
(RT-09); (b) responsável apresentado como email do próprio utilizador quando
corresponde (MVP individual), sem inventar nomes de terceiros; (c) opcionais numa
área `<details>` recolhida para manter a criação a dois campos.

## 11. Pendências / reservas

- Arquivar/reactivar, filtros, paginação, campos opcionais completos na lista e
  botão "marcar como revisto" → **PR04/PR05**.
- Vistas agregadas (documentos/decisões/pendências/execuções) e nível de atenção →
  fora desta pipeline (F1-P04+); a ficha não simula dados nem contagens.

## 12. Estado da pipeline e próximo passo

- **F1-P03 Em execução (3/6).**
- Próximo: **F1-P03-PR04** — ciclo de vida (arquivo/reactivação), operação
  explícita "marcar como revisto", filtros e paginação no backend. Não iniciado.
