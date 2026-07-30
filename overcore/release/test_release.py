#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testes do release/manifesto do Overcore (PRB-016). Sai != 0 em qualquer falha."""
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
import gen_release as G

BAD_PATH = re.compile(r"(^/)|(^[a-zA-Z]:)|(^\\\\)|(\.\.)|(\.git)|(\\)")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    fail = 0

    def check(cond, msg):
        nonlocal fail
        print(("  OK  " if cond else "  ERRO ") + msg)
        if not cond:
            fail += 1

    # 1) --check determinístico (em dia após gerar)
    check(G.main(["--check"]) == 0, "1) release em dia (determinístico)")

    manifest = json.load(open(os.path.join(HERE, "manifest.json"), encoding="utf-8"))

    # 2) manifesto sem commit autorreferente e sem auto-hash
    check("commit" not in manifest, "2a) manifesto não tem campo 'commit'")
    check("manifest.json" not in manifest.get("checksums", {}), "2b) manifesto não hasheia a si mesmo")

    # 3) executável vazio
    check(manifest.get("executable") == [], "3) conteúdo executável vazio")

    # 4) todo declarativo existe, tem checksum e o checksum bate
    decls = manifest.get("declarative", [])
    checks = manifest.get("checksums", {})
    ok_all = True
    for rel in decls:
        full = os.path.join(HERE, rel.replace("/", os.sep))
        if not os.path.isfile(full):
            print(f"     faltando: {rel}"); ok_all = False; continue
        if rel not in checks:
            print(f"     sem checksum: {rel}"); ok_all = False; continue
        if sha(open(full, "rb").read()) != checks[rel]:
            print(f"     checksum difere: {rel}"); ok_all = False
    check(ok_all, "4) todos os declarativos existem com checksum correto")

    # 5) nenhum arquivo consumido fora do declarativo (exceto manifesto e .py)
    on_disk = set()
    for root, dirs, fs in os.walk(HERE):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for fn in fs:
            # Excluir o manifesto e arquivos NÃO-payload (docs/tooling/config do Git):
            # .gitattributes fixa LF para os checksums baterem no Git — não é conteúdo do release.
            if fn.endswith((".py", ".pyc")) or fn in ("manifest.json", "README.md", ".gitattributes"):
                continue
            on_disk.add(os.path.relpath(os.path.join(root, fn), HERE).replace("\\", "/"))
    check(on_disk == set(decls), f"5) arquivos em disco == declarativo (extra: {on_disk - set(decls)})")

    # 6) paths seguros
    bad = [p for p in decls if BAD_PATH.search(p)]
    check(not bad, f"6) caminhos seguros (ruins: {bad})")

    # 7) skills referenciadas pelo catálogo têm SKILL.md no snapshot
    cat = json.load(open(os.path.join(HERE, "catalog.json"), encoding="utf-8"))
    ref = G.referenced_skills(cat)
    missing = [s for s in ref if f"skills/{s}/SKILL.md" not in decls]
    check(not missing, f"7) todas as skills referenciadas presentes (faltam: {missing})")

    # 8) catálogo do release PROMOVIDO (nenhuma entrada draft)
    drafts = [e["id"] for e in cat["agents"] if e.get("status") == "draft"]
    check(not drafts, f"8) catálogo do release promovido a active (ainda draft: {drafts})")

    # 9) skills-meta cobre as referenciadas
    meta = json.load(open(os.path.join(HERE, "skills-meta.json"), encoding="utf-8"))
    check(set(meta.keys()) == ref, "9) skills-meta cobre exatamente as skills referenciadas")

    print("\nRELEASE:", "TUDO VERDE" if fail == 0 else f"{fail} FALHA(S)")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
