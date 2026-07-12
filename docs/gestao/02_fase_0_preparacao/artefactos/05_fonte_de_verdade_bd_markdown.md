# Fronteira entre base de dados e Markdown — VentureOps AI

* Fase: F0 — Preparação e alinhamento
* Item tratado: F0-B06 (F0-06)
* Decisão bloqueadora: DB-06
* Estado do artefacto: Confirmado com reservas (DEC-20260712-04); marcadores documentais fechados (DEC-F0-FINAL-08)
* Prompt de origem: F0-P04-PR01; marcadores documentais acrescentados no fecho formal da Fase 0 (2026-07-12)

Âmbito: para cada tipo de informação do modelo funcional, a **fonte oficial**
(base de dados ou Markdown), a **política de versões documentais** e as **regras
de actualização**. Ao nível funcional: não se desenha esquema de base de dados,
chaves nem estrutura de pastas, e não se decide a tecnologia de armazenamento
(F0-B11). Base: modelo funcional em
`docs/gestao/02_fase_0_preparacao/artefactos/02_fluxo_e_modelo_funcional.md` §6.

---

## 1. Factos

* FV-01 — Princípio de uma fonte oficial por tipo de informação: a base de dados controla estado, relações e permissões; o Markdown controla o conteúdo documental; a mesma informação não deve ser editável de forma independente nos dois locais (arquitectura §2.3; visão §12, princípios 5–7).
* FV-02 — A base de dados guarda entidades, relações, estados, permissões, metadados, histórico funcional e as **referências** às versões dos ficheiros; o conteúdo Markdown é guardado como ficheiro em armazenamento próprio (arquitectura §6.1).
* FV-03 — A separação PostgreSQL/ficheiros dá portabilidade e versões independentes, mas exige que o backend garanta a consistência entre metadados e objectos (arquitectura §15.2).
* FV-04 — Requisito transversal RT-04 (backlog macro): a base de dados e o Markdown não podem manter valores operacionais concorrentes.
* FV-05 — O modelo funcional (artefacto 02, §6) define oito entidades núcleo e trata a versão de documento como imutável e o pacote de contexto como associação execução–versões.

---

## 2. Matriz de fonte de verdade (decisão proposta)

Estado geral: **Proposta / A validar**. Cada tipo de informação tem **exactamente
uma** fonte oficial. "BD" = base de dados relacional (dados estruturados);
"Markdown" = ficheiro de conteúdo documental versionado.

| Tipo de informação | Fonte oficial | Notas |
|---|---|---|
| Identidade e relações de todas as entidades | BD | Ids e associações; nunca no Markdown |
| Estados das entidades (produto, documento, decisão, pendência, função, execução) | BD | Conforme F0-B05 |
| Permissões, memberships, papéis | BD | Detalhe em F0-B10 |
| Eventos de auditoria | BD | Append-only |
| Empresa — dados estruturados (nome, estado, configuração) | BD | — |
| Empresa — contexto narrativo (se existir) | Markdown | Documento de contexto da empresa |
| Produto — ficha administrativa mínima (nome, propósito curto, estado, responsável, datas de revisão) | BD | Campos de F0-B07 |
| Produto — descrição/contexto alargado | Markdown | Documento associado ao produto |
| Documento — metadados (título, tipo, estado, versão actual, autor, datas) | BD | Título é metadado de identificação (ver §3) |
| Documento — `is_outdated` (boolean) | BD | Fecha INC-03/DEC-F0-FINAL-08; valor inicial `false`; alimenta R-AT-05 (artefacto 06); sem valor concorrente no Markdown |
| Documento — `export_policy` (`allowed`\|`confirm`\|`denied`) | BD | Fecha INC-03/DEC-F0-FINAL-08; valor inicial `confirm`; `denied` bloqueia exportação/pacote de contexto; aplicado pelo backend |
| Documento — conteúdo (corpo) | Markdown | Ficheiro |
| Versão de documento — metadados (número, autor, data, resumo da alteração, referência de integridade) | BD | — |
| Versão de documento — conteúdo | Markdown | Ficheiro imutável |
| Decisão — campos (título, estado, responsável, data, produto) | BD | — |
| Decisão — detalhe extenso (opcional) | Markdown | Documento de detalhe da decisão |
| Pendência — campos (título, tipo, estado, prioridade, prazo, responsável) | BD | — |
| Pendência — notas extensas (opcional) | Markdown | Opcional |
| Função organizacional — campos (nome, tipo, propósito, limites resumidos, necessidade de aprovação, estado) | BD | — |
| Função organizacional — instruções detalhadas | Markdown | Documento de instruções |
| Execução — estrutura (produto, função, estado, validação, datas, objectivo curto) | BD | Inclui referências às versões usadas |
| Execução — resultado (conteúdo) | Markdown | Documento de resultado |
| Resultado — estado de validação e origem | BD | Conteúdo é Markdown (linha acima) |
| Pacote de contexto | BD (associação) + Markdown (derivado) | Associação execução↔versões e objectivo/instruções na BD; o pacote exportado é **gerado** a partir do conteúdo das versões, não é fonte |
| Visão de atenção | Derivada (sem fonte própria) | Calculada a partir da BD; não persistida (artefacto 02, §6.5) |

Nenhum tipo de informação do modelo funcional fica sem classificação.

---

## 3. Metadados duplicados e regras anti-concorrência (decisão proposta)

Estado: **Proposta / A validar**. Garantem RT-04 (FV-04).

