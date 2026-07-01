#!/usr/bin/env python3
"""Shared helpers for the Curator agent.

The Curator is the internal-discovery twin of ``agents/researcher/``: it turns
raw-text contributions (from GitHub Issues labelled ``contribution``) into
reviewable SKILL.md drafts and opens PRs. Humans decide the merge.

Everything here is stdlib-only so the loop runs on a clean Python 3.11 with no
install step.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

# Windows consoles/pipes default to cp1252 and crash on box-drawing/emoji in prints.
# Force UTF-8 output everywhere the curator scripts run.
try:  # pragma: no cover - platform dependent
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
def find_root(start: Path | None = None) -> Path:
    """Walk up until we find the repo root (the folder holding docs/indices)."""
    here = (start or Path(__file__)).resolve()
    for parent in [here, *here.parents]:
        if (parent / "docs" / "indices" / "skills_index.json").exists():
            return parent
    # Fallback: agents/curator/scripts/loop_common.py -> repo root is parents[3]
    return Path(__file__).resolve().parents[3]


ROOT = find_root()
CURATOR = ROOT / "agents" / "curator"
QUEUE = CURATOR / "queue"
RUNS = CURATOR / "runs"
LEDGERS = CURATOR / "ledgers"
REPORTS = CURATOR / "reports"
CONFIG_PATH = CURATOR / "orchestration" / "config.json"
INDEX_PATH = ROOT / "docs" / "indices" / "skills_index.json"

INBOX = QUEUE / "inbox.jsonl"
PARKED = QUEUE / "parked.jsonl"
DONE = QUEUE / "done.jsonl"
QUARANTINE = QUEUE / "quarantine.jsonl"

TERMINAL_STATUSES = {"done", "rejected", "parked", "merged"}


# ---------------------------------------------------------------------------
# Time / ids / slugs
# ---------------------------------------------------------------------------
def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def short_id(*parts: str) -> str:
    h = hashlib.sha1("::".join(parts).encode("utf-8")).hexdigest()
    return h[:10]


def slugify(text: str, max_len: int = 48) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text[:max_len].strip("-") or "contribution"


# ---------------------------------------------------------------------------
# Text similarity (mirrors agents/researcher/scripts/novelty_check.py)
# ---------------------------------------------------------------------------
STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "from", "into", "when",
    "agent", "agents", "skill", "skills", "context", "use", "using", "used",
    "you", "your", "how", "what", "why", "para", "como", "com", "que", "uma",
    "dos", "das", "por", "não", "nao", "the", "and", "code", "file", "files",
}


def tokens(text: str) -> set[str]:
    raw = re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{2,}", (text or "").lower())
    return {t.replace("_", "-") for t in raw if t not in STOPWORDS}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


# ---------------------------------------------------------------------------
# IO
# ---------------------------------------------------------------------------
def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: Any) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def write_jsonl(path: Path, rows: Iterable[dict]) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def append_jsonl(path: Path, row: dict) -> None:
    ensure_dir(path.parent)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# Domain loaders
# ---------------------------------------------------------------------------
def load_config() -> dict:
    return read_json(CONFIG_PATH, default={})


def load_index() -> list[dict]:
    return read_json(INDEX_PATH, default=[])


def run_dir(contrib_id: str) -> Path:
    return RUNS / contrib_id


if __name__ == "__main__":
    print(f"ROOT       = {ROOT}")
    print(f"CURATOR    = {CURATOR}")
    print(f"INDEX      = {INDEX_PATH} (exists={INDEX_PATH.exists()})")
    idx = load_index()
    print(f"index size = {len(idx)}")
