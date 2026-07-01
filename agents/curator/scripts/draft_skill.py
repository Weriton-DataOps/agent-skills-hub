#!/usr/bin/env python3
"""Turn a raw-text contribution into a SKILL.md draft scaffold.

Deterministic scaffolding only: it extracts a name/slug/description and lays out
the canonical SKILL.md sections, carrying the credit watermark (origin/author/
contributed_via) into the frontmatter. The prose is a DRAFT — the Opus judge and
the human reviewer refine it before merge.
"""

from __future__ import annotations

import re

from loop_common import slugify, today

MAX_DESC = 160


def _first_sentence(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    m = re.split(r"(?<=[.!?])\s", text, maxsplit=1)
    return (m[0] if m else text)[:MAX_DESC].strip()


def _extract_steps(text: str) -> list[str]:
    steps = []
    for line in text.splitlines():
        s = line.strip()
        if re.match(r"^(\d+[.)]|[-*•])\s+", s):
            steps.append(re.sub(r"^(\d+[.)]|[-*•])\s+", "", s))
    return steps


def draft(rec: dict, triage_info: dict | None = None) -> dict:
    triage_info = triage_info or {}
    title = (rec.get("title") or "").strip()
    raw = rec.get("raw_text", "") or ""
    name = slugify(title or _first_sentence(raw))
    description = (title or _first_sentence(raw)).strip()
    if len(description) > MAX_DESC:
        description = description[: MAX_DESC - 1].rstrip() + "…"
    risk = triage_info.get("risk_hint", "unknown")

    origin = rec.get("origin", "human")
    author = rec.get("author_display") or rec.get("author_login") or "desconhecido"
    contributed_via = rec.get("issue_url") or f"local:{rec.get('contrib_id','')}"

    steps = _extract_steps(raw)
    steps_md = "\n".join(f"{i}. {s}" for i, s in enumerate(steps, 1)) if steps else \
        "1. _(rascunho — descrever o passo-a-passo a partir do texto bruto abaixo)_"

    tags = rec.get("tags") or []
    tags_md = ", ".join(f"`{t}`" for t in tags) if tags else "_(sem tags)_"

    frontmatter = (
        "---\n"
        f"name: {name}\n"
        f'description: "{description.replace(chr(34), chr(39))}"\n'
        f"risk: {risk}\n"
        "source: community\n"
        f'date_added: "{today()}"\n'
        f"origin: {origin}\n"
        f'author: "{author}"\n'
        f"contributed_via: {contributed_via}\n"
        "status: draft\n"
        "---\n"
    )

    body = f"""
> ⚠️ **RASCUNHO gerado pelo Curator** — aguardando julgamento (rubric) e revisão humana.
> Não é skill oficial até o merge do PR pelo dono.

# {name.replace('-', ' ').title()}

## Quando usar
{description}

Tags: {tags_md}

## Problema / Contexto
{raw.strip()}

## Passos
{steps_md}

## Armadilhas / O que evitar
- _(rascunho — o que deu errado antes, o que não fazer)_

## Crédito
- **Autor:** {author}
- **Origem:** `{origin}`
- **Via:** {contributed_via}
"""

    skill_md = frontmatter + body
    return {
        "slug": name,
        "name": name,
        "description": description,
        "risk": risk,
        "skill_md": skill_md,
    }
