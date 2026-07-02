---
name: center-stage-carousel
description: "Carrossel center-stage arrastável de produção: palco central com vizinhos em peek, arrasto 1:1 (0ms) com snap suave (800ms), arrasto≠clique, autoplay que pausa em hover/foco/reduced-motion e touch que não sequestra o scroll."
risk: safe
source: "overcore:producao (Portal GR)"
date_added: "2026-07-02"
origin: producao:portal-gr
author: "Weriton — GR Group"
contributed_via: https://github.com/Weriton-DataOps/agent-skills-hub/issues/9
---

# Center-Stage Carousel — o carrossel que discrimina intenção

## Quando usar
Cards de destaque com narrativa guiada (comunicados, cases, ofertas) onde o item central
é o protagonista e os vizinhos convidam à navegação. Padrão extraído de **produção**
(landing do Portal GR) — não de tutorial.

## As 8 regras do ofício

1. **Palco central.** Ativo `scale(1)`; vizinhos `scale(0.86)`; z-index em camadas
   (30/20/10). Profundidade por escala e sobreposição — **não** por sombra falsa.
2. **Peek por breakpoint.** Desktop: metade do vizinho visível (`translateX(±55%)`).
   Mobile: vizinhos a ±100% — só o centro aparece; peek em tela estreita é ruído.
3. **Arrasto 1:1.** `transition-duration: 0ms` **enquanto arrasta** (o transform soma o
   deslocamento do cursor) e **~800ms no soltar**, easing `cubic-bezier(0.22, 1, 0.36, 1)`
   — ease-out forte, sem overshoot (A26-safe). Snap de ±1 slide por gesto.
4. **Sem pop-in.** Slides fora da vista ficam no DOM com `opacity: 0` para entrarem
   deslizando; nunca montar/desmontar durante a animação.
5. **Arrasto ≠ clique.** Uma ref de "houve arrasto" bloqueia navegação após o gesto;
   clique no vizinho **foca** o slide (não navega). `pointerdown` no elemento,
   `move`/`up` no `window`.
6. **Autoplay educado.** Pausa em: hover, foco interno, arrasto em andamento e
   `prefers-reduced-motion`. Intervalo generoso (~10s) — tempo de imagem limpa.
7. **Touch decente.** `touch-action: pan-y`: o scroll vertical nunca é sequestrado;
   gesto vertical cancela o arrasto sem trocar slide.
8. **Acessível.** `aria-hidden` nos não-centrais; foco interno pausa o autoplay;
   setas/dots continuam existindo para quem não arrasta.

## Anti-padrões que este ofício mata
- Carrossel que troca de slide quando você só queria clicar.
- Autoplay que continua rodando embaixo do mouse (ou com reduced-motion ativo).
- Slide que "pisca" ao montar porque saiu/entrou do DOM.
- Página mobile que não rola porque o carrossel comeu o gesto vertical.

## Exemplo vivo
Demo interativa no showcase do Atelier: `agents/design/showcase/index.html` (seção Fotos).

## Lição
Carrossel bom não é o que desliza — é o que **discrimina intenção** (arrasto vs clique
vs scroll) e respeita o usuário (pausa, reduced-motion, touch).
