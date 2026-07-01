#!/usr/bin/env python3
"""Ingest contributions from GitHub Issues labelled `contribution` (production path).

Reads a fine-grained token from env (Issues:read only) and pulls open issues with
the `contribution` label into queue/inbox.jsonl. Stdlib-only (urllib). If no token
is configured it explains what to do and exits cleanly, so it never crashes a demo.

Env:
  CURATOR_ISSUES_TOKEN   fine-grained PAT, scope: Issues (read) on the hub repo
  CURATOR_GITHUB_REPO    e.g. Weriton-DataOps/agent-skills-hub  (or read from config)
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

from loop_common import INBOX, append_jsonl, load_config, now_iso, read_jsonl, short_id


def _origin_from_body(body: str, fallback: str = "human") -> str:
    for line in (body or "").splitlines():
        low = line.lower()
        if "origin:" in low:
            return line.split(":", 1)[1].strip() or fallback
    return fallback


def fetch_issues(repo: str, token: str) -> list[dict]:
    url = f"https://api.github.com/repos/{repo}/issues?labels=contribution&state=open&per_page=100"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "curator-agent",
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> None:
    cfg = load_config()
    feeds = cfg.get("feeds", {})
    repo = os.environ.get("CURATOR_GITHUB_REPO") or feeds.get("github_repo", "")
    token = os.environ.get(feeds.get("token_env", "CURATOR_ISSUES_TOKEN"), "") \
        or os.environ.get("CURATOR_ISSUES_TOKEN", "")

    if not token or not repo or "<" in repo:
        print("[ingest_issues] token/repo não configurados — pulando (use ingest_local.py p/ testar).")
        print("  defina CURATOR_ISSUES_TOKEN e CURATOR_GITHUB_REPO (ou feeds.github_repo no config).")
        return

    try:
        issues = fetch_issues(repo, token)
    except urllib.error.HTTPError as exc:
        print(f"[ingest_issues] erro HTTP {exc.code}: {exc.reason}")
        return
    except Exception as exc:  # noqa: BLE001
        print(f"[ingest_issues] falha ao buscar issues: {exc}")
        return

    existing = {r.get("contrib_id") for r in read_jsonl(INBOX)}
    added = 0
    for issue in issues:
        if "pull_request" in issue:  # issues endpoint also returns PRs
            continue
        number = issue.get("number")
        html_url = issue.get("html_url", "")
        contrib_id = short_id("gh", str(number), html_url)
        if contrib_id in existing:
            continue
        user = issue.get("user", {}) or {}
        body = issue.get("body", "") or ""
        rec = {
            "contrib_id": contrib_id,
            "source": "github-issue",
            "issue_number": number,
            "issue_url": html_url,
            "title": (issue.get("title") or "").strip(),
            "raw_text": body.strip(),
            "author_login": user.get("login", ""),
            "author_display": user.get("login", ""),
            "origin": _origin_from_body(body, "human"),
            "tags": [lbl.get("name") for lbl in issue.get("labels", []) if lbl.get("name") != "contribution"],
            "submitted_at": issue.get("created_at", now_iso()),
            "attempts": 0,
            "last_status": "ingested",
        }
        append_jsonl(INBOX, rec)
        existing.add(contrib_id)
        added += 1

    print(f"[ingest_issues] {added} nova(s) contribuição(ões) de {repo} → {INBOX}")


if __name__ == "__main__":
    main()
