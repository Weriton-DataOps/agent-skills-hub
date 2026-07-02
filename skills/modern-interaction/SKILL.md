---
name: modern-interaction
description: "Padrões modernos de interação para UI gerada: Popover API, inert/<dialog>, CSS Anchor Positioning, roving tabindex e a cura do dropdown clipado por overflow. Aplicar ao construir ou revisar qualquer elemento interativo (menus, modais, tooltips, formulários, tabs)."
risk: safe
source: "pbakaus/impeccable (Apache-2.0, modificado)"
date_added: "2026-07-02"
origin: impeccable
upstream: https://github.com/pbakaus/impeccable
attribution: "Derivado de skill/reference/interaction-design.md — traduzido para PT-BR e adaptado ao pipeline do Atelier/OverCore. Arquivo modificado (Apache-2.0 §4b)."
---

# Interações modernas

## Quando usar

Sempre que uma peça tiver comportamento — botão, formulário, modal, dropdown, tooltip, tabs, menu. Consulte antes de escrever a peça (etapa 4 do Atelier) e ao rodar `/varrer`, cuja checklist de estados (hover/focus/empty/loading/error) é exatamente a tabela abaixo. Cobre os bugs recorrentes de UI gerada: dropdown clipado por `overflow`, focus ring removido, modal sem trap de foco, gesto invisível.

## Os oito estados interativos

Todo elemento interativo precisa destes estados desenhados:

| Estado | Quando | Tratamento visual |
|---|---|---|
| **Default** | Em repouso | Estilo base |
| **Hover** | Ponteiro sobre (não touch) | Elevação sutil, mudança de cor |
| **Focus** | Foco por teclado/programático | Anel visível (ver abaixo) |
| **Active** | Sendo pressionado | Afundado, mais escuro |
| **Disabled** | Não interativo | Opacidade reduzida, sem ponteiro |
| **Loading** | Processando | Spinner, skeleton |
| **Error** | Estado inválido | Borda vermelha, ícone, mensagem |
| **Success** | Concluído | Check verde, confirmação |

**O erro mais comum:** desenhar hover sem focus, ou vice-versa. São coisas diferentes — usuário de teclado nunca vê hover. No Atelier, peça devolvida por artesão sem os oito estados não passa da revisão silenciosa.

## Focus ring: do jeito certo

**Nunca `outline: none` sem substituto.** É violação de acessibilidade. Use `:focus-visible` para mostrar foco só a usuários de teclado:

```css
/* Esconde o anel para mouse/touch */
button:focus {
  outline: none;
}

/* Mostra o anel para teclado */
button:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}
```

**Design do anel de foco:**
- Contraste alto (mínimo 3:1 contra as cores adjacentes — medido, não estimado, como a A11 exige)
- 2-3px de espessura
- Com offset do elemento (fora, não dentro)
- Consistente em todos os elementos interativos — a cor vem do token de acento do DESIGN.md, nunca inventada inline

## Formulários: o não-óbvio

**Placeholder não é label.** Ele some ao digitar. Sempre use `<label>` visível. **Valide no blur**, não a cada tecla (exceção: força de senha). Erros ficam **abaixo** do campo, conectados por `aria-describedby`.

## Estados de loading

**Updates otimistas:** mostre sucesso imediatamente, faça rollback em falha. Use para ações de baixo risco (likes, follows) — nunca para pagamentos ou ações destrutivas. **Skeleton > spinner:** o skeleton antecipa a forma do conteúdo e parece mais rápido que um spinner genérico.

## Modais: a abordagem `inert`

Prender o foco em modais exigia JavaScript complexo. Hoje, use o atributo `inert`:

```html
<!-- Com o modal aberto -->
<main inert>
  <!-- O conteúdo atrás do modal não recebe foco nem clique -->
</main>
<dialog open>
  <h2>Título do modal</h2>
  <!-- O foco fica dentro do modal -->
</dialog>
```

Ou use o `<dialog>` nativo:

```javascript
const dialog = document.querySelector('dialog');
dialog.showModal();  // Abre com trap de foco, fecha no Escape
```

## A Popover API

Para tooltips, dropdowns e overlays não-modais, use popovers nativos:

```html
<button popovertarget="menu">Abrir menu</button>
<div id="menu" popover>
  <button>Opção 1</button>
  <button>Opção 2</button>
</div>
```

**Ganhos:** light-dismiss (clique fora fecha), empilhamento correto, fim das guerras de z-index, acessível por padrão — sem uma linha de JavaScript.

## Posicionamento de dropdown e overlay

