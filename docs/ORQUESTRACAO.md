# OverCore — Orquestração: agentes × skills × instruções × modelos de IA

> Documento de arquitetura do **OverCore** — invocado no VS Code por `/overcore`.

## Visão geral

O **OverCore** é um sistema de orquestração multi-agente construído sobre um **hub público de skills** (1451 skills, cada uma com `SKILL.md` + frontmatter, indexadas em `docs/indices/skills_index.json` e agrupadas em `docs/indices/marketplace.json`). O hub é a única fonte de verdade. Dois consumidores leem o hub por fetch direto do repositório público: o **Pipeline Studio** (o orquestrador Agent-SDK do dono, que monta agentes em runtime) e o **VS Code** (skills do Claude Code expostas como comandos `/`). Qualquer agente do Pipeline ou usuário do VS Code que descubra um fix/atalho contribui **texto bruto** via GitHub Issues com label `contribution` — nunca toca no corpus. Um agente **Curator**, gêmeo iso-mórfico do `agents/researcher/` existente, roda na máquina do dono numa rotina, lê essas Issues, avalia com rubric, deduplica contra as 1451 skills, formata como `SKILL.md` e **abre um PR**. O dono — e só o dono — faz o merge, que re-distribui o índice para os dois consumidores. **Nenhum auto-merge em lugar nenhum.**

```
                          ┌─────────────────────────────────────────────┐
                          │        HUB PÚBLICO (agent-skills-hub)         │
                          │  skills/<id>/SKILL.md  (1451)                 │
                          │  docs/indices/skills_index.json  (fonte de    │
                          │  verdade: target/risk/category por skill)     │
                          │  docs/indices/marketplace.json (bundles)      │
                          └───────────────▲───────────────▲──────────────┘
            fetch por SHA (público)       │               │   git pull / subtree
        ┌─────────────────────────────────┘               └──────────────────────┐
        │                                                                         │
┌───────┴────────────────────────┐                              ┌─────────────────┴───────────────┐
│   CONSUMIDOR 1                  │                              │   CONSUMIDOR 2                   │
│   Pipeline Studio (Agent-SDK)   │                              │   VS Code  "/"  (Claude Code)    │
│   Router → monta agentes em RT  │                              │   skills do hub como comandos /  │
│   gate_state, runs/<id>/        │                              │   filtro targets.claude=supported│
└───────┬─────────────────────────┘                             └─────────────────┬────────────────┘
        │  descobre fix / atalho                                    descobre fix / atalho
        │                                                                          │
        │            TEXTO BRUTO via GitHub Issue (label "contribution")           │
        └──────────────────────────────┐         ┌─────────────────────────────────┘
                                        ▼         ▼
                          ┌─────────────────────────────────────┐
                          │   GitHub Issues  label=contribution  │
                          │   (token-robô Issues:write apenas)   │
                          └───────────────────┬──────────────────┘
                                              │ ingest (token-robô Issues:read)
                                              ▼
                  ┌───────────────────────────────────────────────────────┐
                  │   CURATOR  (agents/curator/, roda na máquina do dono)  │
                  │   ingest → triage → dedup → evaluate → draft →         │
                  │   index-update → prepare-pr                            │
                  │   (espelha agents/researcher/, reusa novelty_check.py) │
                  └───────────────────────────┬───────────────────────────┘
                                              │ abre PR  (branch curator/<id>)
                                              ▼
                          ┌─────────────────────────────────────┐
                          │      GATE HUMANO  —  o DONO revisa    │
                          │      e faz MERGE (nunca o agente)     │
                          └───────────────────┬──────────────────┘
                                              │ merge → bump versão do índice
                                              ▼
                          re-distribuição → os 2 consumidores releem o HEAD
```

## Como um agente é montado (runtime)

Toda instanciação de agente — em qualquer papel — segue **uma única sequência canônica**, registrada passo a passo em `runs/<id>/` espelhando o layout do `researcher/`. Isso torna o sistema reproduzível e auditável:

