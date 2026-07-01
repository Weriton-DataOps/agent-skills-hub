#!/usr/bin/env python3
"""Show the curator queue and per-run state at a glance."""

from __future__ import annotations

from collections import Counter

from loop_common import INBOX, RUNS, read_json, read_jsonl


def main() -> None:
    inbox = read_jsonl(INBOX)
    print(f"# inbox: {INBOX}")
    if not inbox:
        print("  (vazio)")
    else:
        by_status = Counter(r.get("last_status", "ingested") for r in inbox)
        for status, n in sorted(by_status.items()):
            print(f"  {status:<20} {n}")
        print()
        for r in inbox:
            print(f"  - {r['contrib_id']}  [{r.get('last_status','ingested'):<18}]  \"{r.get('title','')[:60]}\"")

    print(f"\n# runs: {RUNS}")
    if not RUNS.exists():
        print("  (nenhum run ainda)")
        return
    for rd in sorted(RUNS.iterdir()):
        st = read_json(rd / "run-state.json", default={})
        if st:
            print(f"  - {rd.name}  state={st.get('state'):<18} pre_verdict={st.get('pre_verdict')}  skill={st.get('slug')}")


if __name__ == "__main__":
    main()
