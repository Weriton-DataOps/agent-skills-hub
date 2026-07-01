---
name: safegate-owasp
description: Referência OWASP Top 10:2025, API Security Top 10 e padrões de autenticação atuais (RFC 9700, JWT, MFA/passkeys). Use ao revisar ou escrever código de aplicação web/API, autenticação, autorização ou sessões.
---

# OWASP e autenticação — referência 2025/2026

## OWASP Top 10:2025 (edição vigente)

| # | Categoria | Atenção neste contexto |
|---|---|---|
| A01 | Broken Access Control (absorveu SSRF) | Risco nº 1: cliente acessar contrato de outro cliente. RBAC server-side a cada request. |
| A02 | Security Misconfiguration | Debug off em prod, CORS restrito, headers de segurança, sem stack trace ao usuário. |
| A03 | Software Supply Chain Failures (NOVA) | Dependências, build e distribuição. Lockfiles, Dependabot, Actions com pin por SHA. |
| A04 | Cryptographic Failures | bcrypt/argon2 para senhas; TLS em tudo; sem MD5/SHA1; segredos fora do código. |
| A05 | Injection | Queries SEMPRE parametrizadas (nunca f-string/concatenação); escape de saída (XSS). |
| A06 | Insecure Design | Threat modeling antes de construir; limites de negócio (ex.: nº de tentativas). |
| A07 | Authentication Failures | Rate limit + lockout em login, MFA, sessão com expiração, sem enumeração de usuários. |
| A08 | Software/Data Integrity Failures | CI/CD íntegro, atualizações assinadas, deserialização segura. |
| A09 | Security Logging & Alerting Failures | Trilha de auditoria (quem/quando/o quê) + ALERTAS, não só logs. |
| A10 | Mishandling of Exceptional Conditions (NOVA) | Erro nunca pode "fail open" nem pular validação; catch genérico é suspeito. |

Fonte: https://owasp.org/Top10/2025/

## OWASP API Security Top 10 (2023) — para a API do app de clientes

1. **API1 BOLA** — troca de ID na URL acessa objeto alheio. Checar ownership em TODA rota.
2. API2 Broken Authentication
3. API3 Broken Object Property Level Authorization (mass assignment; não serializar campos demais)
4. API4 Unrestricted Resource Consumption — **rate limiting obrigatório**
5. API5 Broken Function Level Authorization — endpoint admin acessível por usuário comum
6. API6 Unrestricted Access to Sensitive Business Flows
7. API7 SSRF
8. API8 Security Misconfiguration
9. API9 Improper Inventory Management — endpoints antigos/esquecidos expostos
10. API10 Unsafe Consumption of APIs

## Autenticação — estado da arte (RFC 9700, jan/2025 + NIST SP 800-63B-4, jul/2025)

- **OAuth2/OIDC**: PKCE SEMPRE (todos os clientes). Implicit grant e password grant (ROPC) estão DEPRECADOS — não usar.
- **Tokens**: access token curto (5–15 min para dados financeiros); refresh token com **rotação obrigatória** (reuso de refresh antigo = roubo → revogar a família inteira de sessão).
- **Armazenamento no navegador**: NUNCA localStorage. Cookies `HttpOnly; Secure; SameSite=Lax/Strict` (prefixo `__Host-`).
- **JWT**: whitelist explícita de algoritmo na verificação (`algorithms=['RS256']`); rejeitar `alg: none`; validar `exp`, `iss`, `aud`. Ataque clássico: confusão RS256→HS256 usando a chave pública como segredo HMAC.
- **Para sessões web simples**, cookie de sessão server-side tradicional costuma ser MAIS seguro que JWT no navegador (revogável).
- **MFA**: phishing-resistant é o baseline — **passkeys/WebAuthn** preferencial (AAL2 com passkey sincronizada); TOTP como mínimo; SMS é fraco.
- **Senhas (NIST)**: comprimento > complexidade; sem expiração periódica; checar contra listas de senhas vazadas.
- **RBAC**: papel vem da sessão validada no SERVIDOR a cada request — jamais do front-end ou de parâmetro do cliente.

## Gate de go-live

Usar **OWASP ASVS 5.0 nível 2** como checklist de verificação antes de expor a app
(obrigatório para apps com dados pessoais/financeiros): https://github.com/OWASP/ASVS

Cheat sheets prescritivos por tópico: https://cheatsheetseries.owasp.org/
