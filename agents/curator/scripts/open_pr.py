#!/usr/bin/env python3
"""Prepare (and optionally open) the PR for a promoted contribution.

Default is --dry-run: assembles the PR "package" (branch, title, file list, body)
and prints it, touching neither git nor GitHub. With --push it creates the branch
`curator/<id>`, stages ONLY the promoted skill + index (never `git add -A`), commits,
pushes, and opens the PR via the GitHub API. Merge stays 100% human.

Env for --push:
  CURATOR_PR_TOKEN     fine-grained PAT: Contents:write + Pull requests:write on the hub repo
  CURATOR_GITHUB_REPO  e.g. Weriton-DataOps/agent-skills-hub (or feeds.github_repo in config)

Usage:
  python open_pr.py --id <contrib_id>            # dry-run: show the PR package
  python open_pr.py --id <contrib_id> --push     # create branch, commit, push, open PR
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import urllib.error
import urllib.request

from loop_common import ROOT, load_config, read_json, run_dir


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, check=True,
                          capture_output=True, text=True).stdout.strip()


def _paths_for(slug: str) -> list[str]:
    return [f"skills/{slug}/SKILL.md", "docs/indices/skills_index.json"]


def _open_pr_api(repo: str, token: str, branch: str, base: str, title: str, body: str) -> None:
    url = f"https://api.github.com/repos/{repo}/pulls"
    payload = json.dumps({"title": title, "head": branch, "base": base, "body": body, "draft": True}).encode()
    req = urllib.request.Request(url, data=payload, method="POST", headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "curator-agent",
        "Content-Type": "application/json",
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        print(f"PR aberto (draft): {data.get('html_url')}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Prepare/open the PR for a promoted contribution.")
    ap.add_argument("--id", required=True)
    ap.add_argument("--push", action="store_true", help="create branch, commit, push, open PR (needs token)")
    ap.add_argument("--base", default="main", help="base branch (default main)")
    args = ap.parse_args()

    rd = run_dir(args.id)
    state = read_json(rd / "run-state.json", default={})
    if not state:
        print(f"run não encontrado: {rd}")
        return
    slug = state["slug"]
    branch = f"curator/{args.id}"
    title = f"curator: promove {slug}"
    body = (rd / "pr-body.md").read_text(encoding="utf-8") if (rd / "pr-body.md").exists() else title
    paths = _paths_for(slug)

    if not args.push:
        print("== PR PACKAGE (dry-run — git e GitHub intocados) ==")
        print(f"branch : {branch}")
        print(f"base   : {args.base}")
        print(f"title  : {title}")
        print(f"files  : {', '.join(paths)}")
        print("---- pr-body.md ----")
        print(body)
        print("--------------------")
        print("rode com --push (e o token CURATOR_PR_TOKEN) para abrir de verdade.")
        return

    cfg = load_config()
    repo = os.environ.get("CURATOR_GITHUB_REPO") or cfg.get("feeds", {}).get("github_repo", "")
    token = os.environ.get("CURATOR_PR_TOKEN", "")
    if not token or not repo or "<" in repo:
        print("[open_pr] CURATOR_PR_TOKEN / repo não configurados — abortando push.")
        return

    # only the promoted files, never `git add -A`
    _git("checkout", "-b", branch)
    _git("add", *paths)
    _git("commit", "-m", f"{title}\n\nvia contribuição {args.id}")
    _git("push", "-u", "origin", branch)
    try:
        _open_pr_api(repo, token, branch, args.base, title, body)
    except urllib.error.HTTPError as exc:
        print(f"[open_pr] erro HTTP {exc.code} ao abrir PR: {exc.reason} (branch já foi empurrado)")


if __name__ == "__main__":
    main()
