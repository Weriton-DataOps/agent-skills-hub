---
name: safegate-exposicao-externa
description: Checklist de go-live para expor aplicação ao público externo sem expor a VPN, servidores e bancos internos. Use ao planejar, revisar ou publicar o app de clientes, configurar Cloudflare, reverse proxy, firewall ou DNS.
---

# Expor app externa sem expor a rede interna

## Arquitetura alvo (consenso 2025/2026 para PME — Zero Trust, NIST SP 1800-35)

```
Internet → Cloudflare (DNS proxy + WAF + DDoS + TLS + rate limiting)
         → Cloudflare Tunnel (cloudflared — conexão OUTBOUND-only)
         → Nginx/Traefik (reverse proxy, único ponto de entrada interno)
         → App de clientes em sub-rede/VLAN SEGREGADA
         → Banco via usuário dedicado e restrito (nunca admin)
```

Por que Cloudflare Tunnel: o daemon `cloudflared` abre conexão de DENTRO para fora —
**zero portas abertas no firewall, sem IP público, servidores invisíveis à internet**.
O free tier cobre TLS automático, DDoS e WAF básico — suficiente para começar.

## Checklist de go-live (bloqueantes)

### Rede
- [ ] Nenhuma porta de entrada aberta no firewall para a app (usar Tunnel)
- [ ] App externa em sub-rede/VLAN própria, SEM rota livre para a VPN interna/DW/servidores
- [ ] Banco inacessível da internet; só a sub-rede da app o alcança, com TLS
- [ ] Origem só aceita tráfego da Cloudflare (Authenticated Origin Pulls/mTLS)
- [ ] Sistemas internos (Streamlit, admin, dashboards) NÃO expostos — se precisar de acesso remoto, Cloudflare Access

### Edge / proxy
- [ ] WAF ativado (managed rules) + rate limiting na edge
- [ ] TLS full(strict) + HSTS; certificado válido e renovação automática
- [ ] Headers no proxy: CSP, HSTS, X-Content-Type-Options, frame-ancestors, Referrer-Policy
- [ ] Modo de DNS "proxied" (laranja) — IP de origem nunca exposto em registro DNS, histórico ou e-mail (SPF)

### Aplicação
- [ ] Auth conforme skill `safegate-owasp` (PKCE, MFA, cookies HttpOnly, refresh rotation)
- [ ] RBAC server-side: cliente→só seus contratos; consultor→só seus clientes; gestor→tudo
- [ ] Rate limiting + lockout em login; sem enumeração de usuários
- [ ] `/security-review` rodado no código + ASVS 5.0 nível 2 verificado
- [ ] Erros genéricos ao usuário (sem stack trace); debug desligado

### Banco e dados
- [ ] Usuário de banco dedicado e mínimo (ver skill `safegate-postgres`)
- [ ] RLS para isolamento por cliente
- [ ] CPF/dados financeiros criptografados e mascarados (LGPD)

### Operação
- [ ] Logs de acesso e auditoria centralizados, com alertas (não só armazenados)
- [ ] Backup testado + plano de rollback do deploy
- [ ] Runbook de incidente pronto (agente `resposta-incidentes`)

## Fases recomendadas

1. **Antes do go-live**: tudo acima marcado como bloqueante.
2. **Primeiros 30 dias**: monitorar WAF events, tentativas de login, erros 4xx/5xx anômalos; ajustar rate limits.
3. **Evolução**: Cloudflare Access para admin, mTLS interno, pentest autorizado, CIS Controls v8.1 IG1 como roadmap.

Referências: https://developers.cloudflare.com/reference-architecture/design-guides/secure-application-delivery/ · https://csrc.nist.gov/pubs/sp/1800/35/final