1. **Papel** — o Router escolhe um dos papéis do roster. O papel define três coisas fixas: as **skills de papel** (sempre injetadas), a **rubric** do estágio e o **tier de modelo** default. Tier é atributo do PAPEL+ESTÁGIO, gravado em `runs/<id>/router.jsonl`, nunca escolhido ad-hoc pelo subagente.
2. **Instruções** — injeta o `METODO-CONSTRUCAO.md` (gate duro: ideia → croqui → refinado → código → validação) mais a rubric do estágio (do researcher/curator). É aqui que o papel recebe seu mandato e seus limites.
3. **Skills (descoberta via índice)** — descoberta em duas fases sobre `skills_index.json` (ver "## Descoberta de skills"): filtro determinista por `plugin.targets` + `risk`, depois seleção por `category` exata ou ranking lexical. O agente carrega no máximo **N=6** skills: as de papel-fixo + as descobertas pela tarefa. Cada skill resolvida vira `skills/<id>/SKILL.md` lido em tempo de montagem.
4. **Modelo** — o tier sai do mapa fixo (ver "## Roteamento de modelos de IA"). Haiku para mecânico, Sonnet para execução, Opus para julgamento difícil.
5. **Execução** — sempre em **worktree/branch**, nunca no `main`.
6. **Validação** — o papel Validação **roda de verdade** (executa app/teste, captura evidência: screenshot/log/exit-code em `runs/<id>/validation/`).
7. **Verdict** — `PASS | HUMAN_REVIEW | FAIL`.
8. **PR** — preparado pelo agente; **nunca auto-merge**.

O **Router** (claude-sonnet-4-6) é a única porta de entrada do Pipeline Studio. Recebe a tarefa bruta, classifica em uma de 6 rotas (`design`, `codigo`, `validacao`, `research`, `curate`, `contribuir`), monta o agente-alvo e cuida do `gate_state`. Não executa trabalho de domínio. Loga cada decisão em `runs/<id>/router.jsonl` com `{route, model_tier, skills[], gate_state}`. Escala para claude-opus-4-8 **só** quando a classificação fica abaixo do limiar de confiança (ambiguidade entre rotas) ou quando há conflito entre verdicts de subagentes.

## Roster de agentes

| Agente | Função | Skills que puxa | Instruções / rubric | Modelo default |
|---|---|---|---|---|
| **Router / Supervisor** | Única porta de entrada; classifica em 6 rotas, monta o agente-alvo, dono do `gate_state`. Não faz trabalho de domínio. | (nenhuma de domínio; usa o índice para resolver as dos outros) | Mapa de rotas + máquina de `gate_state` | claude-sonnet-4-6 (→ opus-4-8 em ambiguidade/conflito) |
| **Design — modo croqui** | Estrutura, hierarquia, navegação; output HTML tosco e descartável. | `brainstorming`, `example-skills:frontend-design` | METODO etapa *croqui* | claude-haiku-4-5 |
| **Design — modo refinado** | Mesmo papel reentra: tipografia, cor, estado, animação. | `ui-ux-pro-max`, `example-skills:frontend-design`, `example-skills:theme-factory` | METODO etapa *refinado* (após aprovação humana do croqui) | claude-sonnet-4-6 |
| **Código** | Implementa só após `gate_state == refinado_aprovado`; recebe `refinado.html` aprovado como contexto fixo. Output em worktree. | `test-driven-development`, `clean-code`, `writing-plans` + skills de stack por `category` (ex.: `vercel:react-best-practices`) | METODO etapa *código* | claude-sonnet-4-6 (→ opus-4-8 se Router marcar alto-risco) |
| **Validação** | Roda de verdade: executa app/teste, captura evidência, emite verdict. | `verification-before-completion`, `example-skills:webapp-testing`, `code-review-checklist` | METODO etapa *validação* | claude-sonnet-4-6 (→ opus-4-8 + `differential-review` + `backend-security-coder` quando toca auth/input/endpoints) |
| **Researcher** | Descoberta externa (feeds/web): discover → … → prepare-pr → human-merge. Existe; vira a rota `research`. | (rubrics próprias do researcher) | Estágios do researcher | conforme estágio (ver roteamento) |
| **Curator** | Descoberta interna: ingest de Issues `contribution` → … → prepare-pr → human-merge. Gêmeo do researcher. | reusa `novelty_check.py`, `validate_repo.py` | rubric `promotion.md` (gates C1–C5) | conforme estágio (ver roteamento) |

