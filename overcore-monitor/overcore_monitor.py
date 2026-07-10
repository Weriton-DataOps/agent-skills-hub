#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OverCore · Monitor — painel de monitoramento em tempo real para o terminal.

Mostra, ao vivo, tudo que o OverCore esta executando: agentes/subagentes, em quais
projetos, quais comandos/skills, tempo, tokens, custo estimado, ferramenta atual e logs.

Fonte de dados: um fluxo de eventos JSONL (append-only) emitido pelos hooks do
Claude Code (ver hook.py). Cada linha e um evento. O painel faz "tail" desse arquivo.

Uso:
    python overcore_monitor.py --demo               # sessao simulada (ver funcionando ja)
    python overcore_monitor.py --events eventos.jsonl   # ao vivo, lendo os hooks
    python overcore_monitor.py --demo --snapshot    # renderiza 1 quadro e sai (teste/CI)

Requisitos: pip install rich   (opcional: pip install psutil  -> CPU/memoria reais)
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import re
import sys
import threading
import time
from collections import deque, defaultdict
from dataclasses import dataclass, field
from queue import Queue, Empty

try:
    from rich.console import Console, Group
    from rich.live import Live
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.text import Text
    from rich.table import Table
    from rich.columns import Columns
    from rich.align import Align
    from rich import box
except Exception:  # pragma: no cover
    sys.stderr.write("\n[OverCore Monitor] Falta a lib 'rich'. Instale:\n    pip install rich\n\n")
    raise

try:
    import psutil  # opcional
except Exception:
    psutil = None


# ------------------------------------------------------------------ config -----

# Preco por 1M de tokens (USD), entrada/saida. EDITE conforme as tarifas atuais.
PRICES = {
    "opus":   (15.0, 75.0),
    "sonnet": (3.0, 15.0),
    "haiku":  (0.80, 4.0),
    "fable":  (5.0, 25.0),
    "gpt-4o": (2.5, 10.0),
}
DEFAULT_MODEL = "sonnet"

# status -> (emoji, cor, rotulo)
STATUS = {
    "waiting":    ("⏳", "grey70",       "Aguardando"),
    "init":       ("\U0001f680", "cyan",     "Inicializando"),
    "running":    ("⚙️", "green",  "Executando"),
    "processing": ("\U0001f504", "yellow",   "Processando"),
    "done":       ("✅", "bright_green", "Finalizado"),
    "error":      ("❌", "red",          "Erro"),
    "paused":     ("⏸️", "grey58", "Pausado"),
}
ACTIVE = {"init", "running", "processing", "paused"}
SPIN = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
BRAND = "◆"  # losango

# tools -> icone
TOOL_ICON = {
    "Read": "\U0001f4c4", "Edit": "✏️", "Write": "\U0001f4dd",
    "Grep": "\U0001f50e", "Glob": "\U0001f5c2️", "Bash": "⚡",
    "Workflow": "\U0001f9ec", "Task": "\U0001f9e9", "WebFetch": "\U0001f310",
    "Agent": "\U0001f916",
}

# Rastreamos TUDO (qualquer agente/skill do Claude Code). O que for do OverCore ganha destaque.
OVERCORE_VERBS = {
    "/overcore", "/atelier", "/croqui", "/refinar", "/varrer", "/tipografar", "/cor",
    "/animar", "/polir", "/criticar", "/endurecer", "/embarcar", "/impactar", "/adaptar",
    "/artesao", "/cristalizar", "/safegate", "/validar", "/planejar",
}
OVERCORE_AGENTS = {
    "router", "supervisor", "atelier", "design", "codigo", "safegate", "researcher",
    "curator", "plan", "validacao", "overcore",
}


def is_overcore(skill: str, name: str) -> bool:
    s = (skill or "").lower().strip()
    if any(s.startswith(v) for v in OVERCORE_VERBS):
        return True
    n = (name or "").lower()
    return any(k in n for k in OVERCORE_AGENTS)


# --------------------------------------------------------------- utilidades ----

