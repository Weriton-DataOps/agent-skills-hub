---
name: safegate-vercel
description: Segurança e produção na Vercel — WAF, rate limiting, proteção de previews, variáveis de ambiente, e como conectar a Vercel aos bancos internos atrás da VPN sem expô-los. Use ao criar, configurar ou fazer deploy de qualquer sistema na Vercel, ou ao decidir como a app acessa dados internos.
---

# Vercel em produção — segurança (2026)

## Arquitetura-alvo (Vercel para clientes + infra interna isolada)

```
Cliente ──HTTPS──> Vercel (WAF + rate limit + BotID + Next.js)
                      │
        ┌─────────────┴──────────────┐
        ▼ LEITURA (baixa latência)   ▼ ESCRITA / tempo real
  Postgres gerenciado          Cloudflare Access (service token/mTLS)
  (Neon/Supabase/Marketplace)        │ Cloudflare Tunnel (saída — zero portas abertas)
        ▲ CDC/ETL (conexão de SAÍDA) ▼
  ┌─────┴────────────────── API interna mínima (BFF) ─────┐
  │  VPN: SQL Server / PostgreSQL / sistemas internos      │
  └────────────────────────────────────────────────────────┘
```

## REGRA DE OURO: a Vercel NUNCA conecta direto no banco interno

A Vercel é nuvem externa. Opções em ordem de recomendação para PME:

1. **Réplica em Postgres gerenciado** (Neon/Supabase/Vercel Marketplace) para leitura:
   sincronização de DENTRO para fora (ETL/CDC iniciado pelo servidor interno — nenhuma porta
   aberta). Replique SÓ as colunas necessárias (minimização LGPD). Vazamento na app não alcança a VPN.
2. **API interna mínima via Cloudflare Tunnel** para escrita/dados ao vivo: BFF com endpoints
   específicos (nunca SQL genérico), protegido por **Cloudflare Access + Service Token** ou mTLS;
   a function da Vercel manda o token no header. Usuário de banco least-privilege por trás.
3. **Static IPs** (Pro, ~US$100/mês/projeto): allowlist no firewall — fraco sozinho (IPs em VPC
   compartilhada); só como camada extra. **Secure Compute** é Enterprise-only.
4. ❌ NUNCA: porta do PostgreSQL/SQL Server aberta na internet, "nem só com allowlist de IP".

## Variáveis de ambiente e segredos

- **TODA credencial como Sensitive Env Var** (write-only, redigida em logs). Lição do incidente
  de abril/2026: variáveis NÃO-sensitive de clientes foram enumeradas via OAuth comprometido —
  trate não-sensitive como potencialmente legível.
- Escopos separados: **preview NUNCA usa credencial/banco de produção** (PR malicioso roda com
  env vars de preview). Use banco de staging/branch database.
- `NEXT_PUBLIC_*` vai para o bundle do navegador — é PÚBLICO por definição. Auditar sempre.
- Cloud (AWS/GCP/Azure): preferir **OIDC federation** da Vercel (tokens curtos, sem secret estático).
- MFA obrigatório nas contas Vercel e GitHub (o vetor do incidente de 2026 foi conta/OAuth).

## Firewall e abuso (o que ativar por plano)

- **Grátis em todos os planos**: DDoS L3–L7, WAF custom rules (IP, país, path), Bot Filter,
  rate limiting (1 regra no Hobby), BotID Basic, Attack Challenge Mode (saber acionar num ataque).
- Rate limiting do WAF em `/api/auth/*`, login, formulários públicos; complementar no código com
  `@upstash/ratelimit` + Redis (serverless não tem estado em memória entre invocações).
- Managed rulesets OWASP completas = Enterprise; Password Protection = add-on Pro; Trusted IPs = Enterprise.

## Previews — o elo fraco

- URLs `*.vercel.app` de preview são públicas por padrão → ativar **Vercel Authentication**
  (todos os planos) para todo preview. Risco: vazar features, dados de staging, endpoints sem hardening.
- `VERCEL_AUTOMATION_BYPASS_SECRET` para CI/E2E (sempre redigido).

## Next.js — regras de produção

- **Middleware NÃO é fronteira de segurança** (CVE-2025-29927: header `x-middleware-subrequest`
  pulava o middleware inteiro — bypass de auth, CVSS 9.1). Re-verificar sessão E permissão na
  camada de dados (DAL), em cada Server Action e API route. Manter Next.js SEMPRE na última patch.
- **Server Action = endpoint HTTP público**: em cada uma → zod no input + autenticação + autorização
  de ownership; derivar IDs da sessão, não do client.
- **`server-only`** em módulos com credenciais/queries; **Taint API** ou DTOs para nunca passar o
  objeto `user`/registro completo a client components (vazamento clássico de CPF/hash).
- Headers em `next.config`: HSTS, nosniff, frame-ancestors, Referrer-Policy, Permissions-Policy;
  **CSP** com nonce + `strict-dynamic` (começar em Report-Only).
- Cron jobs: validar `CRON_SECRET` no handler. Webhooks: validar assinatura HMAC sempre.

## Cloudflare NA FRENTE da Vercel? NÃO.

Proxy duplo degrada o WAF/BotID da Vercel, duplica cache e adiciona falha. O arranjo certo:
**DNS-only (nuvem cinza) para o app na Vercel** + Cloudflare proxied SOMENTE no hostname do
túnel da API interna. WAF da Vercel protege o app público; Cloudflare blinda a porta interna.

## Checklist de go-live Vercel

- [ ] Domínio próprio + redirect da URL `*.vercel.app`
- [ ] WAF: Bot Filter + rate limiting em auth + regras custom
- [ ] Vercel Authentication em previews; env de preview ≠ produção
- [ ] 100% segredos como sensitive; `NEXT_PUBLIC_` auditado
- [ ] Banco interno isolado (réplica gerenciada ou Tunnel+service token)
- [ ] Auth na camada de dados (não só middleware); zod; `server-only`/DTOs
- [ ] Headers + CSP; Next.js atualizado
- [ ] Log Drains (retenção padrão é ~3 dias!) + Sentry + uptime externo
- [ ] Instant Rollback testado; MFA em Vercel/GitHub

Fontes: https://vercel.com/docs/deployment-protection · https://vercel.com/docs/connectivity/secure-compute · https://vercel.com/docs/oidc · https://nextjs.org/docs/app/guides/data-security · https://securitylabs.datadoghq.com/articles/nextjs-middleware-auth-bypass/ · https://vercel.com/kb/guide/cloudflare-with-vercel
