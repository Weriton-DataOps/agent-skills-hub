#!/usr/bin/env python3
"""Anti-duplication check against the indexed skills corpus.

Reuses the tokenizer/Jaccard approach of agents/researcher/scripts/novelty_check.py
but runs against docs/indices/skills_index.json (name + description). No LLM.

Verdict bands (threshold default 0.18, ×1.75 = likely-duplicate):
  score >= 0.315 -> likely_duplicate  (gate C3 fail -> REJECT with pointer)
  score >= 0.18  -> human_review
  else           -> pass
"""

from __future__ import annotations

import argparse
import json

from loop_common import jaccard, load_index, now_iso, tokens

DEFAULT_THRESHOLD = 0.18
DUP_MULTIPLIER = 1.75


def dedup(text: str, index: list[dict] | None = None, threshold: float = DEFAULT_THRESHOLD, top_n: int = 5) -> dict:
    index = index if index is not None else load_index()
    dup_threshold = round(threshold * DUP_MULTIPLIER, 4)
    query = tokens(text)

    scored = []
    for item in index:
        corpus = f"{item.get('name', '')} {item.get('description', '')}"
        score = jaccard(query, tokens(corpus))
        if score > 0:
            shared = sorted(query & tokens(corpus))
            scored.append((score, item, shared))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:top_n]
    max_score = round(top[0][0], 4) if top else 0.0

    if max_score >= dup_threshold:
        verdict = "likely_duplicate"
    elif max_score >= threshold:
        verdict = "human_review"
    else:
        verdict = "pass"

    return {
        "checked_at": now_iso(),
        "threshold": threshold,
        "duplicate_threshold": dup_threshold,
        "max_score": max_score,
        "verdict": verdict,
        "top_overlaps": [
            {
                "skill_id": item.get("id"),
                "path": item.get("path"),
                "score": round(score, 4),
                "shared_terms": shared[:12],
            }
            for score, item, shared in top
        ],
    }


def _cli() -> None:
    ap = argparse.ArgumentParser(description="Dedup a raw contribution against the skills index.")
    ap.add_argument("--text", help="raw text; if omitted reads stdin")
    ap.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    args = ap.parse_args()
    import sys
    text = args.text if args.text is not None else sys.stdin.read()
    print(json.dumps(dedup(text, threshold=args.threshold), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    _cli()