Dropdown renderizado com `position: absolute` dentro de um container com `overflow: hidden` ou `overflow: auto` é clipado. **É o bug de dropdown mais comum em código gerado** — e é defeito renderizado, reprovação direta no `/varrer`.

### CSS Anchor Positioning

A solução moderna usa a API de CSS Anchor Positioning para amarrar o overlay ao gatilho sem JavaScript:

```css
.trigger {
  anchor-name: --menu-trigger;
}

.dropdown {
  position: fixed;
  position-anchor: --menu-trigger;
  position-area: block-end span-inline-end;
  margin-top: 4px;
}

/* Vira para cima se não houver espaço abaixo */
@position-try --flip-above {
  position-area: block-start span-inline-end;
  margin-bottom: 4px;
}
```

Como o dropdown usa `position: fixed`, ele escapa de qualquer clipping de `overflow` nos ancestrais. O bloco `@position-try` trata as bordas do viewport automaticamente. **Suporte:** Chrome 125+, Edge 125+. Ainda fora do Firefox e do Safari — forneça fallback para eles.

### Combo Popover + Anchor

Combinar a Popover API com anchor positioning entrega empilhamento, light-dismiss, acessibilidade e posicionamento correto num padrão só:

```html
<button popovertarget="menu" class="trigger">Abrir</button>
<div id="menu" popover class="dropdown">
  <button>Opção 1</button>
  <button>Opção 2</button>
</div>
```

O atributo `popover` coloca o elemento na **top layer**, acima de todo o resto independente de z-index ou overflow. Portal desnecessário.

### Padrão Portal / Teleport

Em frameworks de componentes, renderize o dropdown na raiz do documento e posicione via JavaScript:

- **React**: `createPortal(dropdown, document.body)`
- **Vue**: `<Teleport to="body">`
- **Svelte**: biblioteca de portal ou montagem em `document.body`

Calcule a posição a partir do `getBoundingClientRect()` do gatilho e aplique `position: fixed` com `top` e `left`. Recalcule em scroll e resize.

### Fallback com position: fixed

Para navegadores sem anchor positioning, `position: fixed` com coordenadas manuais evita o clipping de overflow:

```css
.dropdown {
  position: fixed;
  /* top/left definidos via JS a partir do getBoundingClientRect() do gatilho */
}
```

Cheque os limites do viewport antes de renderizar. Se o dropdown estourar a borda inferior, vire-o para cima do gatilho; se estourar a direita, alinhe-o à direita do gatilho.

## Ações destrutivas: undo > confirmação

**Undo é melhor que diálogo de confirmação.** Usuários clicam em confirmações no automático. Remova da UI imediatamente, mostre toast com "desfazer", delete de verdade quando o toast expirar. Reserve confirmação para o genuinamente irreversível (exclusão de conta), ações de alto custo ou operações em lote.

## Navegação por teclado

### Roving tabindex

Em grupos de componentes (tabs, itens de menu, radio groups), só um item é tabulável; as setas movem dentro do grupo:

```html
<div role="tablist">
  <button role="tab" tabindex="0">Tab 1</button>
  <button role="tab" tabindex="-1">Tab 2</button>
  <button role="tab" tabindex="-1">Tab 3</button>
</div>
```

As setas movem o `tabindex="0"` entre os itens. Tab pula para o próximo componente inteiro — nunca item a item.

### Skip links

Ofereça skip links (`<a href="#main-content">Pular para o conteúdo</a>`) para o teclado saltar a navegação. Escondido fora da tela, visível no foco. Vale em qualquer registro, mas é obrigatório em DOCS, onde leitura é o trabalho.

## Descobribilidade de gestos

Swipe-to-delete e afins são invisíveis. Sinalize que existem:

- **Revelação parcial**: botão de deletar espiando pela borda
- **Onboarding**: coach marks no primeiro uso
- **Alternativa**: sempre um caminho visível (menu com "Excluir")

Nunca faça do gesto o único caminho para uma ação.

## Não faça

- Remover indicador de foco sem alternativa.
- Placeholder como label.
- Alvo de toque menor que **44×44px** (a área de clique pode crescer via pseudo-elemento sem inflar o visual).
- Mensagem de erro genérica.
- Controle customizado sem ARIA e sem suporte a teclado.
- Dropdown `position: absolute` dentro de container com overflow — use popover, anchor positioning, portal ou `fixed`.
- Animar a abertura de menus/modais fora dos tokens de motion do DESIGN.md (e em registro APP, animação decorativa nem entra — A12).
