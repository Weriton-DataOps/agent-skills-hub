---
name: safegate-arquitetura
description: Arquitetura de segurança PADRÃO que TODO sistema/app da organização deve seguir — segredos centralizados em cofre, deploy por terceiros sem acesso a senhas, banco com least-privilege que impede deleções indevidas, separação de ambientes e o gate de "seguro para produção". Use ao iniciar qualquer projeto novo, revisar arquitetura, definir acesso de equipes externas, ou planejar deploy/CI/CD.
---

# Arquitetura de Segurança Padrão — GR Group

Toda aplicação nova ou existente DEVE convergir para este modelo. Os 5 pilares respondem
diretamente aos problemas reais da organização: acessos espalhados, terceiros fazendo deploy,
e o incidente de deleção de dados por um colaborador.

## Pilar 1 — Segredos centralizados (acabar com .env espalhado)

**Problema hoje:** 16+ `.env` com senhas reais espalhados num drive SMB (Y:) lido por várias contas.

**Padrão:** UM cofre de segredos como fonte única da verdade. Ninguém copia senha em arquivo.
- Ferramenta: **Infisical** (open-source, self-host na VPN) ou Doppler/HashiCorp Vault/Bitwarden Secrets.
- Regra: **nenhum segredo em `.env` versionável, em Y:, em código ou em chat.** `.env` só existe
  localmente no servidor de runtime, gerado pelo cofre, com ACL restrita — ou injetado pela CI.
- Cada segredo tem **dono, escopo (qual app/ambiente) e rotação**. Acesso ao cofre por papel.
- Migração: inventariar os `.env` atuais → cadastrar no cofre → rotacionar tudo que esteve no Y: → apagar do Y:.

## Pilar 2 — Deploy por terceiros SEM acesso a senha (o caso do .28 homolog)

**Objetivo:** equipes de fora do departamento criam e fazem deploy no homolog (.28) só com
**commit + push** — e NUNCA enxergam segredo de banco ou de infra.

**Sim, "só commit e push" é o modelo certo** — desde que o deploy seja feito pela CI, não pela pessoa:

```
Dev externo  ──commit+push──▶  GitHub (repo, branch 'homolog')
                                   │  dispara GitHub Actions
                                   ▼
                       Runner self-hosted no .28 (ou deploy SSH)
                                   │  injeta segredos do AMBIENTE 'homolog'
                                   │  (GitHub Environments secrets OU cofre)
                                   ▼
                          Build + deploy na app do .28
```

Regras:
- O dev tem acesso ao **Git** (push na branch homolog) e **nada mais**. Sem SSH ao .28, sem senha de banco, sem acesso ao cofre.
- Os segredos vivem em **GitHub Environments** (ambiente `homolog`) ou no cofre — a Action os injeta em runtime. O dev vê `${{ secrets.DB_URL }}`, nunca o valor.
- **Produção é um ambiente separado** com *required reviewers*: deploy em prod exige aprovação sua. O dev externo nunca dispara prod.
- O workflow (`deploy.yml`) é **protegido** — só revisores internos alteram (CODEOWNERS + branch protection). Senão um PR malicioso troca o pipeline e vaza segredo.
- O agente/CI do dev usa um **token de deploy de escopo mínimo**, não credenciais pessoais amplas.

## Pilar 3 — Banco: adicionar sim, destruir não (o incidente da deleção)

**Problema:** um colaborador deletou dados que não podia. Causa raiz: role de banco com poder demais
e/ou acesso direto ao banco de produção.

**Padrão de roles por ambiente** (PostgreSQL — ver `safegate-postgres` para o SQL):

| Papel | Pode | NÃO pode |
|---|---|---|
| `app_xxx` (a aplicação) | SELECT, INSERT, UPDATE nas tabelas dela | DELETE em massa, TRUNCATE, DROP, ALTER |
| `migrator_xxx` (só a CI roda) | DDL controlado: CREATE/ALTER coluna, criar tabela | rodar fora da CI; usado por pessoa |
| `bi_readonly` (dashboards/BI) | SELECT no schema silver | qualquer escrita |
| pessoa física | **nada direto em produção** | conexão direta ao banco de prod |

Mecanismos que impedem a deleção indevida:
1. **Tirar DELETE/TRUNCATE/DROP da role da app** (ou limitar DELETE a linhas próprias via RLS).
2. **Soft delete**: coluna `deleted_at` em vez de apagar a linha. "Apagar" = marcar, reversível.
3. **Migrações só pela CI** com a role `migrator` — o dev escreve o arquivo de migração (Prisma/Flyway/
   Liquibase), revisado em PR; ninguém roda DDL na mão em prod. Cria coluna/adiciona linha = migração versionada.
4. **Sem acesso humano direto ao banco de produção.** Mudança em prod só via migração aprovada.
5. **Backups PITR testados** (pgBackRest/Barman): mesmo o pior caso é recuperável a um ponto no tempo.
6. **Auditoria (pgAudit)**: registra quem rodou qual DELETE/DDL e quando — responde "quem apagou?".

## Pilar 4 — Separação de ambientes

`dev` (máquina do dev) → `homolog` (.28) → `produção`. Bancos, segredos e credenciais
**distintos** por ambiente. Homolog nunca usa dados/credenciais de produção. Promoção entre
ambientes só pela CI, com aprovação para produção.

## Pilar 5 — Identidade e acesso centralizados

- **Onde a app roda**: cliente → Vercel (ver `safegate-vercel`); interno → servidores na VPN (ver `safegate-exposicao-externa`). Vercel nunca fala direto com banco interno.
- **Acesso de pessoas**: idealmente um IdP único (SSO) e MFA. No mínimo: contas nominais (não compartilhadas), least-privilege, e revisão periódica de quem acessa o quê.
- **GitHub**: 2FA obrigatório na org, branch protection, secret scanning + push protection, sem colaborador externo com write em repo crítico (ver `safegate-github`).

## GATE — "Seguro para produção" (todo sistema novo passa por aqui)

Um sistema só vai a produção quando responde SIM a tudo:
- [ ] Zero segredo no repositório/Y:; tudo vem do cofre ou de GitHub Environments
- [ ] Deploy 100% pela CI; ninguém com senha de banco/infra na mão
- [ ] Role de app sem DELETE em massa/DROP/ALTER; migrações só pela CI; soft delete onde faz sentido
- [ ] Banco de produção sem acesso humano direto; backup PITR testado
- [ ] Auth server-side + RBAC; rate limiting; headers de segurança (ver `safegate-owasp`)
- [ ] Ambientes separados (dev/homolog/prod) com credenciais distintas
- [ ] Logging/auditoria respondendo "quem fez, quando, o quê"
- [ ] `/security-review` rodado; sem red flags da skill `safegate-dev-seguro`
- [ ] LGPD: dados pessoais mapeados, mascarados, com retenção (ver `safegate-lgpd`)

## Roadmap de adoção (ordem)

1. Subir o cofre (Infisical na VPN) e migrar os segredos do Y: + rotacionar.
2. Criar os 3 roles de banco por app (app/migrator/bi) e remover acesso humano direto a prod.
3. Montar o pipeline homolog (.28) por GitHub Actions com Environments — testar com um app piloto.
4. Aplicar o gate a todo projeto novo; trazer os existentes um a um.
