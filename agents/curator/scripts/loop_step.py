#!/usr/bin/env python3
"""Advance one contribution: triage -> dedup -> draft -> proposal + reports.

This is the deterministic backbone. It NEVER emits a terminal PROMOTE on its own:
the cheap gates can only send a contribution to HUMAN_REVIEW or REJECT; anything
clean is left as `drafted` / PENDING_JUDGE for the Opus LLM-judge (rubric) and
then the human merge. Mirrors agents/researcher/ one-item-per-step conservatism.

Usage:
  python loop_step.py            # advance the first pending contribution
  python loop_step.py --id <id>  # advance a specific contribution
"""

from __future__ import annotations

import argparse

import draft_skill
import triage as triage_mod
from dedup_check import dedup
from loop_common import (
    INBOX, TERMINAL_STATUSES, ensure_dir, load_index, now_iso,
    read_jsonl, run_dir, today, write_json, write_jsonl,
)

JUDGE_MODEL = "claude-opus-4-8"


def _pre_verdict(tri: dict, ded: dict) -> tuple[str, str, str]:
    """Return (verdict, next_status, reason). Deterministic pre-filter only."""
    if tri["has_secret"]:
        return "HUMAN_REVIEW", "needs_human_review", "possível segredo no texto (gate C4)"
    if tri["too_short"]:
        return "HUMAN_REVIEW", "needs_human_review", "texto curto demais (gate C5)"
    if ded["verdict"] == "likely_duplicate":
        top = ded["top_overlaps"][0] if ded["top_overlaps"] else {}
        return "REJECT", "rejected", f"provável duplicata de {top.get('skill_id')} (gate C3)"
    if ded["verdict"] == "human_review":
        return "HUMAN_REVIEW", "needs_human_review", "sobreposição parcial com skill existente (gate C3)"
    return "PENDING_JUDGE", "drafted", "gates baratos ok — aguardando juiz Opus + revisão humana"


def advance(rec: dict, index: list[dict]) -> dict:
    cid = rec["contrib_id"]
    rd = run_dir(cid)
    ensure_dir(rd / "reports")
    history = [{"state": "ingested", "at": rec.get("submitted_at"), "reason": "recebido"}]

    tri = triage_mod.triage(rec)
    write_json(rd / "reports" / "triage.json", tri)
    history.append({"state": "triaged", "at": tri["triaged_at"], "reason": "; ".join(tri["notes"]) or "ok"})

    ded = dedup(rec.get("raw_text", ""), index=index)
    write_json(rd / "reports" / "dedup-report.json", ded)
    history.append({"state": "deduped", "at": ded["checked_at"],
                    "reason": f"verdict={ded['verdict']} max_score={ded['max_score']}"})

    drafted = draft_skill.draft(rec, tri)
    prop_dir = ensure_dir(rd / "proposals" / drafted["slug"])
    (prop_dir / "SKILL.md").write_text(drafted["skill_md"], encoding="utf-8")
    history.append({"state": "drafted", "at": now_iso(), "reason": f"skill={drafted['slug']}"})

    verdict, next_status, reason = _pre_verdict(tri, ded)

    evaluation = {
        "contrib_id": cid,
        "slug": drafted["slug"],
        "deterministic_gates": {
            "C3_not_duplicate": ded["verdict"] == "pass",
            "C4_safe": not tri["has_secret"],
            "C5_self_contained": not tri["too_short"],
        },
        "pending_judge": verdict == "PENDING_JUDGE",
        "judge_model": JUDGE_MODEL,
        "rubric_scores": {
            "actionability": None, "generality": None, "non_duplication": None,
            "safety": None, "skill_ergonomics": None,
            "_note": f"preenchido pelo juiz {JUDGE_MODEL} (LLM-as-judge sobre rubrics/promotion.md)",
        },
        "pre_verdict": verdict,
        "reason": reason,
    }
    write_json(rd / "reports" / "evaluation.json", evaluation)

    state = {
        "contrib_id": cid,
        "title": rec.get("title"),
        "slug": drafted["slug"],
        "origin": rec.get("origin"),
        "author": rec.get("author_display") or rec.get("author_login"),
        "state": next_status,
        "pre_verdict": verdict,
        "final_verdict_by": f"{JUDGE_MODEL} (LLM-judge) + merge humano",
        "reason": reason,
        "dedup": {"verdict": ded["verdict"], "max_score": ded["max_score"],
                  "closest": ded["top_overlaps"][0] if ded["top_overlaps"] else None},
        "created_at": now_iso(),
        "state_history": history,
    }
    write_json(rd / "run-state.json", state)
    _write_pr_body(rd, rec, drafted, verdict, reason, ded)
    return state


def _write_pr_body(rd, rec, drafted, verdict, reason, ded):
    closest = ded["top_overlaps"][0] if ded["top_overlaps"] else None
    closest_md = f"`{closest['skill_id']}` (score {closest['score']})" if closest else "nenhuma"
    body = f"""## Contribuição → skill (rascunho do Curator)

- **Skill:** `skills/{drafted['slug']}/`
- **Origem:** `{rec.get('origin')}`  ·  **Autor:** {rec.get('author_display') or rec.get('author_login')}
- **Via:** {rec.get('issue_url') or 'local:' + rec.get('contrib_id','')}
- **Pré-verdict (gates determinísticos):** `{verdict}` — {reason}
- **Dedup:** verdict `{ded['verdict']}`, max_score `{ded['max_score']}`, mais próxima: {closest_md}

> ⚠️ Verdict final da rubric = juiz **{JUDGE_MODEL}**. **Merge = decisão humana.** Nenhum auto-merge.

### Checklist do revisor
- [ ] Rubric (C1–C5) aprovada pelo juiz
- [ ] Dedup confere (não é duplicata real)
- [ ] Frontmatter + marca d'água de crédito preenchidos
- [ ] `SKILL.md` acionável e auto-contido
"""
    (rd / "pr-body.md").write_text(body, encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Advance one contribution through the curator pipeline.")
    ap.add_argument("--id", help="specific contrib_id; default = first pending")
    args = ap.parse_args()

    inbox = read_jsonl(INBOX)
    if not inbox:
        print(f"inbox vazio: {INBOX}\nUse: python ingest_local.py --title ... --file raw.md")
        return

    target = None
    for rec in inbox:
        status = rec.get("last_status", "ingested")
        if args.id:
            if rec.get("contrib_id") != args.id or status in TERMINAL_STATUSES:
                continue
        elif status != "ingested":
            # drain mode only advances NEW items; drafted/parked/rejected are left as-is
            continue
        target = rec
        break

    if target is None:
        print("nada pendente para avançar (tudo em estado terminal). Veja: python loop_status.py")
        return

    state = advance(target, load_index())

    # persist new status back into the inbox
    for rec in inbox:
        if rec["contrib_id"] == target["contrib_id"]:
            rec["last_status"] = state["state"]
            rec["attempts"] = rec.get("attempts", 0) + 1
    write_jsonl(INBOX, inbox)

    print("-" * 64)
    print(f"contrib    : {state['contrib_id']}  \"{state['title']}\"")
    print(f"skill      : skills/{state['slug']}/")
    print(f"dedup      : {state['dedup']['verdict']} (max_score={state['dedup']['max_score']})")
    print(f"pre-verdict: {state['pre_verdict']}  ->  {state['reason']}")
    print(f"final      : {state['final_verdict_by']}")
    print(f"artefatos  : {run_dir(state['contrib_id'])}")
    print("-" * 64)


if __name__ == "__main__":
    main()
