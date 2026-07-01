#!/usr/bin/env python3
"""Open a contribution Issue (the write-path) from raw text — no git access needed.

Used by the `/overcore contribuir` command in VS Code and by Pipeline Studio agents.
Order of preference:
  1. token via env (CURATOR_ISSUES_TOKEN) → GitHub REST API  (the "token-robô")
  2. an authenticated `gh` CLI                → gh issue create
  3. neither → prints the payload + instructions (dry)

Usage:
  python contribute.py --title "..." --origin vscode-claude --tags "a,b" --file raw.md
  echo "texto..." | python contribute.py --title "..." --origin pipeline-studio:designer
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

from loop_common import load_config

LABEL = "contribution"


def _repo() -> str:
    return os.environ.get("CURATOR_GITHUB_REPO") or load_config().get("feeds", {}).get("github_repo", "")


def _body(raw: str, origin: str, tags: list[str]) -> str:
    return (
        f"{raw.strip()}\n\n"
        f"---\n"
        f"origin: {origin}\n"
        f"tags: {', '.join(tags)}\n"
        f"_enviado via OverCore `/overcore contribuir`_\n"
    )


def _via_api(repo: str, token: str, title: str, body: str) -> str | None:
    url = f"https://api.github.com/repos/{repo}/issues"
    payload = json.dumps({"title": title, "body": body, "labels": [LABEL]}).encode()
    req = urllib.request.Request(url, data=payload, method="POST", headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "overcore-contribute",
        "Content-Type": "application/json",
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8")).get("html_url")


def _via_gh(repo: str, title: str, body: str) -> str | None:
    try:
        out = subprocess.run(
            ["gh", "issue", "create", "--repo", repo, "--title", title, "--body", body, "--label", LABEL],
            check=True, capture_output=True, text=True)
        return out.stdout.strip().splitlines()[-1] if out.stdout.strip() else "(criada)"
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def main() -> None:
    ap = argparse.ArgumentParser(description="Abre uma Issue de contribuição a partir de texto bruto.")
    ap.add_argument("--title", required=True)
    ap.add_argument("--origin", default="human")
    ap.add_argument("--tags", default="")
    ap.add_argument("--file", help="arquivo com o texto bruto; senão lê o stdin")
    args = ap.parse_args()

    raw = open(args.file, encoding="utf-8").read() if args.file else sys.stdin.read()
    if not raw.strip():
        ap.error("texto bruto vazio (use --file ou pipe no stdin)")

    repo = _repo()
    if not repo or "<" in repo:
        ap.error("repo não configurado (CURATOR_GITHUB_REPO ou feeds.github_repo no config)")

    tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    title = f"[contrib] {args.title.strip()}"
    body = _body(raw, args.origin, tags)

    token = os.environ.get("CURATOR_ISSUES_TOKEN", "")
    if token:
        try:
            url = _via_api(repo, token, title, body)
            print(f"Issue criada (API): {url}")
            return
        except urllib.error.HTTPError as exc:
            print(f"[contribute] erro HTTP {exc.code} via API: {exc.reason} — tentando gh…")

    url = _via_gh(repo, title, body)
    if url:
        print(f"Issue criada (gh): {url}")
        return

    print("[contribute] sem token e sem gh autenticado — nada foi enviado.")
    print("Configure CURATOR_ISSUES_TOKEN (Issues:write) ou rode `gh auth login`.")
    print(f"--- payload que seria enviado para {repo} ---")
    print(f"título: {title}")
    print(body)


if __name__ == "__main__":
    main()
