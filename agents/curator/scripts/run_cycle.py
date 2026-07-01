#!/usr/bin/env python3
"""Run one full curator cycle: ingest -> draft -> judge -> promote.

Default is DRY (no --apply on the index, no --push on the PR) so it's safe to schedule
and inspect. Pass --live to actually materialize skills and open PRs. Merge is always human.

  ingest_issues  -> drena loop_step (todas as pendentes)
                 -> drena judge (todas as drafted)
                 -> para cada 'judged_promote': update_index (--apply se --live) + open_pr (--push se --live)

Usage:
  python run_cycle.py            # ciclo em modo dry (inspeciona, não escreve/empurra)
  python run_cycle.py --live     # ciclo real (materializa skill + abre PR)
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from loop_common import RUNS, ROOT, read_json

SCRIPTS = Path(__file__).resolve().parent
MAX_ITERS = 500  # backstop contra loop infinito


def run(script: str, *args: str) -> str:
    proc = subprocess.run([sys.executable, str(SCRIPTS / script), *args],
                          cwd=ROOT, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    out = (proc.stdout or "") + (proc.stderr or "")
    print(out.rstrip())
    return out


def drain(script: str, stop_marker: str) -> None:
    for _ in range(MAX_ITERS):
        out = run(script)
        if stop_marker in out:
            break


def promote_ready(live: bool) -> None:
    if not RUNS.exists():
        return
    for rd in sorted(RUNS.iterdir()):
        st = read_json(rd / "run-state.json", default={})
        if st.get("state") != "judged_promote":
            continue
        cid = st.get("contrib_id", rd.name)
        print(f"\n>> promovendo {cid} ({st.get('slug')})")
        run("update_index.py", "--id", cid, *(["--apply"] if live else []))
        run("open_pr.py", "--id", cid, *(["--push"] if live else []))


def main() -> None:
    ap = argparse.ArgumentParser(description="Um ciclo completo do curador.")
    ap.add_argument("--live", action="store_true", help="materializa skill (--apply) e abre PR (--push)")
    args = ap.parse_args()

    print("== 1) INGEST ==")
    run("ingest_folder.py")            # pasta contributions/inbox/ (agentes com o repo)
    run("ingest_issues.py")            # GitHub Issues (usuarios do plugin, se houver token)

    print("\n== 2) DRAFT (drena loop_step) ==")
    drain("loop_step.py", "nada pendente")

    print("\n== 3) JUDGE (drena judge — Opus, se houver SDK+chave) ==")
    drain("judge.py", "nada para julgar")

    print(f"\n== 4) PROMOTE ({'LIVE' if args.live else 'DRY'}) ==")
    promote_ready(args.live)

    print("\n== FIM DO CICLO ==")
    run("loop_status.py")


if __name__ == "__main__":
    main()