def fmt_dur(s: float) -> str:
    if s is None:
        return "--"
    if s < 60:
        return f"{s:0.1f}s"
    m, sec = divmod(int(s), 60)
    if m < 60:
        return f"{m}m{sec:02d}s"
    h, m = divmod(m, 60)
    return f"{h}h{m:02d}m"


def human_num(n: float) -> str:
    if n is None:
        return "--"
    n = float(n)
    for unit in ("", "k", "M", "B"):
        if abs(n) < 1000:
            return (f"{n:0.0f}{unit}" if unit == "" else f"{n:0.1f}{unit}")
        n /= 1000
    return f"{n:0.1f}T"


def bar(pct: float, width: int, color: str) -> Text:
    pct = max(0.0, min(1.0, pct or 0.0))
    filled = int(round(pct * width))
    t = Text()
    t.append("█" * filled, style=color)
    t.append("░" * (width - filled), style="grey37")
    return t


def indet_bar(width: int, color: str) -> Text:
    """Barra indeterminada (quando nao sabemos o total de etapas) — bloco que corre."""
    seg = 5
    pos = int(time.time() * 12) % (width + seg)
    t = Text()
    for i in range(width):
        on = (pos - seg) < i <= pos
        t.append("█" if on else "░", style=color if on else "grey37")
    return t


def cost_of(model: str, tin: int, tout: int) -> float:
    pin, pout = PRICES.get((model or "").lower(), PRICES[DEFAULT_MODEL])
    return (tin / 1_000_000) * pin + (tout / 1_000_000) * pout


_MARKUP = re.compile(r"\[/?[a-zA-Z0-9 _#]*\]")


def strip_markup(s: str) -> str:
    return _MARKUP.sub("", s or "")


# ------------------------------------------------------------------ estado -----

@dataclass
class Agent:
    id: str
    name: str
    project: str = "?"
    skill: str = ""              # /comando ou skill
    tool: str = ""               # ferramenta atual
    status: str = "waiting"
    step: int = 0
    steps: int = 0
    parent: str | None = None    # subagente de quem
    model: str = DEFAULT_MODEL
    start: float = 0.0
    updated: float = 0.0
    done_ts: float | None = None
    tokens_in: int = 0
    tokens_out: int = 0
    api_calls: int = 0
    ai_time: float = 0.0         # tempo em chamadas de IA
    ext_time: float = 0.0        # tempo em chamadas externas
    last: str = ""               # ultima atividade
    logs: deque = field(default_factory=lambda: deque(maxlen=6))
    error: str = ""
    overcore: bool = False       # atividade do OverCore (recebe destaque)
    skills_used: dict = field(default_factory=dict)   # skill -> nº de vezes acionada
    subs_used: dict = field(default_factory=dict)     # tipo de subagente -> nº de vezes

    @property
    def elapsed(self) -> float:
        end = self.done_ts if self.done_ts else time.time()
        return max(0.0, end - self.start) if self.start else 0.0

    @property
    def pct(self) -> float:
        if self.status == "done":
            return 1.0
        if self.steps > 0:
            return min(1.0, self.step / self.steps)
        return 0.0

    @property
    def eta(self) -> float | None:
        p = self.pct
        if self.status in ("done", "error") or p <= 0.01:
            return None
        return self.elapsed * (1 - p) / p

    @property
    def tokens(self) -> int:
        return self.tokens_in + self.tokens_out

    @property
    def cost(self) -> float:
        return cost_of(self.model, self.tokens_in, self.tokens_out)


