#!/usr/bin/env python3
"""Opus judge — the AI curation decision (PROMOTE / REVISE / HUMAN_REVIEW / REJECT).

Runs AFTER loop_step.py has drafted a contribution (state=drafted / PENDING_JUDGE).
Calls Claude Opus 4.8 (the judge, per docs/ORQUESTRACAO.md) with the rubric, the raw
text, the drafted SKILL.md, and the dedup/triage reports, and forces a structured
verdict via tool use.

Safety rails (never bypassed):
  - The judge model (Opus) is NEVER the model that drafted the skill (generator != judge).
  - If the SDK is missing, the API key is unset, or the API errors, the item degrades to
    HUMAN_REVIEW — it is NEVER auto-promoted.
  - A PROMOTE is overridden to HUMAN_REVIEW if the recomputed weighted total < 1.4, a hard
    gate (C3/C4) fails, or dedup flagged a likely duplicate. Trust, but verify the arithmetic.

Needs (production):  pip install anthropic   and   ANTHROPIC_API_KEY=...
Usage:
  python judge.py                 # judge the first drafted contribution
  python judge.py --id <id>       # judge a specific contribution
"""

from __future__ import annotations

import argparse
import json

from loop_common import (
    CURATOR, INBOX, TERMINAL_STATUSES, now_iso, read_json, read_jsonl,
    run_dir, write_json, write_jsonl,
)

JUDGE_MODEL = "claude-opus-4-8"
WEIGHTS = {
    "actionability": 0.30,
    "generality": 0.25,
    "non_duplication": 0.20,
    "safety": 0.15,
    "skill_ergonomics": 0.10,
}
PROMOTE_THRESHOLD = 1.4

VERDICT_TOOL = {
    "name": "emit_verdict",
    "description": "Emite o veredito da rubric de promoção para esta contribuição.",
    "strict": True,
    "input_schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "scores": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "actionability": {"type": "integer", "enum": [0, 1, 2]},
                    "generality": {"type": "integer", "enum": [0, 1, 2]},
                    "non_duplication": {"type": "integer", "enum": [0, 1, 2]},
                    "safety": {"type": "integer", "enum": [0, 1, 2]},
                    "skill_ergonomics": {"type": "integer", "enum": [0, 1, 2]},
                },
                "required": ["actionability", "generality", "non_duplication", "safety", "skill_ergonomics"],
            },
            "gates": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "C1_actionable": {"type": "boolean"},
                    "C2_generic": {"type": "boolean"},
                    "C3_not_duplicate": {"type": "boolean"},
                    "C4_safe": {"type": "boolean"},
                    "C5_self_contained": {"type": "boolean"},
                },
                "required": ["C1_actionable", "C2_generic", "C3_not_duplicate", "C4_safe", "C5_self_contained"],
            },
            "verdict": {"type": "string", "enum": ["PROMOTE", "REVISE", "HUMAN_REVIEW", "REJECT"]},
            "rationale": {"type": "string", "description": "1-3 frases justificando o veredito."},
            "suggested_revisions": {"type": "string", "description": "O que melhorar (vazio se PROMOTE)."},
        },
        "required": ["scores", "gates", "verdict", "rationale", "suggested_revisions"],
    },
}


def _recompute_total(scores: dict) -> float:
    return round(sum(WEIGHTS[k] * scores.get(k, 0) for k in WEIGHTS), 3)


def _materials(rd, rec) -> str:
    rubric = (CURATOR / "rubrics" / "promotion.md").read_text(encoding="utf-8")
    state = read_json(rd / "run-state.json", default={})
    slug = state.get("slug", "")
    skill_md = (rd / "proposals" / slug / "SKILL.md").read_text(encoding="utf-8") if slug else ""
    dedup = read_json(rd / "reports" / "dedup-report.json", default={})
    triage = read_json(rd / "reports" / "triage.json", default={})
    dedup_brief = {"verdict": dedup.get("verdict"), "max_score": dedup.get("max_score"),
                   "closest": (dedup.get("top_overlaps") or [{}])[0]}
    return (
        f"# RUBRIC (siga à risca)\n{rubric}\n\n"
        f"# CONTRIBUIÇÃO — texto bruto\n{rec.get('raw_text', '')}\n\n"
        f"# SKILL.md RASCUNHADO\n{skill_md}\n\n"
        f"# DEDUP (determinístico)\n{json.dumps(dedup_brief, ensure_ascii=False)}\n\n"
        f"# TRIAGE (determinístico)\n{json.dumps({'has_secret': triage.get('has_secret'), 'too_short': triage.get('too_short')}, ensure_ascii=False)}\n\n"
        "# TAREFA\nVocê é o JUIZ (Opus). Pontue cada dimensão (0/1/2), avalie os 5 gates, e emita o "
        "veredito PELA RUBRIC via a ferramenta emit_verdict. Regras duras: se C3 (duplicado) ou C4 "
        "(segredo/inseguro) falharem, NÃO promova. Só PROMOTE com total ponderado >= 1.4 e dedup=pass. "
        "Na dúvida, HUMAN_REVIEW — nunca promova no escuro. Chame emit_verdict exatamente uma vez."
    )


