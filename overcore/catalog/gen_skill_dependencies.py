#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador do arquivo DERIVADO `skill-dependencies.json`.

Fonte ÚNICA de verdade: o campo `requiredSubSkills` no frontmatter de
`skills/<id>/SKILL.md`. O processo canônico do Hub propaga esse campo para o
`skills_index.json`. Este gerador projeta as dependências para o catálogo e
grava o SHA-256 de cada SKILL.md, para que o validador detecte projeção
desatualizada e FALHE FECHADO.

Uso: python gen_skill_dependencies.py   (reescreve skill-dependencies.json)
     python gen_skill_dependencies.py --check   (não escreve; sai !=0 se divergir)
"""
import hashlib
import json
import os
import re
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
HUB_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SKILLS_DIR = os.path.join(HUB_ROOT, "skills")
OUT = os.path.join(HERE, "skill-dependencies.json")
SCHEMA_VERSION = "0.3.0"


def sha256_file(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def frontmatter_block(text):
    """Retorna o bloco de frontmatter (entre o 1º '---' e o próximo '---'), ou ''."""
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    return text[3:end] if end != -1 else ""


def read_required_subskills(path):
    """Extrai SÓ o campo estruturado `requiredSubSkills` do frontmatter, sem parsear o
    bloco inteiro (muitos SKILL.md da comunidade não são YAML estritamente válido). O
    valor é uma lista em sintaxe JSON/YAML-flow — parseada isoladamente."""
    with open(path, "r", encoding="utf-8") as fh:
        block = frontmatter_block(fh.read())
    if not block:
        return None
    for line in block.splitlines():
        m = re.match(r"\s*requiredSubSkills\s*:\s*(.+)$", line)
        if m:
            val = yaml.safe_load(m.group(1))
            if isinstance(val, list):
                return [str(x) for x in val]
    return None


def build_sources():
    sources = {}
    for sid in sorted(os.listdir(SKILLS_DIR)):
        md = os.path.join(SKILLS_DIR, sid, "SKILL.md")
        if not os.path.isfile(md):
            continue
        deps = read_required_subskills(md)
        if not deps:
            continue
        sources[sid] = {
            "skillMd": f"skills/{sid}/SKILL.md",
            "skillMdSha256": sha256_file(md),
            "requiredSubSkills": list(deps),
        }
    return sources


def render(sources):
    doc = {
        "schemaVersion": SCHEMA_VERSION,
        "generator": "gen_skill_dependencies.py",
        "note": (
            "AUTO-GERADO. Fonte única de verdade: campo `requiredSubSkills` no frontmatter de "
            "skills/<id>/SKILL.md (propagado ao skills_index.json pelo processo canônico do Hub). "
            "Regenere com `python gen_skill_dependencies.py`. O validador confere igualdade "
            "origem↔projeção e o SHA-256 de cada fonte; divergência falha fechado."
        ),
        "sources": sources,
    }
    return json.dumps(doc, ensure_ascii=False, indent=2) + "\n"


def main(argv):
    sources = build_sources()
    rendered = render(sources)
    if "--check" in argv:
        current = open(OUT, encoding="utf-8").read() if os.path.isfile(OUT) else ""
        if current != rendered:
            print("skill-dependencies.json DESATUALIZADO — rode gen_skill_dependencies.py")
            return 1
        print("skill-dependencies.json em dia")
        return 0
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(rendered)
    print(f"gerado: {OUT} ({len(sources)} skill(s) com dependências)")
    for sid, s in sources.items():
        print(f"  {sid}: {s['requiredSubSkills']} sha={s['skillMdSha256'][:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
