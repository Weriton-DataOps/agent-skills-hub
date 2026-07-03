---
name: fixing-motion-performance
description: Audit and fix animation performance issues including layout thrashing, compositor properties, scroll-linked motion, and blur effects. Use when animations stutter, transitions jank, or reviewing CSS/JS animation performance.
risk: safe
source: community
---

# fixing-motion-performance

Fix animation performance issues.

## how to use

- `/fixing-motion-performance`
  Apply these constraints to any UI animation work in this conversation.

- `/fixing-motion-performance <file>`
  Review the file against all rules below and report:
  - violations (quote the exact line or snippet)
  - why it matters (one short sentence)
  - a concrete fix (code-level suggestion)

Do not migrate animation libraries unless explicitly requested. Apply rules within the existing stack.

## When to Use
Reference these guidelines when:
- adding or changing UI animations (CSS, WAAPI, Motion, rAF, GSAP)
- refactoring janky interactions or transitions
- implementing scroll-linked motion or reveal-on-scroll
- animating layout, filters, masks, gradients, or CSS variables
- reviewing components that use will-change, transforms, or measurement

## rendering steps glossary

- composite: transform, opacity
- paint: color, borders, gradients, masks, images, filters
- layout: size, position, flow, grid, flex

## rule categories by priority

| priority | category | impact |
|----------|----------|--------|
| 1 | never patterns | critical |
| 2 | choose the mechanism | critical |
| 3 | measurement | high |
| 4 | scroll | high |
| 5 | paint | medium-high |
| 6 | layers | medium |
| 7 | blur and filters | medium |
| 8 | view transitions | low |
| 9 | tool boundaries | critical |

## quick reference

### 1. never patterns (critical)

- do not interleave layout reads and writes in the same frame
- do not animate layout continuously on large or meaningful surfaces
- do not drive animation from scrollTop, scrollY, or scroll events
- no requestAnimationFrame loops without a stop condition
- do not mix multiple animation systems that each measure or mutate layout

### 2. choose the mechanism (critical)

- default to transform and opacity for motion
- use JS-driven animation only when interaction requires it
- paint or layout animation is acceptable only on small, isolated surfaces
- one-shot effects are acceptable more often than continuous motion
- prefer downgrading technique over removing motion entirely

### 3. measurement (high)

- measure once, then animate via transform or opacity
- batch all DOM reads before writes
- do not read layout repeatedly during an animation
- prefer FLIP-style transitions for layout-like effects
- prefer approaches that batch measurement and writes

### 4. scroll (high)

- prefer Scroll or View Timelines for scroll-linked motion when available
- use IntersectionObserver for visibility and pausing
- do not poll scroll position for animation
- pause or stop animations when off-screen
- scroll-linked motion must not trigger continuous layout or paint on large surfaces

### 5. paint (medium-high)

- paint-triggering animation is allowed only on small, isolated elements
- do not animate paint-heavy properties on large containers
- do not animate CSS variables for transform, opacity, or position
- do not animate inherited CSS variables
- scope animated CSS variables locally and avoid inheritance

### 6. layers (medium)

- compositor motion requires layer promotion, never assume it
- use will-change temporarily and surgically
- avoid many or large promoted layers
- validate layer behavior with tooling when performance matters

### 7. blur and filters (medium)

- keep blur animation small (<=8px)
- use blur only for short, one-time effects
- never animate blur continuously
- never animate blur on large surfaces
- prefer opacity and translate before blur

### 8. view transitions (low)

- use view transitions only for navigation-level changes
- avoid view transitions for interaction-heavy UI
- avoid view transitions when interruption or cancellation is required
- treat size changes as potentially layout-triggering

### 9. tool boundaries (critical)

- do not migrate or rewrite animation libraries unless explicitly requested
- apply these rules within the existing animation system
- never partially migrate APIs or mix styles within the same component

## common fixes

```css
/* layout thrashing: animate transform instead of width */
/* before */ .panel { transition: width 0.3s; }
/* after */  .panel { transition: transform 0.3s; }

/* scroll-linked: use scroll-timeline instead of JS */
/* before */ window.addEventListener('scroll', () => el.style.opacity = scrollY / 500)
/* after */  .reveal { animation: fade-in linear; animation-timeline: view(); }
```

```js
// measurement: batch reads before writes (FLIP)
// before — layout thrash
el.style.left = el.getBoundingClientRect().left + 10 + 'px';
// after — measure once, animate via transform
const first = el.getBoundingClientRect();
el.classList.add('moved');
const last = el.getBoundingClientRect();
el.style.transform = `translateX(${first.left - last.left}px)`;
requestAnimationFrame(() => { el.style.transition = 'transform 0.3s'; el.style.transform = ''; });
```

## review guidance

- enforce critical rules first (never patterns, tool boundaries)
- choose the least expensive rendering work that matches the intent
- for any non-default choice, state the constraint that justifies it (surface size, duration, or interaction requirement)
- when reviewing, prefer actionable notes and concrete alternatives over theory

## Absorvido de Impeccable (Apache-2.0, modificado)