class State:
    def __init__(self):
        self.agents: dict[str, Agent] = {}
        self.timeline: deque = deque(maxlen=240)
        self.session_start = time.time()
        self.order: list[str] = []  # ordem de chegada

    # -- ingestao -----------------------------------------------------------
    def apply(self, ev: dict):
        t = ev.get("type", "")
        aid = ev.get("id") or ev.get("agent") or "?"
        now = ev.get("ts") or time.time()

        if aid not in self.agents and t not in ("session", "note"):
            a = Agent(id=aid, name=ev.get("agent", aid))
            self.agents[aid] = a
            self.order.append(aid)
        a = self.agents.get(aid)
        if a is not None:  # qualquer evento pode carregar/atualizar projeto, skill e destaque OC
            if ev.get("project"):
                a.project = ev["project"]
            if ev.get("skill"):
                a.skill = ev["skill"]
            if ev.get("overcore"):
                a.overcore = True

        if t == "agent_start":
            a.name = ev.get("agent", a.name)
            a.project = ev.get("project", a.project)
            a.skill = ev.get("skill", a.skill)
            a.parent = ev.get("parent", a.parent)
            a.model = ev.get("model", a.model)
            a.steps = ev.get("steps", a.steps)
            oc = ev.get("overcore")
            a.overcore = bool(oc) if oc is not None else is_overcore(a.skill, a.name)
            a.status = "init"
            a.start = now
            a.updated = now
            self._tl(now, f"[b]{a.name}[/] iniciou  [dim]{a.project} {a.skill}[/]", "\U0001f680", a.project, a.overcore)
            a.logs.append((now, "iniciou"))
        elif t == "status":
            a.status = ev.get("status", a.status)
            a.updated = now
            if a.status in ("done", "error"):
                a.done_ts = now
        elif t == "progress":
            a.step = ev.get("step", a.step)
            a.steps = ev.get("steps", a.steps)
            if a.status in ("init", "waiting"):
                a.status = "running"
            a.updated = now
        elif t == "tool":
            a.tool = ev.get("tool", "")
            a.status = ev.get("status", "running")
            a.last = ev.get("message", f"{a.tool}")
            a.updated = now
            ic = TOOL_ICON.get(a.tool, "•")
            a.logs.append((now, f"{a.tool}: {ev.get('message','')}".strip(": ")))
            if ev.get("skill_used"):
                a.skills_used[ev["skill_used"]] = a.skills_used.get(ev["skill_used"], 0) + 1
            if ev.get("subagent_used"):
                a.subs_used[ev["subagent_used"]] = a.subs_used.get(ev["subagent_used"], 0) + 1
            self._tl(now, f"{a.name} → [b]{a.tool}[/] [dim]{ev.get('message','')}[/]", ic, a.project, a.overcore)
        elif t == "tokens":
            a.tokens_in += ev.get("in", 0)
            a.tokens_out += ev.get("out", 0)
            a.api_calls += ev.get("calls", 1)
            a.ai_time += ev.get("dt", 0.0)
            a.model = ev.get("model", a.model)
            a.updated = now
        elif t == "api":  # chamada externa (nao-IA)
            a.ext_time += ev.get("dt", 0.0)
            a.last = ev.get("message", a.last)
            self._tl(now, f"{a.name} [dim]API {ev.get('message','')}[/]", "\U0001f310", a.project, a.overcore)
        elif t == "log":
            a.last = ev.get("message", a.last)
            a.logs.append((now, ev.get("message", "")))
            a.updated = now
        elif t == "agent_done":
            a.status = ev.get("status", "done")
            a.done_ts = now
            a.step = a.steps or a.step
            a.tool = ""
            ic, _, _ = STATUS.get(a.status, ("✅", "", ""))
            self._tl(now, f"[b]{a.name}[/] {STATUS.get(a.status,('','',''))[2].lower()} em {fmt_dur(a.elapsed)}", ic, a.project, a.overcore)
            a.logs.append((now, f"finalizado ({fmt_dur(a.elapsed)})"))
        elif t == "error":
            a.status = "error"
            a.error = ev.get("message", "erro")
            a.done_ts = now
            self._tl(now, f"[red]{a.name} falhou:[/] {a.error}", "❌", a.project, a.overcore)

    def _tl(self, ts, text, icon, project="", overcore=False):
        if overcore:
            text = "[bold magenta]" + BRAND + "[/] " + text
        self.timeline.append((ts, icon, text, project))

    # -- derivados ----------------------------------------------------------
    def by_project(self) -> dict[str, list[Agent]]:
        d = defaultdict(list)
        for aid in self.order:
            a = self.agents[aid]
            d[a.project].append(a)
        return d

    def counts(self):
        c = defaultdict(int)
        for a in self.agents.values():
            c[a.status] += 1
        return c

    def totals(self):
        tin = sum(a.tokens_in for a in self.agents.values())
        tout = sum(a.tokens_out for a in self.agents.values())
        cost = sum(a.cost for a in self.agents.values())
        calls = sum(a.api_calls for a in self.agents.values())
        ai = sum(a.ai_time for a in self.agents.values())
        ext = sum(a.ext_time for a in self.agents.values())
        return tin, tout, cost, calls, ai, ext

    def global_pct(self) -> float:
        ags = list(self.agents.values())
        if not ags:
            return 0.0
        return sum(a.pct for a in ags) / len(ags)

    def subagents(self) -> int:
        return sum(1 for a in self.agents.values() if a.parent)

    def done_list(self):
        return [a for a in self.agents.values() if a.status == "done"]

    def slowest(self, n=3):
        done = [a for a in self.agents.values() if a.done_ts]
        return sorted(done, key=lambda a: a.elapsed, reverse=True)[:n]

    def avg_time(self):
        done = [a for a in self.agents.values() if a.done_ts]
        return (sum(a.elapsed for a in done) / len(done)) if done else 0.0

    # -- serializacao p/ a web ---------------------------------------------
    def _agent_dict(self, a: Agent) -> dict:
        return {
            "id": a.id, "name": a.name, "project": a.project, "skill": a.skill,
            "tool": a.tool, "status": a.status, "step": a.step, "steps": a.steps,
            "pct": a.pct, "elapsed": a.elapsed, "eta": a.eta, "tokens": a.tokens,
            "tokens_in": a.tokens_in, "tokens_out": a.tokens_out, "cost": a.cost,
            "calls": a.api_calls, "model": a.model, "last": a.last, "overcore": a.overcore,
            "parent": a.parent, "ai_time": a.ai_time, "ext_time": a.ext_time,
            "logs": [{"ts": ts, "msg": m} for ts, m in list(a.logs)],
        }

    def snapshot(self) -> dict:
        by = self.by_project()
        projects = []
        for p, ags in by.items():
            sk, su = {}, {}
            for a in ags:
                for k, v in a.skills_used.items():
                    sk[k] = sk.get(k, 0) + v
                for k, v in a.subs_used.items():
                    su[k] = su.get(k, 0) + v
            projects.append({
                "name": p,
                "n_active": sum(1 for a in ags if a.status in ACTIVE),
                "n_overcore": sum(1 for a in ags if a.overcore),
                "agents": [self._agent_dict(a) for a in ags],
                "skills_roster": sorted(sk.items(), key=lambda x: -x[1]),
                "agents_roster": sorted(su.items(), key=lambda x: -x[1]),
            })
        tin, tout, cost, calls, ai, ext = self.totals()
        c = self.counts()
        cpu = mem = None
        if psutil:
            try:
                cpu = psutil.cpu_percent()
                mem = psutil.virtual_memory().percent
            except Exception:
                pass
        tl = []
        for ts, icon, text, proj in list(self.timeline)[-40:]:
            clean = strip_markup(text)
            tl.append({"ts": ts, "icon": icon, "text": clean, "project": proj,
                       "overcore": clean.strip().startswith(BRAND)})
        return {
            "now": time.time(),
            "session": time.time() - self.session_start,
            "demo": DEMO,
            "summary": {
                "projetos": len(by), "ativos": sum(c[s] for s in ACTIVE),
                "subagentes": self.subagents(), "concluidos": c["done"],
                "aguardando": c["waiting"], "falhas": c["error"],
                "tokens": tin + tout, "tokens_in": tin, "tokens_out": tout,
                "cost": cost, "calls": calls, "ai_time": ai, "ext_time": ext,
                "global_pct": self.global_pct(), "avg_time": self.avg_time(),
            },
            "projects": projects,
            "timeline": tl,
            "slowest": [{"name": a.name, "elapsed": a.elapsed, "overcore": a.overcore}
                        for a in self.slowest(5)],
            "cpu": cpu, "mem": mem,
        }


