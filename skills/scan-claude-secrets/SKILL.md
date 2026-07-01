---
name: scan-claude-secrets
description: "Audita os arquivos de config do Claude Code (settings.json / settings.local.json) atrás de tokens e senhas vazados na allowlist de permissões — um ponto cego que Gitleaks e Semgrep não cobrem."
risk: safe
source: overcore:safegate
date_added: "2026-07-01"
origin: safegate
---

# Scan Claude Secrets

## Quando usar
- Auditoria de segurança de uma máquina/projeto que usa Claude Code.
- Antes de tornar um repo público (checar se `.claude/` tem segredo).
- Como checagem periódica do SafeGate.

## O ponto cego
Quando você **aprova** um comando que tem uma credencial embutida (ex.:
`git remote set-url origin https://ghp_...@github.com/...`, `PGPASSWORD=... psql ...`),
o Claude Code **congela aquele comando** na lista `permissions.allow` do `settings.json`
pra não perguntar de novo. Com o tempo, esse arquivo vira um **depósito de segredos** —
e scanners tradicionais (Gitleaks, Semgrep, secret scanning do GitHub) **não olham pra lá**,
porque não é "código".

Arquivos afetados:
- `~/.claude/settings.json` e `~/.claude/settings.local.json` (global)
- `<projeto>/.claude/settings.json` e `settings.local.json` (por projeto)

## Como escanear (read-only)
```
python scripts/scan.py
```
Reporta cada achado **mascarado** (só o tipo: "token do GitHub", "senha", "connection
string"), **nunca o valor**. Padrões cobertos: tokens `ghp_/gho_/ghs_/github_pat_`,
`password=`, `PGPASSWORD`, `Authorization: token`, e connection strings `://user:senha@host`.

## Como remediar
```
python scripts/scan.py --fix     # remove as entradas (cria .bak)
```
Depois, **o passo que importa**: **ROTACIONE** os segredos expostos —
remover do arquivo **não invalida** o token/senha.

| Segredo | Onde rotacionar |
|---|---|
| Token GitHub | Settings → Developer settings → Tokens → revogar |
| Senha de banco | reset no provedor (Supabase) ou `ALTER USER ... PASSWORD` |
| Token de API/serviço | trocar no sistema de origem |

## Prevenção
- Nunca embuta credencial no comando; use variável de ambiente ou credential helper.
- Ative push protection / secret scanning no GitHub.
- Rode este scan periodicamente (o SafeGate pode chamá-lo).

## Gates (o que barrar)
- **Segredo em `permissions.allow`** → severidade **Alta**: remova + rotacione.
- **`.env` fora do `.gitignore`** num repo → severidade **Alta**.
- **Repo público com `.claude/` versionado** → conferir antes de publicar.
