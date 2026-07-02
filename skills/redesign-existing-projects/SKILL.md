---
name: redesign-existing-projects
description: "Use when upgrading existing websites or apps by auditing generic UI patterns and applying premium design fixes without rewrites."
category: frontend
risk: safe
source: community
source_repo: Leonxlnx/taste-skill
source_type: community
date_added: "2026-04-17"
author: Leonxlnx
tags: [frontend, redesign, design-audit, ui]
tools: [claude, cursor, codex, antigravity]
---
# Redesign Skill

## When to Use

- Use when the user asks to redesign, restyle, modernize, polish, or improve an existing website or app UI.
- Use when the task is to audit current frontend code and make targeted visual improvements without changing the product architecture.
- Use when the design feels generic, AI-generated, poorly spaced, visually flat, or missing responsive, interactive, loading, empty, or error states.

## Limitations

- This skill upgrades existing UI but does not authorize framework migrations, information-architecture rewrites, or product-scope expansion by default.
- Preserve working behavior, routing, data flows, accessibility semantics, and tests while making visual changes.
- Validate redesigned screens in the actual app across supported browsers and viewport sizes before considering the work complete.


## How This Works

When applied to an existing project, follow this sequence:

1. **Scan** — Read the codebase. Identify the framework, styling method (Tailwind, vanilla CSS, styled-components, etc.), and current design patterns.
2. **Diagnose** — Run through the audit below. List every generic pattern, weak point, and missing state you find.
3. **Fix** — Apply targeted upgrades working with the existing stack. Do not rewrite from scratch. Improve what's there.

## Design Audit

### Typography

Check for these problems and fix them:

- **Browser default fonts or Inter everywhere.** Replace with a font that has character. Good options: `Geist`, `Outfit`, `Cabinet Grotesk`, `Satoshi`. For editorial/creative projects, pair a serif header with a sans-serif body.
- **Headlines lack presence.** Increase size for display text, tighten letter-spacing, reduce line-height. Headlines should feel heavy and intentional.
- **Body text too wide.** Limit paragraph width to roughly 65 characters. Increase line-height for readability.
- **Only Regular (400) and Bold (700) weights used.** Introduce Medium (500) and SemiBold (600) for more subtle hierarchy.
- **Numbers in proportional font.** Use a monospace font or enable tabular figures (`font-variant-numeric: tabular-nums`) for data-heavy interfaces.
- **Missing letter-spacing adjustments.** Use negative tracking for large headers, positive tracking for small caps or labels.
- **All-caps subheaders everywhere.** Try lowercase italics, sentence case, or small-caps instead.
- **Orphaned words.** Single words sitting alone on the last line. Fix with `text-wrap: balance` or `text-wrap: pretty`.

### Color and Surfaces

- **Pure `#000000` background.** Replace with off-black, dark charcoal, or tinted dark (`#0a0a0a`, `#121212`, or a dark navy).
- **Oversaturated accent colors.** Keep saturation below 80%. Desaturate accents so they blend with neutrals instead of screaming.
- **More than one accent color.** Pick one. Remove the rest. Consistency beats variety.
- **Mixing warm and cool grays.** Stick to one gray family. Tint all grays with a consistent hue (warm or cool, not both).
- **Purple/blue "AI gradient" aesthetic.** This is the most common AI design fingerprint. Replace with neutral bases and a single, considered accent.
- **Generic `box-shadow`.** Tint shadows to match the background hue. Use colored shadows (e.g., dark blue shadow on a blue background) instead of pure black at low opacity.
- **Flat design with zero texture.** Add subtle noise, grain, or micro-patterns to backgrounds. Pure flat vectors feel sterile.
- **Perfectly even gradients.** Break the uniformity with radial gradients, noise overlays, or mesh gradients instead of standard linear 45-degree fades.
- **Inconsistent lighting direction.** Audit all shadows to ensure they suggest a single, consistent light source.
- **Random dark sections in a light mode page (or vice versa).** A single dark-background section breaking an otherwise light page looks like a copy-paste accident. Either commit to a full dark mode or keep a consistent background tone throughout. If contrast is needed, use a slightly darker shade of the same palette — not a sudden jump to `#111` in the middle of a cream page.
- **Empty, flat sections with no visual depth.** Sections that are just text on a plain background feel unfinished. Add high-quality background imagery (blurred, overlaid, or masked), subtle patterns, or ambient gradients. Use reliable placeholder sources like `https://picsum.photos/seed/{name}/1920/1080` when real assets are not available. Experiment with background images behind hero sections, feature blocks, or CTAs — even a subtle full-width photo at low opacity adds presence.

