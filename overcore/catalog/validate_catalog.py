#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validador do catálogo canônico do Overcore (PRB-017A).

Camadas:
  1. JSON Schema Draft 2020-12 (envelope + cada entrada via $defs.entry).
  2. Validação semântica reproduzível (regras que o Schema não expressa).
  3. Resolução de skills no índice (docs/indices/skills_index.json) e no
     filesystem (skills/<id>/SKILL.md), com target/runtime e risco.
  4. Varredura de segredos / caminhos privados / prompt de usuário real.

Uso:
  python validate_catalog.py                 # valida o catalog.json canônico
  python validate_catalog.py <arquivo.json>  # valida um catálogo específico
  python validate_catalog.py --suite         # roda canônico + todas as fixtures

Sai com código != 0 quando há falha (ou quando o resultado da fixture diverge
do esperado, no modo --suite).
"""
import hashlib
import json
import os
import re
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
HUB_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SCHEMA_PATH = os.path.join(HERE, "catalog.schema.json")
CANONICAL = os.path.join(HERE, "catalog.json")
SKILL_DEPS_PATH = os.path.join(HERE, "skill-dependencies.json")
SKILLS_INDEX = os.path.join(HUB_ROOT, "docs", "indices", "skills_index.json")
SKILLS_DIR = os.path.join(HUB_ROOT, "skills")

SUPPORTED_SCHEMA_VERSION = "0.3.0"
REQUIRED_CORRELATION = {"workflowId", "runId", "parentRunId", "agentId", "taskId"}
MAX_SKILLS = 6
SAFE_RISKS = {"safe"}  # único risco confiável para uso em ação mutável
# Skills de risco não-safe (inclui 'unknown') NÃO podem escrever/commitar/executar silenciosamente.
MUTATING_TOOLS = {
    "fs:escrever", "fs:apagar", "git:commit", "git:push", "git:remote", "shell:exec",
    "agent:run", "oracle:despacho:executar",
}
# Contrato completo do registro de execução futura (telemetry.executionRecord.required).
MANDATORY_EXEC_FIELDS = {
    "agentId", "subagentId", "skillsResolved", "overcoreVersion", "overcoreCommit",
    "catalogVersion", "workflowId", "runId", "parentRunId", "taskId", "terminalStatus",
}

# Padrões de segredo / caminho privado / prompt real de usuário.
SECRET_PATTERNS = [
    (r"sk-[A-Za-z0-9]{20,}", "chave estilo OpenAI (sk-...)"),
    (r"gh[pousr]_[A-Za-z0-9]{20,}", "token GitHub (gh?_...)"),
    (r"AKIA[0-9A-Z]{16}", "AWS access key id"),
    (r"xox[baprs]-[A-Za-z0-9-]{10,}", "token Slack (xox...)"),
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "bloco de chave privada PEM"),
    (r"[A-Za-z]:\\\\Users\\\\[^\\\"/]+", "caminho privado do host (C:\\Users\\<user>)"),
    (r"/(?:home|Users)/[A-Za-z0-9._-]+/", "caminho privado do host (/home|/Users/<user>)"),
    (r"(?i)\b(?:api[_-]?key|password|passwd|secret|bearer)\b\s*[:=]\s*['\"][^'\"]{6,}", "credencial embutida"),
]


class Fail(Exception):
    pass


def load_json(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def schema_validate(catalog, errors):
    """Camada 1 — JSON Schema Draft 2020-12."""
    try:
        from jsonschema import Draft202012Validator
    except Exception as exc:  # pragma: no cover
        errors.append(f"[schema] jsonschema indisponível: {exc}")
        return
    schema = load_json(SCHEMA_PATH)
    validator = Draft202012Validator(schema)
    for err in sorted(validator.iter_errors(catalog), key=lambda e: list(e.path)):
        loc = "/".join(str(p) for p in err.path) or "(raiz)"
        errors.append(f"[schema] {loc}: {err.message}")


def load_skill_index():
    idx = load_json(SKILLS_INDEX)
    return {s["id"]: s for s in idx}


def load_skill_deps_doc():
    """Documento DERIVADO completo (com hashes das fontes)."""
    return load_json(SKILL_DEPS_PATH)


def load_skill_deps():
    """Projeção {id: {requiredSubSkills: [...]}} usada pela regra de dependências."""
    return (load_skill_deps_doc().get("sources") or {})


def sha256_file(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def frontmatter_block(text):
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    return text[3:end] if end != -1 else ""


def read_required_subskills(path):
    """Extrai SÓ o campo estruturado `requiredSubSkills` do frontmatter (origem)."""
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as fh:
        block = frontmatter_block(fh.read())
    for line in block.splitlines():
        m = re.match(r"\s*requiredSubSkills\s*:\s*(.+)$", line)
        if m:
            val = yaml.safe_load(m.group(1))
            if isinstance(val, list):
                return [str(x) for x in val]
    return None


def check_dep_sync(skills_dir, index_map, deps_doc, errors):
    """Confere a IGUALDADE origem(frontmatter) ↔ índice(propagação) ↔ projeção(derivada),
    e o SHA-256 de cada fonte. Qualquer divergência falha FECHADO (projeção desatualizada)."""
    sources = (deps_doc or {}).get("sources") or {}
    for sid, proj in sources.items():
        md = os.path.join(skills_dir, sid, "SKILL.md")
        if not os.path.isfile(md):
            errors.append(f"[deps] projeção referencia SKILL.md ausente: '{sid}'")
            continue
        # hash da fonte (detecta projeção desatualizada)
        if proj.get("skillMdSha256") != sha256_file(md):
            errors.append(f"[deps] projeção DESATUALIZADA p/ '{sid}': SHA-256 do SKILL.md difere — regerar skill-dependencies.json")
        fm_deps = read_required_subskills(md)
        proj_deps = proj.get("requiredSubSkills") or []
        if sorted(fm_deps or []) != sorted(proj_deps):
            errors.append(f"[deps] projeção != origem (frontmatter) p/ '{sid}': {proj_deps} vs {fm_deps}")
        idx_deps = (index_map.get(sid) or {}).get("requiredSubSkills")
        if sorted(idx_deps or []) != sorted(fm_deps or []):
            errors.append(f"[deps] índice (propagação) != origem p/ '{sid}': {idx_deps} vs {fm_deps}")
    # completude: skill do índice com requiredSubSkills tem de estar na projeção
    for sid, meta in index_map.items():
        if meta.get("requiredSubSkills") and sid not in sources:
            errors.append(f"[deps] '{sid}' tem requiredSubSkills no índice mas falta na projeção derivada")


def semantic_validate(catalog, errors):
    """Camadas 2 e 3 — regras semânticas + resolução de skills."""
    agents = catalog.get("agents", [])
    index = load_skill_index()
    deps_doc = load_skill_deps_doc()
    skill_deps = (deps_doc.get("sources") or {})

    # Sincronização de dependências: origem(frontmatter) ↔ índice ↔ projeção derivada + hashes.
    check_dep_sync(SKILLS_DIR, index, deps_doc, errors)

    # Versão do schema declarada no catálogo (defesa em profundidade além do JSON Schema).
    if catalog.get("schemaVersion") != SUPPORTED_SCHEMA_VERSION:
        errors.append(f"[semântica] schemaVersion do catálogo != {SUPPORTED_SCHEMA_VERSION}: {catalog.get('schemaVersion')}")

    # IDs únicos.
    seen = {}
    for i, e in enumerate(agents):
        eid = e.get("id")
        if eid in seen:
            errors.append(f"[semântica] id duplicado: '{eid}' (posições {seen[eid]} e {i})")
        else:
            seen[eid] = i
    ids = set(seen)

    # oracle-coordinator presente exatamente uma vez, como kind agent.
    coords = [e for e in agents if e.get("id") == "oracle-coordinator"]
    if len(coords) != 1:
        errors.append(f"[semântica] oracle-coordinator deve aparecer exatamente 1x (achado {len(coords)})")
    elif coords[0].get("kind") != "agent":
        errors.append("[semântica] oracle-coordinator deve ter kind 'agent'")

    # Índice determinístico: ordem = ids em kebab ascendente.
    ordered = [e.get("id", "") for e in agents]
    if ordered != sorted(ordered):
        errors.append(f"[semântica] ordem não-determinística do índice de agentes: {ordered} != {sorted(ordered)}")

    for e in agents:
        eid = e.get("id", "?")
        kind = e.get("kind")
        skills = e.get("skills", {}) or {}
        required = skills.get("required", []) or []
        optional = skills.get("optional", []) or []
        max_total = skills.get("maxTotal", MAX_SKILLS)

        # Cada agente/subagente possui skills próprias.
        if kind in ("agent", "subagent") and not required:
            errors.append(f"[semântica] '{eid}' (kind {kind}) não declara skills.required próprias")

        # Nenhuma entrada excede 6 skills resolvidas / respeita maxTotal.
        resolved = list(dict.fromkeys(required + optional))  # únicas, preservando ordem
        if len(resolved) > MAX_SKILLS:
            errors.append(f"[semântica] '{eid}' resolve {len(resolved)} skills (> {MAX_SKILLS})")
        if len(resolved) > max_total:
            errors.append(f"[semântica] '{eid}' resolve {len(resolved)} skills (> maxTotal {max_total})")
        if max_total > MAX_SKILLS:
            errors.append(f"[semântica] '{eid}' maxTotal {max_total} > {MAX_SKILLS}")

        # Skills existem no índice e no filesystem; target/runtime; risco.
        allowed_tools = set(((e.get("tools", {}) or {}).get("allowed") or []))
        mutates = bool(allowed_tools & MUTATING_TOOLS)
        for sid in resolved:
            meta = index.get(sid)
            if not meta:
                errors.append(f"[semântica] '{eid}' usa skill inexistente no índice: '{sid}'")
                continue
            skill_md = os.path.join(SKILLS_DIR, sid, "SKILL.md")
            if not os.path.isfile(skill_md):
                errors.append(f"[semântica] '{eid}' skill '{sid}' sem SKILL.md em skills/{sid}/SKILL.md")
            claude = ((meta.get("plugin", {}) or {}).get("targets", {}) or {}).get("claude")
            if claude != "supported":
                errors.append(f"[semântica] '{eid}' skill '{sid}' não suportada no runtime Claude (targets.claude={claude})")
            # Regra DURA de risco: skill não-safe (inclui 'unknown') não pode operar numa entrada
            # com ferramenta mutável — sem escape por requiresHumanApproval. Fecha escrita/commit/
            # implementação silenciosa de skills de brainstorming/verificação.
            risk = meta.get("risk")
            if risk not in SAFE_RISKS and mutates:
                errors.append(
                    f"[semântica] '{eid}' usa skill de risco '{risk}' ('{sid}') em entrada com ferramenta mutável ({sorted(allowed_tools & MUTATING_TOOLS)}) — proibido")

        # Dependências obrigatórias declaradas (skill-dependencies.json): sem herança implícita —
        # cada entrada precisa resolver as sub-skills obrigatórias das suas próprias skills.
        resolved_set = set(resolved)
        for sid in resolved:
            dep = skill_deps.get(sid)
            if not dep:
                continue
            for sub in dep.get("requiredSubSkills", []) or []:
                if sub not in resolved_set:
                    errors.append(
                        f"[semântica] '{eid}' usa '{sid}' mas não resolve a dependência obrigatória '{sub}'")

        # Contrato completo de telemetria de execução futura.
        er = (e.get("telemetry", {}) or {}).get("executionRecord")
        if kind in ("agent", "subagent"):
            if not er:
                errors.append(f"[semântica] '{eid}' sem telemetry.executionRecord (contrato de execução ausente)")
            else:
                miss_er = MANDATORY_EXEC_FIELDS - set(er.get("required", []) or [])
                if miss_er:
                    errors.append(f"[semântica] '{eid}' executionRecord.required incompleto, falta: {sorted(miss_er)}")
                if not (er.get("terminalStatusEnum") or []):
                    errors.append(f"[semântica] '{eid}' executionRecord sem terminalStatusEnum")

        # Rotas SOB DEMANDA (skills.onDemand): garantias OBRIGATÓRIAS + política de carga.
        # NÃO contam no maxTotal, mas o CONJUNTO EFETIVO ao ativar tem de respeitar maxTotal.
        ondemand = skills.get("onDemand") or []
        if len(ondemand) > 1:
            errors.append(f"[semântica] '{eid}' tem {len(ondemand)} rotas onDemand (máx 1 por entrada — exclusividade)")
        base_ids = resolved  # unique(required + optional)
        REQ_FORBIDS = {"implementacao", "escrita-de-arquivo", "commit"}
        CONFIRM_MODES = ("explicit-or-confirmed", "auto-requires-confirmation")
        for route in ondemand:
            rsid = route.get("skill")
            meta = index.get(rsid)
            if not meta:
                errors.append(f"[semântica] '{eid}' rota onDemand usa skill inexistente: '{rsid}'")
                continue
            if not os.path.isfile(os.path.join(SKILLS_DIR, rsid, "SKILL.md")):
                errors.append(f"[semântica] '{eid}' rota onDemand skill '{rsid}' sem SKILL.md")
            rclaude = ((meta.get("plugin", {}) or {}).get("targets", {}) or {}).get("claude")
            if rclaude != "supported":
                errors.append(f"[semântica] '{eid}' rota onDemand skill '{rsid}' não suportada no runtime Claude")
            rrisk = meta.get("risk")
            if rrisk not in SAFE_RISKS and mutates:
                errors.append(f"[semântica] '{eid}' rota onDemand de risco '{rrisk}' ('{rsid}') em entrada com ferramenta mutável — proibido")
            # Garantias obrigatórias (ausência é INVÁLIDA — não se apoia em default do schema).
            if route.get("activation") in CONFIRM_MODES:
                if route.get("autoTriggerRequiresConfirmation") is not True:
                    errors.append(f"[semântica] '{eid}' rota onDemand '{rsid}': autoTriggerRequiresConfirmation ausente ou != true")
                trg = route.get("triggers")
                if not isinstance(trg, list) or not [t for t in trg if t]:
                    errors.append(f"[semântica] '{eid}' rota onDemand '{rsid}': triggers vazio")
                elif len(trg) != len(set(trg)):
                    errors.append(f"[semântica] '{eid}' rota onDemand '{rsid}': triggers com duplicatas")
                if "authorizes" not in route or (route.get("authorizes") or []) != []:
                    errors.append(f"[semântica] '{eid}' rota onDemand '{rsid}': authorizes ausente ou não vazio")
                if "forbids" not in route:
                    errors.append(f"[semântica] '{eid}' rota onDemand '{rsid}': forbids ausente")
                else:
                    miss_f = REQ_FORBIDS - set(route.get("forbids") or [])
                    if miss_f:
                        errors.append(f"[semântica] '{eid}' rota onDemand '{rsid}': forbids incompleto, falta {sorted(miss_f)}")
                h = route.get("handoffTo")
                if not h:
                    errors.append(f"[semântica] '{eid}' rota onDemand '{rsid}': handoffTo ausente")
                elif h not in index and h not in ids:
                    errors.append(f"[semântica] '{eid}' rota onDemand handoffTo '{h}' não resolve (nem skill nem entrada)")
            # Política de carga (§2): conjunto efetivo ao ativar tem de caber em maxTotal.
            replaces = route.get("replaces") or []
            if len(replaces) != len(set(replaces)):
                errors.append(f"[semântica] '{eid}' rota onDemand '{rsid}': replaces com duplicatas")
            for rep in replaces:
                if rep not in base_ids:
                    errors.append(f"[semântica] '{eid}' rota onDemand '{rsid}': replaces '{rep}' não existe nas skills da entrada")
            effective = list(dict.fromkeys([s for s in base_ids if s not in set(replaces)] + [rsid]))
            if len(effective) > max_total:
                errors.append(f"[semântica] '{eid}' rota onDemand '{rsid}': conjunto efetivo {len(effective)} > maxTotal {max_total}")
            if len(base_ids) + 1 > max_total and route.get("loadPolicy") != "replace":
                errors.append(f"[semântica] '{eid}' rota onDemand '{rsid}': base com {len(base_ids)} skills exige loadPolicy 'replace' + substituição")

        # Ferramenta negada não pode aparecer como permitida.
        tools = e.get("tools", {}) or {}
        allowed = set(tools.get("allowed", []) or [])
        denied = set(tools.get("denied", []) or [])
        conflict = allowed & denied
        if conflict:
            errors.append(f"[semântica] '{eid}' tem ferramenta simultaneamente permitida e negada: {sorted(conflict)}")

        # Telemetria: correlação obrigatória.
        corr = set((e.get("telemetry", {}) or {}).get("correlationIds", []) or [])
        missing = REQUIRED_CORRELATION - corr
        if missing:
            errors.append(f"[semântica] '{eid}' telemetria sem correlação obrigatória: {sorted(missing)}")

        # Proveniência válida.
        prov = e.get("provenance", {}) or {}
        if not prov.get("origin") or not prov.get("author") or not prov.get("dateAdded"):
            errors.append(f"[semântica] '{eid}' proveniência incompleta (origin/author/dateAdded)")

        # Delegação aponta para entradas existentes e compatíveis; gate de aprovação p/ despacho.
        deleg = e.get("delegation", {}) or {}
        if deleg.get("canDelegate"):
            subs = deleg.get("subagents", []) or []
            for sub in subs:
                if sub not in ids:
                    errors.append(f"[semântica] '{eid}' delega para entrada inexistente: '{sub}'")
                else:
                    sub_kind = next((x.get("kind") for x in agents if x.get("id") == sub), None)
                    if sub_kind not in ("subagent", "role"):
                        errors.append(f"[semântica] '{eid}' delega para '{sub}' que não é subagent/role (kind {sub_kind})")
            # Quem pode despachar (nega agent:run e delega) precisa de gate human-approval p/ agent:run.
            gates = e.get("gates", []) or []
            has_approval = any(
                g.get("type") == "human-approval"
                and ("agent:run" in (g.get("blocksTransitionTo") or "") or "despacho" in (g.get("blocksTransitionTo") or ""))
                for g in gates
            )
            if not has_approval:
                errors.append(f"[semântica] '{eid}' pode despachar mas não tem gate human-approval bloqueando agent:run/despacho")


def secret_scan(catalog, errors):
    """Camada 4 — nenhum segredo/caminho privado/prompt real de usuário."""
    blob = json.dumps(catalog, ensure_ascii=False)
    for pat, label in SECRET_PATTERNS:
        m = re.search(pat, blob)
        if m:
            errors.append(f"[segredo] {label}: '{m.group(0)[:40]}...'")


def validate_file(path):
    errors = []
    try:
        catalog = load_json(path)
    except Exception as exc:
        return [f"[io] falha ao ler/parsear {path}: {exc}"]
    schema_validate(catalog, errors)
    # Só roda semântica se o parse básico deu certo (estrutura mínima).
    if isinstance(catalog, dict) and isinstance(catalog.get("agents"), list):
        semantic_validate(catalog, errors)
    else:
        errors.append("[semântica] catálogo sem 'agents' array")
    secret_scan(catalog, errors)
    return errors


def run_suite():
    fx = os.path.join(HERE, "fixtures")
    cases = [(CANONICAL, True), ]
    pos = os.path.join(fx, "positive")
    neg = os.path.join(fx, "negative")
    for d, expect_pass in ((pos, True), (neg, False)):
        if os.path.isdir(d):
            for name in sorted(os.listdir(d)):
                if name.endswith(".json"):
                    cases.append((os.path.join(d, name), expect_pass))

    total = len(cases)
    positives = sum(1 for _, exp in cases if exp)
    negatives = total - positives
    conforming = 0
    unexpected = 0
    print(f"{'RESULTADO':10s} {'ESPERADO':9s}  ARQUIVO")
    for path, expect_pass in cases:
        errs = validate_file(path)
        passed = not errs
        match = passed == expect_pass
        if match:
            conforming += 1
        else:
            unexpected += 1
        rel = os.path.relpath(path, HERE)
        status = "PASSOU" if passed else "FALHOU"
        exp = "passar" if expect_pass else "falhar"
        flag = "OK" if match else "XX DIVERGENTE"
        print(f"{status:10s} {exp:9s}  {rel}  [{flag}]")
        if not match:
            for e in errs[:6]:
                print(f"           - {e}")
            if passed and not expect_pass:
                print("           - (esperava-se ao menos uma falha e não houve nenhuma)")
    # Contagem CALCULADA automaticamente (nunca hardcoded).
    print("-" * 60)
    print(f"TOTAL: {total}  (positivos: {positives}, negativos: {negatives})")
    print(f"CONFORMES (comportaram como esperado): {conforming}/{total}")
    print(f"FALHOS INESPERADOS (divergentes): {unexpected}")
    print(f"RESULTADO: {'TUDO VERDE' if unexpected == 0 else 'FALHA'}")
    return 0 if unexpected == 0 else 1


def main(argv):
    if "--suite" in argv:
        return run_suite()
    target = next((a for a in argv[1:] if not a.startswith("--")), CANONICAL)
    errs = validate_file(target)
    if errs:
        print(f"INVÁLIDO: {target}")
        for e in errs:
            print(f"  - {e}")
        return 1
    print(f"VÁLIDO: {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