Researcher e Curator **compartilham os mesmos scripts** em `agents/<x>/scripts` (`validate_repo.py`, `novelty_check.py`, `render_router_report.py`) via import relativo do ROOT, e ambos despejam PRs no mesmo fluxo de revisão humana. A única diferença é a fonte: Researcher puxa de feeds/web; Curator puxa de Issues `contribution`.

## Roteamento de modelos de IA

O tier é atributo do **papel + estágio**, gravado em `router.jsonl` / `run-state.json`, nunca escolhido pelo subagente. Mapa fixo:

| Papel / tarefa | Estágio | Modelo (id correto) |
|---|---|---|
| Triagem, dedup, ingest de Issue, parse texto-bruto | mecânico/classificatório | `claude-haiku-4-5` |
| Croqui (design simples) | rascunho descartável | `claude-haiku-4-5` (fallback Sonnet se ambíguo) |
| Self-check de frontmatter (path bate id? description preenchida?) | verificação barata | `claude-haiku-4-5` |
| Design refinado | refinado | `claude-sonnet-4-6` |
| Código / patch (atualizar `skills_index.json`, `marketplace.json`, scripts) | execução | `claude-sonnet-4-6` |
| Validação que roda de verdade | validação | `claude-sonnet-4-6` |
| Evaluate-rubric (extração/format do `SKILL.md`) | format | `claude-sonnet-4-6` |
| Redação do corpo do PR (rationale, diff-explainer) | PR body | `claude-sonnet-4-6` |
| Router default | roteamento | `claude-sonnet-4-6` |
| Julgamento de rubric (merece virar skill? genérico?) | LLM-as-judge | `claude-opus-4-8` |
| Verdict que para na fila humana (HUMAN_REVIEW/REJECT terminal) | decisão irreversível | `claude-opus-4-8` |
| Desempate pairwise entre candidatos | pairwise | `claude-opus-4-8` |
| Conflito entre verdicts / classificação ambígua / segurança | julgamento difícil | `claude-opus-4-8` |
| Geração narrativa longa (opcional) | narrativa | `claude-fable-5` |
| Runtime alternativo | execução de skill | **Codex (OpenAI)** quando `targets.codex=='supported'` e `targets.claude!='supported'` |

**Regras de escalonamento (degraus duros, barato → caro, só sob gatilho explícito registrado no run):**

- **Degrau 1 — Haiku:** toda tarefa mecânica/classificatória (parse, triagem, dedup, croqui).
- **Degrau 2 — Sonnet:** dispara quando (a) Haiku retorna baixa confiança/ambiguidade, (b) a tarefa produz código ou design refinado, ou (c) o texto da Issue é longo/técnico.
- **Degrau 3 — Opus:** dispara **só** em (a) julgamento de rubric, (b) verdict que para na fila humana, (c) conflito/empate entre dois candidatos (pairwise), (d) síntese final do PR.
- **Nunca pular degraus "por segurança":** um job começa no degrau mínimo e sobe só com gatilho concreto. **REJECT** vindo de Haiku/Sonnet vira **HUMAN_REVIEW** automático — modelos baratos nunca emitem REJECT terminal sozinhos.
- **Gerador ≠ juiz:** o modelo que escreveu o `SKILL.md` (Sonnet) **nunca** julga a própria saída; o juiz é sempre Opus.

**Uso de `plugin.targets.{claude,codex}`** (runtime por skill, leitura de campo, não adivinhação):

- `claude=='supported'` → runtime Claude (Sonnet para rodar/validar; Opus só se exigir julgamento).
- `claude=='blocked'` e `codex=='supported'` → cai para runtime **Codex** (OpenAI).
- ambos `'supported'` → preferir Claude (default do projeto); Codex só como **segunda opinião** em validação crítica (cross-check independente de skill que Opus aprovou).
- ambos `'blocked'` → não auto-validar → park **HUMAN_REVIEW**.
- Se o runtime falhar em execução, degrada para o outro target suportado e marca `degraded_runtime` no run. **Codex é runtime, não juiz:** decisão de merge-prep, rubric e verdict permanecem 100% Claude/Opus.

## Descoberta de skills

A descoberta acontece em **duas fases** sobre o array plano de `docs/indices/skills_index.json`, sem gastar LLM:

