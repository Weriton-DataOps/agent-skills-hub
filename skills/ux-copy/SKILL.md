---
name: ux-copy
description: "Generate UX microcopy in StyleSeed's Toss-inspired voice for buttons, empty states, errors, toasts, confirmations, and form guidance."
category: design
risk: safe
source: community
source_repo: bitjaru/styleseed
source_type: community
date_added: "2026-04-08"
author: bitjaru
tags: [ux, copywriting, microcopy, frontend, styleseed]
tools: [claude, cursor, codex, gemini]
---

# UX Copy

## Overview

Part of [StyleSeed](https://github.com/bitjaru/styleseed), this skill generates concise product copy for common UI states. It follows the Toss-inspired tone: casual but polite, direct, active, and specific enough to help the user recover or proceed.

## When to Use
- Use when you need button labels, helper text, toasts, empty states, or error messages
- Use when a feature has functional UI but weak or robotic wording
- Use when you want consistent product voice across a flow
- Use when confirmation dialogs or state feedback need better phrasing

## Tone Rules

- casual but polite
- active voice over passive voice
- positive framing where it stays honest
- plain language instead of internal jargon
- concise wording where every word earns its place

## Common Patterns

### Buttons

Use a short action verb plus object when needed.

### Empty States

Start with a friendly observation, then suggest the next action.

### Errors

Explain what happened in user-facing language and what to do next. Do not surface raw internal error strings.

### Toasts

Confirm the result quickly. Add an undo action for reversible destructive behavior.

### Forms

Use clear labels, useful placeholders, specific helper text, and corrective error messages.

### Confirmation Dialogs

State the action in plain language and explain the consequence if the decision is risky or irreversible.

## Output

Return:
1. The requested microcopy grouped by UI surface
2. Notes on tone or localization considerations if relevant
3. Any places where the UX likely needs a structural fix in addition to better copy

## Best Practices

- Make the next action obvious
- Avoid generic labels like "Submit" or "OK" when the action can be named precisely
- Blame the system, not the user, when something fails
- Keep error and empty states useful even without visual context

## Absorvido de Impeccable (Apache-2.0, modificado)

> Derivado de [`pbakaus/impeccable`](https://github.com/pbakaus/impeccable) (referências de clarify, distill e delight), licença Apache-2.0. Este conteúdo foi **modificado**: traduzido para PT-BR, desacoplado do produto original e adaptado ao vocabulário do Atelier (registro LANDING/APP/DOCS, `/varrer`, DESIGN.md) — aviso de alteração conforme cláusula 4b da licença.

### Rótulos que dizem a consequência

Nunca "OK", "Enviar", "Sim/Não" — são rótulos preguiçosos e ambíguos. Todo botão diz o que vai acontecer, no padrão verbo + objeto:

| Ruim | Bom | Por quê |
|------|-----|---------|
| OK | Salvar alterações | Diz o que vai acontecer |
| Enviar | Criar conta | Foca no resultado, não no mecanismo |
| Sim | Excluir mensagem | Confirma a ação, não a pergunta |
| Cancelar | Continuar editando | Esclarece o que "cancelar" significa aqui |
| Clique aqui | Baixar PDF | Descreve o destino |

Para ações destrutivas, nomeie a destruição:
- "Excluir" quando é permanente; "Remover" implica recuperável — não troque um pelo outro.
- "Excluir 5 itens", nunca "Excluir selecionados" — mostre a contagem.

### Erros: fórmula e templates

Toda mensagem de erro responde três perguntas: **(1) o que houve? (2) por quê? (3) como resolver?** — "O e-mail precisa de um @. Exemplo: nome@exemplo.com", nunca "Entrada inválida".

| Situação | Template |
|----------|----------|
| **Erro de formato** | "[Campo] precisa estar em [formato]. Exemplo: [exemplo]" |
| **Obrigatório faltando** | "Informe [o que falta]" |
| **Permissão negada** | "Você não tem acesso a [coisa]. [O que fazer em vez disso]" |
| **Erro de rede** | "Não conseguimos alcançar [coisa]. Verifique sua conexão e [ação]." |
| **Erro de servidor** | "Algo deu errado do nosso lado. Já estamos verificando. [Ação alternativa]" |

Nunca culpe o usuário: "Informe a data no formato DD/MM/AAAA", não "Você digitou uma data inválida". E nunca humor em erro — o usuário já está frustrado; seja útil, não engraçadinho.

### Undo > confirmação

A maioria dos diálogos de confirmação é falha de design: prefira executar e oferecer **desfazer** (toast com "Desfazer" para ação destrutiva reversível). Quando a confirmação for inevitável (irreversível de verdade):
- Nomeie a ação específica: "Excluir 'Projeto Alpha'? Isso não pode ser desfeito.", nunca "Tem certeza?".
- Botões com consequência: "Excluir projeto" / "Manter projeto", nunca "Sim" / "Não".
- Não banalize: confirmação só para ação de risco — confirmar tudo treina o usuário a clicar sem ler.

### Expansão i18n

Copy que cabe em inglês estoura em outras línguas. Reserve espaço no layout desde o croqui:

| Idioma | Expansão sobre o inglês |
|--------|-------------------------|
| Alemão | +30% |
| Francês | +20% |
| Finlandês | +30-40% |
| Chinês | -30% (menos caracteres, mesma largura) |

Padrões amigáveis à tradução: mantenha números separados ("Novas mensagens: 3", não "Você tem 3 novas mensagens"); cada string é uma frase completa (a ordem das palavras muda por idioma); sem abreviações ("5 minutos atrás", não "5 min atrás"); dê contexto ao tradutor sobre onde a string aparece.

### Registro: onde a personalidade mora

A voz muda de distribuição conforme o registro da tela (LANDING/APP/DOCS do Atelier):

- **LANDING (registro brand)**: personalidade *distribuída* — voz na copy inteira, transições entre seções, recompensas de descoberta, toques sazonais.
- **APP/DASHBOARD (registro product)**: personalidade só em *momentos ganhos* — conclusão de tarefa, primeira ação, recuperação de erro, marcos atingidos. O resto da experiência é carregado por confiabilidade e consistência; delícia espalhada em toda parte vira ruído.
- Em qualquer registro: momento de delícia dura **< 1 segundo**, nunca bloqueia a funcionalidade, é pulável, e não se repete idêntico a cada interação.

### Cadência de copy de IA a evitar

Tells de texto gerado por máquina — reprovados no `/varrer` (regra A28):

- **> 2 travessões por bloco** de texto.
- Padrão **"X. Não Y."** repetido 3+ vezes ("Simples. Não complicado." / "Rápido. Não lento.").
- Loading/empty com clichê de IA: "Herding pixels", "Teaching robots to dance", "Consulting the magic 8-ball", "Counting backwards from infinity" e afins — instantaneamente reconhecíveis como copy de máquina.

Em vez disso, escreva mensagens específicas do que o produto realmente faz: "Sincronizando com as mudanças do time...", "Processando seus números de ontem...", "Preparando seu painel...". Para esperas longas, dê expectativa: "Analisando seus dados... costuma levar 30-60 segundos".

## Additional Resources

- [StyleSeed repository](https://github.com/bitjaru/styleseed)
- [Source skill](https://github.com/bitjaru/styleseed/blob/main/seeds/toss/.claude/skills/ux-copy/SKILL.md)

## Limitations
- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
