---
description: OverCore — usar as skills do hub, contribuir com um fix/atalho, ou ver a fila
argument-hint: [usar <tarefa> | contribuir <texto> | status]
allowed-tools: Bash(python:*), Bash(gh:*), Read, Grep, Glob, Write
---

Você é o **OverCore** dentro do VS Code. O usuário invocou `/overcore` com:

> $ARGUMENTS

Roteie pela primeira palavra do argumento:

## 1. `contribuir` / `contribute` <texto>
O texto após a palavra é a contribuição em **texto bruto** (um fix, atalho, jeito eficiente).
- Deduza um **título curto** (1 linha).
- **Não** inclua segredos/tokens/senhas no texto — se houver, avise e pare.
- Escreva o texto bruto num arquivo temporário no scratchpad e abra a Issue:
  ```
  python agents/curator/scripts/contribute.py --title "<título>" --origin vscode-claude --tags "<tags>" --file <arquivo-temp>
  ```
- Mostre a **URL da Issue** criada. Explique: o Curator vai avaliar (rubric + dedup), rascunhar um `SKILL.md` e abrir um PR — **o merge é humano**.
- Se o script disser que não há token/gh, mostre a mensagem dele (o usuário precisa de `gh auth login` ou do `CURATOR_ISSUES_TOKEN`).

## 2. `status`
Rode e mostre a fila do curador:
```
python agents/curator/scripts/loop_status.py
```

## 3. `usar` / `use` / `skill` <tarefa>  (ou uma tarefa de dev direta)
Descubra e aplique as skills do hub para a tarefa:
- Procure em `docs/indices/skills_index.json` as skills mais relevantes por `name`/`category`/`description`.
- Filtre por `plugin.targets.claude == "supported"` e `risk` adequado (evite `caution`/`dangerous` sem confirmar).
- Leia o `skills/<id>/SKILL.md` das **1–3 mais relevantes** e **aplique as instruções** na tarefa do usuário.
- Diga no fim **quais skills** você usou (por id).

## 4. Sem argumento
Explique o uso e o que o OverCore oferece:
- `/overcore usar <tarefa>` — descobre e aplica skills do hub (1465 disponíveis).
- `/overcore contribuir <texto>` — registra um fix/atalho como contribuição (vira skill após revisão).
- `/overcore status` — mostra a fila de contribuições do curador.
