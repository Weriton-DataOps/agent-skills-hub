# OverCore — Setup ponta a ponta

São **dois papéis**: o **usuário final** (instala o plugin e usa/contribui) e o
**mantenedor** (roda o curador que avalia as contribuições). Comece pelo plugin.

## 0. O plugin `/overcore` (usuário final)

Qualquer pessoa, em qualquer projeto no Claude Code:

```
/plugin marketplace add Weriton-DataOps/agent-skills-hub
/plugin install overcore@overcore-hub
```

Depois: `/overcore usar <tarefa>`, `/overcore contribuir <texto>`, `/overcore status`.
Requer o repo **público**; contribuir usa a conta do próprio usuário (`gh auth login`).

**Testar o plugin localmente (antes de publicar), como mantenedor:**
```
/plugin marketplace add C:\Users\wp.santos\Documents\agent-skills-hub
/plugin install overcore@overcore-hub
/reload-plugins
```
(Para o `usar` funcionar, o repo precisa estar no GitHub e público — ele busca as skills do raw.)

O restante deste guia é para o **mantenedor** (o curador que roda na sua máquina).

## 1. Pré-requisitos (mantenedor)

- **Python 3.11+** (o curador é stdlib-only).
- **`pip install anthropic`** — só para o juiz Opus (`judge.py`).
- **git** e, opcional, **`gh`** (GitHub CLI) autenticado (`gh auth login`).

## 2. Tokens e variáveis de ambiente

Ninguém recebe acesso de escrita ao git — quem escreve é **um token-robô**. Crie PATs
fine-grained (GitHub → Settings → Developer settings → Fine-grained tokens), escopados
**só** ao repo `Weriton-DataOps/agent-skills-hub`:

| Variável | Escopo do token | Usada por |
|---|---|---|
| `CURATOR_ISSUES_TOKEN` | **Issues: Read** (curador) / **Write** (contribuidor) | `ingest_issues.py`, `contribute.py` |
| `CURATOR_PR_TOKEN` | **Contents: Write** + **Pull requests: Write** | `open_pr.py --push` |
| `CURATOR_GITHUB_REPO` | — (valor: `Weriton-DataOps/agent-skills-hub`) | todos |
| `ANTHROPIC_API_KEY` | chave da Anthropic | `judge.py` (Opus 4.8) |

No Windows (persistente):
```powershell
setx CURATOR_ISSUES_TOKEN "github_pat_..."
setx CURATOR_PR_TOKEN     "github_pat_..."
setx CURATOR_GITHUB_REPO  "Weriton-DataOps/agent-skills-hub"
setx ANTHROPIC_API_KEY    "sk-ant-..."
```
(Abra um novo terminal depois do `setx`.)

## 3. Label no repo

Crie a label `contribution` (uma vez):
```
gh label create contribution --repo Weriton-DataOps/agent-skills-hub --color 0e8a16 --description "Contribuição bruta para o Curator"
```

## 4. Testar local (sem token, seguro)

```bash
python agents/curator/scripts/ingest_local.py --title "meu fix" --origin human --file meu.md
python agents/curator/scripts/run_cycle.py         # ciclo DRY: ingest -> draft -> judge -> (promote dry)
python agents/curator/scripts/loop_status.py
```

## 5. Rodar de verdade

Com os tokens + a chave definidos:
```bash
python agents/curator/scripts/run_cycle.py --live   # materializa skill + abre PR (merge continua humano)
```

## 6. Agendar (Windows Task Scheduler)

```powershell
# modo DRY (seguro) diário às 07:00:
.\agents\curator\orchestration\register-task.ps1

# modo real (abre PRs) às 06:30:
.\agents\curator\orchestration\register-task.ps1 -Time 06:30 -Live

Start-ScheduledTask -TaskName OverCore-Curator   # rodar na hora
```

## 7. Usar no VS Code

Na caixa do Claude:
- `/overcore usar <tarefa>` — descobre e aplica skills do hub.
- `/overcore contribuir <texto>` — registra um fix/atalho (vira skill após revisão).
- `/overcore status` — mostra a fila do curador.

## Fluxo completo

```
/overcore contribuir  ─┐
Pipeline Studio        ─┼─►  Issue (label: contribution)  ─►  run_cycle:  ingest → draft → judge(Opus) → PR  ─►  VOCÊ faz o merge
                        │                                                                                          │
                        └───────────────────────  re-distribui pros consumidores  ◄──────────────────────────────┘
```

Detalhes da arquitetura: [`ORQUESTRACAO.md`](ORQUESTRACAO.md) · intake: [`CONTRIBUTING-INTAKE.md`](CONTRIBUTING-INTAKE.md).
