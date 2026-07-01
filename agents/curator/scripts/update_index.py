#!/usr/bin/env python3
"""Materialize a promoted contribution into the real library.

Copies the drafted SKILL.md into skills/<slug>/ and inserts a matching entry into
docs/indices/skills_index.json, carrying the credit watermark (origin/author/
contributed_via). Default is --dry-run (writes only a preview + prints the entry);
--apply actually mutates skills/ and the index.

Idempotent: refuses to add a slug/id that already exists in the index.

Usage:
  python update_index.py --id <contrib_id>            # preview only
  python update_index.py --id <contrib_id> --apply    # write skill + index entry
"""

from __future__ import annotations

import argparse
import re
import shutil

from loop_common import (
    INBOX, INDEX_PATH, ROOT, ensure_dir, load_index, read_json, read_jsonl,
    run_dir, today, write_json,
)

SKILLS_DIR = ROOT / "skills"


def _parse_frontmatter(text: str) -> dict:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    fm: dict = {}
    if not m:
        return fm
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"')
    return fm


def _inbox_rec(cid: str) -> dict:
    for r in read_jsonl(INBOX):
        if r.get("contrib_id") == cid:
            return r
    return {}


def build_entry(state: dict, fm: dict, rec: dict) -> dict:
    slug = state["slug"]
    tags = rec.get("tags") or []
    category = tags[0] if tags else "community"
    origin = state.get("origin") or fm.get("origin") or "human"
    return {
        "id": slug,
        "path": f"skills/{slug}",
        "category": category,
        "name": slug,
        "description": fm.get("description", state.get("title", "")),
        "risk": fm.get("risk", "unknown"),
        "source": f"overcore:{origin}",
        "date_added": fm.get("date_added", today()),
        "plugin": {
            "targets": {"codex": "unknown", "claude": "supported"},
            "setup": {"type": "none", "summary": "", "docs": None},
            "reasons": [],
        },
        "origin": origin,
        "author": state.get("author") or fm.get("author") or "desconhecido",
        "contributed_via": fm.get("contributed_via", f"local:{state['contrib_id']}"),
    }


def _insert_sorted(index: list[dict], entry: dict) -> list[dict]:
    ids = [it.get("id", "") for it in index]
    pos = len(index)
    for i, existing in enumerate(ids):
        if existing > entry["id"]:
            pos = i
            break
    return index[:pos] + [entry] + index[pos:]


def main() -> None:
    ap = argparse.ArgumentParser(description="Materialize a promoted contribution into skills/ + index.")
    ap.add_argument("--id", required=True, help="contrib_id of the run to promote")
    ap.add_argument("--apply", action="store_true", help="actually write files (default: dry-run preview)")
    args = ap.parse_args()

    rd = run_dir(args.id)
    state = read_json(rd / "run-state.json", default={})
    if not state:
        print(f"run não encontrado: {rd}")
        return
    slug = state["slug"]
    skill_src = rd / "proposals" / slug / "SKILL.md"
    if not skill_src.exists():
        print(f"SKILL.md rascunhado não encontrado: {skill_src}")
        return

    skill_text = skill_src.read_text(encoding="utf-8")
    fm = _parse_frontmatter(skill_text)
    rec = _inbox_rec(args.id)
    entry = build_entry(state, fm, rec)

    index = load_index()
    if any(it.get("id") == slug for it in index):
        print(f"[idempotente] já existe uma skill com id '{slug}' no índice — nada a fazer.")
        return

    if not args.apply:
        write_json(rd / "proposals" / slug / "index-entry.json", entry)
        print("== PREVIEW (dry-run — nada foi escrito em skills/ ou no índice) ==")
        print(f"skill iria para : skills/{slug}/SKILL.md")
        print(f"índice: {len(index)} -> {len(index) + 1} entradas")
        print(f"entrada: id={entry['id']} category={entry['category']} risk={entry['risk']} source={entry['source']}")
        print(f"preview salvo em: {rd / 'proposals' / slug / 'index-entry.json'}")
        print("rode de novo com --apply para escrever de verdade.")
        return

    # apply: skill file
    dest = ensure_dir(SKILLS_DIR / slug) / "SKILL.md"
    shutil.copyfile(skill_src, dest)

    # apply: index (write with the same format the file already uses: ascii-escaped, indent=2)
    new_index = _insert_sorted(index, entry)
    import json
    INDEX_PATH.write_text(json.dumps(new_index, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")

    print("== APLICADO ==")
    print(f"skill escrita : {dest}")
    print(f"índice        : {len(index)} -> {len(new_index)} entradas (id={slug})")
    print("Revise no git; depois use open_pr.py para abrir o PR.")


if __name__ == "__main__":
    main()
