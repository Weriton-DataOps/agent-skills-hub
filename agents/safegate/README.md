# SafeGate 🛡️

Agente de cibersegurança da organização, montado no Claude Code. Protege bancos de dados,
servidores, sistemas internos e o aplicação exposta ao público exposto fora da VPN.

## O que tem aqui

### Subagentes (`.claude/agents/`) — invoque pelo nome ou deixe o Claude acionar sozinho

| Agente | Quando usar |
|---|---|
| `auditor-seguranca` | Auditar código/diffs contra OWASP Top 10:2025 e API Top 10 (read-only) |
| `arquiteto-zero-trust` | Decisões de infra: expor app, Cloudflare Tunnel, WAF, proxy, segmentação |
| `dba-seguranca` | Roles, RLS, pgAudit, criptografia, backups, revisão de SQL/migrações |
| `guardiao-lgpd` | Conformidade LGPD: inventário de dados, direitos do titular, ANPD |
| `resposta-incidentes` | Suspeita de invasão, vazamento, segredo commitado, ransomware |

### Skills (`.claude/skills/`) — conhecimento carregado automaticamente quando relevante

- `safegate-dev-seguro` — **red flags durante a codificação** + gates de "pronto p/ produção" (commit → PR → deploy)
- `safegate-owasp` — OWASP Top 10:2025, API Top 10, RFC 9700 (OAuth2), JWT, MFA/passkeys
- `safegate-vercel` — **produção na Vercel**: WAF, previews, env vars sensíveis, e como acessar bancos internos sem expô-los
- `safegate-exposicao-externa` — go-live em servidor próprio sem expor a VPN (Cloudflare Tunnel)
- `safegate-postgres` — hardening PostgreSQL com SQL pronto (roles, RLS, pgAudit, PITR)
- `safegate-lgpd` — obrigações técnicas LGPD/ANPD (incl. prazo de 3 dias úteis para incidentes)
- `safegate-github` — segredos, supply chain (A03:2025), Actions, branch protection

### Modelo de hospedagem

| Tipo de sistema | Onde roda | Skill que governa |
|---|---|---|
| Acesso de clientes | Vercel | `safegate-vercel` |
| Acesso interno (Streamlit, admin, DW) | Servidores próprios na VPN | `safegate-exposicao-externa` |
| Bancos de dados | Servidores próprios — NUNCA expostos | `safegate-postgres` |

## Potencializar com plugins da comunidade (bem avaliados, fontes auditáveis)

```
# 1. Oficial Anthropic — revisão de segurança contínua em 3 camadas
/plugin install security-guidance@claude-plugins-official
# e o comando nativo, sob demanda em qualquer diff:
/security-review

# 2. Trail of Bits (~5,6k ⭐ — consultoria de segurança de elite)
/plugin marketplace add trailofbits/skills
/plugin install differential-review@trailofbits
/plugin install static-analysis@trailofbits        # CodeQL + Semgrep
/plugin install insecure-defaults@trailofbits
/plugin install supply-chain-risk-auditor@trailofbits

# 3. wshobson/agents (~36k ⭐ — maior marketplace comunitário)
/plugin marketplace add wshobson/agents
/plugin install security-scanning        # security-auditor + threat-modeling (STRIDE)
/plugin install comprehensive-review
/plugin install incident-response
```

⚠️ **Cuidado com marketplaces abertos**: já houve hijacking de Claude Code via plugins
maliciosos em registries não verificados. Instale apenas de fontes auditáveis
(Anthropic, Trail of Bits, wshobson) e inspecione o código de qualquer skill antes.

## Ferramentas de scan recomendadas (os agentes usam via Bash se instaladas)

- **Semgrep** (SAST) · **Gitleaks** (segredos) · **Trivy** (dependências/containers/IaC)
- Juntas substituem boa parte do GitHub Advanced Security pago.

## Roteiro de implantação (ordem de impacto)

1. **Não abrir portas**: Cloudflare Tunnel + WAF; app de clientes em sub-rede segregada
2. **Identidade**: OAuth2/PKCE, MFA (passkeys), cookies HttpOnly, refresh rotation, RBAC server-side
3. **Banco**: usuário dedicado mínimo, RLS por cliente, pgAudit, backup PITR testado
4. **GitHub**: push protection, Dependabot, CodeQL, branch protection, Actions com pin por SHA
5. **LGPD**: criptografia/mascaramento de CPF, trilha de auditoria, runbook de incidente (3 dias úteis)
6. **Contínuo**: CIS Controls v8.1 IG1 como roadmap + ASVS 5.0 nível 2 como gate de go-live

## Referências normativas (versões vigentes em 2026)

- OWASP Top 10:2025 · OWASP API Security Top 10 (2023) · ASVS 5.0 · Cheat Sheet Series
- RFC 9700 — OAuth 2.0 Security Best Current Practice (2025)
- NIST SP 800-63B-4 (autenticação/passkeys, 2025) · NIST SP 1800-35 (Zero Trust, 2025)
- CIS Controls v8.1 · Guia ANPD para Agentes de Pequeno Porte · Res. CD/ANPD 15/2024
