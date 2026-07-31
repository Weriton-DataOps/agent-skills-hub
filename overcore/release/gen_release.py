#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador do RELEASE CANDIDATE determinístico do Overcore (PRB-016).

Produz, em `overcore/release/`, o snapshot mínimo que o atualizador do Studio baixa por SHA
exato e valida antes de ativar:

    overcore/release/
      manifest.json            (manifesto do release — NÃO se auto-hasheia, sem campo `commit`)
      catalog.json             (catálogo PROMOVIDO: status draft -> active)
      catalog.schema.json      (schema canônico, cópia)
      skill-dependencies.json  (projeção de dependências, cópia)
      skills-meta.json         (índice de skills PODADO: só as referenciadas, com risco/runtime)
      skills/<id>/SKILL.md      (cada SKILL.md referenciado pelo catálogo)

Regras:
  - determinístico: `publishedAt` é FIXO (não muda por execução); listas ordenadas.
  - a identidade autoritativa do snapshot é o SHA Git (obtido por ls-remote/fetch), NÃO um campo
    interno; por isso o manifesto NÃO tem `commit` e NÃO inclui o próprio hash nos checksums.
  - todo arquivo consumido (exceto o manifesto) tem SHA-256 em `checksums`.
  - conteúdo executável é VAZIO nesta versão.
  - caminhos relativos, normalizados com `/`, sem `..`/absoluto/drive/UNC.
  - a promoção draft->active NÃO altera o catálogo canônico de desenvolvimento; só o release.

Uso:
  python gen_release.py           # (re)gera overcore/release/
  python gen_release.py --check    # verifica sem escrever (!=0 se divergente/desatualizado)