### Layout

- **Everything centered and symmetrical.** Break symmetry with offset margins, mixed aspect ratios, or left-aligned headers over centered content.
- **Three equal card columns as feature row.** This is the most generic AI layout. Replace with a 2-column zig-zag, asymmetric grid, horizontal scroll, or masonry layout.
- **Using `height: 100vh` for full-screen sections.** Replace with `min-height: 100dvh` to prevent layout jumping on mobile browsers (iOS Safari viewport bug).
- **Complex flexbox percentage math.** Replace with CSS Grid for reliable multi-column structures.
- **No max-width container.** Add a container constraint (around 1200-1440px) with auto margins so content doesn't stretch edge-to-edge on wide screens.
- **Cards of equal height forced by flexbox.** Allow variable heights or use masonry when content varies in length.
- **Uniform border-radius on everything.** Vary the radius: tighter on inner elements, softer on containers.
- **No overlap or depth.** Elements sit flat next to each other. Use negative margins to create layering and visual depth.
- **Symmetrical vertical padding.** Top and bottom padding are always identical. Adjust optically — bottom padding often needs to be slightly larger.
- **Dashboard always has a left sidebar.** Try top navigation, a floating command menu, or a collapsible panel instead.
- **Missing whitespace.** Double the spacing. Let the design breathe. Dense layouts work for data dashboards, not for marketing pages.
- **Buttons not bottom-aligned in card groups.** When cards have different content lengths, CTAs end up at random heights. Pin buttons to the bottom of each card so they form a clean horizontal line regardless of content above.
- **Feature lists starting at different vertical positions.** In pricing tables or comparison cards, the list of features should start at the same Y position across all columns. Use consistent spacing above the list or fixed-height title/price blocks.
- **Inconsistent vertical rhythm in side-by-side elements.** When placing cards, columns, or panels next to each other, align shared elements (titles, descriptions, prices, buttons) across all items. Misaligned baselines make the layout look broken.
- **Mathematical alignment that looks optically wrong.** Centering by the math doesn't always look centered to the eye. Icons next to text, play buttons in circles, or text in buttons often need 1-2px optical adjustments to feel right.

### Interactivity and States

- **No hover states on buttons.** Add background shift, slight scale, or translate on hover.
- **No active/pressed feedback.** Add a subtle `scale(0.98)` or `translateY(1px)` on press to simulate a physical click.
- **Instant transitions with zero duration.** Add smooth transitions (200-300ms) to all interactive elements.
- **Missing focus ring.** Ensure visible focus indicators for keyboard navigation. This is an accessibility requirement, not optional.
- **No loading states.** Replace generic circular spinners with skeleton loaders that match the layout shape.
- **No empty states.** An empty dashboard showing nothing is a missed opportunity. Design a composed "getting started" view.
- **No error states.** Add clear, inline error messages for forms. Do not use `window.alert()`.
- **Dead links.** Buttons that link to `#`. Either link to real destinations or visually disable them.
- **No indication of current page in navigation.** Style the active nav link differently so users know where they are.
- **Scroll jumping.** Anchor clicks jump instantly. Add `scroll-behavior: smooth`.
- **Animations using `top`, `left`, `width`, `height`.** Switch to `transform` and `opacity` for GPU-accelerated, smooth animation.

### Content

