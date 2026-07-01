---
name: safegate-postgres
description: Hardening de PostgreSQL (e princípios para SQL Server) — roles, least privilege, RLS, pgAudit, criptografia, backup/PITR. Use ao criar usuários de banco, escrever migrações/DDL, configurar conexões de aplicação ou revisar permissões.
---

# Segurança PostgreSQL — receitas prontas

## 1. Role dedicada por aplicação (nunca superuser)

```sql
-- Role da aplicação externa: o mínimo absoluto
CREATE ROLE app_clientes LOGIN PASSWORD '<gerada-forte-no-secret-manager>';
REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA app TO app_clientes;
GRANT SELECT, INSERT, UPDATE ON app.contratos, app.clientes TO app_clientes;
-- SEM DELETE se o negócio não exige; JAMAIS DROP/ALTER/TRUNCATE/CREATE

-- Role somente-leitura para dashboards/Streamlit/DW
CREATE ROLE bi_leitura LOGIN PASSWORD '<...>';
GRANT USAGE ON SCHEMA app TO bi_leitura;
GRANT SELECT ON ALL TABLES IN SCHEMA app TO bi_leitura;
ALTER DEFAULT PRIVILEGES IN SCHEMA app GRANT SELECT ON TABLES TO bi_leitura;
```

## 2. Row-Level Security (isolamento por cliente — defesa contra IDOR/BOLA)

```sql
ALTER TABLE app.contratos ENABLE ROW LEVEL SECURITY;
ALTER TABLE app.contratos FORCE ROW LEVEL SECURITY;  -- vale até para o dono da tabela

CREATE POLICY contratos_por_cliente ON app.contratos
  USING (cliente_id = current_setting('app.cliente_id')::int);
-- A aplicação faz: SET app.cliente_id = '<id-da-sessão-autenticada>';
-- Mesmo com bug de autorização na app, o banco só devolve as linhas do cliente.
```

## 3. Rede e autenticação

```
# postgresql.conf
listen_addresses = '10.0.20.5'          # nunca '*'
password_encryption = scram-sha-256
ssl = on

# pg_hba.conf — só a sub-rede da app, com TLS e SCRAM
hostssl  app_db  app_clientes  10.0.20.0/24  scram-sha-256
# NUNCA: host all all 0.0.0.0/0 md5/trust
```

Connection string da app: `sslmode=verify-full` (mínimo `require`), credencial em
variável de ambiente/secret manager — nunca no código nem em repositório.

## 4. Auditoria — pgAudit

```
shared_preload_libraries = 'pgaudit'
pgaudit.log = 'write, ddl, role'    # acrescentar 'read' em tabelas sensíveis via pgaudit.role
pgaudit.log_parameter = on
log_connections = on
```
Responde: quem fez, quando, o que alterou. Em SQL Server: SQL Audit + TDE.
Logs enviados para fora do servidor (centralizados) e com retenção definida.

## 5. Criptografia

- At-rest: volume criptografado (LUKS) ou TDE (SQL Server).
- Coluna/aplicação para CPF e dados financeiros (`pgcrypto` ou criptografia na app), com chave FORA do banco.
- Mascaramento em views de relatório: `'***.' || right(cpf, 2)`.

## 6. Backup

- pgBackRest ou Barman com WAL archiving → **PITR** (recuperação a ponto no tempo).
- Regra 3-2-1; backup criptografado; uma cópia offline/imutável (ransomware).
- **Restore testado periodicamente** — agendar teste mensal. Backup não testado não é backup.

## Red flags em revisão de código/config

- Connection string com usuário `postgres`/`sa`/admin
- Senha hardcoded ou commitada
- Query montada com f-string/concatenação (SQL injection)
- `sslmode=disable` ou ausente
- `GRANT ALL` ou role compartilhada entre sistemas
