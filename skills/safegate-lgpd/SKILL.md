---
name: safegate-lgpd
description: Obrigações técnicas da LGPD e regulamentos ANPD para sistemas que tratam CPF, RG, contatos e dados financeiros. Use ao modelar dados pessoais, criar formulários/cadastros, definir retenção, logs ou responder a incidentes com dados pessoais.
---

# LGPD — obrigações técnicas práticas (PME)

## Base legal e enquadramento

- CPF, RG, telefone, e-mail, dados financeiros = **dados pessoais** (Art. 5º). Dados financeiros
  não são "sensíveis" no sentido estrito, mas a ANPD os trata como critério de **risco relevante**
  em incidentes → prioridade máxima de proteção.
- Art. 46–49: medidas técnicas e administrativas aptas a proteger os dados + **privacy by design**.
- Organização de pequeno porte: Res. CD/ANPD nº 2/2022 dá regime simplificado e prazos dobrados.

## As 4 perguntas que todo sistema deve responder

1. **Quais dados armazenamos?** → inventário por campo, com finalidade e base legal
2. **Quem acessa?** → RBAC + trilha de auditoria (quem/quando/o quê)
3. **Por quanto tempo?** → política de retenção e rotina de eliminação
4. **Onde ficam?** → banco, logs, backups, exports, planilhas — TODOS os lugares contam

## Regras técnicas no código e no banco

- CPF/dados financeiros: criptografia em repouso + mascaramento em telas, relatórios e logs
  (`***.***.123-45`).
- Dados pessoais NUNCA em: logs de aplicação, mensagens de erro, URLs/query strings, git,
  ambientes de teste (usar dados sintéticos/anonimizados).
- Direitos do titular (Art. 18): o sistema precisa conseguir localizar, corrigir, exportar e
  **eliminar** todos os dados de um CPF — projete isso desde o início (chave de busca por titular).
- Registro das operações de tratamento (Art. 37).
- Contratos com operadores (cloud, Cloudflare, e-mail) cobrindo papel de operador e
  transferência internacional de dados.

## Incidentes — Res. CD/ANPD nº 15/2024 (RCIS)

- Incidente com risco ou dano relevante (dados financeiros contam!): comunicar **ANPD e
  titulares em até 3 dias úteis** após a confirmação (dobrado p/ pequeno porte).
- Implicação técnica: monitoramento e auditoria precisam DETECTAR e DIMENSIONAR um vazamento
  nesse prazo — pgAudit, logs de acesso, alertas. Sem isso, a organização descumpre o prazo por
  não saber o que vazou.
- Canal oficial: https://www.gov.br/anpd/pt-br/canais_atendimento/agente-de-tratamento/comunicado-de-incidente-de-seguranca-cis

## Radar regulatório (Agenda ANPD 2025–2026)

A ANPD está normatizando **padrões técnicos mínimos de segurança**, RIPD e
anonimização/pseudonimização — antecipe-se implementando o checklist do
**Guia ANPD de Segurança da Informação para Agentes de Tratamento de Pequeno Porte**
(referência oficial e gratuita):
https://www.gov.br/anpd/pt-br/centrais-de-conteudo/materiais-educativos-e-publicacoes/guia-orientativo-sobre-seguranca-da-informacao-para-agentes-de-tratamento-de-pequeno-porte
