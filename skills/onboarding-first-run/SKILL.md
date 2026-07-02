---
name: onboarding-first-run
description: "Desenha onboarding e first-run que levam o usuário ao primeiro valor no menor tempo possível: anatomia dos 5 tipos de empty state, progressive disclosure, tours guiados e métricas de verificação. Use ao criar telas de primeiro uso, empty states ou fluxos de boas-vindas."
risk: safe
source: "pbakaus/impeccable (Apache-2.0, modificado)"
date_added: "2026-07-02"
origin: impeccable
upstream: https://github.com/pbakaus/impeccable
attribution: "Derivado de skill/reference/onboard.md — traduzido para PT-BR e adaptado ao pipeline do Atelier/OverCore. Arquivo modificado (Apache-2.0 §4b)."
---

# Onboarding e first-run — o primeiro minuto do usuário

O trabalho do onboarding não é ensinar o produto. É levar a pessoa ao momento que prova que o produto vale o tempo dela — o "aha moment" — o mais rápido possível. Tudo o mais é cerimônia.

**Contexto necessário antes de desenhar:** qual é o aha moment que se quer que o usuário alcance, e qual o nível de experiência dele. Sem essas duas respostas, qualquer onboarding é chute.

## Quando usar

- Ao desenhar a primeira tela que um usuário novo vê (welcome, setup de conta, primeiro projeto).
- Ao criar **qualquer empty state** — primeira vez, busca sem resultado, erro de carregamento, falta de permissão.
- Ao decidir se uma feature nova merece tour, tooltip, anúncio ou nada.
- No Atelier: quando o `/croqui` de uma tela inclui estado vazio ou fluxo de primeiro uso, e no `/varrer` como parte do checklist de estados (empty é estado obrigatório, não decoração opcional).

## Diagnóstico — antes de desenhar

Responda em três blocos:

1. **O desafio**
   - O que os usuários estão tentando realizar?
   - O que na experiência atual confunde ou trava?
   - Onde eles empacam ou abandonam?
   - Qual é o aha moment que queremos que alcancem?

2. **Os usuários**
   - Nível de experiência? (Iniciantes, power users, misto?)
   - Motivação? (Explorando por vontade própria ou obrigados pelo trabalho?)
   - Tempo disponível? (5 minutos? 30 minutos?)
   - Alternativas que conhecem? (Vêm de concorrente ou o conceito é novo?)

3. **Sucesso**
   - Qual o mínimo que precisam aprender para ter sucesso?
   - Qual a ação-chave que queremos que tomem? (Primeiro projeto? Primeiro convite?)
   - Como saberemos que funcionou? (Taxa de conclusão? Tempo até valor?)

**CRÍTICO:** onboarding leva o usuário ao valor o mais rápido possível — não ensina tudo que é possível ensinar.

## Princípios

### Mostre, não conte
- Demonstre com exemplos funcionais, não descrições.
- Funcionalidade real dentro do onboarding, nunca "modo tutorial" apartado do produto.
- Progressive disclosure: ensine UMA coisa por vez.

### Torne opcional (quando possível)
- Usuários experientes pulam.
- Nunca bloqueie o acesso ao produto.
- Ofereça "Pular" ou "Prefiro explorar sozinho" — visível, não escondido.

### Tempo até o valor
- Aha moment o mais cedo possível.
- Conceitos mais importantes primeiro (front-load).
- Ensine os **20% que entregam 80% do valor**.
- Features avançadas ficam para descoberta contextual, depois.

### Contexto acima de cerimônia
- Ensine a feature quando o usuário precisa dela, não tudo de antemão.
- **Empty states são oportunidades de onboarding** — o melhor momento de ensinar é o vazio.
- Tooltips e dicas no ponto de uso.

### Respeite a inteligência do usuário
- Não infantilize nem sobre-explique.
- Seja conciso e claro.
- Assuma que padrões convencionais o usuário decifra sozinho.

## Onboarding inicial do produto

**Tela de boas-vindas**
- Proposta de valor clara (o que é este produto?).
- O que o usuário vai aprender/realizar.
- Estimativa de tempo honesta.
- Opção de pular.

**Setup de conta**
- Mínimo de informação obrigatória (colete o resto depois).
- Explique por que cada dado é pedido.
- Defaults inteligentes onde couber.
- Login social quando fizer sentido.

**Introdução de conceitos**
- Apresente **1 a 3 conceitos centrais** — nunca todos.
- Linguagem simples, com exemplos.
- Interativo quando possível (fazer, não só ler).
- Indicação de progresso ("passo 1 de 3").

**Primeiro sucesso**
- Guie o usuário a realizar algo real.
- Exemplos pré-populados ou templates.
- Celebre a conclusão (sem exagero).
- Próximos passos claros.

## Descoberta e adoção de features

**Empty states** — em vez de espaço em branco, mostre:
- O que vai aparecer ali (descrição + ilustração/screenshot).
- Por que isso tem valor.
- CTA claro para criar o primeiro item.
- Opção de exemplo ou template.

Modelo:

```
Nenhum projeto ainda
Projetos organizam seu trabalho e a colaboração com seu time.
[Criar seu primeiro projeto] ou [Começar de um template]
```

**Tooltips contextuais**
- Aparecem no momento relevante (primeira vez que o usuário vê a feature).
- Apontam direto para o elemento de UI em questão.
- Explicação breve + benefício.
- Dispensáveis (com "Não mostrar de novo").
- Link "Saiba mais" opcional.

