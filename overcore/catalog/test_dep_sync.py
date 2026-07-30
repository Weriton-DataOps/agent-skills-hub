#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de SINCRONIZAÇÃO de dependências (PRB-017A — pendência 2).

Prova que:
  A) o Hub real está em sincronia (origem frontmatter ↔ índice ↔ projeção derivada);
  B) alterar a dependência NA ORIGEM (frontmatter) deixa a projeção DESATUALIZADA e o
     validador a REJEITA (hash + conteúdo divergem) — falha fechada;
  C) falta de propagação para o índice também é rejeitada.

Sai != 0 se qualquer expectativa falhar.
"""
import os
import shutil
import sys
import tempfile

import validate_catalog as V


def real_frontmatter_and_hash():
    md = os.path.join(V.SKILLS_DIR, "acceptance-orchestrator", "SKILL.md")
    return V.read_required_subskills(md), V.sha256_file(md)


def make_temp_skill(modified_deps):
    """Copia o SKILL.md real do acceptance-orchestrator para um skills_dir temporário,
    trocando a linha requiredSubSkills — conteúdo (e portanto hash) mudam."""
    src = os.path.join(V.SKILLS_DIR, "acceptance-orchestrator", "SKILL.md")
    text = open(src, encoding="utf-8").read()
    import re
    new_line = 'requiredSubSkills: ' + str(modified_deps).replace("'", '"')
    text2 = re.sub(r"requiredSubSkills\s*:\s*.+", new_line, text, count=1)
    tmp = tempfile.mkdtemp(prefix="depsync-")
    d = os.path.join(tmp, "skills", "acceptance-orchestrator")
    os.makedirs(d)
    open(os.path.join(d, "SKILL.md"), "w", encoding="utf-8", newline="\n").write(text2)
    return tmp


def main():
    failures = 0

    def check(cond, msg):
        nonlocal failures
        print(("  OK  " if cond else "  ERRO ") + msg)
        if not cond:
            failures += 1

    index = V.load_skill_index()
    deps_doc = V.load_skill_deps_doc()

    # A) Hub real em sincronia.
    errs = []
    V.check_dep_sync(V.SKILLS_DIR, index, deps_doc, errs)
    check(errs == [], f"A) Hub real em sincronia (esperado 0 erros, obtido {len(errs)}: {errs[:2]})")

    # B) Origem alterada => projeção (antiga) desatualizada => rejeitada.
    new_deps = ["create-issue-gate", "closed-loop-delivery", "verification-before-completion", "code-review-checklist"]
    tmp = make_temp_skill(new_deps)
    try:
        # índice acompanha a nova origem (isola a falha na PROJEÇÃO desatualizada)
        idx2 = dict(index)
        idx2["acceptance-orchestrator"] = dict(index["acceptance-orchestrator"])
        idx2["acceptance-orchestrator"]["requiredSubSkills"] = new_deps
        errs_b = []
        V.check_dep_sync(os.path.join(tmp, "skills"), idx2, deps_doc, errs_b)
        rejected = any("acceptance-orchestrator" in e and ("DESATUALIZADA" in e or "projeção != origem" in e) for e in errs_b)
        check(rejected, f"B) projeção desatualizada REJEITADA (erros: {errs_b})")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # C) Falta de propagação para o índice => rejeitada.
    idx3 = dict(index)
    idx3["acceptance-orchestrator"] = {k: v for k, v in index["acceptance-orchestrator"].items() if k != "requiredSubSkills"}
    errs_c = []
    V.check_dep_sync(V.SKILLS_DIR, idx3, deps_doc, errs_c)
    check(any("propagação" in e or "índice" in e for e in errs_c), f"C) índice sem propagação REJEITADO (erros: {errs_c})")

    print("\nDEP-SYNC:", "TUDO VERDE" if failures == 0 else f"{failures} FALHA(S)")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
