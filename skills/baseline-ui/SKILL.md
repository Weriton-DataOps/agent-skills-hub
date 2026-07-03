---
name: baseline-ui
description: Validates animation durations, enforces typography scale, checks component accessibility, and prevents layout anti-patterns in Tailwind CSS projects. Use when building UI components, reviewing CSS utilities, styling React views, or enforcing design consistency.
risk: unknown
source: community
---

# Baseline UI

Enforces an opinionated UI baseline to prevent AI-generated interface slop.

## When to Use
- You are building or reviewing Tailwind-based UI and want a strict baseline for accessibility, motion, typography, and layout.
- The task is to prevent generic or sloppy AI-generated interface decisions before they spread through the codebase.
- You need concrete UI constraints to apply to a file review or an ongoing frontend implementation.

## How to use

- `/baseline-ui`
  Apply these constraints to any UI work in this conversation.

- `/baseline-ui <file>`
  Review the file against all constraints below and output:
  - violations (quote the exact line/snippet)
  - why it matters (1 short sentence)
  - a concrete fix (code-level suggestion)

## Stack

- MUST use Tailwind CSS defaults unless custom values already exist or are explicitly requested
- MUST use `motion/react` (formerly `framer-motion`) when JavaScript animation is required
- SHOULD use `tw-animate-css` for entrance and micro-animations in Tailwind CSS
- MUST use `cn` utility (`clsx` + `tailwind-merge`) for class logic

## Components

