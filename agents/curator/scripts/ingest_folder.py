#!/usr/bin/env python3
"""Ingest contributions from a FOLDER in the repo (contributions/inbox/).

This is the drop-zone channel: an agent (Pipeline Studio, or Claude working in this
repo) writes a markdown file with a suggested improvement into contributions/inbox/.
The curator ingests those files into its queue, then triage/dedup/judge/promote run
as usual. Processed files are moved to contributions/processed/ so they aren't
re-ingested.

Complements ingest_issues.py (the GitHub Issues channel used by external plugin users
who don't have the repo checked out).

File format (flexible): the first non-empty line is the title; an optional
`origin:` / `tags:` line is parsed; everything is kept as the raw text.

Usage:
  python ingest_folder.py
"""

from __future__ import annotations

from pathlib import Path

from loop_common import INBOX, ROOT, append_jsonl, ensure_dir, now_iso, read_jsonl, short_id

CONTRIB = ROOT / "contributions"
CONTRIB_INBOX = CONTRIB / "inbox"
CONTRIB_PROCESSED = CONTRIB / "processed"
SKIP = {"README.md", ".gitkeep"}


def _parse(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    title = next((l.strip().lstrip("# ").strip() for l in lines if l.strip()), path.stem)
    origin, tags = "agent", []
    for line in lines:
        low = line.lower().strip()
        if low.startswith("origin:"):
            origin = line.split(":", 1)[1].strip() or origin
        elif low.startswith("tags:"):
            tags = [t.strip() for t in line.split(":", 1)[1].split(",") if t.strip()]
    return {"title": title[:120], "raw_text": text.strip(), "origin": origin, "tags": tags}


def main() -> None:
    if not CONTRIB_INBOX.exists():
        print(f"pasta de inbox não existe ainda: {CONTRIB_INBOX}")
        return

    files = [p for p in sorted(CONTRIB_INBOX.iterdir())
             if p.is_file() and p.suffix.lower() == ".md" and p.name not in SKIP]
    if not files:
        print(f"[ingest_folder] nenhuma sugestão nova em {CONTRIB_INBOX}")
        return

    existing = {r.get("contrib_id") for r in read_jsonl(INBOX)}
    ensure_dir(CONTRIB_PROCESSED)
    added = 0
    for path in files:
        meta = _parse(path)
        contrib_id = short_id("folder", path.name, meta["raw_text"][:200])
        if contrib_id not in existing:
            append_jsonl(INBOX, {
                "contrib_id": contrib_id,
                "source": "folder",
                "issue_number": None,
                "issue_url": None,
                "title": meta["title"],
                "raw_text": meta["raw_text"],
                "author_login": "",
                "author_display": meta["origin"],
                "origin": meta["origin"],
                "tags": meta["tags"],
                "submitted_at": now_iso(),
                "attempts": 0,
                "last_status": "ingested",
            })
            existing.add(contrib_id)
            added += 1
        # move para processed (mesmo se duplicado, pra limpar a inbox)
        dest = CONTRIB_PROCESSED / path.name
        if dest.exists():
            dest = CONTRIB_PROCESSED / f"{path.stem}-{contrib_id}{path.suffix}"
        path.replace(dest)

    print(f"[ingest_folder] {added} sugestão(ões) da pasta → {INBOX} (arquivos movidos p/ contributions/processed/)")


if __name__ == "__main__":
    main()
