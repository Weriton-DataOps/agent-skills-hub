---
name: safegate-github
description: Segurança no GitHub — segredos, supply chain, branch protection, CI/CD. Use ao configurar repositórios, GitHub Actions, revisar workflows, lidar com segredo commitado ou configurar Dependabot/CodeQL.
---

# Segurança no GitHub (responde ao novo A03:2025 — Supply Chain)

## Configuração mínima de TODO repositório da organização

1. **Push Protection + Secret Scanning** — bloqueia segredo ANTES de entrar no histórico.
   Habilitar org-wide (Settings → Code security). Adicionar padrões customizados para
   chaves internas (ex.: prefixos de tokens próprios).
2. **Dependabot** — alerts + security updates automáticos; `dependabot.yml` para version updates
   de npm/pip/Docker/Actions.
3. **CodeQL (code scanning)** — SAST nativo via Actions; cobre Python e JS/TS (Next.js).
4. **Branch protection / rulesets na main**: PR review obrigatório, status checks verdes
   (CI + CodeQL), bloqueio de force-push, commits assinados.
5. **MFA obrigatório** na organização; least privilege em teams (ninguém com admin "por conveniência").

## Actions / CI seguro

- **Pin de Actions por SHA completo**, nunca por tag:
  `uses: actions/checkout@8f4b7f84864484a7bf31766abe9204da3cbe65b3  # v4`
- `permissions:` mínimo no workflow (`contents: read` por padrão).
- Deploy via **OIDC** (sem secrets de cloud de longa duração no repositório).
- Secrets de CI só em GitHub Secrets/vault — nunca em workflow, código ou log.
- Artifact Attestations para vincular build→repositório (SLSA Build L2; L3 com reusable workflows).

## Segredo commitado — runbook

1. **ROTACIONAR a credencial imediatamente** (este é o passo que importa — o segredo já vazou).
2. Só depois, limpar histórico (`git filter-repo`) se necessário.
3. Verificar logs de uso da credencial vazada (houve acesso indevido? → LGPD/incidente).
4. Causa raiz: por que o push protection não bloqueou? Habilitar/ajustar.

## Higiene de código

- `.env`, chaves, dumps de banco e planilhas com dados de cliente no `.gitignore` — e
  auditar o histórico atual com `gitleaks detect` antes de tornar qualquer repo menos restrito.
- Dados pessoais reais NUNCA em fixtures/seeds/testes do repositório.
- Repositórios privados por padrão; revisão antes de qualquer mudança de visibilidade.

## Stack open-source complementar (alternativa ao GitHub Advanced Security pago)

- **Semgrep** (SAST) + **Gitleaks** (segredos) + **Trivy** (dependências/containers/IaC)
  rodando no CI e disponíveis localmente para os agentes de auditoria usarem via Bash.