# --------------------------------------------------------------- renderizacao --

def stat_tile(label: str, value: str, color: str) -> Text:
    t = Text()
    t.append(f"{value}\n", style=f"bold {color}")
    t.append(label, style="grey62")
    return t


def render_header(st: State) -> Panel:
    c = st.counts()
    tin, tout, cost, calls, ai, ext = st.totals()
    projs = len({a.project for a in st.agents.values()})
    gp = st.global_pct()
    session = time.time() - st.session_start

    title = Text()
    title.append(f" {BRAND} ", style="bold magenta")
    title.append("OverCore", style="bold white")
    title.append("  Monitor  ", style="grey62")
    title.append("DEMO" if DEMO else "LIVE", style="bold black on yellow" if DEMO else "bold black on green")

    tiles = Table.grid(expand=True, padding=(0, 2))
    for _ in range(10):
        tiles.add_column(justify="center", ratio=1)
    tiles.add_row(
        stat_tile("PROJETOS", str(projs), "cyan"),
        stat_tile("ATIVOS", str(sum(c[s] for s in ACTIVE)), "green"),
        stat_tile("SUBAGENTES", str(st.subagents()), "blue"),
        stat_tile("CONCLUIDOS", str(c["done"]), "bright_green"),
        stat_tile("AGUARDANDO", str(c["waiting"]), "grey70"),
        stat_tile("FALHAS", str(c["error"]), "red"),
        stat_tile("TOKENS", human_num(tin + tout), "magenta"),
        stat_tile("CUSTO ~", f"${cost:0.3f}", "yellow"),
        stat_tile("CHAMADAS IA", str(calls), "cyan"),
        stat_tile("SESSAO", fmt_dur(session), "white"),
    )

    gbar = Text()
    gbar.append("PROGRESSO GLOBAL  ", style="grey62")
    gbar.append(bar(gp, 46, "magenta"))
    gbar.append(f"  {gp*100:0.0f}%", style="bold magenta")
    gbar.append(f"   IA {fmt_dur(ai)} · externo {fmt_dur(ext)}", style="grey54")

    body = Group(Align.center(title), Text(), tiles, Text(), gbar)
    return Panel(body, box=box.ROUNDED, border_style="magenta", padding=(1, 2))