- MUST use accessible component primitives for anything with keyboard or focus behavior (`Base UI`, `React Aria`, `Radix`)
- MUST use the project’s existing component primitives first
- NEVER mix primitive systems within the same interaction surface
- SHOULD prefer [`Base UI`](https://base-ui.com/react/components) for new primitives if compatible with the stack
- MUST add an `aria-label` to icon-only buttons
- NEVER rebuild keyboard or focus behavior by hand unless explicitly requested

## Interaction

- MUST use an `AlertDialog` for destructive or irreversible actions
- SHOULD use structural skeletons for loading states
- NEVER use `h-screen`, use `h-dvh`
- MUST respect `safe-area-inset` for fixed elements
- MUST show errors next to where the action happens
- NEVER block paste in `input` or `textarea` elements

## Animation

- NEVER add animation unless it is explicitly requested
- MUST animate only compositor props (`transform`, `opacity`)
- NEVER animate layout properties (`width`, `height`, `top`, `left`, `margin`, `padding`)
- SHOULD avoid animating paint properties (`background`, `color`) except for small, local UI (text, icons)
- SHOULD use `ease-out` on entrance
- NEVER exceed `200ms` for interaction feedback
- MUST pause looping animations when off-screen
- SHOULD respect `prefers-reduced-motion`
- NEVER introduce custom easing curves unless explicitly requested
- SHOULD avoid animating large images or full-screen surfaces

## Typography

- MUST use `text-balance` for headings and `text-pretty` for body/paragraphs
- MUST use `tabular-nums` for data
- SHOULD use `truncate` or `line-clamp` for dense UI
- NEVER modify `letter-spacing` (`tracking-*`) unless explicitly requested

## Layout

- MUST use a fixed `z-index` scale (no arbitrary `z-*`)
- SHOULD use `size-*` for square elements instead of `w-*` + `h-*`

## Performance

- NEVER animate large `blur()` or `backdrop-filter` surfaces
- NEVER apply `will-change` outside an active animation
- NEVER use `useEffect` for anything that can be expressed as render logic

## Design

- NEVER use gradients unless explicitly requested
- NEVER use purple or multicolor gradients
- NEVER use glow effects as primary affordances
- SHOULD use Tailwind CSS default shadow scale unless explicitly requested
- MUST give empty states one clear next action
- SHOULD limit accent color usage to one per view
- SHOULD use existing theme or Tailwind CSS color tokens before introducing new ones

## Absorvido de Impeccable (Apache-2.0, modificado)

> Derivado de [pbakaus/impeccable](https://github.com/pbakaus/impeccable) (`reference/layout.md`, `reference/polish.md`, `reference/audit.md`), licença Apache-2.0. Conteúdo **modificado**: traduzido para PT-BR, desacoplado do produto original e adaptado ao vocabulário do Atelier (`/varrer`, registros LANDING/APP/DOCS, DESIGN.md, tokens herdados).

### Espaçamento e layout

- MUST usar escala base de **4pt** (4, 8, 12, 16, 24, 32, 48, 64, 96px) em vez de 8pt — 8pt é grossa demais: você vai precisar de 12px entre 8 e 16 com frequência.
- SHOULD nomear tokens de espaçamento semanticamente (`--space-xs` … `--space-xl`), nunca pelo valor (`--spacing-8`).
- MUST preferir `gap` a `margin` para espaçar irmãos — elimina os hacks de margin collapse.
- SHOULD criar ritmo, não uniformidade: agrupamento apertado entre irmãos relacionados (8–12px), separação generosa entre seções distintas (48–96px). Espaçamento igual em tudo = zero hierarquia.
- SHOULD usar `clamp()` para espaçamento fluido só em registro LANDING; em registro APP a responsividade é estrutural (colapsar sidebar, tabela responsiva), nunca fluida — consistência É affordance.
- MUST usar **container queries** para componentes e media queries de viewport apenas para o layout da página: o mesmo card fica compacto numa sidebar estreita e expande na área principal, sem variante nova.

```css
.card-container { container-type: inline-size; }
.card { display: grid; gap: var(--space-md); }
@container (min-width: 400px) {
  .card { grid-template-columns: 120px 1fr; }
}
```

### Ajustes ópticos

- Texto em `margin-left: 0` parece levemente indentado por causa do espaço em branco da própria letra; margem negativa (`-0.05em`) alinha opticamente.
- Glifo centrado geometricamente costuma parecer descentrado (ícone de play desloca para a direita; seta desloca na direção que aponta). Ajuste SÓ quando tiver certeza de que parece errado — nunca especulativamente.
- MUST garantir alvo de toque de **44×44px** mesmo quando o elemento visual é menor; expanda a hit-area com padding ou pseudo-element:

```css
.icon-button { width: 24px; height: 24px; position: relative; }
.icon-button::before {
  content: ''; position: absolute; inset: -10px;
}
```

### Taxonomia de causa-raiz de violação

Toda violação encontrada (na revisão de arquivo ou no `/varrer`) deve ser classificada ANTES do fix — corrigir o sintoma sem nomear a causa é como o drift se acumula:

| Causa-raiz | Diagnóstico | Fix correto |
|---|---|---|
| **Token faltante** | O valor deveria existir no DESIGN.md/sistema e não existe | Propor o token novo no gate; nunca hard-codar |
| **One-off** | Componente/token compartilhado já existe e não foi usado | Trocar pela versão herdada |
| **Desalinhamento conceitual** | Fluxo, IA ou hierarquia destoa das features vizinhas | Retrabalhar o fluxo — polir a superfície é decoração sobre drift |

Cada categoria pede um remédio diferente: remendar o valor, trocar pelo compartilhado, ou refazer o fluxo. Nunca aplique o mesmo às três. Se algo no sistema for ambíguo, pergunte — nunca adivinhe princípio de design system.

### Score de auditoria (/20) e severidade P0–P3

Na revisão (`/baseline-ui <file>` ou `/varrer`), além da lista de violações, pontue 5 dimensões de **0 a 4** cada:

| # | Dimensão | Âncora 0 | Âncora 4 |
|---|---|---|---|
| 1 | Acessibilidade | Inacessível (falha WCAG A) | WCAG AA integral, beira AAA |
| 2 | Performance | Layout thrash, nada otimizado | Rápido, enxuto, bem otimizado |
| 3 | Theming | Tudo hard-coded | Sistema de tokens completo, dark mode perfeito |
| 4 | Responsivo | Só desktop, quebra no mobile | Fluido em todos os viewports, alvos de toque corretos |
| 5 | Anti-padrões | Galeria de AI slop (5+ tells) | Zero tells, design distinto e intencional |

**Faixas do total**: 18–20 Excelente (só polimento) · 14–17 Bom (atacar dimensões fracas) · 10–13 Aceitável (trabalho significativo) · 6–9 Ruim (revisão grande) · 0–5 Crítico (problema fundamental).

Toda issue recebe severidade:

- **P0 Bloqueante** — impede completar a tarefa; corrigir imediatamente.
- **P1 Grave** — dificuldade significativa ou violação WCAG AA; corrigir antes do release.
- **P2 Menor** — incômodo com workaround; corrigir na próxima passada.
- **P3 Polimento** — sem impacto real no usuário; se sobrar tempo.

Regras do relatório: toda issue explica o **impacto** (por que importa), a recomendação é específica (nada genérico), registre também o que está funcionando bem, e nem tudo pode ser P0 — excesso de P3 é ruído. **Re-medição é obrigatória**: depois dos fixes, rode a auditoria de novo e compare o score — melhoria sem número novo é opinião.

### Prova de evidência — script limpo nunca é prova

- Saída de detector/QA automatizado é evidência de **defeito**, nunca de qualidade: resultado limpo não prova que o design é forte.
- **Screenshot não lido não conta.** Renderizar sem observar equivale a não ter renderizado; a validação exige olhar o caminho real de interação no browser.
- Corrija o que a automação apontar, mas NUNCA cite resultado limpo como aprovação de gate.

## Limitations
- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