def judge_via_opus(prompt: str) -> dict:
    """Returns the tool input dict, or raises. Import is lazy so missing SDK degrades cleanly."""
    import anthropic  # noqa: PLC0415

    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY
    resp = client.messages.create(
        model=JUDGE_MODEL,
        max_tokens=16000,
        thinking={"type": "adaptive"},
        output_config={"effort": "high"},
        tools=[VERDICT_TOOL],
        messages=[{"role": "user", "content": prompt}],
    )
    for block in resp.content:
        if getattr(block, "type", None) == "tool_use" and block.name == "emit_verdict":
            return dict(block.input)
    raise RuntimeError("o juiz não chamou emit_verdict")


def _apply_safety_override(result: dict, dedup_verdict: str) -> tuple[str, str]:
    total = _recompute_total(result["scores"])
    gates = result.get("gates", {})
    verdict = result["verdict"]
    if verdict == "PROMOTE":
        if total < PROMOTE_THRESHOLD:
            return "HUMAN_REVIEW", f"override: total {total} < {PROMOTE_THRESHOLD}"
        if not gates.get("C3_not_duplicate", True) or not gates.get("C4_safe", True):
            return "HUMAN_REVIEW", "override: gate duro C3/C4 falhou"
        if dedup_verdict == "likely_duplicate":
            return "HUMAN_REVIEW", "override: dedup=likely_duplicate"
    return verdict, ""


STATE_BY_VERDICT = {
    "PROMOTE": "judged_promote",
    "REVISE": "needs_human_review",
    "HUMAN_REVIEW": "needs_human_review",
    "REJECT": "rejected",
}


def _degrade(rd, cid, reason: str) -> dict:
    state = read_json(rd / "run-state.json", default={})
    state["final_verdict"] = "HUMAN_REVIEW"
    state["verdict_by"] = f"{JUDGE_MODEL} (indisponível)"
    state["judge_note"] = reason
    state["state"] = "needs_human_review"
    state.setdefault("state_history", []).append(
        {"state": "judge_unavailable", "at": now_iso(), "reason": reason})
    write_json(rd / "run-state.json", state)
    return state


def main() -> None:
    ap = argparse.ArgumentParser(description="Opus judge for a drafted contribution.")
    ap.add_argument("--id", help="contrib_id; default = first drafted run")
    args = ap.parse_args()

    inbox = read_jsonl(INBOX)
    target = None
    for rec in inbox:
        if args.id and rec.get("contrib_id") != args.id:
            continue
        if rec.get("last_status") == "drafted":
            target = rec
            break
    if target is None:
        print("nada para julgar (nenhuma contribuição em estado 'drafted'). Veja: python loop_status.py")
        return

    cid = target["contrib_id"]
    rd = run_dir(cid)
    prompt = _materials(rd, target)
    dedup_verdict = read_json(rd / "reports" / "dedup-report.json", default={}).get("verdict", "pass")

    try:
        result = judge_via_opus(prompt)
    except ModuleNotFoundError:
        state = _degrade(rd, cid, "SDK 'anthropic' não instalado (pip install anthropic)")
        _persist_status(inbox, cid, state["state"])
        print(f"[juiz indisponível] {state['judge_note']} → HUMAN_REVIEW")
        return
    except Exception as exc:  # noqa: BLE001 — API/auth/parse error must never auto-promote
        state = _degrade(rd, cid, f"falha ao chamar o juiz: {type(exc).__name__}: {exc}")
        _persist_status(inbox, cid, state["state"])
        print(f"[juiz indisponível] {state['judge_note']} → HUMAN_REVIEW")
        return

    total = _recompute_total(result["scores"])
    final_verdict, override = _apply_safety_override(result, dedup_verdict)
    next_status = STATE_BY_VERDICT.get(final_verdict, "needs_human_review")

    evaluation = {
        "contrib_id": cid,
        "judge_model": JUDGE_MODEL,
        "scores": result["scores"],
        "weighted_total_recomputed": total,
        "gates": result["gates"],
        "verdict_raw": result["verdict"],
        "verdict_final": final_verdict,
        "override": override,
        "rationale": result["rationale"],
        "suggested_revisions": result["suggested_revisions"],
        "judged_at": now_iso(),
    }
    write_json(rd / "reports" / "evaluation.json", evaluation)

    state = read_json(rd / "run-state.json", default={})
    state.update({
        "final_verdict": final_verdict,
        "verdict_by": JUDGE_MODEL,
        "weighted_total": total,
        "state": next_status,
        "judge_rationale": result["rationale"],
    })
    state.setdefault("state_history", []).append(
        {"state": f"judged:{final_verdict}", "at": now_iso(),
         "reason": (override or result["rationale"])[:160]})
    write_json(rd / "run-state.json", state)
    _persist_status(inbox, cid, next_status)

    print("-" * 64)
    print(f"contrib     : {cid}  \"{target.get('title','')}\"")
    print(f"scores      : {result['scores']}  (total ponderado = {total})")
    print(f"verdict      : {result['verdict']}" + (f"  ->  {final_verdict}  ({override})" if override else ""))
    print(f"proximo estado: {next_status}")
    if final_verdict == "PROMOTE":
        print(f"pronto para : python update_index.py --id {cid} --apply  &&  python open_pr.py --id {cid}")
    print("-" * 64)


def _persist_status(inbox: list[dict], cid: str, status: str) -> None:
    for rec in inbox:
        if rec["contrib_id"] == cid:
            rec["last_status"] = status
    write_jsonl(INBOX, inbox)


if __name__ == "__main__":
    main()
