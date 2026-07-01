#!/usr/bin/env python3
"""Escaneia os arquivos de config do Claude Code atrás de segredo vazado.

Ponto cego: quando você aprova um comando com credencial embutida, o Claude Code
congela aquele comando na allowlist de permissions. Scanners tradicionais (Gitleaks,
Semgrep) não olham esse arquivo — ele não é "codigo".

Read-only por padrao (so reporta, mascarado, sem vazar o valor). --fix remove as
entradas com backup. NUNCA imprime o segredo em si.

Uso:
  python scan.py            # audita e reporta (nao altera nada)
  python scan.py --fix      # remove as entradas (cria .bak). Depois ROTACIONE os segredos.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

TARGETS = [
    Path.home() / ".claude" / "settings.json",
    Path.home() / ".claude" / "settings.local.json",
    Path.cwd() / ".claude" / "settings.json",
    Path.cwd() / ".claude" / "settings.local.json",
]

SECRET = re.compile(
    r"gh[opsu]_[A-Za-z0-9]{16,}|github_pat_[A-Za-z0-9_]{20,}"
    r"|password\s*=|PGPASSWORD|Authorization:\s*token"
    r"|://[^\s:/@]+:[^\s@/]+@",
    re.IGNORECASE,
)


def kind(s: str) -> str:
    if re.search(r"gh[opsu]_|github_pat_", s):
        return "token do GitHub"
    if re.search(r"password\s*=|PGPASSWORD", s, re.I):
        return "senha (password=)"
    if re.search(r"Authorization:\s*token", s, re.I):
        return "token em header"
    if re.search(r"://[^\s:/@]+:[^\s@/]+@", s):
        return "connection string com credencial"
    return "segredo"


def scan_file(p: Path, fix: bool) -> tuple[int, int]:
    if not p.exists():
        return 0, 0
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return 0, 0
    perm = d.get("permissions", {})
    found = removed = 0
    for key in ("allow", "deny", "ask"):
        arr = perm.get(key)
        if not isinstance(arr, list):
            continue
        hits = [x for x in arr if isinstance(x, str) and SECRET.search(x)]
        for h in hits:
            print(f"  [{p}] permissions.{key}: {kind(h)}")
            found += 1
        if fix and hits:
            perm[key] = [x for x in arr if not (isinstance(x, str) and SECRET.search(x))]
            removed += len(hits)
    if fix and removed:
        shutil.copyfile(str(p), str(p) + ".bak")
        d["permissions"] = perm
        p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return found, removed


def main() -> None:
    ap = argparse.ArgumentParser(description="Scanner de segredos nos configs do Claude Code.")
    ap.add_argument("--fix", action="store_true", help="remove as entradas com segredo (cria .bak)")
    args = ap.parse_args()

    total_found = total_removed = 0
    for p in TARGETS:
        f, r = scan_file(p, args.fix)
        total_found += f
        total_removed += r

    print(f"\nsegredos encontrados: {total_found}")
    if args.fix:
        print(f"removidos: {total_removed} (backup .bak criado)")
        print("IMPORTANTE: remover != revogar. ROTACIONE os tokens/senhas expostos.")
    elif total_found:
        print("rode com --fix para remover. Depois ROTACIONE os segredos (remover != revogar).")
    else:
        print("nenhum segredo nos configs do Claude Code.")


if __name__ == "__main__":
    main()
