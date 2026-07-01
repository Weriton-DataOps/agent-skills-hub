# Rubric de Promoção — Curator

> Esta é a **instrução do juiz** (`claude-opus-4-8`, LLM-as-judge). O juiz recebe:
> o texto bruto da contribuição, o `SKILL.md` rascunhado, o `dedup-report.json` e o
> `triage.json`. Devolve o preenchimento de `contribution-evaluation.json` + o verdict.
>
> Regra de ouro: **o juiz nunca é o mesmo modelo que escreveu o rascunho** (Sonnet
> escreve, Opus julga). Modelos baratos (Haiku/Sonnet) **não** emitem REJECT terminal:
> na dúvida, rebaixam para HUMAN_REVIEW.

## Os 5 gates duros

| Gate | Critério | Falha → |
|---|---|---|
| **C1 · Acionável** | Diz **o que fazer, quando e o que evitar** — não é só conhecimento de fundo. | HUMAN_REVIEW |
| **C2 · Genérico/Reutilizável** | Vale **fora** do contexto onde o bug nasceu. Nomes internos / caminhos / segredos → sanitizar ou REJECT. | REJECT / sanitização |
| **C3 · Não-Duplicado** | Passa no `dedup_check` contra as 1465 skills. | REJECT (com ponteiro para a skill existente) |
| **C4 · Seguro** | Sem credenciais, sem comando destrutivo não-gated. `risk` classificado `safe`/`caution`/`dangerous`. | HUMAN_REVIEW / REJECT |
| **C5 · Auto-contido** | Texto suficiente para virar `SKILL.md` acionável **sem** ida-e-volta com o autor. | HUMAN_REVIEW |

## Scoring (0 / 1 / 2 por dimensão)

| Dimensão | Peso |
|---|---|
| Acionabilidade | 30% |
| Generalidade | 25% |
| Não-Duplicação | 20% |
| Segurança | 15% |
| Ergonomia de Skill | 10% |

**Total ponderado ∈ [0, 2].** Promove só com **total ≥ 1.4 e nenhum gate duro falho.**

## Verdicts

- **PROMOTE** — todos os gates passam, total ≥ 1.4, dedup=`pass` → segue para PR.
- **REVISE** — gate macio falho **ou** 0.9 ≤ total < 1.4 **ou** dedup=`human_review` com melhoria possível → propõe **delta/merge numa skill existente** em vez de skill nova.
- **HUMAN_REVIEW** — dúvida de juízo, dedup=`human_review`, ou C2/C4 ambíguo → park em `queue/parked.jsonl` + linha em `reports/parked-review.md`.
- **REJECT** — qualquer gate duro falho, ou total < 0.9, ou dedup=`likely_duplicate` → registra em `ledgers/rejected.jsonl` com ponteiro para a skill existente.

## Antes do juiz (checagens determinísticas, sem LLM)

O `loop_step.py` já rodou `triage.py` (segredo/curto) e `dedup_check.py` (Jaccard vs índice) e
pré-filtrou. O juiz Opus só é chamado para o que chegou como **PENDING_JUDGE**. Se Opus estiver
indisponível, o item vai direto para **HUMAN_REVIEW** — nunca recebe PROMOTE automático.