* R-01 — Um **valor operacional** (estado, prazo, responsável, associação, permissão) tem uma única fonte: a **BD**. O Markdown não define estados nem relações operacionais.
* R-02 — O **conteúdo documental** (corpo narrativo) tem uma única fonte: o **ficheiro Markdown versionado**. A BD não guarda o corpo do documento como valor editável, apenas metadados e a referência à versão actual.
* R-03 — Quando um metadado precisa de aparecer dentro de um documento (por exemplo, título ou nome do produto no cabeçalho), essa ocorrência é uma **cópia de identificação não autoritativa**; a fonte oficial permanece a BD. Editar o cabeçalho no Markdown não altera o metadado na BD, e vice-versa.
* R-04 — Nenhum campo é editável de forma independente nos dois locais (arquitectura §2.3). Qualquer projecção de metadados para dentro do conteúdo, se existir, é unidireccional (BD → apresentação) e não reversível pela edição do conteúdo.

---

## 4. Política de versões documentais (decisão proposta)

Estado: **Proposta / A validar**.

* V-01 — **Quando se cria versão:** cada alteração **submetida/guardada** do conteúdo de um documento cria uma nova versão. Não se cria versão por cada tecla nem por rascunho não submetido. (A granularidade exacta — cada gravação vs apenas alterações submetidas — liga-se a uma questão em aberto da arquitectura; ver P-02.)
* V-02 — **Imutabilidade:** cada versão é imutável; nunca se edita uma versão existente. Uma alteração produz sempre uma nova versão. A versão actual do documento é indicada por referência na BD.
* V-03 — **Recuperação:** qualquer versão anterior pode ser consultada e recuperada. Propõe-se que recuperar signifique **criar uma nova versão a partir do conteúdo de uma anterior**, preservando o histórico completo, em vez de apagar versões intermédias (alternativa — repontar a versão actual — em P-03).
* V-04 — **Metadados de versão** (número sequencial, autor, data, resumo da alteração, referência de integridade) residem na BD; o conteúdo de cada versão reside no ficheiro.

---

## 5. Regras de actualização (decisão proposta)

Estado: **Proposta / A validar**.

* U-01 — **Acesso mediado pelo backend:** toda a leitura e escrita de conteúdo documental passa pelo backend; a IA não acede directamente ao armazenamento nem à base de dados (arquitectura §2.6, §5.3).
* U-02 — **Quem actualiza:** o Operador (Editor/Owner) actualiza conteúdo e metadados. Alterações decorrentes de uma execução aprovada são aplicadas de forma **controlada** (passo E6 do fluxo) e geram uma nova versão; um resultado de IA aprovado **não** altera automaticamente o documento (artefacto 02, §2.2 e §6.5).
* U-03 — **Conflito de concorrência:** uma edição feita sobre uma versão desactualizada é detectada por comparação com a versão base; em caso de conflito, a alteração é **rejeitada** e é pedida a reaplicação sobre a versão actual, sem sobrescrita silenciosa (arquitectura §4.6, §10.4).
* U-04 — **Metadados estruturados:** actualizados na BD através do backend; as mudanças de estado seguem as transições definidas em F0-B05.
* U-05 — **Consistência BD↔ficheiro:** a criação de uma versão (referência e metadados na BD) e a escrita do respectivo ficheiro devem ser tratadas como uma operação coordenada pelo backend; a resolução técnica desta coordenação pertence à implementação (Fase 1), não a esta fase.

---

## 6. Hipóteses assumidas

* CH-01 — Assumiu-se que o "propósito" curto da ficha do produto é um campo estruturado (BD) e que descrições extensas residem em documentos Markdown (coerente com F0-B07, §4).
* CH-02 — Assumiu-se que o objectivo/instrução específico de uma execução é um campo curto na BD, e que instruções detalhadas de uma função residem num documento Markdown.
* CH-03 — Assumiu-se a recuperação de versão como criação de nova versão a partir de uma anterior (V-03), preservando histórico.
* CH-04 — Assumiu-se que a visão de atenção não tem fonte própria (derivada da BD), coerente com o modelo funcional.

## 7. Pontos a validar por humano

* P-01 — Confirmar a matriz de fonte de verdade (secção 2), em especial os tipos com componente estruturada e documental (produto, decisão, função, execução).
* P-02 — Confirmar a granularidade de versionamento (V-01): versão a cada gravação vs apenas a cada alteração submetida (questão em aberto da arquitectura §17, ponto 10).
* P-03 — Confirmar a semântica de recuperação (V-03): nova versão a partir de anterior vs repontar a versão actual.
* P-04 — Mecanismo de armazenamento do Markdown no piloto (filesystem vs object storage): requisitos mínimos já definidos (artefacto 09, §3.2); **a selecção da plataforma concreta foi transferida para `MVP-20`** (DEC-F0-FINAL-02), a decidir antes da implementação e validação operacional desse item, não bloqueante para a decomposição do MVP.
* P-05 — Confirmar que pendências e empresa podem ter conteúdo documental opcional em Markdown, ou se ficam apenas estruturadas no MVP.

## 8. Critérios de verificação deste artefacto

* Cada tipo de informação tem exactamente uma fonte oficial — secção 2 (matriz completa; nenhum tipo sem classificação). ✔
* A política de versões define quando se cria versão e garante recuperabilidade — secção 4 (V-01 a V-04). ✔
* As regras impedem valores operacionais concorrentes (RT-04) — secção 3 (R-01 a R-04). ✔
* As dependências do levantamento técnico estão como ponto a validar, não como decisão — P-04 (armazenamento, F0-B11). ✔
