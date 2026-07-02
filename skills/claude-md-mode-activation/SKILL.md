---
name: claude-md-mode-activation
description: "Ao ligar um modo persistente via CLAUDE.md, auto-adote o comportamento na sessão atual E grave o bloco para as próximas — porque o CLAUDE.md só é carregado no boot da sessão."
risk: safe
source: overcore:contribution
date_added: "2026-07-01"
origin: vscode-claude
author: "Weriton-DataOps"
contributed_via: https://github.com/Weriton-DataOps/agent-skills-hub/issues/4
---

# Ativação de modo via CLAUDE.md

## Quando usar
Ao construir uma feature (slash command, skill) que **liga um modo persistente** gravando regras no
`CLAUDE.md` de um projeto — ex.: um "modo orquestrador", um perfil de agente, um conjunto de convenções.

## A pegadinha
O `CLAUDE.md` é lido pelo Claude Code **apenas no início da sessão**. Se o comando que ativa roda
**no meio da sessão** (a sessão já começou), o bloco recém-escrito **não entra no contexto do agente**
até um reload / nova sessão. Resultado: *"rodou uma vez → já vale"* é **falso** sem recarregar.

## O padrão (duas frentes)
A ativação deve fazer **as duas coisas**:

1. **Gravar o bloco no `CLAUDE.md`** → persiste para as **próximas** sessões (carrega no boot).
2. **Instruir o agente a adotar o comportamento IMEDIATAMENTE** na sessão atual → efeito sem reload.

Assim o efeito é **imediato E persistente**, sem exigir recarga manual.

## Notas de implementação
- **Marcadores** para remoção limpa e idempotência:
  ```
  <!-- X:START --> ... <!-- X:END -->
  ```
  Um "off" remove tudo entre os marcadores; a ativação não duplica se o marcador já existe.
- Ofereça um **desligar** explícito (ex.: `/x off`) que tira o bloco — não confie em "desabilitar o plugin",
  porque o `CLAUDE.md` é um arquivo à parte que sobrevive ao plugin.
- O modo é **por projeto** (cada pasta tem seu `CLAUDE.md`): ative uma vez por projeto.

## Armadilha a evitar
Achar que desligar/remover o plugin desativa o modo. Não desativa — a regra está no `CLAUDE.md` do projeto.
O desligamento tem que **editar o `CLAUDE.md`**.
