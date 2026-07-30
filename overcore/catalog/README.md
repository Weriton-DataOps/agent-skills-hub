# Overcore — Catálogo canônico

Fonte de verdade das entradas operacionais do Overcore (agentes, subagentes,
papéis, gates, componentes de motor) que **Pipeline Studio** e **Oracle**
resolvem em runtime. O Agent-SDK **não** guarda cópia alternativa dessas
definições nem do schema — consome este catálogo via snapshot versionado no
cache do Electron; nunca lê o working tree do hub em produção.

## Layout

```
overcore/catalog/
├── catalog.schema.json        # JSON Schema Draft 2020-12 (envelope + $defs.entry)
├── catalog.json               # catálogo canônico (envelope + agents[] inline)
├── skill-dependencies.json    # DERIVADO (auto-gerado) — dependências obrigatórias + hashes das fontes
├── gen_skill_dependencies.py  # gera o derivado a partir do frontmatter dos SKILL.md
├── validate_catalog.py        # validador: schema + semântica + resolução + deps-sync + segredos
├── test_dep_sync.py           # prova que projeção desatualizada é rejeitada
├── fixtures/{positive,negative}
└── README.md
```

## Versões

- **schemaVersion** (`0.3.0`): 0.1.0 (promovido da Fase 1) → 0.2.0 (+`telemetry.executionRecord`)
  → **0.3.0** (+`skills.onDemand`). **Sem compatibilidade fictícia** — consumidores exigem 0.3.0.
- **catalogVersion** (`0.3.0`): versão do conteúdo. **version** (por entrada): SemVer da definição.

`agents[]` em ordem kebab ascendente por `id` é o índice determinístico.

## Entradas atuais (PRB-017A)

| id | kind | modelo | skills obrigatórias | opcionais | rota onDemand | delega |
|---|---|---|---|---|---|---|
| `oracle-coordinator` | agent | sonnet→opus | requirements-discovery, architecture, blueprint, agent-orchestrator | verification-before-completion, create-issue-gate | **brainstorming** | oracle-planner, oracle-validator |
| `oracle-planner` | subagent | sonnet | blueprint, create-issue-gate | architecture | — | — |
| `oracle-validator` | subagent | sonnet→opus | verification-before-completion, closed-loop-delivery | advanced-evaluation, create-issue-gate | — | — |

Cobertura: **descoberta de requisito** → `requirements-discovery` (skill canônica do Overcore,
estritamente conversacional, `risk: safe`) + `architecture`; **planejamento** → `blueprint`;
**orquestração** → `agent-orchestrator`; **verificação** → `verification-before-completion`;
**critérios de aceite** → `create-issue-gate` + `closed-loop-delivery`.

### `brainstorming` como rota SOB DEMANDA (não permanente)

`requirements-discovery` é a etapa ANTERIOR, não substituta global de `brainstorming`. Esta última
**permanece** como capacidade — mas fora da lista obrigatória: é uma rota `skills.onDemand` (não conta
no limite de 6; não é sempre carregada). Contrato:

- **Ativação** `explicit-or-confirmed`: pedido explícito inicia a sessão; trigger automático PEDE
  CONFIRMAÇÃO (`autoTriggerRequiresConfirmation: true`).
- **Triggers:** pedido explícito · trabalho criativo · nova funcionalidade/arquitetura/fluxo/UI ·
  duas ou mais soluções plausíveis · `requirements-discovery` concluído com espaço de solução aberto.
- **Não autoriza** implementação, escrita de arquivo ou commit (`authorizes: []`,
  `forbids ⊇ {implementacao, escrita-de-arquivo, commit}`).
- **Handoff:** após o design aprovado, segue para `blueprint`.

**Garantias OBRIGATÓRIAS (ausência é inválida — não se apoia em `default`).** Schema (`if/then`),
validador semântico e resolvedor falham FECHADO se, numa rota `explicit-or-confirmed`/
`auto-requires-confirmation`, faltar/violar: `autoTriggerRequiresConfirmation === true`; `triggers`
com ≥1 item, sem vazios e sem duplicatas; `authorizes` presente e **vazio**; `forbids` contendo os
três; `handoffTo` presente e **resolvível** no snapshot; skill com `SKILL.md`+metadados+runtime; risco
compatível com as ferramentas. Máximo **1 rota por entrada** (exclusividade).

