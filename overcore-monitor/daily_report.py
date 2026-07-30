#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Painel DO DIA — leitura geral de tudo que rodou hoje, a partir dos transcripts do
Claude Code (~/.claude/projects). Agrega: projetos tocados, sessoes, subagentes,
skills, tokens/custo reais e, com DESTAQUE, o OverCore (quantas sessoes, o que fez,
skills, subagentes).

Notas:
- Custo consciente de cache (Anthropic): input, output, cache-write 1.25x, cache-read 0.1x.
  Token "headline" = input + output (frescos); cache_read NAO entra no volume (so no custo).
- Skill = a tool "Skill" do Claude Code (input.skill traz o nome). Modo OverCore tambem
  e detectado pelo projeto (hub) alem das skills OverCore.
Zero config. build_daily() devolve um dict JSON-avel.
"""
import os
import glob
import json
import time
import collections
from datetime import datetime, date

from overcore_monitor import PRICES, DEFAULT_MODEL
from transcript_source import _epoch, _model_key, _project_from_path, _prompt_text

OC_SKILLS = {
    "overcore", "atelier", "croqui", "refinar", "varrer", "tipografar", "cor", "animar",
    "polir", "criticar", "endurecer", "embarcar", "impactar", "adaptar", "artesao",
    "cristalizar", "safegate", "validar", "planejar",
}


def _projects_root():
    return os.path.join(os.path.expanduser("~"), ".claude", "projects")


def _is_oc_project(name: str) -> bool:
    n = (name or "").lower()
    return "agent-skills" in n or "overcore" in n


def _is_oc_skill(s: str) -> bool:
    s = (s or "").lower().lstrip("/").strip()
    return any(s == k or s.startswith(k) for k in OC_SKILLS)


def _line_cost(mk, i, o, cc, cr):
    pin, pout = PRICES.get(mk, PRICES[DEFAULT_MODEL])
    return (i * pin + o * pout + cc * pin * 1.25 + cr * pin * 0.1) / 1_000_000


def build_daily(root=None, when=None, lookback_h=48) -> dict:
    root = root or _projects_root()
    when = when or date.today()
    now = time.time()

    def sess():
        return {"project": "?", "sub": False, "turns": 0, "tin": 0, "tout": 0, "cache": 0,
                "cost": 0.0, "tools_by": collections.Counter(), "skills": collections.Counter(),
                "prompts": [], "first": None, "last": None, "overcore": False, "model": "",
                "last_tool": "", "last_action": "", "task": ""}
    sessions = collections.defaultdict(sess)
    skill_calls = []   # cada invocacao da tool Skill (quando uma skill foi chamada)
    proj_recent = collections.defaultdict(list)   # acoes recentes por projeto (feed ao vivo)

    projects = collections.defaultdict(lambda: {
        "name": "", "sessions": set(), "tools": 0, "tin": 0, "tout": 0, "cost": 0.0,
        "first": None, "last": None, "overcore": False, "models": collections.Counter()})
    skills = collections.Counter()
    tools = collections.Counter()
    subagents = set()
    tot = {"tin": 0, "tout": 0, "cache": 0, "cost": 0.0, "tools": 0}

    try:
        files = glob.glob(os.path.join(root, "**", "*.jsonl"), recursive=True)
    except Exception:
        files = []

    for f in files:
        try:
            if os.path.getmtime(f) < now - lookback_h * 3600:
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
                if ts and datetime.fromtimestamp(ts).date() != when:
                    continue
                t = d.get("type")
                sr = sessions[sid]
                sr["id"] = sid

                if t == "assistant":
                    m = d.get("message", {}) or {}
                    proj = _project_from_path(f)
                    mk = _model_key(m.get("model"))
                    sr["project"] = proj; sr["sub"] = is_sub; sr["model"] = mk; sr["turns"] += 1
                    if is_sub:
                        subagents.add(sid)
                    oc_proj = _is_oc_project(proj)
                    if oc_proj:
                        sr["overcore"] = True
                    if ts:
                        sr["first"] = ts if sr["first"] is None else min(sr["first"], ts)
                        sr["last"] = ts if sr["last"] is None else max(sr["last"], ts)
                    u = m.get("usage") or {}
                    i = u.get("input_tokens", 0); o = u.get("output_tokens", 0)
                    cc = u.get("cache_creation_input_tokens", 0); cr = u.get("cache_read_input_tokens", 0)
                    c = _line_cost(mk, i, o, cc, cr)
                    sr["tin"] += i; sr["tout"] += o; sr["cache"] += cc + cr; sr["cost"] += c
                    tot["tin"] += i; tot["tout"] += o; tot["cache"] += cc + cr; tot["cost"] += c
                    P = projects[proj]; P["name"] = proj; P["sessions"].add(sid); P["models"][mk] += 1
                    P["tin"] += i; P["tout"] += o; P["cost"] += c
                    if oc_proj:
                        P["overcore"] = True
                    if ts:
                        P["first"] = ts if P["first"] is None else min(P["first"], ts)
                        P["last"] = ts if P["last"] is None else max(P["last"], ts)
                    for b in (m.get("content") or []):
                        if isinstance(b, dict) and b.get("type") == "tool_use":
                            name = b.get("name", "?")
                            ti = b.get("input") or {}
                            desc = str(ti.get("description") or ti.get("command") or ti.get("file_path")
                                       or ti.get("pattern") or "")[:80]
                            tools[name] += 1; sr["tools_by"][name] += 1
                            P["tools"] += 1; tot["tools"] += 1
                            sr["last_tool"] = name
                            if desc:
                                sr["last_action"] = desc
                            if name == "Skill":
                                sk = str(ti.get("skill", "?")).lstrip("/")
                                skills[sk] += 1; sr["skills"][sk] += 1
                                oc = _is_oc_skill(sk)
                                if oc:
                                    sr["overcore"] = True
                                skill_calls.append({"ts": ts, "kind": "skill", "name": sk,
                                                    "project": proj, "session": sid[:8], "overcore": oc,
                                                    "model": mk})
                                proj_recent[proj].append((ts, "skill", "/" + sk))
                            elif name in ("Agent", "Task", "Workflow"):
                                sub = str(ti.get("subagent_type") or ti.get("description") or "sub")[:26]
                                proj_recent[proj].append((ts, "agente", "→ " + sub))
                            else:
                                proj_recent[proj].append((ts, "tool", (name + ((" " + desc) if desc else ""))[:78]))

                elif t in ("user", "last-prompt"):
                    txt = _prompt_text(d).strip()
                    if not txt or txt.startswith("[") or "tool_result" in txt[:40] or txt[:1] == "<":
                        continue
                    if len(sr["prompts"]) < 4:
                        sr["prompts"].append(txt[:90])
                    if not sr["task"]:
                        sr["task"] = txt[:52]      # rotulo da sessao = 1a tarefa/prompt
                    if txt.startswith("/"):
                        verb = txt.split()[0].lstrip("/")
                        skills[verb] += 1; sr["skills"][verb] += 1
                        if _is_oc_skill(verb):
                            sr["overcore"] = True

    # propaga overcore para o projeto
    for sid, s in sessions.items():
        if s["overcore"]:
            projects[s["project"]]["overcore"] = True

    oc_sess = [s for s in sessions.values() if s["overcore"]]
    oc_tools = collections.Counter()
    oc_skills = collections.Counter()
    oc_actions = []
    oc_tin = oc_tout = 0; oc_cost = 0.0; oc_turns = 0; oc_sub = 0
    for s in oc_sess:
        oc_tools.update(s["tools_by"]); oc_skills.update(s["skills"])
        oc_tin += s["tin"]; oc_tout += s["tout"]; oc_cost += s["cost"]; oc_turns += s["turns"]
        if s["sub"]:
            oc_sub += 1
        for p in s["prompts"][:2]:
            if len(oc_actions) < 16:
                oc_actions.append(p)

    # historico de CHAMADAS: cada subagente e cada skill invocada hoje, com dados da acao
    agent_calls = []
    for s in sessions.values():
        if s["sub"]:
            dur = (s["last"] - s["first"]) if (s["last"] and s["first"]) else None
            agent_calls.append({"ts": s["first"], "kind": "agente",
                "name": (s["task"] or "subagente")[:44], "project": s["project"],
                "session": s["id"][:8], "tools": sum(s["tools_by"].values()),
                "tokens": s["tin"] + s["tout"], "cost": round(s["cost"], 3), "dur": dur,
                "tools_by": s["tools_by"].most_common(5), "overcore": s["overcore"], "model": s["model"]})
    calls = sorted(agent_calls + skill_calls, key=lambda c: (c.get("ts") or 0), reverse=True)

    # EXECUTANDO AGORA: sessoes com atividade nos ultimos 120s
    active = sorted(
        [{"id": s["id"][:8], "project": s["project"], "sub": s["sub"], "turns": s["turns"],
          "tokens": s["tin"] + s["tout"], "cost": round(s["cost"], 3), "tool": s["last_tool"],
          "action": s["last_action"], "overcore": s["overcore"], "model": s["model"],
          "last": s["last"], "task": s["task"]}
         for s in sessions.values() if s["last"] and s["last"] > now - 240],
        key=lambda x: x["last"], reverse=True)

    sess_by_proj = collections.defaultdict(list)
    for s in sessions.values():
        sess_by_proj[s["project"]].append(s)

    ACTIVE_WIN = 240  # s p/ considerar "executando agora" (aguenta pausas de raciocinio)

    def proj_out(p):
        name = p["name"]
        ss = sess_by_proj.get(name, [])
        sk, active, agents_detail = collections.Counter(), [], []
        for s in ss:
            for k, v in s["skills"].items():
                sk[k] += v
            is_act = bool(s["last"] and s["last"] > now - ACTIVE_WIN)
            title = s["task"] or ("subagente" if s["sub"] else "Claude Code")
            if s["turns"] > 0:
                agents_detail.append({
                    "title": title, "sub": s["sub"], "overcore": s["overcore"],
                    "turns": s["turns"], "tokens": s["tin"] + s["tout"], "active": is_act,
                    "model": s["model"], "tools": s["tools_by"].most_common(6),
                    "skills": list(s["skills"].keys()), "last_tool": s["last_tool"],
                    "last_action": s["last_action"], "last": s["last"],
                })
            if is_act:
                active.append({
                    "title": title, "sub": s["sub"], "tool": s["last_tool"], "action": s["last_action"],
                    "tokens": s["tin"] + s["tout"], "turns": s["turns"],
                    "overcore": s["overcore"], "model": s["model"], "session": s["id"][:8],
                    "last": s["last"], "skill": next(iter(s["skills"]), ""),
                })
        active.sort(key=lambda x: x["last"], reverse=True)
        agents_detail.sort(key=lambda x: (x["active"], x["tokens"]), reverse=True)
        rec = sorted(proj_recent.get(name, []), key=lambda x: (x[0] or 0), reverse=True)[:12]
        return {"name": name, "sessions": len(p["sessions"]), "tools": p["tools"],
                "tokens": p["tin"] + p["tout"], "cost": round(p["cost"], 3),
                "first": p["first"], "last": p["last"], "overcore": p["overcore"],
                "model": (p["models"].most_common(1)[0][0] if p["models"] else ""),
                "skills": sk.most_common(12), "agents_detail": agents_detail,
                "active": active, "recent": [{"ts": r[0], "kind": r[1], "label": r[2]} for r in rec]}

    proj_list = sorted((proj_out(p) for p in projects.values()),
                       key=lambda x: (len(x["active"]), x["cost"]), reverse=True)
    sess_list = sorted(sessions.values(), key=lambda s: (s["last"] or 0), reverse=True)

    return {
        "date": when.isoformat(), "generated": now,
        "totals": {
            "projetos": len(projects), "sessoes": len(sessions), "subagentes": len(subagents),
            "tools": tot["tools"], "tokens": tot["tin"] + tot["tout"],
            "tokens_in": tot["tin"], "tokens_out": tot["tout"], "cache": tot["cache"],
            "cost": round(tot["cost"], 2), "skills": sum(skills.values()),
        },
        "overcore": {
            "uses": len(oc_sess), "turns": oc_turns, "subagents": oc_sub,
            "tokens": oc_tin + oc_tout, "cost": round(oc_cost, 2),
            "skills": oc_skills.most_common(20), "tools": oc_tools.most_common(12),
            "actions": oc_actions,
        },
        "active": active,
        "calls": calls[:80],
        "projects": proj_list,
        "skills": skills.most_common(24),
        "tools": tools.most_common(16),
        "sessions": [{"id": s["id"] if "id" in s else "", "project": s["project"], "sub": s["sub"],
                      "tokens": s["tin"] + s["tout"], "cost": round(s["cost"], 3),
                      "tools": sum(s["tools_by"].values()), "turns": s["turns"],
                      "first": s["first"], "last": s["last"], "overcore": s["overcore"],
                      "skills": list(s["skills"].keys()), "model": s["model"]}
                     for s in sess_list[:40]],
    }


if __name__ == "__main__":
    import sys
    json.dump(build_daily(), sys.stdout, ensure_ascii=False, indent=1, default=lambda o: None)