def render_agent_card(a: Agent) -> Panel:
    emoji, color, label = STATUS.get(a.status, ("•", "white", a.status))
    live = a.status in ACTIVE

    head = Text()
    if a.overcore:
        head.append(BRAND + " ", style="bold magenta")
    if a.status in ("running", "processing", "init"):
        head.append(SPIN[int(time.time() * 12) % len(SPIN)] + " ", style=color)
    else:
        head.append(emoji + " ", style=color)
    head.append(a.name, style="bold white" if a.overcore else "grey82")
    if a.parent:
        head.append(f"  ↳ sub de {a.parent}", style="grey50")
    head.append(f"   {label.upper()}", style=f"bold {color}")
    if a.overcore:
        head.append("  OVERCORE", style="bold magenta")

    sub = Text()
    sub.append((a.skill or "—") + "   ", style="cyan")
    if a.tool:
        sub.append(f"{TOOL_ICON.get(a.tool,'•')} {a.tool}", style="yellow")

    pb = Text()
    if a.steps > 0:
        pb.append(bar(a.pct, 22, color))
        pb.append(f" {a.pct*100:0.0f}%", style=f"bold {color}")
        pb.append(f"   etapa {a.step}/{a.steps}", style="grey62")
    elif a.status in ACTIVE:
        pb.append(indet_bar(22, color))
        pb.append("   trabalhando…", style="grey62")
    else:
        pb.append(bar(a.pct, 22, color))
        pb.append(f" {a.pct*100:0.0f}%", style=f"bold {color}")

    meta = Table.grid(expand=True, padding=(0, 1))
    meta.add_column(ratio=1)
    meta.add_column(ratio=1)
    meta.add_column(ratio=1)
    eta = a.eta
    meta.add_row(
        Text(f"⏱ {fmt_dur(a.elapsed)}", style="white"),
        Text(f"ETA {fmt_dur(eta) if eta else '--'}", style="grey70"),
        Text(f"{TOOL_ICON.get('Agent')} {a.model}", style="grey62"),
    )
    meta.add_row(
        Text(f"▸ {human_num(a.tokens)} tok", style="magenta"),
        Text(f"~${a.cost:0.3f}", style="yellow"),
        Text(f"{a.api_calls} chamadas", style="cyan"),
    )

    last = Text(f"→ {a.last}"[:64], style="grey74") if a.last else Text("")

    logs = Text()
    for ts, msg in list(a.logs)[-3:]:
        logs.append(f"  {time.strftime('%H:%M:%S', time.localtime(ts))} ", style="grey42")
        logs.append(f"{msg}\n"[:70], style="grey62")

    grp = Group(head, sub, Text(), pb, Text(), meta, last, logs)
    border = "magenta" if a.overcore else (color if live else "grey37")
    return Panel(grp, box=box.HEAVY if a.overcore else box.ROUNDED, border_style=border, padding=(0, 1),
                 title=f"[grey50]{a.project}[/]", title_align="left")