**Política de carga — nunca 7 skills ativas.** `required+optional` não conta a rota, mas ATIVAR não
pode exceder `maxTotal`. Contrato declarativo: `loadPolicy: "replace"` + `replaces: [...]`. Conjunto
efetivo = `(required + optional − replaces) + skill onDemand`. Regras (validador **e** resolvedor):
`replaces` aponta para skill da própria entrada, sem duplicatas; base com 6 skills exige `replace`
com substituição; efetivo ≤ `maxTotal`. A rota canônica usa `replaces: ["verification-before-completion"]`
⇒ efetivo = **6**. O resolvedor devolve `loadPolicy`, `replaces`, `effectiveSkills` e `effectiveLimit`
para o runtime futuro aplicar a política.

### Risco `unknown` tratado (não escondido)

`verification-before-completion` e `brainstorming` são `risk: unknown` no índice. Regra dura
(validador + resolvedor): skill de risco não-`safe` só pode ser usada por entrada **sem nenhuma
ferramenta mutável** em `tools.allowed` — logo não escreve/commita/implementa silenciosamente. As
entradas do Oracle são não-mutáveis; passam. `requirements-discovery` é `safe`.

### Dependências obrigatórias — fonte ÚNICA

Origem de verdade: campo **`requiredSubSkills` no frontmatter** de `skills/<id>/SKILL.md` (ex.:
`acceptance-orchestrator` → `create-issue-gate` + `closed-loop-delivery` +
`verification-before-completion`), propagado ao `skills_index.json`. `skill-dependencies.json` é o
arquivo **DERIVADO auto-gerado** (`gen_skill_dependencies.py`) que carrega o **SHA-256 de cada fonte**.
O validador (`check_dep_sync`) confere igualdade origem↔índice↔projeção e o hash; **divergência falha
fechado** (`test_dep_sync.py` prova que alterar a origem rejeita a projeção desatualizada). Regenerar:
`python gen_skill_dependencies.py`; verificar sem escrever: `--check`. Sem herança implícita: cada
entrada resolve suas próprias dependências, dentro do limite de 6.

### Telemetria de execução (`telemetry.executionRecord`)

Cada entrada declara o registro obrigatório de uma execução futura: `agentId`, `subagentId`,
`skillsResolved`, `overcoreVersion`, `overcoreCommit`, `catalogVersion`, `workflowId`, `runId`,
`parentRunId`, `taskId`, `terminalStatus` (+ `tokens`/`costUsd`/`durationMs` opcionais). Nada é
executado nesta rodada.

## Política de níveis e despacho

nível 1 conversa/leitura · 2 tarefa/validação · 3 despacho. Nível 3 exige aprovação humana antes de
`agent:run`, nos campos: `agent:run`/`oracle:despacho:executar` em `tools.denied` + gate
`type: human-approval` `blocksTransitionTo: agent:run`. O validador exige o gate para quem delega.

## Validação e geração

```bash
python gen_skill_dependencies.py          # (re)gera o derivado a partir do frontmatter
python gen_skill_dependencies.py --check   # verifica sem escrever (!=0 se desatualizado)
python validate_catalog.py                 # valida o catalog.json canônico
python validate_catalog.py --suite         # canônico + todas as fixtures
python test_dep_sync.py                    # prova de sincronização das dependências
```

Requer `jsonschema` (Draft 2020-12) e `PyYAML`. Sai com código ≠ 0 em qualquer falha. O `--suite`
**calcula e imprime** a contagem (TOTAL / CONFORMES / FALHOS INESPERADOS / RESULTADO) — não é
hardcoded. Execução final desta rodada: **25 casos** (2 positivos + 23 negativos), **25/25 conformes**,
0 divergentes.

## Consumo (Agent-SDK)

`electron/overcore/catalogResolver.ts` resolve de um **snapshot injetado**: aplica o **JSON Schema
Draft 2020-12 completo** (schema do snapshot, via `@cfworker/json-schema`, dep direta) e as regras
semânticas — skills próprias, existência, runtime Claude, risco, dependências, `executionRecord` e
rotas `onDemand`. Falha **fechada**, sem entrada parcial e sem fallback local. Teste de integração
monta o snapshot copiando os **arquivos reais do hub**.

## Estado (honesto)

`status: draft` em todas as entradas: validável, mas ativação real bloqueada por **PRB-016** (sem
`<userData>/overcore/active.json`, sem resolução de produção). Conversa e despacho indisponíveis no
runtime real. Próximo passo: PRB-016.