**Fase 1 — Filtro determinista:**
- Por **runtime**: `plugin.targets.claude=='supported'` quando o runtime é Claude (descarta os `blocked`); `plugin.targets.codex` quando o runtime é Codex/OpenAI.
- Por **risco**: tarefas sem aprovação humana só carregam `risk=='safe'` (`caution`/`dangerous` exigem gate explícito).

**Fase 2 — Seleção:**
- **Match por `category` exata** quando o Router já sabe o domínio (há ~75 categorias) — evita ruído.
- **Senão, ranking lexical** por `name`+`description` contra a tarefa, usando o **mesmo tokenizador/Jaccard do `novelty_check.py`**.

O agente carrega no máximo **N=6** skills: as de papel-fixo (injetadas pelo papel) + as descobertas pela tarefa. Cada skill resolvida vira o path absoluto `skills/<id>/SKILL.md`, lido em tempo de montagem.

**Para os consumidores:**
- **Pipeline Studio** faz fetch direto do raw público de `skills_index.json` e `marketplace.json` no início de cada run; cacheia por **commit SHA** e recarrega só quando o HEAD muda. O Router resolve `name`→`path` e busca o `SKILL.md` cru sob demanda. Sem cópia local versionada — a fonte de verdade é sempre o HEAD do hub.
- **VS Code `/`** usa o mesmo `skills_index.json` como catálogo; o filtro `targets.claude=='supported'` garante que só skills válidas para Claude Code apareçam. Skills com `plugin.setup.type != 'none'` exibem `setup.summary`/`docs` antes de ativar. Atualização = `git pull`/subtree, não mecanismo próprio.

## Ciclo de contribuição (Curator)

O Curator é um espelho iso-mórfico do `agents/researcher/`: trata cada Issue `contribution` como mais um "source" e roda uma máquina de estados conservadora de **um-passo-por-loop** (`loop_step_max_advances=1`), append-only em `state_history` com `{state, timestamp, reason, evidence}`.

**Lifecycle (estados em `run-state.json`):**

```
ingested → triaged → evaluated → deduped → drafted → indexed
   → pr_opened → human_review → (merged | parked | rejected) → redistributed
```

