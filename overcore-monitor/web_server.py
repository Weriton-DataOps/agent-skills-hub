#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OverCore Monitor · Web — serve o painel no navegador (link localhost).

Reaproveita todo o nucleo (State/demo/hooks) de overcore_monitor.py, expoe /state em
JSON e serve o dashboard HTML que se atualiza sozinho (polling). Sem dependencias alem
da stdlib (e do 'rich', que so e importado de carona; nao e usado aqui).

Uso:
    python web_server.py --demo                 # sessao simulada
    python web_server.py --events eventos.jsonl # ao vivo (hooks)
    python web_server.py --demo --port 8770

Depois abra:  http://localhost:8770/
"""
import argparse
import json
import os
import threading
import time
from queue import Queue, Empty
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

import overcore_monitor as om
import daily_report
import live_report
import transcript_source

HERE = os.path.dirname(os.path.abspath(__file__))

state = om.State()
q: Queue = Queue()
stop = threading.Event()

# painel DO DIA (agregacao dos transcripts), atualizado em background
_day = {"t": 0.0, "d": {"loading": True}}
# painel de EXECUCAO AO VIVO (so o que roda agora), atualizado rapido
_live = {"t": 0.0, "d": {"loading": True}}


def drain_loop():
    while not stop.is_set():
        try:
            while True:
                state.apply(q.get_nowait())
        except Empty:
            pass
        time.sleep(0.05)


def day_refresh_loop():
    while not stop.is_set():
        try:
            _day["d"] = daily_report.build_daily()
            _day["t"] = time.time()
        except Exception as e:
            _day["d"] = {"error": str(e)}
        stop.wait(5)


def live_refresh_loop():
    while not stop.is_set():
        try:
            _live["d"] = live_report.build_live()
            _live["t"] = time.time()
        except Exception as e:
            _live["d"] = {"error": str(e)}
        stop.wait(2)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):  # silencia o log de acesso
        pass

    def _send(self, code, body, ctype):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def do_GET(self):
        path = self.path.split("?")[0]
        pages = {"/": "dia.html", "/dia": "dia.html", "/dia.html": "dia.html",
                 "/exec": "exec.html", "/exec.html": "exec.html",
                 "/live": "index.html", "/index.html": "index.html"}
        if path in pages:
            try:
                with open(os.path.join(HERE, pages[path]), "rb") as f:
                    self._send(200, f.read(), "text/html; charset=utf-8")
            except Exception as e:  # pragma: no cover
                self._send(500, str(e), "text/plain; charset=utf-8")
        elif path == "/state":
            try:
                self._send(200, json.dumps(state.snapshot()), "application/json")
            except Exception as e:
                self._send(500, json.dumps({"error": str(e)}), "application/json")
        elif path == "/day":
            self._send(200, json.dumps(_day["d"], default=lambda o: None), "application/json")
        elif path == "/live-data":
            self._send(200, json.dumps(_live["d"], default=lambda o: None), "application/json")
        else:
            self._send(404, "not found", "text/plain")


def main():
    ap = argparse.ArgumentParser(description="OverCore Monitor Web")
    ap.add_argument("--demo", action="store_true", help="feed simulado (monitor ao vivo)")
    ap.add_argument("--events", default=None, help="feed do JSONL dos hooks")
    ap.add_argument("--transcripts", nargs="?", const=True, default=None,
                    help="feed dos transcripts do Claude Code (opcional: caminho da pasta projects)")
    ap.add_argument("--port", type=int, default=8770)
    args = ap.parse_args()

    om.DEMO = bool(args.demo)
    if args.events:
        threading.Thread(target=om.tail_events, args=(args.events, q, stop), daemon=True).start()
    elif args.transcripts:
        root = None if args.transcripts is True else args.transcripts
        threading.Thread(target=transcript_source.feed_transcripts, args=(q, stop, root), daemon=True).start()
    elif args.demo:
        threading.Thread(target=om.demo_feed, args=(q, stop), daemon=True).start()
    threading.Thread(target=drain_loop, daemon=True).start()
    threading.Thread(target=day_refresh_loop, daemon=True).start()
    threading.Thread(target=live_refresh_loop, daemon=True).start()

    srv = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"OverCore Monitor Web  ->  por projeto: http://localhost:{args.port}/   |   execução ao vivo: http://localhost:{args.port}/exec")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        stop.set()
        srv.shutdown()


if __name__ == "__main__":
    main()
