#!/usr/bin/env python3
"""Filtra o índice remoto do OverCore por uma busca — leve, cross-platform, sem arquivo temp.

Empacotado com o plugin: o `/overcore usar` chama este script em vez de baixar o índice
inteiro (1473 entradas) pro contexto. Imprime só as candidatas relevantes.

Uso: python find_skills.py <termos da tarefa>
"""

from __future__ import annotations

import json
import sys
import urllib.request

INDEX = "https://raw.githubusercontent.com/Weriton-DataOps/agent-skills-hub/main/docs/indices/skills_index.json"


def main() -> None:
    terms = [w for w in " ".join(sys.argv[1:]).lower().replace(",", " ").split() if len(w) > 2]
    if not terms:
        print("uso: find_skills.py <termos da tarefa>")
        return
    try:
        with urllib.request.urlopen(INDEX, timeout=20) as r:
            idx = json.load(r)
    except Exception as exc:  # noqa: BLE001
        print(f"erro ao baixar o indice: {exc}")
        return

    scored = []
    for x in idx:
        if x.get("plugin", {}).get("targets", {}).get("claude") != "supported":
            continue
        if x.get("risk") in ("dangerous",):
            continue
        name = x.get("name", "").lower()
        cat = x.get("category", "").lower()
        desc = x.get("description", "").lower()
        # nome pesa muito mais que descricao (evita 'deploy' casar com tudo)
        score = 0
        for t in terms:
            if t in name:
                score += 3
            if t in cat:
                score += 2
            if t in desc:
                score += 1
        if score:
            scored.append((score, x))

    scored.sort(key=lambda s: (-s[0], s[1].get("id", "")))
    if not scored:
        print("nenhuma skill bateu com a busca - refine os termos.")
        return
    print(f"# {len(scored)} candidatas (top 12) - escolha 1-3 e baixe o SKILL.md:")
    for score, x in scored[:12]:
        print(f"[{score}] {x['id']} :: {x.get('description','')[:85]}")


if __name__ == "__main__":
    main()
