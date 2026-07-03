---
name: expanding-gallery
description: "Accordion expansível com carrossel aninhado, de produção: painéis flex que expandem (rótulo rotacionado nos fechados), setas de foto só no painel ativo com crossfade+scale, outline de acento e scrim de legibilidade. Exploração E narrativa no mesmo componente."
risk: safe
source: "overcore:producao"
date_added: "2026-07-02"
origin: producao
author: "Weriton — GR Group"
contributed_via: https://github.com/Weriton-DataOps/agent-skills-hub/issues/10
---

# Expanding Gallery — accordion com carrossel aninhado

## Quando usar
**N itens, cada um com M fotos** (empreendimentos, imóveis, destinos, produtos com
galeria): o accordion mostra o conjunto; o carrossel aninhado conta a história de UM
item. Padrão extraído de **produção** (seletor de itens com galeria de um portal de reservas real).

## As 5 regras do ofício

1. **Painéis em flex.** O ativo expande (`flex: 7`); os demais encolhem a um mínimo
   legível (`min-width ~46px`); `transition` de `flex-grow` ~0.7s, contida no próprio
   container (reflow *bounded* — A12-safe).
2. **Rótulo rotacionado.** Painel fechado: nome a `rotate(-90deg)` com
   `transform-origin: left bottom`. Painel ativo: horizontal. Resolve "como nomear
   painel estreito" sem truncar nem esconder.
3. **Carrossel só no ativo.** Setas anterior/próxima **existem apenas no painel
   expandido**; a troca de foto é crossfade (`opacity`) + `scale(1.07)` — um mini
   Ken Burns na transição. Painel fechado não tem controle nenhum: menos ruído.
4. **Sinalização do ativo.** Outline de acento (3px, `outline-offset: -3px`)
   transicionando de `transparent` para a cor da marca; scrim de gradiente
   (`black/75 → transparent`) garante o rótulo legível sobre **qualquer** foto.
5. **Interação completa.** `role="button"` + `tabindex` nos painéis (teclado incluso);
   uma âncora visual constante (ex.: pin de localização) segura a identidade do item
   em qualquer largura.

## Cuidado conhecido (reveal-safety — A12)
A versão original monta painéis com `opacity:0 + translateX` inline aguardando o JS de
entrada — se o JS falhar, a seção nasce invisível. Ao reusar: **conteúdo visível por
padrão**; a animação de entrada apenas melhora o default, nunca o condiciona.

## Exemplo vivo
Demo interativa no showcase do Atelier: `agents/design/showcase/index.html` (seção Fotos).

## Lição
Accordion mostra o conjunto; carrossel conta a história de um. **Aninhados, entregam
exploração e narrativa no mesmo componente** — sem duas seções separadas na página.
