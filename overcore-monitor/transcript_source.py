#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fonte ZERO-CONFIG: le os transcripts que o Claude Code JA grava em
~/.claude/projects/**/*.jsonl e transforma em eventos do monitor.

Mostra a atividade REAL de todas as sessoes da maquina (tokens reais inclusos),
sem tocar em settings.json e sem custo por tool. Vazio quando nada roda.

Uso pelo web_server.py --transcripts  (ou --transcripts C:/caminho/projects).
"""
import os
import glob
import json
import time
from datetime import datetime

try:
    from overcore_monitor import is_overcore
except Exception:
    def is_overcore(t): return False


def _epoch(iso: str) -> float:
    try:
        return datetime.strptime(iso.replace("Z", "+0000"), "%Y-%m-%dT%H:%M:%S.%f%z").timestamp()
    except Exception:
        return time.time()


def _model_key(m: str) -> str:
    m = (m or "").lower()
    for k in ("opus", "sonnet", "haiku", "fable"):
        if k in m:
            return k
    return "sonnet"


def _project(path: str, cwd: str) -> str:
    if cwd:
        b = os.path.basename(str(cwd).rstrip("/\\"))
        if b:
            return b
    return os.path.basename(os.path.dirname(path)).replace("--", "/").lstrip("cy/") or "?"


def _project_from_path(path: str) -> str:
    """Projeto ESTAVEL da sessao: a pasta do transcript sob ~/.claude/projects/<DIR>/...
    (nao o cwd por-turno, que muda quando o agente navega)."""
    parts = path.replace("\\", "/").split("/")
    dirname = ""
    if "projects" in parts:
        i = parts.index("projects")
        if i + 1 < len(parts):
            dirname = parts[i + 1]
    if not dirname:
        dirname = os.path.basename(os.path.dirname(path))
    name = dirname
    for cut in ("Documents-", "Desktop-", "Comercial-", "wp-santos-"):
        if cut in name:
            name = name.split(cut)[-1]
    for pre in ("c--", "C--", "y--", "Y--"):
        if name.startswith(pre):
            name = name[len(pre):]
    return name or dirname or "?"


def _prompt_text(d: dict) -> str:
    msg = d.get("message")
    if isinstance(msg, dict):
        c = msg.get("content")
        if isinstance(c, str):
            return c
        if isinstance(c, list):
            out = ""
            for b in c:
                if isinstance(b, dict) and b.get("type") == "text":
                    out += b.get("text", "")
                elif isinstance(b, str):
                    out += b
            return out
    if isinstance(d.get("prompt"), str):
        return d["prompt"]
    return ""


def feed_transcripts(q, stop, root=None, lookback=1200, idle=100):
    """Tail continuo dos transcripts. lookback: janela (s) de arquivos a considerar;
    idle: sem novas linhas por > idle s -> sessao vira 'done'."""
    root = root or os.path.join(os.path.expanduser("~"), ".claude", "projects")
    pos, started, last_ts, done = {}, {}, {}, set()

    def emit(ev):
        ev.setdefault("ts", time.time())
        q.put(ev)

    def process(path, seed):
        try:
            size = os.path.getsize(path)
        except OSError:
            return
        p = pos.get(path)
        if p is None:
            p = max(0, size - 24000) if seed else 0   # 1a vez: so a cauda
        if p > size:
            p = 0
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                f.seek(p)
                lines = f.readlines()
                pos[path] = f.tell()
        except OSError:
            return

        sub = "subagents" in path.replace("\\", "/")
        aid = os.path.splitext(os.path.basename(path))[0][:18]
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except Exception:
                continue
            t = d.get("type")
            ts = _epoch(d.get("timestamp", "")) if d.get("timestamp") else time.time()

            if t == "assistant":
                m = d.get("message", {}) or {}
                proj = _project(path, d.get("cwd", ""))
                mk = _model_key(m.get("model"))
                if aid not in started:
                    started[aid] = True
                    emit({"type": "agent_start", "id": aid,
                          "agent": ("subagente" if (sub or d.get("isSidechain")) else "Claude Code"),
                          "project": proj, "skill": "", "model": mk,
                          "parent": (d.get("sessionId", "")[:8] if sub else None),
                          "overcore": ("agent-skills" in proj.lower() or "overcore" in proj.lower())})
                done.discard(aid)
                last_ts[aid] = time.time()
                for b in (m.get("content") or []):
                    if isinstance(b, dict) and b.get("type") == "tool_use":
                        name = b.get("name", "")
                        ti = b.get("input", {}) or {}
                        desc = str(ti.get("description") or ti.get("command") or ti.get("file_path")
                                   or ti.get("pattern") or ti.get("prompt") or "")[:60]
                        ev = {"type": "tool", "id": aid, "tool": name, "project": proj,
                              "message": desc, "status": "processing"}
                        if name == "Skill":  # skill do OverCore/Claude -> mostra qual + acumula
                            sk = str(ti.get("skill", "")).lstrip("/")
                            if sk:
                                ev["skill"] = "/" + sk
                                ev["skill_used"] = "/" + sk
                                ev["message"] = "skill: " + sk
                                if is_overcore("/" + sk, ""):
                                    ev["overcore"] = True
                        elif name in ("Agent", "Task", "Workflow"):  # spawn de subagente -> acumula
                            sub = str(ti.get("subagent_type") or ti.get("description") or "subagente")[:26]
                            ev["message"] = "→ subagente: " + sub
                            ev["subagent_used"] = sub
                        emit(ev)
                u = m.get("usage") or {}
                tin = u.get("input_tokens", 0)   # tokens FRESCOS (cache_read fica de fora do volume)
                tout = u.get("output_tokens", 0)
                if tin or tout:
                    emit({"type": "tokens", "id": aid, "in": tin, "out": tout,
                          "calls": 1, "model": mk, "dt": 0})
                emit({"type": "progress", "id": aid, "step": 0, "steps": 0})

            elif t in ("user", "last-prompt"):
                txt = _prompt_text(d).strip()
                if txt and not txt.startswith("[") and "tool_result" not in txt[:40] and "<" not in txt[:2]:
                    upd = {"type": "log", "id": aid, "message": txt[:80]}
                    if sub:
                        upd["skill"] = "▸ " + txt[:28]      # tarefa recebida pelo subagente
                    if txt.startswith("/"):
                        upd["skill"] = txt.split()[0]
                        if is_overcore(txt, ""):
                            upd["overcore"] = True
                    elif is_overcore(txt, ""):
                        upd["overcore"] = True
                    emit(upd)
                    last_ts[aid] = time.time()

    seeded = False
    while not stop.is_set():
        now = time.time()
        try:
            files = glob.glob(os.path.join(root, "**", "*.jsonl"), recursive=True)
        except Exception:
            files = []
        for f in files:
            try:
                if os.path.getmtime(f) > now - lookback:
                    process(f, seed=not seeded)
            except OSError:
                continue
        seeded = True
        for aid, ts in list(last_ts.items()):
            if aid not in done and now - ts > idle:
                emit({"type": "agent_done", "id": aid, "status": "done"})
                done.add(aid)
        time.sleep(2.0)