**Anúncios de feature**
- Destaque novidades no lançamento: o que mudou e por que importa.
- Deixe o usuário experimentar na hora.
- Dispensável.

**Onboarding progressivo**
- Ensine features quando o usuário as encontra.
- Badges ou indicadores em features novas/não usadas.
- Desbloqueie complexidade gradualmente — nunca todas as opções de uma vez.

## Tours guiados e walkthroughs

**Quando usar:** interfaces complexas com muitas features; mudanças significativas em produto existente; ferramentas de domínio específico que exigem conhecimento prévio.

**Como desenhar:**
- Spotlight no elemento específico (escureça o resto da página).
- Passos curtos: **3 a 7 passos no máximo por tour**.
- Usuário navega livremente entre passos.
- "Pular tour" sempre presente.
- Reexecutável (via menu de ajuda).

**Boas práticas:**
- Interativo > passivo: deixe o usuário clicar nos botões reais.
- Foque no fluxo de trabalho, não na feature ("Crie um projeto", não "Este é o botão de projeto").
- Dados de exemplo para que as ações funcionem de verdade.

## Tutoriais interativos

**Quando usar:** o usuário precisa de prática hands-on; conceitos complexos ou desconhecidos; alto risco (melhor errar em ambiente seguro).

**Como desenhar:**
- Sandbox com dados de exemplo.
- Objetivos claros ("Crie um gráfico de vendas por região").
- Guia passo a passo.
- Validação (confirme que fez certo).
- Momento de formatura ("você está pronto").

## Documentação e ajuda in-product

- Links de ajuda contextuais espalhados pela interface.
- Referência de atalhos de teclado.
- Central de ajuda pesquisável; vídeos para fluxos complexos.

Padrões: ícone `?` junto a features complexas; "Saiba mais" em tooltips; dica de atalho visível (`⌘K` na caixa de busca).

## Anatomia do empty state

Todo empty state precisa de **5 elementos**:

1. **O que estará aqui** — "Seus projetos recentes vão aparecer aqui."
2. **Por que importa** — "Projetos organizam seu trabalho e a colaboração com seu time."
3. **Como começar** — [Criar projeto] ou [Importar de template].
4. **Interesse visual** — ilustração ou ícone (nunca só texto em página branca). No Atelier: dentro dos tokens do DESIGN.md, e respeitando A17 (nada de gradiente abstrato genérico como placeholder).
5. **Ajuda contextual** — "Precisa de ajuda? [Assista ao tutorial de 2 min]."

### Os 5 tipos de empty state

| Tipo | Situação | Tratamento |
|---|---|---|
| **Primeiro uso** | Nunca usou a feature | Enfatize o valor, ofereça template |
| **Usuário limpou** | Apagou tudo de propósito | Toque leve, recriar deve ser fácil — não venda o valor de novo |
| **Sem resultados** | Busca ou filtro retornou vazio | Sugira outra query, ofereça limpar filtros |
| **Sem permissão** | Não pode acessar | Explique por quê e como obter acesso |
| **Estado de erro** | Falha ao carregar | Explique o que aconteceu, ofereça retry |

Confundir os tipos é erro clássico: mostrar o pitch de "primeiro uso" para quem acabou de apagar tudo intencionalmente é patronizar; mostrar um vazio mudo em erro de carregamento é abandonar o usuário.

## Implementação

- **Tooltips:** Tippy.js, Popper.js.
- **Tours:** Intro.js, Shepherd.js, React Joyride.
- **Modais:** focus trap, backdrop, ESC fecha.
- **Progresso:** persistir estados "visto" (ex.: localStorage) — `onboarding-completed`, `feature-tooltip-seen-<feature>`.
- **Analytics:** rastrear conclusão e pontos de abandono.

**IMPORTANTE:** nunca mostre o mesmo onboarding duas vezes. Rastreie conclusão e respeite dispensas.

## NUNCA

- Forçar o usuário por onboarding longo antes de poder usar o produto.
- Patronizar com explicações do óbvio.
- Repetir tooltip já dispensado.
- Bloquear toda a UI durante o tour (deixe explorar).
- Criar modo tutorial apartado do produto real.
- Despejar informação de uma vez (progressive disclosure!).
- Esconder o "Pular" ou dificultar encontrá-lo.
- Esquecer o usuário recorrente (nunca reexibir o onboarding inicial).

## Verificação de qualidade

Teste com usuários reais e meça:

- **Tempo de conclusão** — conseguem terminar o onboarding rápido?
- **Compreensão** — entendem depois de concluir?
- **Ação** — tomam o próximo passo desejado?
- **Taxa de skip** — muitos pulando? (Talvez esteja longo demais ou sem valor.)
- **Taxa de conclusão** — estão concluindo? (Se baixa, simplifique.)
- **Tempo até o valor** — quanto tempo até o primeiro valor real?

No Atelier: o empty state entra no checklist de estados do `/varrer` (hover/focus/empty/loading/error) e responde às regras anti-slop como qualquer peça — declare o registro da tela (LANDING/APP/DOCS) antes, porque o tom do empty state muda com ele (venda em LANDING, sobriedade operacional em APP). Quando o usuário chega ao aha moment rápido e sem abandono, encaminhe o acabamento com `/polir`.