Derivado de `pbakaus/impeccable` (`reference/animate.md` e `reference/optimize.md`), licença Apache-2.0. Conteúdo **modificado**: traduzido para PT-BR, desacoplado do produto original e adaptado ao pipeline do Atelier — aplicar ao revisar peças e no `/varrer`; durações e easings entram como tokens de motion no DESIGN.md, nunca inline.

### Durações — regra 100/300/500

Timing importa mais que easing para "parecer certo". Todo valor vira token de motion no DESIGN.md.

| Duração | Uso | Exemplos |
|----------|----------|----------|
| **100–150ms** | Feedback instantâneo (micro) | Press de botão, toggle, mudança de cor |
| **200–300ms** | Mudanças de estado (transição) | Menu abrindo, tooltip, estado de hover |
| **300–500ms** | Mudanças de layout | Accordion, modal, drawer |
| **500–800ms** | Entradas | Page load, hero reveal (só em registro LANDING) |

- **Saída = 75% da entrada.** Animações de saída são sempre mais rápidas que as de entrada.
- Nunca acima de **500ms para feedback** — vira lag percebido.
- Registro APP/DASHBOARD: 150–250ms na maioria das transições; zero coreografia de page-load — o usuário está numa tarefa e não vai esperar por ela.

### Stagger — teto de 500ms total

- Stagger de irmãos é legítimo para cards-em-grid ou itens de lista aparecendo. Fade-and-rise em toda seção scrollada não é lista e não é legítimo — é tell de UI gerada.
- **Teto: 500ms de stagger total** (ex.: 10 itens × 50ms). Com mais itens, reduza o delay por item ou limite quantos participam do stagger.
- Implementação limpa: `animation-delay: calc(var(--i, 0) * 50ms)` com `--i: 0`, `--i: 1`… por item.

### Limiar de percepção — 80ms

Qualquer resposta abaixo de ~80ms é percebida como instantânea (o cérebro bufferiza a entrada sensorial nesse intervalo para sincronizar a percepção). É o alvo para micro-interações.

- **Início preemptivo**: comece a transição enquanto carrega (skeleton, zoom de abertura) — o usuário percebe trabalho acontecendo.
- **Conclusão antecipada**: mostre conteúdo progressivamente; não espere tudo (imagens progressivas, skeleton com fade).
- **UI otimista**: atualize a interface na hora e trate falha depois — só para ações de baixo risco (like, follow); nunca para pagamento ou operação destrutiva.
- Easing altera duração percebida: ease-in (acelerando ao fim) encurta a tarefa percebida; ease-out satisfaz em entradas.
- Cautela: resposta rápida demais reduz valor percebido em operações complexas (busca, análise) — às vezes um atraso breve sinaliza "trabalho real".

### Easing — banimentos

- **Proibido**: bounce, elastic e spring — datados, chamam atenção para a animação em si e não para o estado.
- **Proibido**: qualquer `cubic-bezier` com valores de y fora de **[-0.1, 1.1]** — é overshoot/elastic disfarçado de curva custom (ex.: `cubic-bezier(0.34, 1.56, 0.64, 1)` e `cubic-bezier(0.68, -0.6, 0.32, 1.6)` reprovam).
- Preferidas (desaceleração natural, registradas como tokens no DESIGN.md, nunca os defaults do CSS):

```css
--ease-out-quart: cubic-bezier(0.25, 1, 0.5, 1);   /* suave */
--ease-out-quint: cubic-bezier(0.22, 1, 0.36, 1);  /* um pouco mais seco */
--ease-out-expo:  cubic-bezier(0.16, 1, 0.3, 1);   /* confiante, decisivo */
```

### aspect-ratio contra CLS

Animação e carregamento nunca empurram layout (CLS < 0.1):

- Declare dimensões ou `aspect-ratio` em imagens, vídeos e embeds — reserve o espaço antes de o conteúdo chegar.
- Não injete conteúdo acima do já renderizado; reserve espaço para ads/embeds.
- Skeletons devem ocupar o mesmo footprint do conteúdo final.

```css
/* reserva o espaço da imagem antes do load */
.image-container { aspect-ratio: 16 / 9; }
```

### O ban real são propriedades de layout (refina "choose the mechanism")

O mecanismo correto não é "só transform e opacity". A regra dura é:

- **Proibido animar casualmente propriedades que dirigem layout**: `width`, `height`, `top`, `left`, margens. Para efeitos de layout, use FLIP, `grid-template-rows` ou transform.
- **Permitido, com fronteira declarada**: blur/filter/backdrop-filter, clip-path/masks, sombras e shifts de cor quando *bounded* — superfície pequena ou isolada, `contain` onde couber, suavidade verificada no navegador do viewport-alvo. Os limites da categoria "blur and filters" continuam valendo (blur ≤8px, nunca contínuo, nunca em superfície grande).
- Material por efeito: transform/opacity para movimento, press e reveals simples; blur para foco/profundidade/vidro; clip-path para wipes e transições editoriais; sombra/glow para energia e estado ativo; `grid-template-rows` ou FLIP para expandir sem animar `height` direto.

No `/varrer`, isto refina a leitura da A12: reprove animação de propriedade de layout; não reprove blur/clip-path bounded só por não serem transform/opacity — exija a justificativa da fronteira (tamanho da superfície, duração, `contain`).

## Limitations
- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