def render_done_chip(a: Agent) -> Text:
    emoji, color, _ = STATUS.get(a.status, ("✅", "green", ""))
    t = Text()
    t.append(f"{emoji} ", style=color)
    t.append(f"{a.name[:16]:<16}", style="grey78")
    t.append(f" {fmt_dur(a.elapsed):>6}", style="grey54")
    t.append(f"  {a.skill}"[:22], style="grey42")
    return t


def render_project_column(project: str, agents: list[Agent], st: State) -> Panel:
    actives = [a for a in agents if a.status in ACTIVE]
    dones = [a for a in agents if a.status in ("done", "error")]

    blocks = []
    if actives:
        for a in actives[:3]:
            blocks.append(render_agent_card(a))
    else:
        blocks.append(Align.center(Text("sem agente ativo", style="grey42")))

    if dones:
        blocks.append(Text("\n CONCLUIDOS NESTA SESSAO", style="bold grey54"))
        for a in dones[-4:]:
            blocks.append(render_done_chip(a))

    # mini timeline do projeto
    evs = [e for e in st.timeline if e[3] == project][-4:]
    if evs:
        blocks.append(Text("\n O QUE ACONTECEU", style="bold grey54"))
        for ts, icon, text, _ in evs:
            line = Text()
            line.append(f" {time.strftime('%H:%M:%S', time.localtime(ts))} ", style="grey42")
            line.append(Text.from_markup(f"{icon} {text}"))
            blocks.append(line)

    n_act = len(actives)
    n_oc = sum(1 for a in agents if a.overcore)
    title = Text()
    if n_oc:
        title.append(f"{BRAND} ", style="bold magenta")
    title.append(f"{project} ", style="bold white")
    title.append(f" {n_act} ativo{'s' if n_act != 1 else ''} ", style="black on green" if n_act else "grey50")
    if n_oc:
        title.append(f" {n_oc} OverCore ", style="black on magenta")
    border = "magenta" if (n_oc and n_act) else "grey30"
    return Panel(Group(*blocks), box=box.ROUNDED, border_style=border,
                 title=title, title_align="left", padding=(0, 1))


def render_timeline(st: State) -> Panel:
    rows = []
    for ts, icon, text, _ in list(st.timeline)[-16:][::-1]:
        line = Text()
        line.append(f"{time.strftime('%H:%M:%S', time.localtime(ts))} ", style="grey42")
        line.append(Text.from_markup(f"{icon} {text}"))
        rows.append(line)
    return Panel(Group(*rows) if rows else Text("aguardando eventos…", style="grey42"),
                 title="[b]Timeline[/]  eventos ao vivo", title_align="left",
                 border_style="cyan", box=box.ROUNDED, padding=(0, 1))


