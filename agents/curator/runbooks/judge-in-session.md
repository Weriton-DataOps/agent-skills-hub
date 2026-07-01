# Runbook — Juiz na sessão (o Claude Code é o juiz)

Modelo de operação do OverCore: **o juiz é a própria sessão do Claude Code** (você conversando com o
Claude), não um `judge.py` com chave/SDK à parte. O mantenedor não roda `run_cycle.py` nem instala
`anthropic` — ele pede ao Claude para avaliar, e o Claude julga **e sobe**.

## Fluxo

1. **Contribuições chegam** como GitHub Issues (label `contribution`) ou arquivos em `contributions/inbox/`.
2. O mantenedor abre o Claude Code e pede: *"avalie as contribuições pendentes do OverCore"*.
3. O **Claude (juiz)**:
   - lista as Issues abertas: `gh issue list --repo <owner>/<repo> --label contribution --state open`;
   - para cada uma, lê o texto bruto e roda a checagem determinística barata:
     `python agents/curator/scripts/dedup_check.py --text "..."` (dedup vs as skills existentes);
   - aplica a rubric [`rubrics/promotion.md`](../rubrics/promotion.md) (gates C1–C5 + scoring);
   - decide **PROMOTE / REVISE / HUMAN_REVIEW / REJECT**.
4. Para **PROMOTE**, o Claude **sobe**:
   - escreve `skills/<slug>/SKILL.md` (slug limpo, com a marca d'água de crédito: `origin`/`author`/`contributed_via`);
   - insere no `docs/indices/skills_index.json`;
   - abre o PR e comenta/fecha a Issue de origem (`promovido em <skill> via #<PR>`).
5. **O merge continua humano.** O Claude prepara o PR; o mantenedor faz o merge.

## Por que este modelo
- **Sem chave/SDK extra**: o Claude Code já é o modelo — dispensa `pip install anthropic` e uma chave separada.
- **Mesma rubric, mesmo rigor**: o juiz segue `promotion.md`; gerador ≠ juiz continua valendo (quem rascunhou não se auto-aprova).
- **Barato**: a parte determinística (dedup) é Python; o julgamento é uma avaliação de texto, não um pipeline pesado.

## Scripts ainda úteis (opcionais)
- `dedup_check.py` — dedup determinístico (o juiz usa como evidência).
- `update_index.py` / `open_pr.py` — o juiz pode chamá-los para materializar e abrir o PR.
- `ingest_issues.py` / `loop_step.py` / `run_cycle.py` — continuam existindo para operação automática,
  mas **não são necessários** no modo "juiz na sessão".
