#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OverCore Monitor · hook — emite eventos do Claude Code para o painel.

Registre no settings.json do Claude Code (ver README). Recebe o JSON do hook no
stdin, extrai o que interessa e ANEXA uma linha ao JSONL que o monitor le (--events).

Rastreia TUDO (qualquer sessao/tool/skill). Marca overcore=true quando detecta OverCore.
NUNCA quebra a sessao: qualquer erro sai silencioso com codigo 0.

Log padrao: eventos.jsonl ao lado deste arquivo (ou env OVERCORE_MONITOR_LOG).
"""
import sys
import os
import json
import time

LOG = os.environ.get(
    "OVERCORE_MONITOR_LOG",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "eventos.jsonl"),
)

OVERCORE_VERBS = (
    "/overcore", "/atelier", "/croqui", "/refinar", "/varrer", "/tipografar", "/cor",
    "/animar", "/polir", "/criticar", "/endurecer", "/embarcar", "/impactar", "/adaptar",
    "/artesao", "/cristalizar", "/safegate", "/validar", "/planejar",
)


def is_overcore(text: str) -> bool:
    t = (text or "").lower().strip()
    return any(t == v or t.startswith(v + " ") or t.startswith(v) for v in OVERCORE_VERBS)


def emit(ev: dict):
    ev.setdefault("ts", time.time())
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(ev, ensure_ascii=False) + "\n")
    except Exception:
        pass


def main():
    raw = sys.stdin.read()
    try:
        d = json.loads(raw) if raw.strip() else {}
    except Exception:
        d = {}

    hook = d.get("hook_event_name") or os.environ.get("CLAUDE_HOOK_EVENT", "")
    sid = str(d.get("session_id") or "sessao")[:8]
    cwd = d.get("cwd") or os.getcwd()
    project = os.path.basename(str(cwd).rstrip("/\\")) or "?"
    aid = f"{project}:{sid}"

    if hook == "SessionStart":
        emit({"type": "agent_start", "id": aid, "agent": "Claude Code",
              "project": project, "skill": "", "model": d.get("model", "sonnet"),
              "overcore": False})

    elif hook == "UserPromptSubmit":
        prompt = (d.get("prompt") or "").strip()
        skill = prompt.split()[0] if prompt.startswith("/") else ""
        oc = is_overcore(prompt)
        emit({"type": "agent_start", "id": aid,
              "agent": "OverCore" if oc else "Claude Code",
              "project": project, "skill": skill, "overcore": oc})
        emit({"type": "log", "id": aid, "message": prompt[:80]})

    elif hook == "PreToolUse":
        tool = d.get("tool_name", "")
        ti = d.get("tool_input", {}) or {}
        desc = (ti.get("description") or ti.get("command") or ti.get("file_path")
                or ti.get("pattern") or ti.get("prompt") or "")
        emit({"type": "tool", "id": aid, "tool": tool, "project": project,
              "message": str(desc)[:60], "status": "running"})
        # spawn de subagente/worker -> vira um agente proprio no painel
        if tool in ("Agent", "Task", "Workflow"):
            label = str(ti.get("subagent_type") or ti.get("description") or "sub")[:16]
            sub = f"{aid}:{label}"
            emit({"type": "agent_start", "id": sub, "agent": label,
                  "project": project, "skill": str(ti.get("description", ""))[:24],
                  "parent": "Claude Code", "overcore": is_overcore(str(ti.get("description", "")))})

    elif hook == "PostToolUse":
        emit({"type": "log", "id": aid,
              "message": f"{d.get('tool_name','tool')} concluida"})

    elif hook in ("SubagentStop", "Stop"):
        emit({"type": "agent_done", "id": aid, "status": "done"})

    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