"""
import hashlib
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))          # overcore/release
OVERCORE = os.path.dirname(HERE)                             # overcore
HUB_ROOT = os.path.dirname(OVERCORE)                         # agent-skills-hub
CATALOG_DIR = os.path.join(OVERCORE, "catalog")
SKILLS_DIR = os.path.join(HUB_ROOT, "skills")
SKILLS_INDEX = os.path.join(HUB_ROOT, "docs", "indices", "skills_index.json")
OUT = HERE

# publishedAt FIXO (epoch) — determinismo. Não usar relógio.
RELEASE_PUBLISHED_AT = 1785369600  # 2026-07-31T00:00:00Z — release candidate 0.4.0 (19 agentes do Pipeline)
RELEASE_VERSION = "0.4.0"
RELEASE_CHANGELOG = (
    "OverCore 0.4.0: adiciona os 19 agentes canônicos do Pipeline "
    "(discovery, prd-generator, prd-validator, prd-completo, tech-decisions, spec-generation, spec-enricher, "
    "planner, sprint-validator, coder, evaluator, design-studio, safegate, acceptance-review, intake, harness, "
    "database, security, code-quality) ao lado do oracle-coordinator e subagentes; catálogo promovido a active."
)
MANIFEST_FORMAT_VERSION = "1.0.0"
CHANNEL = "stable"
MIN_STUDIO_VERSION = "0.1.0"


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def load(path):
    with open(path, "rb") as fh:
        return fh.read()


def load_lf(path):
    """Lê e NORMALIZA para LF — o release é determinístico e independente de core.autocrlf do host.
    (Com .gitattributes `-text`, o git guarda esses bytes VERBATIM; o consumidor vê o mesmo hash.)"""
    return load(path).replace(b"\r\n", b"\n")


def load_dep_sources():
    """Projeção canônica de dependências: {id: {requiredSubSkills, ...}}."""
    p = os.path.join(CATALOG_DIR, "skill-dependencies.json")
    return (json.loads(load(p).decode("utf-8")).get("sources") or {})


def referenced_skills(catalog):
    """Skills usadas pelo catálogo + FECHO TRANSITIVO das dependências obrigatórias, para que a
    projeção do release nunca aponte para um SKILL.md ausente."""
    ref = set()
    for e in catalog.get("agents", []):
        sk = e.get("skills", {}) or {}
        for k in ("required", "optional"):
            for s in sk.get(k, []) or []:
                ref.add(s)
        for r in sk.get("onDemand", []) or []:
            if r.get("skill"):
                ref.add(r["skill"])
            if r.get("handoffTo"):
                ref.add(r["handoffTo"])
    deps = load_dep_sources()
    changed = True
    while changed:
        changed = False
        for sid in list(ref):
            for sub in (deps.get(sid, {}) or {}).get("requiredSubSkills", []) or []:
                if sub not in ref:
                    ref.add(sub)
                    changed = True
    return ref


def pruned_dependencies(release_skills, files):
    """Projeção PODADA exatamente para as skills do release: cada entrada tem o SHA-256 do SKILL.md
    DO RELEASE e todas as sub-skills obrigatórias presentes no release (transitivas)."""
    deps = load_dep_sources()
    sources = {}
    for sid in sorted(release_skills):
        entry = deps.get(sid)
        if not entry:
            continue
        reqs = list(entry.get("requiredSubSkills", []) or [])
        # fecho garante presença; confirma explicitamente:
        if not all(r in release_skills for r in reqs):
            raise SystemExit(f"dependência transitiva ausente no release para {sid}: {reqs}")
        sources[sid] = {
            "skillMd": f"skills/{sid}/SKILL.md",
            "skillMdSha256": sha256_bytes(files[f"skills/{sid}/SKILL.md"]),
            "requiredSubSkills": reqs,
        }
    doc = {
        "schemaVersion": "0.3.0",
        "generator": "gen_release.py",
        "note": "Projeção PODADA para as skills do release + dependências transitivas. skillMdSha256 confere o SKILL.md incluído no release; divergência falha fechado na validação.",
        "sources": sources,
    }
    return (json.dumps(doc, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def promote(catalog):
    """Promove entradas draft -> active para uso em produção (não toca o canônico)."""
    c = json.loads(json.dumps(catalog))  # deep copy
    for e in c.get("agents", []):
        if e.get("status") == "draft":
            e["status"] = "active"
    return c


def build_files():
    """Constrói o conteúdo (path_rel -> bytes) do snapshot, determinístico."""
    canonical = json.loads(load(os.path.join(CATALOG_DIR, "catalog.json")).decode("utf-8"))
    promoted = promote(canonical)
    schema = load_lf(os.path.join(CATALOG_DIR, "catalog.schema.json"))
    idx = {s["id"]: s for s in json.loads(load(SKILLS_INDEX).decode("utf-8"))}

    ref = sorted(referenced_skills(canonical))
    meta = {}
    files = {}
    for sid in ref:
        s = idx.get(sid)
        if not s:
            raise SystemExit(f"skill referenciada ausente do índice: {sid}")
        meta[sid] = {
            "risk": s.get("risk"),
            "claudeSupported": (((s.get("plugin", {}) or {}).get("targets", {}) or {}).get("claude") == "supported"),
        }
        md = os.path.join(SKILLS_DIR, sid, "SKILL.md")
        if not os.path.isfile(md):
            raise SystemExit(f"SKILL.md ausente: {sid}")
        files[f"skills/{sid}/SKILL.md"] = load_lf(md)

    files["catalog.json"] = (json.dumps(promoted, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    files["catalog.schema.json"] = schema
    files["skills-meta.json"] = (json.dumps(meta, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    files["skill-dependencies.json"] = pruned_dependencies(set(ref), files)
    return files


def build_manifest(files, channel=CHANNEL):
    declarative = sorted(files.keys())
    checksums = {p: sha256_bytes(files[p]) for p in declarative}
    manifest = {
        "manifestFormatVersion": MANIFEST_FORMAT_VERSION,
        "name": "overcore",
        "version": RELEASE_VERSION,
        "channel": channel,
        "minStudioVersion": MIN_STUDIO_VERSION,
        "catalog": "catalog.json",
        "catalogSchema": "catalog.schema.json",
        "dependencies": "skill-dependencies.json",
        "skillsIndex": "skills-meta.json",
        "declarative": declarative,
        "executable": [],
        "checksums": {p: checksums[p] for p in declarative},
        "changelog": RELEASE_CHANGELOG,
        "publishedAt": RELEASE_PUBLISHED_AT,
    }
    return manifest


ALLOWED_CHANNELS = ("stable", "beta")


def parse_channel(argv):
    if "--channel" in argv:
        i = argv.index("--channel")
        ch = argv[i + 1] if i + 1 < len(argv) else ""
        if ch not in ALLOWED_CHANNELS:
            raise SystemExit(f"canal inválido: {ch!r} (use stable|beta)")
        return ch
    return CHANNEL


def render(channel=CHANNEL):
    files = build_files()
    manifest = build_manifest(files, channel)
    out = dict(files)
    out["manifest.json"] = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    return out


def _skip(fn):
    return fn.endswith((".py", ".pyc")) or fn in ("README.md", ".gitattributes")


def current_on_disk():
    out = {}
    for root, dirs, fs in os.walk(OUT):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for fn in fs:
            if _skip(fn):
                continue
            full = os.path.join(root, fn)
            rel = os.path.relpath(full, OUT).replace("\\", "/")
            out[rel] = load(full)
    return out


def main(argv):
    channel = parse_channel(argv)
    rendered = render(channel)
    if "--check" in argv:
        disk = current_on_disk()
        rk, dk = set(rendered), set(disk)
        if rk != dk:
            print(f"release DESATUALIZADO — arquivos divergentes: falta {sorted(rk - dk)} / sobra {sorted(dk - rk)}")
            return 1
        for k in rk:
            if rendered[k] != disk[k]:
                print(f"release DESATUALIZADO — conteúdo difere em {k} (rode gen_release.py)")
                return 1
        print("release em dia")
        return 0
    # (re)escreve — limpa arquivos gerados sob OUT (preserva .py e __pycache__)
    for root, dirs, fs in os.walk(OUT):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for fn in fs:
            if not _skip(fn):
                os.remove(os.path.join(root, fn))
    for rel, data in rendered.items():
        full = os.path.join(OUT, rel.replace("/", os.sep))
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "wb") as fh:
            fh.write(data)
    print(f"release gerado em {OUT} ({len(rendered)} arquivos)")
    for k in sorted(rendered):
        print(f"  {k}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