- **Generic names like "John Doe" or "Jane Smith".** Use diverse, realistic-sounding names.
- **Fake round numbers like `99.99%`, `50%`, `$100.00`.** Use organic, messy data: `47.2%`, `$99.00`, `+1 (312) 847-1928`.
- **Placeholder company names like "Acme Corp", "Nexus", "SmartFlow".** Invent contextual, believable brand names.
- **AI copywriting cliches.** Never use "Elevate", "Seamless", "Unleash", "Next-Gen", "Game-changer", "Delve", "Tapestry", or "In the world of...". Write plain, specific language.
- **Exclamation marks in success messages.** Remove them. Be confident, not loud.
- **"Oops!" error messages.** Be direct: "Connection failed. Please try again."
- **Passive voice.** Use active voice: "We couldn't save your changes" instead of "Mistakes were made."
- **All blog post dates identical.** Randomize dates to appear real.
- **Same avatar image for multiple users.** Use unique assets for every distinct person.
- **Lorem Ipsum.** Never use placeholder latin text. Write real draft copy.
- **Title Case On Every Header.** Use sentence case instead.

### Component Patterns

- **Generic card look (border + shadow + white background).** Remove the border, or use only background color, or use only spacing. Cards should exist only when elevation communicates hierarchy.
- **Always one filled button + one ghost button.** Add text links or tertiary styles to reduce visual noise.
- **Pill-shaped "New" and "Beta" badges.** Try square badges, flags, or plain text labels.
- **Accordion FAQ sections.** Use a side-by-side list, searchable help, or inline progressive disclosure.
- **3-card carousel testimonials with dots.** Replace with a masonry wall, embedded social posts, or a single rotating quote.
- **Pricing table with 3 towers.** Highlight the recommended tier with color and emphasis, not just extra height.
- **Modals for everything.** Use inline editing, slide-over panels, or expandable sections instead of popups for simple actions.
- **Avatar circles exclusively.** Try squircles or rounded squares for a less generic look.
- **Light/dark toggle always a sun/moon switch.** Use a dropdown, system preference detection, or integrate it into settings.
- **Footer link farm with 4 columns.** Simplify. Focus on main navigational paths and legally required links.

### Iconography

- **Lucide or Feather icons exclusively.** These are the "default" AI icon choice. Use Phosphor, Heroicons, or a custom set for differentiation.
- **Rocketship for "Launch", shield for "Security".** Replace cliche metaphors with less obvious icons (bolt, fingerprint, spark, vault).
- **Inconsistent stroke widths across icons.** Audit all icons and standardize to one stroke weight.
- **Missing favicon.** Always include a branded favicon.
- **Stock "diverse team" photos.** Use real team photos, candid shots, or a consistent illustration style instead of uncanny stock imagery.

### Code Quality

- **Div soup.** Use semantic HTML: `<nav>`, `<main>`, `<article>`, `<aside>`, `<section>`.
- **Inline styles mixed with CSS classes.** Move all styling to the project's styling system.
- **Hardcoded pixel widths.** Use relative units (`%`, `rem`, `em`, `max-width`) for flexible layouts.
- **Missing alt text on images.** Describe image content for screen readers. Never leave `alt=""` or `alt="image"` on meaningful images.
- **Arbitrary z-index values like `9999`.** Establish a clean z-index scale in the theme/variables.
- **Commented-out dead code.** Remove all debug artifacts before shipping.
- **Import hallucinations.** Check that every import actually exists in `package.json` or the project dependencies.
- **Missing meta tags.** Add proper `<title>`, `description`, `og:image`, and social sharing meta tags.

### Strategic Omissions (What AI Typically Forgets)

- **No legal links.** Add privacy policy and terms of service links in the footer.
- **No "back" navigation.** Dead ends in user flows. Every page needs a way back.
- **No custom 404 page.** Design a helpful, branded "page not found" experience.
- **No form validation.** Add client-side validation for emails, required fields, and format checks.
- **No "skip to content" link.** Essential for keyboard users. Add a hidden skip-link.
- **No cookie consent.** If required by jurisdiction, add a compliant consent banner.

## Upgrade Techniques

When upgrading a project, pull from these high-impact techniques to replace generic patterns:

