# ◆ OverCore · Monitor

Painel de monitoramento **em tempo real, no terminal**, para acompanhar tudo que o
OverCore (e qualquer sessão do Claude Code) está executando: agentes/subagentes, em
quais projetos, quais comandos/skills, tempo, tokens, custo, ferramenta atual e logs.

Rastreia **tudo**; o que é do **OverCore ganha destaque** (losango `◆` magenta, borda
reforçada, tag `OVERCORE`). O resto aparece neutro.

Feito com **Rich** — bordas elegantes, cores, barras animadas, spinners, sem piscar.

---

## Instalar

```bash
pip install rich          # obrigatório
pip install psutil        # opcional — CPU/memória reais
```

## Ver funcionando já (demo)

```bash
python overcore_monitor.py --demo
```

Sobe uma sessão simulada do OverCore (Router, Atelier, SafeGate, Researcher…) misturada
com agentes "normais" do Claude Code, pra você ver o painel vivo. `Ctrl+C` sai.

> Teste rápido sem terminal interativo: `python overcore_monitor.py --demo --snapshot`
> (renderiza 1 quadro e sai).

## Ao vivo (dados reais)

```bash
python overcore_monitor.py --events eventos.jsonl
```

O painel faz *tail* desse JSONL. Quem escreve nele é o **hook** (abaixo).

---

## Plugar nos hooks do Claude Code (dados reais)

O `hook.py` recebe o evento do Claude Code no stdin e **anexa uma linha** ao
`eventos.jsonl`. Registre-o no seu `settings.json` (global ou do projeto):

```json
{
  "hooks": {
    "SessionStart":     [{ "hooks": [{ "type": "command", "command": "python \"C:\\Users\\wp.santos\\Documents\\agent-skills-hub\\overcore-monitor\\hook.py\"" }] }],
    "UserPromptSubmit": [{ "hooks": [{ "type": "command", "command": "python \"C:\\Users\\wp.santos\\Documents\\agent-skills-hub\\overcore-monitor\\hook.py\"" }] }],
    "PreToolUse":       [{ "matcher": "*", "hooks": [{ "type": "command", "command": "python \"C:\\Users\\wp.santos\\Documents\\agent-skills-hub\\overcore-monitor\\hook.py\"" }] }],
    "PostToolUse":      [{ "matcher": "*", "hooks": [{ "type": "command", "command": "python \"C:\\Users\\wp.santos\\Documents\\agent-skills-hub\\overcore-monitor\\hook.py\"" }] }],
    "SubagentStop":     [{ "hooks": [{ "type": "command", "command": "python \"C:\\Users\\wp.santos\\Documents\\agent-skills-hub\\overcore-monitor\\hook.py\"" }] }],
    "Stop":             [{ "hooks": [{ "type": "command", "command": "python \"C:\\Users\\wp.santos\\Documents\\agent-skills-hub\\overcore-monitor\\hook.py\"" }] }]
  }
}
```

Depois, em **dois terminais**: um roda o Claude Code normalmente; o outro roda
`python overcore_monitor.py --events "C:\...\overcore-monitor\eventos.jsonl"`.

- O caminho do log pode ser trocado com a env `OVERCORE_MONITOR_LOG`.
- O hook **nunca quebra a sessão** — erro sai silencioso com código 0.

---

## Esquema de evento (JSONL)

Uma linha = um evento. Campos por tipo:

| type | campos | efeito no painel |
|---|---|---|
| `agent_start` | `id, agent, project, skill, model, steps, parent, overcore` | cria/abre o card |
| `progress` | `id, step, steps` | barra de progresso |
| `tool` | `id, tool, message, status` | ferramenta atual + log + timeline |
| `tokens` | `id, in, out, calls, dt, model` | tokens/custo/tempo de IA |
| `api` | `id, dt, message` | tempo em chamadas externas |
| `log` | `id, message` | última atividade + log |
| `agent_done` | `id, status` | fecha o card (✅/❌) |
| `error` | `id, message` | marca erro |

`overcore: true` força o destaque; se omitido, o painel detecta pelos verbos
(`/atelier`, `/safegate`, …) e pelo roster.

---

## O que já entrega × o que é da próxima volta

**Já:** status (⏳🚀⚙️🔄✅❌⏸️), tempo, ETA, barra (determinada e indeterminada),
etapa X/Y, ferramenta atual, última atividade, logs, colunas por projeto, timeline ao
vivo, resumo executivo, custo estimado, CPU/mem, tempo médio, ranking dos mais lentos,
tempo em IA × externo, contadores de tokens/chamadas — **sem piscar**.

**Próxima volta (se quiser):**
- **Tokens/custo reais por turno** — os hooks de tool não expõem uso de tokens; a fonte
  precisa é o **transcript** (`transcript_path`) do Claude Code. Um leitor de transcript
  enriquece tokens/custo com precisão. Hoje, no modo `--events`, tokens vêm do que o hook
  conseguir; no `--demo` são simulados.
- **Expandir um agente pra logs completos** (interativo, com teclado/mouse) — melhor em
  **Textual** (mesma família do Rich). Este v1 usa Rich Live (leitura, não interação).
- **Preços** editáveis no topo do `overcore_monitor.py` (`PRICES`) — confira as tarifas
  atuais da Anthropic/OpenAI.

---

`python overcore_monitor.py --help` lista as opções.
