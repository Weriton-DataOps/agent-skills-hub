#!/usr/bin/env python3
"""Cheap deterministic triage of a raw contribution.

Runs BEFORE any LLM judge. It cannot PROMOTE anything on its own — it can only
flag a contribution for HUMAN_REVIEW (secrets / too short) so cheap checks never
let unsafe content through. Mirrors the "gates before judge" rule of the design.
"""

from __future__ import annotations

import argparse
import json
import re

from loop_common import now_iso

# Patterns that suggest a secret leaked into the raw text (gate C4 — Seguro).
SECRET_PATTERNS = [
    ("aws_access_key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("private_key_block", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("bearer_token", re.compile(r"(?i)bearer\s+[A-Za-z0-9\-\._~\+\/]{20,}")),
    ("generic_api_key", re.compile(r"(?i)(api[_-]?key|secret|passwd|password|token)\s*[:=]\s*['\"]?[A-Za-z0-9\-_]{12,}")),
    ("connection_string", re.compile(r"(?i)(postgres|mysql|mongodb(?:\+srv)?|redis)://[^\s]+:[^\s]+@")),
    ("slack_token", re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}")),
]

MIN_CHARS = 120  # gate C5 — Auto-contido


def triage(rec: dict) -> dict:
    text = rec.get("raw_text", "") or ""
    char_len = len(text.strip())
    word_len = len(text.split())

    secret_hits = []
    for name, pat in SECRET_PATTERNS:
        m = pat.search(text)
        if m:
            sample = m.group(0)
            secret_hits.append({"pattern": name, "sample": sample[:6] + "…(redacted)"})

    too_short = char_len < MIN_CHARS
    has_secret = bool(secret_hits)

    notes = []
    if too_short:
        notes.append(f"texto curto ({char_len} chars < {MIN_CHARS}) — pode faltar contexto (gate C5).")
    if has_secret:
        notes.append("possível segredo detectado no texto — precisa sanitização (gate C4).")

    return {
        "triaged_at": now_iso(),
        "char_len": char_len,
        "word_len": word_len,
        "too_short": too_short,
        "has_secret": has_secret,
        "secret_hits": secret_hits,
        "risk_hint": "caution" if has_secret else "safe",
        "notes": notes,
    }


def _cli() -> None:
    ap = argparse.ArgumentParser(description="Triage a raw contribution from stdin/--text.")
    ap.add_argument("--text", help="raw text; if omitted, reads stdin")
    args = ap.parse_args()
    import sys
    text = args.text if args.text is not None else sys.stdin.read()
    print(json.dumps(triage({"raw_text": text}), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    _cli()