### Typography Upgrades
- **Variable font animation.** Interpolate weight or width on scroll or hover for text that feels alive.
- **Outlined-to-fill transitions.** Text starts as a stroke outline and fills with color on scroll entry or interaction.
- **Text mask reveals.** Large typography acting as a window to video or animated imagery behind it.

### Layout Upgrades
- **Broken grid / asymmetry.** Elements that deliberately ignore column structure — overlapping, bleeding off-screen, or offset with calculated randomness.
- **Whitespace maximization.** Aggressive use of negative space to force focus on a single element.
- **Parallax card stacks.** Sections that stick and physically stack over each other during scroll.
- **Split-screen scroll.** Two halves of the screen sliding in opposite directions.

### Motion Upgrades
- **Smooth scroll with inertia.** Decouple scrolling from browser defaults for a heavier, cinematic feel.
- **Staggered entry.** Elements cascade in with slight delays, combining Y-axis translation with opacity fade. Never mount everything at once.
- **Spring physics.** Replace linear easing with spring-based motion for a natural, weighty feel on all interactive elements.
- **Scroll-driven reveals.** Content entering through expanding masks, wipes, or draw-on SVG paths tied to scroll progress.

### Surface Upgrades
- **True glassmorphism.** Go beyond `backdrop-filter: blur`. Add a 1px inner border and a subtle inner shadow to simulate edge refraction.
- **Spotlight borders.** Card borders that illuminate dynamically under the cursor.
- **Grain and noise overlays.** A fixed, pointer-events-none overlay with subtle noise to break digital flatness.
- **Colored, tinted shadows.** Shadows that carry the hue of the background rather than using generic black.

## Fix Priority

Apply changes in this order for maximum visual impact with minimum risk:

1. **Font swap** — biggest instant improvement, lowest risk
2. **Color palette cleanup** — remove clashing or oversaturated colors
3. **Hover and active states** — makes the interface feel alive
4. **Layout and spacing** — proper grid, max-width, consistent padding
5. **Replace generic components** — swap cliche patterns for modern alternatives
6. **Add loading, empty, and error states** — makes it feel finished
7. **Polish typography scale and spacing** — the premium final touch

## Rules

- Work with the existing tech stack. Do not migrate frameworks or styling libraries.
- Do not break existing functionality. Test after every change.
- Before importing any new library, check the project's dependency file first.
- If the project uses Tailwind, check the version (v3 vs v4) before modifying config.
- If the project has no framework, use vanilla CSS.
- Keep changes reviewable and focused. Small, targeted improvements over big rewrites.

## Absorvido de Impeccable (Apache-2.0, modificado)

