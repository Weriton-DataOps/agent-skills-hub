---
name: requirements-discovery
description: "Descoberta de requisitos ESTRITAMENTE conversacional e segura — entender intenção, fazer perguntas, levantar restrições, propor alternativas, consolidar requisitos e pedir aprovação. NÃO escreve arquivos, não faz commit, não executa código e não inicia implementação. Skill canônica do Overcore, reutilizável pelo Oracle e pelo futuro Discovery do Pipeline."
risk: safe
source: overcore
date_added: "2026-07-29"
mutates: false
conversationalOnly: true
---

# Requirements Discovery

Skill canônica do Overcore para a fase de **descoberta**: transformar um pedido
vago em requisitos claros, antes de qualquer plano ou código. Substitui, no
contexto do Oracle, a skill genérica `brainstorming` — que é ampla, orientada a
trabalho criativo/de UI e classificada com `risk: unknown`. Aqui o contrato é
estreito e verificável: **só conversa**.

## Quando usar

- O usuário descreve um objetivo, problema ou ideia ainda sem requisitos firmes.
- Antes de montar `OracleTask`, plano, spec ou qualquer implementação.
- Sempre que faltar clareza de intenção, escopo, restrições ou critérios de aceite.

## Contrato de segurança (duro)

Esta skill é **exclusivamente conversacional**. Ela **NÃO PODE**:

- escrever, criar, editar ou apagar arquivos;
- fazer commit, push ou qualquer operação de Git;
- executar código, comandos de shell ou despachar agentes;
- iniciar implementação, scaffolding ou geração de artefatos de produção.

O único efeito colateral permitido é **texto na conversa**: perguntas, opções,
resumos e um pedido explícito de aprovação. Qualquer ação mutável pertence a
outra skill/papel, sob a política de níveis e aprovação do agente hospedeiro.
Uma entrada de catálogo que use esta skill não deve ter ferramenta mutável
permitida.

## Fluxo

1. **Entender a intenção** — reformule o pedido com suas palavras e confirme o
   objetivo real (o "porquê"), não só o "o quê".
2. **Avaliar escopo** — se o pedido reúne vários subsistemas independentes,
   sinalize antes de detalhar; proponha decompor primeiro.
3. **Perguntar o que falta** — uma rodada enxuta de perguntas de alto valor
   (usuários, dados, restrições, integrações, prazos, não-objetivos). Evite
   perguntas cuja resposta não muda a decisão.
4. **Levantar restrições** — técnicas, de negócio, legais/LGPD, de custo e de
   prazo. Nomeie premissas e marque as não confirmadas.
5. **Propor alternativas** — 2–3 caminhos com trade-offs (velocidade ×
   manutenção × segurança × custo); recomende um, sem esconder os demais.
6. **Consolidar requisitos** — objetivo, escopo, fora-de-escopo, restrições,
   premissas, riscos e **critérios de aceite** verificáveis.
7. **Pedir aprovação** — apresente o resumo consolidado e peça confirmação
   explícita antes de qualquer passo de planejamento/execução. Sem aprovação,
   pare.

## Saída

Um bloco de requisitos consolidados em texto (para o agente hospedeiro
transformar em `OracleTask`/plano). A skill **não grava** esse bloco — apenas o
apresenta na conversa e solicita aprovação.

## Anti-padrões

- Pular a descoberta e já propor implementação.
- Fazer dez perguntas de baixa relevância em vez de três decisivas.
- Afirmar requisito como certo sem confirmação do usuário.
- Produzir arquivos/artefatos "para adiantar" — proibido nesta skill.
