# Curator — descoberta interna (contribuições → skills)

O Curator é o **gêmeo interno** do `agents/researcher/`. Enquanto o researcher
descobre conhecimento **externo** (papers, posts), o Curator descobre conhecimento
**interno**: os fixes, atalhos e jeitos eficientes que os agentes do Pipeline Studio
e os usuários do VS Code encontram no dia a dia e sobem como **texto bruto** via
GitHub Issues (label `contribution`).

Ele lê essas Issues, avalia com a rubric, deduplica contra as 1465 skills, rascunha
um `SKILL.md` e **abre um PR**. **O merge é sempre humano — nenhum auto-merge.**

Ver a arquitetura completa em [`docs/ORQUESTRACAO.md`](../../docs/ORQUESTRACAO.md).

## Lifecycle

```
ingested → triaged → deduped → drafted → (PR) → human_review → (merged | parked | rejected)
```

## Rodar o demo local (sem token, hoje)

```bash
# 1) Ingerir uma contribuição em texto bruto (simula uma Issue)
python agents/curator/scripts/ingest_local.py \
  --title "Diagnosticar 500 em API route do Next.js por env var ausente" \
  --author "Weriton" --origin vscode-claude \
  --file agents/curator/examples/sample-contribution.md

# 2) Avançar uma contribuição: triage → dedup → draft → PR body
python agents/curator/scripts/loop_step.py

# 3) Ver a fila e o estado dos runs
python agents/curator/scripts/loop_status.py
```

Saída em `agents/curator/runs/<contrib_id>/`:
- `run-state.json` — estado + histórico + verdict
- `proposals/<slug>/SKILL.md` — o rascunho da skill
- `reports/dedup-report.json` · `reports/triage.json` · `reports/evaluation.json`
- `pr-body.md` — corpo do PR pronto

## Produção (com token)

`ingest_issues.py` puxa as Issues reais quando você define:
- `CURATOR_ISSUES_TOKEN` — PAT fine-grained, escopo **Issues: read** apenas
- `CURATOR_GITHUB_REPO` — ex.: `Weriton-DataOps/agent-skills-hub` (ou `feeds.github_repo` no config)

A rotina (Task Scheduler no Windows) roda `ingest_issues.py` + `loop_step.py`
periodicamente. O `open_pr.py` (a construir) usa um token com escopo de PR para
abrir o PR — nunca faz merge.

## Onde o LLM entra

Os scripts fazem só a parte **determinística** (ingest, triage de segredo, dedup,
scaffold). O **julgamento da rubric** (`rubrics/promotion.md`) é feito pelo juiz
`claude-opus-4-8` sobre o rascunho — e o **merge** é seu.

## Estrutura

```
agents/curator/
  orchestration/config.json   # budgets, gates, feeds, models
  scripts/                    # loop_common, ingest_local, ingest_issues, triage,
                              # dedup_check, draft_skill, loop_step, loop_status
  rubrics/promotion.md        # instrução do juiz (gates C1–C5 + scoring + verdicts)
  examples/                   # contribuição de exemplo p/ testar
  queue/                      # inbox.jsonl, parked.jsonl, done.jsonl  (runtime)
  runs/<contrib_id>/          # artefatos por contribuição            (runtime)
```
