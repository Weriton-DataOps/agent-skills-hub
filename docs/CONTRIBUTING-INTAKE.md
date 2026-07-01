# OverCore — Contrato de Intake: como uma contribuição entra

> Este doc define **como** fixes, atalhos e jeitos eficientes viram candidatos a
> skill no **OverCore** — sem ninguém tocar no git.

## Princípio

**Ninguém recebe acesso de escrita ao repo.** Quem escreve é **um único token-robô**.
As pessoas/agentes se autenticam no *app/plugin*, nunca no *git*. Contribuição = **texto bruto**.

```
Pipeline Studio (agente)  ─┐
VS Code "/" (usuário)      ─┼─►  GitHub Issue (label: contribution)  ─►  Curator (sua máquina)  ─►  PR  ─►  você faz merge
qualquer contribuidor      ─┘        (token-robô Issues:write)              (token Issues:read)
```

## Canal: GitHub Issues (Opção A — zero infra)

A "caixa de entrada" são as próprias **Issues** com a label `contribution`. O formulário
está em [`.github/ISSUE_TEMPLATE/contribution.yml`](../.github/ISSUE_TEMPLATE/contribution.yml).

### Campos do formulário → registro do inbox

| Campo do formulário | Vira no `inbox.jsonl` |
|---|---|
| Título `[contrib] ...` | `title` |
| Texto bruto | `raw_text` |
| Origem (dropdown) | `origin` (`vscode-claude` \| `pipeline-studio:<agent>` \| `human`) |
| Tags | `tags[]` |
| Autor da Issue | `author_login` / `author_display` (marca d'água de crédito) |
| Nº e URL da Issue | `issue_number` / `issue_url` (`contributed_via`) |

## Como cada consumidor publica (sem git)

### VS Code "/"
Uma skill/comando `/contribuir` monta o texto e **abre a Issue via API** do GitHub
usando um **token fine-grained compartilhado, escopo `Issues: write` apenas** naquele repo.
Pior caso de vazamento desse token: alguém abre Issue de spam — **não lê código, não dá push.**

### Pipeline Studio (Agent-SDK)
Quando um agente resolve um bug ou acha um fluxo eficiente, ele chama o mesmo endpoint de
Issue (mesmo token-robô), com `origin: pipeline-studio:<agent-id>`.

## O que o Curator faz com o texto bruto

Ver [`agents/curator/README.md`](../agents/curator/README.md). Resumo:
`ingest → triage (segredo/curto) → dedup (vs 1465) → draft SKILL.md → abre PR → você faz merge`.

## Tokens (resumo de segurança)

| Ator | Escopo do token | Pode |
|---|---|---|
| Contribuidor (VS Code / Pipeline) | `Issues: write` | só abrir Issue |
| Curator (sua máquina) — ingest | `Issues: read` | ler as Issues |
| Curator (sua máquina) — PR | `Pull requests: write`, `Contents: write` (branch) | abrir PR em branch `curator/*` |
| **Merge** | — | **só você, no GitHub** |

## Evolução (Opção B, depois)

Trocar o canal por um endpoint na Vercel que recebe `POST {texto, autor, origem}` e abre a
Issue/commita — aí o token fica **no servidor** e nunca sai. O contrato acima não muda.