> Derivado de [pbakaus/impeccable](https://github.com/pbakaus/impeccable) (Apache-2.0). Conteúdo **modificado**: traduzido para PT-BR, desacoplado do produto original e adaptado ao vocabulário do Atelier (`/varrer`, `/subir`, `DESIGN.md`, registros LANDING/APP/DOCS).

No fluxo Scan → Diagnose → Fix desta skill: o **drift de IA** entra no Diagnose, o **Design-System Lock** governa o Fix, e o **teste de 2ª ordem** roda antes de fixar direção e de novo no `/varrer` final.

### Drift de IA — inconsistência contra vizinhos é sinal de geração

Polimento visual sobre um fluxo deformado é trabalho desperdiçado. Código gerado por IA se trai menos pelo que erra sozinho e mais pelo que faz *diferente das telas vizinhas* sem razão. Antes de corrigir superfície, compare a tela com as features adjacentes do mesmo produto:

- **Divulgação progressiva** — uma tela de configurações expondo 40 campos quando o resto do app revela 5 por vez é drift, mesmo com cada campo perfeitamente estilizado.
- **Forma dos fluxos** — ações de múltiplos passos seguem a mesma forma dos fluxos comparáveis: modal vs página inteira, edição inline vs rota separada, save-on-blur vs submit explícito, update otimista vs pessimista.
- **Peso da hierarquia** — o mesmo peso conceitual recebe o mesmo peso visual em todo lugar; ação primária não vira terciária num canto do produto, e terciária não grita.
- **Chegada e saída de conteúdo** — empty, loading e transições de chegada se comportam como nas features vizinhas.
- **Modelo mental e nomes** — mesmos substantivos e verbos do resto do sistema; um "Workspace" aqui não pode ser "Projeto" três telas adiante.

Todo desvio encontrado recebe uma **causa-raiz** antes do fix — cada categoria pede um fix diferente, e corrigir o sintoma sem nomear a causa é como o drift se acumula:

| Causa | Diagnóstico | Fix |
|---|---|---|
| **Token faltante** | o valor deveria existir no sistema, mas não existe | criar o token — com aprovação nominal (ver Lock abaixo) — e usar |
| **One-off** | componente/token compartilhado já existe, mas não foi usado | trocar pela versão compartilhada e apagar a cópia |
| **Desalinhamento conceitual** | fluxo, arquitetura de informação ou hierarquia não batem com as vizinhas | retrabalhar o fluxo, não a superfície |

Detector e QA automatizado valem só como evidência de *defeito*: **script limpo nunca é prova** de que o design está forte. A prova vem de renderizar, percorrer o caminho real de interação e observar.

### Design-System Lock no redesign

Quando o projeto tem `DESIGN.md`, tokens ou estilos de componente estabelecidos, esse sistema é a **fronteira** do redesign. "Deixar mais ousado" nunca é licença para gradiente ciano/roxo, glass, neon em fundo escuro ou gradiente em métrica — esse é o reflexo, o oposto de ousado. Fortaleça a linguagem existente antes de adicionar linguagem nova:

- Amplifique via **ênfase, proporção, ritmo, densidade, contraste, copy e relações de layout** — dentro do sistema documentado. É o mandato de `/subir`: contraste/escala/posição, zero decoração nova.
- **Se todo elemento fica mais alto, a composição não fica mais ousada; fica mais chapada.** Eleja UM ponto focal que o usuário deve lembrar e faça o resto sustentá-lo.
- O registro dita o significado: em **LANDING**, "ousado" = ponto de vista mais forte (hierarquia, pacing, uma ideia visual comprometida); em **APP/DASHBOARD**, "ousado" quase nunca é teatro — é hierarquia mais firme, contraste de peso mais claro, densidade de informação mais nítida. Amplificação em clareza, não em drama.
- **Token novo = aprovação nominal.** Se o sistema existente for genuinamente limitado demais para a direção, pare e peça aprovação ANTES de expandir: nomeie cada adição exata (cor, gradiente, sombra, raio, fonte, efeito), o papel que cada uma cumprirá e por que o sistema atual não dá conta. Aprovado, o token entra no `DESIGN.md` junto com a implementação — nunca inline. É a regra A18 do Atelier aplicada ao redesign: herança nunca é sobrescrita.
- Verificação ao final do passe: o resultado é **fiel ao sistema** (a linguagem existente ficou mais forte antes de qualquer coisa nova?) e **sem drift não-documentado** (toda cor, sombra, raio, fonte ou efeito novo está ausente ou explicitamente aprovado e registrado?).

### Teste anti-reflexo de 2ª ordem

O teste de slop roda em duas altitudes; a segunda pega o que a primeira deixa passar:

- **1ª ordem** — se alguém consegue adivinhar tema + paleta só pela categoria do produto, é o primeiro reflexo do dado de treino. Retrabalhe direção e estratégia de cor até a resposta deixar de ser óbvia a partir do domínio.
- **2ª ordem** — se alguém consegue adivinhar a família estética a partir de **categoria + anti-referências** ("ferramenta de IA que *não* é creme-SaaS → editorial-tipográfico"; "fintech que *não* é navy-e-dourado → dark mode estilo terminal"), caiu na armadilha um andar abaixo: o primeiro reflexo foi evitado, o segundo não. **Se categoria + anti-referências ainda predizem a estética resultante, ainda é slop.**

Retrabalhe até as DUAS respostas serem não-óbvias. Na prática do Atelier: antes de fixar a direção do redesign, declare por escrito o que a categoria prediria (1ª ordem) e o que a categoria-menos-o-clichê prediria (2ª ordem); no `/varrer`, confira se o resultado escapa das duas previsões.
