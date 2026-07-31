---
name: safegate-dev-seguro
description: Práticas de desenvolvimento seguro e ALERTAS DE RISCO durante a codificação — red flags que exigem parada imediata, gates de "pronto para produção" e regras por stack (Next.js, Python/Streamlit, SQL). Use SEMPRE que estiver escrevendo ou revisando código de qualquer sistema da organização.
---

# Desenvolvimento seguro — alertas e gates

## 🚨 RED FLAGS — pare e corrija ANTES de continuar

Ao escrever ou revisar código, qualquer um destes itens é um ALERTA que deve ser
apontado imediatamente ao usuário, com severidade:

| 🚨 Alerta | Por quê |
|---|---|
| Senha/API key/token/connection string literal no código | Vai vazar via git. Mover para env var/secret manager AGORA |
| Query SQL com f-string/concatenação/`+` | SQL injection — usar SEMPRE query parametrizada |
| Rota/Server Action/endpoint sem verificação de sessão E permissão | Broken Access Control (A01) — risco nº 1 |
| `user_id`/`cliente_id` vindo do request (URL, body, header) em vez da sessão | IDOR/BOLA — cliente acessa dados de outro |
| Token/JWT em `localStorage` | Roubo via XSS — usar cookie HttpOnly |
| `dangerouslySetInnerHTML` / `innerHTML` / `unsafe_allow_html=True` com dado de usuário | XSS |
| `eval()`, `exec()`, `pickle.load()`, `os.system()`/`shell=True` com input externo | Execução remota de código |
| Upload sem validação de tipo/tamanho/nome (path traversal) | Webshell, RCE |
| `catch`/`except` genérico que continua o fluxo silenciosamente | A10 — "fail open" pode pular validação |
| CPF/senha/token em `console.log`/`print`/log | LGPD + credencial em log |
| CORS `*` ou `verify=False`/TLS desabilitado | Misconfiguration |
| Dependência nova sem avaliar (típico typosquatting) ou sem lockfile | Supply chain (A03:2025) |
| Dados reais de cliente em teste/seed/fixture | LGPD — usar dados sintéticos |
| Connection string com usuário `postgres`/`sa`/admin | Least privilege violado |

## Gates — "pronto" só quando passar

**Gate 1 — a cada feature (antes do commit):**
- Input externo validado (zod no TS; pydantic no Python) — tipo, tamanho, formato
- Autenticação + autorização de ownership em TODA rota/action nova
- Nenhum red flag acima presente; segredos só em env vars
- Erros tratados: mensagem genérica ao usuário, detalhe só no log do servidor

**Gate 2 — antes do merge (PR):**
- `/security-review` rodado no diff
- Ação sensível nova tem trilha de auditoria (quem/quando/o quê)
- Scans verdes: CodeQL/Semgrep + Gitleaks + `npm audit`/`pip-audit`
- Migração/SQL revisada pelo agente `dba-seguranca` se tocar permissões/dados pessoais

**Gate 3 — antes do deploy em produção:**
- Sistema na Vercel → checklist da skill `safegate-vercel`
- Sistema interno (servidores próprios) → checklist da skill `safegate-exposicao-externa`
- Dados pessoais novos → revisão `guardiao-lgpd` (finalidade, retenção, mascaramento)
- Rollback conhecido e testado

## Regras por stack

**Next.js/TypeScript** (detalhes na skill `safegate-vercel`):
- Middleware é UX, não segurança — autorização na camada de dados/Server Action
- `server-only` em módulos de dados; DTOs (nunca passar registro completo ao client)
- Server Action = endpoint público: zod + auth + ownership em todas

**Python/Streamlit (sistemas internos):**
- Streamlit não tem auth robusta nativa — NUNCA exposto publicamente; acesso via VPN/Cloudflare Access
- Conexão ao banco com role somente-leitura (`bi_leitura`) quando for dashboard
- `st.secrets`/env vars para credenciais; cuidado com `st.cache_*` guardando dados de um usuário e servindo a outro

**SQL/migrações** (detalhes na skill `safegate-postgres`):
- Toda migração nova de tabela com dados de cliente: avaliar RLS e mascaramento
- GRANTs explícitos e mínimos; nunca `GRANT ALL`

## Princípio geral

Funcionalidade e segurança nascem JUNTAS — segurança "depois" significa retrabalho ou incidente.
Na dúvida entre conveniência e segurança em código que vai para produção, escolha segurança e
explique o trade-off ao usuário.
