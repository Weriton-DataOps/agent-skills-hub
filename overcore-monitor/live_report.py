#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Painel de EXECUCAO AO VIVO — so o que esta rodando NESTA maquina agora.

Le os transcripts do Claude Code (~/.claude/projects) e monta, no espirito do
prompt original (orquestrador profissional): resumo executivo, um card por
agente/subagente com status/tempo/etapas/ferramenta/tokens/logs, timeline global
de eventos, historico recente, ranking dos mais lentos e tempo medio.

Honestidade das metricas:
- tokens, turnos, ferramentas, tempo: REAIS por sessao (o transcript grava).
- CPU/RAM: da MAQUINA (psutil) — o Claude Code nao expoe consumo por sessao.
- ETA/percentual de agente aberto: INDETERMINADO — nao ha "total de etapas"
  conhecido, entao a barra fica em modo "em curso" em vez de um numero inventado.
Zero config. build_live() devolve um dict JSON-avel.
"""
import os
import glob
import json
import time
import collections
from datetime import datetime, date

from transcript_source import _epoch, _model_key, _project_from_path, _prompt_text

try:
    import psutil
    psutil.cpu_percent(interval=None)  # prime: 1a leitura vem 0
except Exception:
    psutil = None

OC_SKILLS = {
    "overcore", "atelier", "croqui", "refinar", "varrer", "tipografar", "cor", "animar",
    "polir", "criticar", "endurecer", "embarcar", "impactar", "adaptar", "artesao",
    "cristalizar", "safegate", "validar", "planejar",
}

LIVE_WIN = 240     # s: sessao "executando agora"
IDLE_WIN = 1800    # s: idle porem ainda "aguardando" (senao vira concluida)
SCAN_MIN = 90      # min: janela de arquivos a varrer (foco no recente)


def _projects_root():
    return os.path.join(os.path.expanduser("~"), ".claude", "projects")


def _is_oc_project(name: str) -> bool:
    n = (name or "").lower()
    return "agent-skills" in n or "overcore" in n


def _is_oc_skill(s: str) -> bool:
    s = (s or "").lower().lstrip("/").strip()
    return any(s == k or s.startswith(k) for k in OC_SKILLS)


def _machine():
    if not psutil:
        return {"ok": False}
    try:
        vm = psutil.virtual_memory()
        return {"ok": True, "cpu": round(psutil.cpu_percent(interval=None), 1),
                "cores": psutil.cpu_count() or 0,
                "mem_pct": round(vm.percent, 1),
                "mem_used": round(vm.used / 1e9, 1), "mem_total": round(vm.total / 1e9, 1)}
    except Exception:
        return {"ok": False}


def _status(s, now):
    age = now - s["last"] if s["last"] else 1e9
    if age <= LIVE_WIN:
        if s.get("last_err"):          # so' e' 'erro' se a ULTIMA ferramenta falhou
            return "erro"
        return "inicializando" if s["turns"] <= 1 else "executando"
    if age <= IDLE_WIN:
        return "aguardando"
    return "finalizado"


def build_live(root=None):
    root = root or _projects_root()
    now = time.time()
    today = date.today()
    S = {}

    def rec(sid):
        if sid not in S:
            S[sid] = {"id": sid, "project": "?", "sub": False, "model": "", "overcore": False,
                      "turns": 0, "tools": 0, "tin": 0, "tout": 0, "first": None, "last": None,
                      "last_tool": "", "last_action": "", "tools_by": collections.Counter(),
                      "skills": collections.Counter(), "logs": collections.deque(maxlen=14),
                      "errors": 0, "last_err": False, "task": ""}
        return S[sid]

    timeline = []

    try:
        files = glob.glob(os.path.join(root, "**", "*.jsonl"), recursive=True)
    except Exception:
        files = []

    for f in files:
        try:
            if os.path.getmtime(f) < now - SCAN_MIN * 60:
                continue
        except OSError:
            continue
        is_sub = "subagents" in f.replace("\\", "/")
        sid = os.path.splitext(os.path.basename(f))[0][:18]
        try:
            fh = open(f, encoding="utf-8", errors="ignore")
        except OSError:
            continue
        with fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                ts = _epoch(d["timestamp"]) if d.get("timestamp") else None
                if ts and datetime.fromtimestamp(ts).date() != today:
                    continue
                t = d.get("type")
                s = rec(sid)

                if t == "assistant":
                    m = d.get("message", {}) or {}
                    proj = _project_from_path(f)
                    mk = _model_key(m.get("model"))
                    s["project"] = proj; s["sub"] = is_sub; s["model"] = mk; s["turns"] += 1
                    if _is_oc_project(proj):
                        s["overcore"] = True
                    if ts:
                        s["first"] = ts if s["first"] is None else min(s["first"], ts)
                        s["last"] = ts if s["last"] is None else max(s["last"], ts)
                    u = m.get("usage") or {}
                    s["tin"] += u.get("input_tokens", 0); s["tout"] += u.get("output_tokens", 0)
                    for b in (m.get("content") or []):
                        if isinstance(b, dict) and b.get("type") == "tool_use":
                            name = b.get("name", "?")
                            ti = b.get("input") or {}
                            desc = str(ti.get("description") or ti.get("command") or ti.get("file_path")
                                       or ti.get("pattern") or ti.get("prompt") or "")[:90]
                            s["tools"] += 1; s["tools_by"][name] += 1
                            s["last_tool"] = name
                            if desc:
                                s["last_action"] = desc
                            kind, label = "tool", (name + ((" " + desc) if desc else ""))[:88]
                            if name == "Skill":
                                sk = str(ti.get("skill", "?")).lstrip("/")
                                s["skills"][sk] += 1
                                if _is_oc_skill(sk):
                                    s["overcore"] = True
                                kind, label = "skill", "/" + sk
                            elif name in ("Agent", "Task", "Workflow"):
                                sub = str(ti.get("subagent_type") or ti.get("description") or "sub")[:30]
                                kind, label = "agente", "→ " + sub
                            s["logs"].append({"ts": ts, "kind": kind, "tool": name, "text": label})
                            timeline.append({"ts": ts, "project": proj, "kind": kind,
                                             "text": label, "overcore": s["overcore"],
                                             "sub": is_sub})

                elif t in ("user", "last-prompt"):
                    # resultado de ferramenta: rastreia se a ULTIMA deu erro (nao o dia todo)
                    msg = d.get("message") or {}
                    cont = msg.get("content") if isinstance(msg, dict) else None
                    if isinstance(cont, list):
                        had_result = had_err = False
                        for b in cont:
                            if isinstance(b, dict) and b.get("type") == "tool_result":
                                had_result = True
                                if b.get("is_error"):
                                    had_err = True
                        if had_result:
                            s["last_err"] = had_err
                            if had_err:
                                s["errors"] += 1
                    txt = _prompt_text(d).strip()
                    if txt and not txt.startswith("[") and "tool_result" not in txt[:40] and txt[:1] != "<":
                        if not s["task"]:
                            s["task"] = txt[:60]

    # classifica
    for s in S.values():
        s["status"] = _status(s, now)
        s["elapsed"] = (s["last"] - s["first"]) if (s["last"] and s["first"]) else 0
        s["age"] = (now - s["last"]) if s["last"] else None

    live = [s for s in S.values() if s["status"] in ("executando", "inicializando", "erro")]
    waiting = [s for s in S.values() if s["status"] == "aguardando"]
    finished = [s for s in S.values() if s["status"] == "finalizado" and s["turns"] > 0]

    def card(s):
        title = s["task"] or ("subagente" if s["sub"] else "Claude Code")
        return {
            "id": s["id"][:8], "title": title, "project": s["project"], "sub": s["sub"],
            "overcore": s["overcore"], "status": s["status"], "model": s["model"],
            "elapsed": round(s["elapsed"]), "age": (round(s["age"]) if s["age"] is not None else None),
            "turns": s["turns"], "calls": s["turns"], "tools": s["tools"],
            "tokens": s["tin"] + s["tout"], "tokens_in": s["tin"], "tokens_out": s["tout"],
            "last_tool": s["last_tool"], "last_action": s["last_action"],
            "errors": s["errors"], "last_err": s["last_err"],
            "tools_by": s["tools_by"].most_common(8),
            "skills": list(s["skills"].keys()),
            "logs": list(s["logs"])[-10:][::-1],
        }

    live_cards = sorted((card(s) for s in live),
                        key=lambda c: (c["overcore"], c["tokens"]), reverse=True)
    wait_cards = sorted((card(s) for s in waiting), key=lambda c: c["tokens"], reverse=True)
    fin_cards = sorted((card(s) for s in finished),
                       key=lambda c: c["elapsed"], reverse=True)

    # agrupa cards vivos por projeto (mantem o "por projeto" que voce pediu)
    by_proj = collections.OrderedDict()
    for c in live_cards + wait_cards:
        by_proj.setdefault(c["project"], {"name": c["project"], "overcore": False, "agents": []})
        by_proj[c["project"]]["agents"].append(c)
        if c["overcore"]:
            by_proj[c["project"]]["overcore"] = True
    projects = list(by_proj.values())
    projects.sort(key=lambda p: (p["overcore"], len([a for a in p["agents"] if a["status"] != "aguardando"])), reverse=True)

    # resumo executivo
    act_last = [s["last"] for s in live if s["last"]]
    act_first = [s["first"] for s in live if s["first"]]
    workflow_elapsed = (max(act_last) - min(act_first)) if (act_last and act_first) else 0
    tokens_live = sum(s["tin"] + s["tout"] for s in live)
    durs = [s["elapsed"] for s in finished if s["elapsed"] > 0]
    ranking = [{"title": (c["title"])[:46], "project": c["project"], "elapsed": c["elapsed"],
                "tokens": c["tokens"], "sub": c["sub"], "overcore": c["overcore"]}
               for c in fin_cards[:6]]

    timeline.sort(key=lambda e: (e["ts"] or 0), reverse=True)

    return {
        "generated": now, "date": today.isoformat(),
        "machine": _machine(),
        "summary": {
            "ativos": len(live),
            "subagentes": sum(1 for s in live if s["sub"]),
            "finalizados": len(finished),
            "aguardando": len(waiting),
            "falhas": sum(1 for s in live if s["status"] == "erro"),
            "workflow_elapsed": round(workflow_elapsed),
            "tokens_live": tokens_live,
            "projetos": len(projects),
            "avg_dur": round(sum(durs) / len(durs)) if durs else 0,
        },
        "projects": projects,
        "finished": fin_cards[:10],
        "ranking": ranking,
        "timeline": timeline[:60],
    }


if __name__ == "__main__":
    import sys
    json.dump(build_live(), sys.stdout, ensure_ascii=False, indent=1, default=lambda o: None)
