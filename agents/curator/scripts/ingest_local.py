#!/usr/bin/env python3
"""Ingest a contribution from the LOCAL machine (offline demo path).

This simulates a GitHub Issue arriving, without needing a token — so the whole
loop can be tested end-to-end today. In production, ingest_issues.py pulls the
same records from GitHub Issues labelled `contribution`.

Usage:
  python ingest_local.py --title "..." --author "Weriton" --origin vscode-claude --file raw.md
  echo "texto..." | python ingest_local.py --title "..." --author "Weriton"
"""

from __future__ import annotations

import argparse
import sys

from loop_common import INBOX, append_jsonl, now_iso, read_jsonl, short_id


def main() -> None:
    ap = argparse.ArgumentParser(description="Ingest a raw-text contribution locally.")
    ap.add_argument("--title", required=True, help="short title of the contribution")
    ap.add_argument("--author", default="local-user", help="display name of the author")
    ap.add_argument("--login", default="", help="github login (optional)")
    ap.add_argument("--origin", default="human",
                    help="vscode-claude | pipeline-studio:<agent> | human")
    ap.add_argument("--tags", default="", help="comma-separated hint tags")
    ap.add_argument("--file", help="path to a file with the raw text; else reads stdin")
    args = ap.parse_args()

    if args.file:
        raw_text = open(args.file, encoding="utf-8").read()
    else:
        raw_text = sys.stdin.read()

    if not raw_text.strip():
        ap.error("raw text is empty (pass --file or pipe text via stdin)")

    submitted_at = now_iso()
    contrib_id = short_id("local", args.title, args.origin, submitted_at)
    rec = {
        "contrib_id": contrib_id,
        "source": "local",
        "issue_number": None,
        "issue_url": None,
        "title": args.title.strip(),
        "raw_text": raw_text.strip(),
        "author_login": args.login.strip(),
        "author_display": args.author.strip(),
        "origin": args.origin.strip(),
        "tags": [t.strip() for t in args.tags.split(",") if t.strip()],
        "submitted_at": submitted_at,
        "attempts": 0,
        "last_status": "ingested",
    }

    existing = {r.get("contrib_id") for r in read_jsonl(INBOX)}
    if contrib_id in existing:
        print(f"já existe no inbox: {contrib_id}")
        return
    append_jsonl(INBOX, rec)
    print(f"ingerido: {contrib_id}  \"{rec['title']}\"  (origin={rec['origin']})")
    print(f"inbox: {INBOX}")


if __name__ == "__main__":
    main()