def render_stats(st: State) -> Panel:
    tin, tout, cost, calls, ai, ext = st.totals()
    tab = Table.grid(expand=True, padding=(0, 1))
    tab.add_column(style="grey62")
    tab.add_column(justify="right")

    cpu = mem = "n/a"
    if psutil:
        try:
            cpu = f"{psutil.cpu_percent():0.0f}%"
            mem = f"{psutil.virtual_memory().percent:0.0f}%"
        except Exception:
            pass
    tab.add_row("CPU", Text(cpu, style="green"))
    tab.add_row("Memoria", Text(mem, style="green"))
    tab.add_row("Tempo medio/agente", Text(fmt_dur(st.avg_time()), style="white"))
    tab.add_row("Tempo em IA", Text(fmt_dur(ai), style="cyan"))
    tab.add_row("Tempo externo", Text(fmt_dur(ext), style="cyan"))
    tab.add_row("Tokens (in/out)", Text(f"{human_num(tin)}/{human_num(tout)}", style="magenta"))
    tab.add_row("Custo estimado", Text(f"${cost:0.4f}", style="bold yellow"))

    rank = Text("\nMAIS LENTOS\n", style="bold grey54")
    for i, a in enumerate(st.slowest(3), 1):
        rank.append(f" {i}. {a.name[:18]:<18} ", style="grey74")
        rank.append(f"{fmt_dur(a.elapsed)}\n", style="red")

    return Panel(Group(tab, rank), title="[b]Metricas[/]", title_align="left",
                 border_style="yellow", box=box.ROUNDED, padding=(0, 1))


def build_layout(st: State) -> Layout:
    root = Layout(name="root")
    root.split_column(
        Layout(render_header(st), name="header", size=9),
        Layout(name="body", ratio=1),
    )
    root["body"].split_row(
        Layout(name="projects", ratio=3),
        Layout(name="side", ratio=1),
    )
    projs = st.by_project()
    cols = [render_project_column(p, ags, st) for p, ags in projs.items()] or \
           [Panel(Align.center(Text("aguardando agentes…", style="grey42")), border_style="grey30")]
    root["projects"].update(Columns(cols, equal=True, expand=True))
    root["side"].split_column(
        Layout(render_timeline(st), name="tl", ratio=2),
        Layout(render_stats(st), name="stats", size=16),
    )
    return root


# ------------------------------------------------------------------ fontes -----

def tail_events(path: str, q: Queue, stop: threading.Event):
    """Le o JSONL do inicio e depois faz tail (novas linhas) em tempo real."""
    pos = 0
    while not stop.is_set():
        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    f.seek(pos)
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                q.put(json.loads(line))
                            except json.JSONDecodeError:
                                pass
                    pos = f.tell()
        except Exception:
            pass
        time.sleep(0.3)