- `ingest_issues.py` puxa Issues `label=contribution` via token-robô (Issues:read) para `queue/inbox.jsonl`.
- Cada linha do inbox: `{contrib_id (hash do issue#+url), issue_number, issue_url, title, raw_text, author_login, author_display, origin ('vscode-claude'|'pipeline-studio:<agent-id>'|'human'), submitted_at, attempts, last_status}`. `author_login` e `origin` são capturados na fonte e **propagados** até o frontmatter/índice (marca d'água de crédito).
- `redistribute` = bump da versão do `skills_index.json` + `CATALOG.md` **após o merge humano**, para que Pipeline Studio e VS Code releiam.

**Rubric de promoção (`agents/curator/rubrics/promotion.md`) — 5 gates duros + scoring:**

| Gate | Critério | Falha → |
|---|---|---|
| **C1 Acionável** | Diz o que fazer/quando/o que evitar, não só conhecimento de fundo | HUMAN_REVIEW |
| **C2 Genérico/Reutilizável** | Vale fora do contexto onde o bug nasceu; segredos/caminhos/nomes internos → REJECT ou exige sanitização | REJECT / sanitização |
| **C3 Não-Duplicado** | Passa no `dedup_check` contra as 1451 | REJECT (likely_duplicate) |
| **C4 Seguro** | Sem credenciais, sem comando destrutivo não-gated; `risk` classificado `safe`/`caution`/`dangerous` | HUMAN_REVIEW / REJECT |
| **C5 Auto-contido** | Texto suficiente para virar `SKILL.md` acionável sem ida-e-volta com o autor | HUMAN_REVIEW |

**Scoring ponderado (0/1/2):** Acionabilidade 30%, Generalidade 25%, Não-Duplicação 20%, Segurança 15%, Ergonomia de Skill 10%. Aprova só com **total ≥ 1.4 e nenhum gate duro falho**.

**Verdicts (espelham o researcher):**

- **PROMOTE** — todos os gates passam, total ≥ 1.4, dedup=pass → segue para draft + index + PR.
- **REVISE** — gate macio falho OU 0.9 ≤ total < 1.4 OU dedup=human_review com melhoria possível → propõe um **delta/merge num skill existente** em vez de skill novo.
- **HUMAN_REVIEW** — dúvida de juízo, dedup=human_review, ou C2/C4 ambíguo → park em `queue/parked.jsonl` + linha em `reports/parked-review.md`.
- **REJECT** — qualquer gate duro falho OU total < 0.9 OU dedup=likely_duplicate (com ponteiro para o skill existente).

O **verdict que para na fila humana é sempre emitido por `claude-opus-4-8`** (LLM-as-judge, avaliador único da rubric; desempate pairwise também em Opus). Antes de chamar o juiz Opus, rodam checagens determinísticas baratas (`validate_repo.py`, `novelty_check.py`, schema-check do índice + self-check Haiku); só o que passa sobe para o juiz. Se Opus estiver indisponível para o verdict, o item **não** recebe verdict automático — vai direto para park HUMAN_REVIEW.

**Anti-duplicação (`dedup_check.py`)** reutiliza a lógica do `novelty_check.py` (tokenização + stopwords + Jaccard) contra `skills_index.json` (`name`+`description`) **e** `skills/*/SKILL.md` (corpo via `salient_text`). Três faixas por threshold (default 0.18; ×1.75 = likely_duplicate): `pass | human_review | likely_duplicate`. Emite `reports/dedup-report.json` com `top_overlaps [{skill_id, path, score, shared_terms}]`.

**Abertura de PR (sem auto-merge):** `open_pr.py` usa token-robô (Pull-Requests:write, Contents:write em branch) para criar branch `curator/<contrib-id>`, commitar o novo `skills/<slug>/SKILL.md` + `skills_index.json` + `CATALOG.md`, e abrir PR com `templates/pr-body.md` (link da Issue, verdict, score, dedup-report, autor/origem, diff do índice). `enable_auto_pr=false` deixa em rascunho até o dono. **Merge é 100% humano.** Pós-merge, `loop_daily` fecha a Issue com comentário do robô (`promovido em <skill_id> via #<PR>`) e marca `contrib_id` em `queue/done.jsonl`, disparando a re-distribuição.

**Estrutura de arquivos de `agents/curator/` (espelha 1:1 o `researcher/`):**

```
agents/curator/
  orchestration/
    config.json            # budgets, intervals, human_review, gates, feeds, mode
    (launchd | task-scheduler)
  queue/
    inbox.jsonl  parked.jsonl  done.jsonl  quarantine.jsonl
  runs/<contrib-id>/
    run-state.json  THREAD.md  sources/  proposals/  reports/
  rubrics/
    promotion.md  dedup.md  safety.md
  templates/
    skill-draft.md  contribution-evaluation.json  dedup-report.json  pr-body.md
  runbooks/
    continuous-operation.md  pr-readiness.md  ingest-issues.md
  scripts/
    ingest_issues.py  triage.py  dedup_check.py  draft_skill.py
    update_index.py  open_pr.py  loop_common.py  loop_step.py
    loop_discover.py  loop_daily.py  loop_status.py  validate_run.py
  ledgers/
    promoted.jsonl  rejected.jsonl
```

**`config.json`** espelha o researcher com 3 acréscimos mínimos (feeds/safety/watermark):

```json
{
  "budgets": { "max_active_runs": 3, "max_runs_per_day": 6, "max_parked": 12,
               "max_failures_per_day": 5, "max_inbox_size": 200 },
  "intervals": { "loop_step_minutes": 10, "loop_discover_hours": 6, "loop_daily_hour_utc": 6 },
  "human_review": { "park_on_verdicts": ["HUMAN_REVIEW", "REJECT"],
                    "park_on_dedup": ["human_review", "likely_duplicate"],
                    "notification_file": "agents/curator/reports/parked-review.md" },
  "gates": { "require_dedup_pass": true, "require_safety_scan": true,
             "max_skill_lines": 500, "forbid_secrets": true, "require_author_watermark": true },
  "feeds": { "issues_label": "contribution", "github_repo": "<owner>/agent-skills-hub",
             "token_env": "CURATOR_ISSUES_TOKEN", "enable_auto_pr": false },
  "mode": "dry-run"
}
```

## Gate humano (MÉTODO)

O Router mantém um campo `gate_state` por run com a máquina de estados que **codifica o hard-gate do `METODO-CONSTRUCAO.md`** como estado bloqueante, não como convenção:

```
ideia → croqui_pronto → [PAUSA: aprovação humana] → croqui_aprovado
      → refinado_pronto → [PAUSA: aprovação humana] → refinado_aprovado
      → codigo → validado
```

As **duas PAUSAS são bloqueantes**:

- O Router **não instancia** o papel Código enquanto `gate_state != 'refinado_aprovado'`.
- A aprovação é um **sinal humano explícito** (arquivo / PR-comment / flag em `runs/<id>/gate.json`), espelhando o `park_on_verdicts` do researcher.
- **Nenhuma transição croqui → código direta é permitida.** O croqui é descartável e barato (Haiku); o refinado precisa de gosto visual (Sonnet); o código só existe depois do refinado aprovado pelo humano.

Esse mesmo princípio — *agentes preparam, humanos decidem* — aparece em três pontos do sistema: o gate de design (refinado → código), o verdict de validação (HUMAN_REVIEW para o dono) e o merge de contribuição (PR-only, merge humano). É a **regra de ouro** unificadora.

## Marca d'água de crédito

O crédito só é auditável se viver no **mesmo par `frontmatter` + `skills_index.json`** que já governa a descoberta — nunca num arquivo lateral. Campos opcionais adicionados ao frontmatter do `SKILL.md` e ao item do índice:

- `origin` — `vscode-claude` | `pipeline-studio:<agent>` | `human` | `researcher`
- `author` — `author_display` ou `author_login` da Issue
- `contributed_via` — `issue_url`
- `date_added` — **data do merge**

`draft_skill.py` preenche a partir do registro do inbox; `update_index.py` copia para o índice. Para as 1451 skills existentes o campo fica **ausente / `legacy`** — não reescrever em massa. `validate_repo.py` ganha a checagem: se `origin ∈ {vscode-claude, pipeline-studio:*}`, então `author` e `contributed_via` são **obrigatórios**. Pós-merge, o robô fecha a Issue de origem com comentário (`promovido em <skill_id> via #<PR>`), fechando o loop de crédito de volta ao autor.

## O que falta construir

- [ ] **`agents/curator/`** completo: árvore de diretórios espelhando o `researcher/` (orchestration, queue, runs, rubrics, templates, runbooks, scripts, ledgers).
- [ ] **`orchestration/config.json`** do curator (budgets/intervals/human_review/gates/feeds/mode) + agendador (launchd/task-scheduler).
- [ ] **Scripts do curator**: `ingest_issues.py`, `triage.py`, `dedup_check.py`, `draft_skill.py`, `update_index.py`, `open_pr.py`, `loop_{common,step,discover,daily,status}.py`, `validate_run.py`.
- [ ] **`rubrics/promotion.md`** (gates C1–C5 + scoring) + `dedup.md` + `safety.md`.
- [ ] **`templates/`**: `skill-draft.md`, `contribution-evaluation.json`, `dedup-report.json`, `pr-body.md`.
- [ ] **`runbooks/`**: `continuous-operation.md`, `pr-readiness.md`, `ingest-issues.md`.
- [ ] **Extensão do schema** do `skills_index.json` e do frontmatter para os campos de crédito (`origin`, `author`, `contributed_via`).
- [ ] **`validate_repo.py`**: checagem de marca d'água obrigatória para contribuições; schema-check do índice.
- [ ] **Router do Pipeline Studio**: classificador de 6 rotas, máquina de `gate_state`, log `router.jsonl`, montador de agentes (filtro+ranking de skills, fetch por SHA).
- [ ] **`gate.json`** por run + mecanismo de sinal humano explícito (arquivo / PR-comment / flag).
- [ ] **Camada de fetch-por-SHA** no orquestrador (cache por commit, recarga no HEAD) e integração do catálogo `/` no VS Code (git pull/subtree).
- [ ] **Token-robô GitHub**: escopo Issues:write para contribuidores; escopo Issues:read + Pull-Requests:write + Contents:write (branch) para o curator.
- [ ] **Template de Issue** `contribution` (o-que-resolvi / contexto / como-reproduzir) + label no repo.
- [x] ~~Definição do nome do projeto~~ → **OverCore** (comando `/overcore`).
