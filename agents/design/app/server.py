#!/usr/bin/env python3
"""Fila do Curador — aplicação real (etapa 6 do wizard do Atelier).

Servidor stdlib-only que serve a UI aprovada no refinado e a alimenta com DADOS VIVOS:
GitHub Issues (via gh), o índice de skills, PRs abertos e a fila local do curador.
O botão "Rodar ciclo" executa run_cycle.py de verdade.

Rodar:  python agents/design/app/server.py   →  http://localhost:8765
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

APP = Path(__file__).resolve().parent
ROOT = APP.parents[2]
INDEX = ROOT / "docs" / "indices" / "skills_index.json"
INBOX = ROOT / "agents" / "curator" / "queue" / "inbox.jsonl"
RUN_CYCLE = ROOT / "agents" / "curator" / "scripts" / "run_cycle.py"
PORT = 8765


def _cfg_repo() -> str:
    try:
        cfg = json.loads((ROOT / "agents/curator/orchestration/config.json").read_text(encoding="utf-8"))
        return cfg.get("feeds", {}).get("github_repo", "")
    except Exception:
        return ""


REPO = _cfg_repo() or "Weriton-DataOps/agent-skills-hub"


def _gh(*args: str) -> list | dict | None:
    try:
        out = subprocess.run(["gh", *args], capture_output=True, text=True,
                             encoding="utf-8", errors="replace", timeout=30)
        return json.loads(out.stdout) if out.returncode == 0 and out.stdout.strip() else None
    except Exception:
        return None


def estado() -> dict:
    idx = json.loads(INDEX.read_text(encoding="utf-8"))
    promoted = {}  # issue number -> index entry
    for x in idx:
        via = str(x.get("contributed_via", ""))
        m = re.search(r"/issues/(\d+)$", via)
        if m:
            promoted[int(m.group(1))] = x

    issues = _gh("issue", "list", "--repo", REPO, "--label", "contribution", "--state", "all",
                 "--json", "number,title,state,author,url,createdAt") or []
    fila = []
    abertas = aguardando = 0
    for i in sorted(issues, key=lambda x: -x["number"]):
        n = i["number"]
        if n in promoted:
            st, stc = "Promovida", "ok"
            acao = {"label": "Ver skill", "url": f"https://github.com/{REPO}/tree/main/{promoted[n]['path']}"}
        elif i["state"] == "OPEN":
            st, stc = "Aguardando juiz", "warn"
            acao = {"label": "Avaliar", "url": i["url"]}
            abertas += 1
            aguardando += 1
        else:
            st, stc = "Fechada", "err"
            acao = {"label": "Ver issue", "url": i["url"]}
        fila.append({"n": n, "titulo": re.sub(r"^\[contrib\]\s*", "", i["title"]),
                     "origem": (i.get("author") or {}).get("login", "—"),
                     "estado": st, "cor": stc, "acao": acao})

    promovidas = sorted(
        [{"skill": x["id"], "via": f"#{k}", "data": x.get("date_added", "")} for k, x in promoted.items()],
        key=lambda p: p["data"], reverse=True)[:6]

    prs = _gh("pr", "list", "--repo", REPO, "--state", "open", "--json", "number,title") or []
    ciclo = "nunca"
    if INBOX.exists():
        ciclo = datetime.fromtimestamp(INBOX.stat().st_mtime).strftime("%d/%m %H:%M")

    return {
        "gerado_em": datetime.now(timezone.utc).strftime("%H:%M:%SZ"),
        "repo": REPO,
        "stats": {"abertas": abertas, "aguardando": aguardando,
                  "promovidas": len(promoted), "indice": len(idx)},
        "fila": fila,
        "promovidas": promovidas,
        "saude": {"ultimo_ciclo": ciclo, "prs": [{"n": p["number"], "titulo": p["title"]} for p in prs],
                  "pr_count": len(prs)},
    }


def rodar_ciclo() -> str:
    try:
        out = subprocess.run([sys.executable, str(RUN_CYCLE)], cwd=ROOT, capture_output=True,
                             text=True, encoding="utf-8", errors="replace", timeout=300)
        tail = "\n".join(((out.stdout or "") + (out.stderr or "")).strip().splitlines()[-14:])
        return tail or "(ciclo sem saída)"
    except Exception as exc:  # noqa: BLE001
        return f"falha ao rodar o ciclo: {exc}"


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):  # silencioso
        pass

    def _send(self, code: int, body: bytes, ctype: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send(200, (APP / "index.html").read_bytes(), "text/html; charset=utf-8")
        elif self.path == "/api/estado":
            try:
                body = json.dumps(estado(), ensure_ascii=False).encode("utf-8")
                self._send(200, body, "application/json; charset=utf-8")
            except Exception as exc:  # noqa: BLE001
                self._send(500, json.dumps({"erro": str(exc)}).encode(), "application/json")
        else:
            self._send(404, b"nao existe", "text/plain")

    def do_POST(self):
        if self.path == "/api/ciclo":
            body = json.dumps({"saida": rodar_ciclo()}, ensure_ascii=False).encode("utf-8")
            self._send(200, body, "application/json; charset=utf-8")
        else:
            self._send(404, b"nao existe", "text/plain")


if __name__ == "__main__":
    print(f"Fila do Curador viva em http://localhost:{PORT}  (repo: {REPO})")
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