def demo_feed(q: Queue, stop: threading.Event):
    """Gera uma sessao simulada e realista do OverCore, em loop."""
    projects = ["(demo) loja-exemplo", "(demo) api-teste", "(demo) site-fake"]
    # (nome, skill, modelo, tools, overcore?) — rastreamos TUDO; True = destaque OverCore
    catalog = [
        ("Router/Supervisor", "/overcore", "sonnet", ["Read", "Grep", "Task"], True),
        ("Design (Atelier)", "/atelier", "opus", ["Read", "Grep", "Write", "Edit"], True),
        ("SafeGate", "/safegate audit", "sonnet", ["Grep", "Bash", "Read"], True),
        ("Researcher", "/overcore contribuir", "haiku", ["WebFetch", "Read"], True),
        ("Plan", "/planejar", "opus", ["Read", "Grep"], True),
        # nao-OverCore (Claude Code "normal") — aparecem sem destaque:
        ("Claude Code", "chat", "sonnet", ["Read", "Edit", "Bash"], False),
        ("Testes", "pytest", "haiku", ["Bash", "Read"], False),
        ("Refactor", "edit", "sonnet", ["Read", "Edit", "Grep"], False),
    ]
    msgs = ["mapeando arquivos", "auditando dependencias", "checklist OWASP",
            "refatorando modulo", "rodando testes", "lendo indice de skills",
            "polindo estados de hover", "verificando LGPD", "montando plano",
            "corrigindo race condition", "gerando croqui", "endurecendo config"]
    counter = [0]

    def new_agent(parent=None):
        counter[0] += 1
        name, skill, model, tools, oc = random.choice(catalog)
        aid = f"a{counter[0]}"
        proj = random.choice(projects)
        steps = random.randint(4, 9)
        q.put({"type": "agent_start", "id": aid, "agent": name, "project": proj,
               "skill": skill, "model": model, "steps": steps, "parent": parent, "overcore": oc})
        return {"id": aid, "tools": tools, "model": model, "steps": steps,
                "step": 0, "next": time.time() + random.uniform(0.4, 1.2),
                "proj": proj, "name": name}

    live = [new_agent() for _ in range(random.randint(2, 3))]
    while not stop.is_set():
        now = time.time()
        for ag in list(live):
            if now < ag["next"]:
                continue
            ag["next"] = now + random.uniform(0.5, 1.6)
            if ag["step"] < ag["steps"]:
                ag["step"] += 1
                tool = random.choice(ag["tools"])
                q.put({"type": "tool", "id": ag["id"], "tool": tool,
                       "message": random.choice(msgs),
                       "status": random.choice(["running", "processing"])})
                q.put({"type": "progress", "id": ag["id"], "step": ag["step"], "steps": ag["steps"]})
                q.put({"type": "tokens", "id": ag["id"], "model": ag["model"],
                       "in": random.randint(400, 2600), "out": random.randint(120, 900),
                       "calls": 1, "dt": random.uniform(0.3, 2.4)})
                if random.random() < 0.15:
                    q.put({"type": "api", "id": ag["id"], "dt": random.uniform(0.1, 0.6),
                           "message": f"resposta em {random.randint(120,480)}ms"})
                if random.random() < 0.08:
                    live.append(new_agent(parent=ag["name"]))
            else:
                status = "error" if random.random() < 0.07 else "done"
                if status == "error":
                    q.put({"type": "error", "id": ag["id"], "message": "timeout na dependencia"})
                else:
                    q.put({"type": "agent_done", "id": ag["id"], "status": "done"})
                live.remove(ag)
        if len(live) < 2 and random.random() < 0.5:
            live.append(new_agent())
        time.sleep(0.12)


# -------------------------------------------------------------------- main -----

DEMO = False


def main():
    global DEMO
    ap = argparse.ArgumentParser(description="OverCore Monitor")
    ap.add_argument("--demo", action="store_true", help="sessao simulada")
    ap.add_argument("--events", default=None, help="arquivo JSONL de eventos (hooks)")
    ap.add_argument("--snapshot", action="store_true", help="renderiza 1 quadro e sai")
    ap.add_argument("--fps", type=float, default=8.0)
    args = ap.parse_args()

    DEMO = args.demo or not args.events
    st = State()
    q: Queue = Queue()
    stop = threading.Event()

    if args.events:
        threading.Thread(target=tail_events, args=(args.events, q, stop), daemon=True).start()
    if DEMO:
        threading.Thread(target=demo_feed, args=(q, stop), daemon=True).start()

    def drain():
        while True:
            try:
                st.apply(q.get_nowait())
            except Empty:
                break

    if args.snapshot:
        # avanca a demo ~2.5s e imprime 1 quadro (teste sem terminal interativo)
        time.sleep(2.5)
        drain()
        Console(width=150).print(build_layout(st))
        stop.set()
        return

    console = Console()
    try:
        with Live(build_layout(st), console=console, screen=True,
                  refresh_per_second=args.fps, redirect_stderr=False) as live:
            while not stop.is_set():
                drain()
                live.update(build_layout(st))
                time.sleep(1.0 / args.fps)
    except KeyboardInterrupt:
        pass
    finally:
        stop.set()
        console.print("[grey62]OverCore Monitor encerrado.[/]")


if __name__ == "__main__":
    main()
