---
name: responsive-adaptation
description: "Adapta uma interface existente a outro contexto (mobile, tablet, desktop, print, email) repensando a experiência em vez de escalar pixels: navegação em 3 estágios, tabela→cards, media queries de pointer/hover e layout de email HTML."
risk: safe
source: "pbakaus/impeccable (Apache-2.0, modificado)"
date_added: "2026-07-02"
origin: impeccable
upstream: https://github.com/pbakaus/impeccable
attribution: "Derivado de skill/reference/adapt.md — traduzido para PT-BR e adaptado ao pipeline do Atelier/OverCore. Arquivo modificado (Apache-2.0 §4b)."
---

# Adaptação responsiva

> **Contexto adicional necessário**: plataformas/dispositivos-alvo e contextos de uso. Se o projeto tem `DESIGN.md`, os breakpoints e tokens de lá são herança — nunca invente novos inline (A18).

Adaptar um design existente a um contexto diferente: outro tamanho de tela, dispositivo, plataforma ou caso de uso. A armadilha é tratar adaptação como escala. O trabalho é **repensar a experiência para o novo contexto** — não encolher pixels.

## Quando usar

- Uma tela aprovada no `/croqui` ou `/refinar` precisa funcionar em outro dispositivo (desktop→mobile, mobile→desktop, tablet, print).
- O `/varrer` acusou navegação quebrada em viewport estreito, tabela transbordando no mobile, ou hover carregando funcionalidade em dispositivo touch.
- A peça é um **email HTML** — registro próprio, com regras que invertem tudo o que vale na web (ver seção Email).
- O registro da tela (LANDING/APP/DOCS) permanece o mesmo entre contextos; o que muda é layout, input e densidade — **nunca a arquitetura de informação**.

---

## 1. Avaliar o desafio de adaptação

Entenda o que precisa ser adaptado e por quê:

1. **Identifique o contexto de origem**:
   - Para que foi desenhado originalmente? (Web desktop? App mobile?)
   - Que premissas foram assumidas? (Tela grande? Mouse? Conexão rápida?)
   - O que funciona bem no contexto atual?

2. **Entenda o contexto de destino**:
   - **Dispositivo**: mobile, tablet, desktop, TV, relógio, impresso?
   - **Método de input**: touch, mouse, teclado, voz, gamepad?
   - **Restrições de tela**: tamanho, resolução, orientação?
   - **Conexão**: wifi rápido, 3G lento, offline?
   - **Contexto de uso**: em movimento vs na mesa, olhada rápida vs leitura focada?
   - **Expectativas do usuário**: o que se espera nessa plataforma?

3. **Identifique os desafios**:
   - O que não vai caber? (Conteúdo, navegação, funcionalidades)
   - O que não vai funcionar? (Hover em touch, alvos de toque minúsculos)
   - O que é inadequado? (Padrões desktop no mobile, padrões mobile no desktop)

**CRÍTICO**: adaptação é repensar a experiência para o novo contexto, não escalar pixels.

## 2. Planejar a estratégia por contexto

### Mobile (desktop → mobile)

**Layout**:
- Coluna única em vez de multi-coluna
- Empilhamento vertical em vez de lado a lado
- Componentes full-width em vez de larguras fixas
- Navegação inferior em vez de topo/lateral

**Interação**:
- Alvos de toque mínimos de **44x44px** (nunca dependentes de hover)
- Gestos de swipe onde couber (listas, carrosséis)
- Bottom sheets em vez de dropdowns
- Design thumbs-first (controles ao alcance do polegar)
- Áreas de toque maiores e com mais espaçamento

**Conteúdo**:
- Revelação progressiva (não mostre tudo de uma vez)
- Priorize o conteúdo primário (secundário vai para abas/acordeões)
- Texto mais curto (mais conciso)
- Texto maior (**mínimo 16px**)

**Navegação**:
- Menu hambúrguer ou navegação inferior
- Reduza a complexidade da navegação
- Headers fixos (sticky) para contexto
- Botão de voltar no fluxo de navegação

### Tablet (abordagem híbrida)

**Layout**:
- Duas colunas (nem uma, nem três)
- Painéis laterais para conteúdo secundário
- Visões master-detail (lista + detalhe)
- Adaptativo por orientação (retrato vs paisagem)

**Interação**:
- Suporte a touch E pointer simultaneamente
- Alvos de 44x44px, mas layouts mais densos que no telefone são aceitáveis
- Gavetas de navegação lateral
- Formulários multi-coluna onde fizer sentido

### Desktop (mobile → desktop)

**Layout**:
- Multi-coluna (use o espaço horizontal)
- Navegação lateral sempre visível
- Múltiplos painéis de informação simultâneos
- Larguras fixas com max-width (não estique até 4K)

**Interação**:
- Estados de hover para informação adicional
- Atalhos de teclado
- Menus de contexto (clique direito)
- Drag and drop onde ajudar
- Multi-seleção com Shift/Cmd

**Conteúdo**:
- Mais informação de cara (menos revelação progressiva)
- Tabelas de dados com muitas colunas
- Visualizações mais ricas
- Descrições mais detalhadas

### Print (tela → impresso)

**Layout**:
- Quebras de página em pontos lógicos
- Remova navegação, footer e elementos interativos
- Preto e branco (ou cor limitada)
- Margens adequadas para encadernação

**Conteúdo**:
- Expanda conteúdo encurtado (URLs completas, seções ocultas)
- Adicione números de página, cabeçalhos e rodapés
- Inclua metadados (data de impressão, título da página)
- Converta gráficos para versões print-friendly

### Email (web → email HTML) — embrião do artesão de email

Email é um registro à parte: os clientes (Outlook, Gmail, Apple Mail) renderizam com motores arcaicos, e quase tudo que é boa prática na web vira erro aqui.

**Layout**:
- Largura estreita (**máximo 600px**)
- **Coluna única, sempre**
- **CSS inline** (nada de stylesheet externa)
- **Layout baseado em tabelas** (compatibilidade entre clientes)

**Interação**:
- CTAs grandes e óbvios (**botões, não links de texto**)
- **Zero hover** (não é confiável em cliente de email)
- Deep links para o app web em qualquer interação complexa

O DESIGN.md continua mandando na paleta e tipografia do email, mas os mecanismos de entrega (tabela, inline, coluna única) sobrepõem qualquer convenção de layout da web.

## 3. Implementar as adaptações

### Breakpoints

Faixas de referência:
- Mobile: **320px–767px**
- Tablet: **768px–1023px**
- Desktop: **1024px+**
- Ou breakpoints guiados pelo conteúdo (onde o design quebra)

**Mobile-first, escrito do jeito certo**: estilos base para mobile, `min-width` para camadas de complexidade. Desktop-first (`max-width`) faz o mobile carregar estilos desnecessários primeiro.

**Breakpoints guiados pelo conteúdo**: não persiga tamanhos de dispositivo; deixe o conteúdo dizer onde quebrar. Comece estreito, estique até o design quebrar, coloque o breakpoint ali. **Três breakpoints costumam bastar (640, 768, 1024px).** Use `clamp()` para valores fluidos sem breakpoint.

### Técnicas de layout

- **CSS Grid/Flexbox**: refluxo automático de layouts
- **Container queries**: adapte pelo contêiner, não pelo viewport
- **`clamp()`**: dimensionamento fluido entre mínimo e máximo
- **Media queries**: estilos distintos por contexto
- **Display**: mostrar/ocultar elementos por contexto (com parcimônia — ver Conteúdo)

### Detecte o input, não só o tamanho de tela

**Tamanho de tela não diz nada sobre o método de input.** Um laptop com touchscreen, um tablet com teclado. Use as queries de pointer e hover:

```css
/* Pointer fino (mouse, trackpad) */
@media (pointer: fine) {
  .button { padding: 8px 16px; }
}

/* Pointer grosso (touch, stylus) */
@media (pointer: coarse) {
  .button { padding: 12px 20px; }  /* Alvo de toque maior */
}

/* Dispositivo suporta hover */
@media (hover: hover) {
  .card:hover { transform: translateY(-2px); }
}

/* Dispositivo sem hover (touch) */
@media (hover: none) {
  .card { /* Sem estado hover — use active */ }
}
```

**Crítico**: nunca dependa de hover para funcionalidade. Usuário de touch não consegue pausar o cursor sobre nada.

### Adaptação de touch

- Aumente alvos de toque (**mínimo 44x44px**)
- Mais espaçamento entre elementos interativos
- Remova interações dependentes de hover
- Adicione feedback de toque (ripples, highlights)
- Considere as zonas do polegar (a base da tela é mais alcançável que o topo)

### Safe areas: trate o notch

Telefones modernos têm notch, cantos arredondados e indicador de home. Use `env()`:

```css
body {
  padding-top: env(safe-area-inset-top);
  padding-bottom: env(safe-area-inset-bottom);
  padding-left: env(safe-area-inset-left);
  padding-right: env(safe-area-inset-right);
}

/* Com fallback */
.footer {
  padding-bottom: max(1rem, env(safe-area-inset-bottom));
}
```

**Habilite viewport-fit** na meta tag:
```html
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
```

### Adaptação de conteúdo

- Use `display: none` com parcimônia (o conteúdo ainda é baixado)
- Progressive enhancement (conteúdo essencial primeiro, enriquecimento em telas maiores)
- Lazy loading para conteúdo fora da tela
- Imagens responsivas (`srcset`, elemento `picture`)

### Imagens responsivas

**`srcset` com descritores de largura**:

```html
<img
  src="hero-800.jpg"
  srcset="
    hero-400.jpg 400w,
    hero-800.jpg 800w,
    hero-1200.jpg 1200w
  "
  sizes="(max-width: 768px) 100vw, 50vw"
  alt="Imagem hero"
>
```

Como funciona: `srcset` lista as imagens disponíveis com suas larguras reais (descritores `w`); `sizes` diz ao navegador a largura de exibição; o navegador escolhe o melhor arquivo pela largura do viewport E pelo device pixel ratio.

**`picture` para direção de arte** — quando você precisa de enquadramentos diferentes (não só resoluções):

```html
<picture>
  <source media="(min-width: 768px)" srcset="wide.jpg">
  <source media="(max-width: 767px)" srcset="tall.jpg">
  <img src="fallback.jpg" alt="...">
</picture>
```

### Padrões de adaptação de layout

- **Navegação em 3 estágios**: hambúrguer + drawer no mobile, horizontal compacta no tablet, completa com rótulos no desktop.
- **Tabela → cards**: no mobile, transforme a tabela em cards com `display: block` e atributos `data-label` (o rótulo da coluna vira legenda de cada valor no card).
- **Revelação progressiva**: `<details>/<summary>` para conteúdo que pode colapsar no mobile.
- **Navegação por registro**: em registro APP, a navegação inferior/master-detail preserva densidade; em LANDING, o hambúrguer não pode esconder o CTA dominante da dobra (A16 continua valendo por viewport, em qualquer largura).

**IMPORTANTE**: teste em dispositivos reais. A emulação do DevTools ajuda, mas não é perfeita.

## NUNCA

- Esconder funcionalidade essencial no mobile (se importa, faça funcionar)
- Assumir que desktop = máquina potente (considere acessibilidade e hardware antigo)
- Usar arquitetura de informação diferente entre contextos (confunde)
- Quebrar as expectativas da plataforma (usuário mobile espera padrões mobile)
- Esquecer a orientação paisagem em mobile/tablet
- Usar breakpoints genéricos às cegas (prefira breakpoints guiados pelo conteúdo)
- Ignorar touch no desktop (muitos desktops têm touchscreen)

## Verificar as adaptações

Checklist de teste entre contextos — alimenta o gate do `/varrer`:

- **Dispositivos reais**: teste em telefones, tablets e desktops de verdade
- **Orientações**: retrato e paisagem
- **Navegadores**: Safari, Chrome, Firefox, Edge
- **Sistemas**: iOS, Android, Windows, macOS
- **Métodos de input**: touch, mouse, teclado
- **Casos extremos**: telas muito pequenas (**320px**) e muito grandes (**4K**)
- **Conexões lentas**: teste com rede limitada (throttling)

### DevTools não basta

A emulação de dispositivo do DevTools serve para layout, mas não captura:

- Interações de toque reais
- Restrições reais de CPU/memória
- Padrões de latência de rede
- Diferenças de renderização de fonte
- Chrome do navegador e aparição de teclado virtual

**Teste no mínimo em**: um iPhone real, um Android real, e um tablet se for relevante. Androids baratos revelam problemas de performance que nenhum simulador mostra.

Quando a adaptação parecer nativa em cada contexto, siga para o `/polir` — o passe final de alinhamento, espaçamento e estados.

---

**Evite**: design desktop-first. Detecção de dispositivo em vez de detecção de recurso (feature detection). Codebases separadas para mobile/desktop. Ignorar tablet e orientação paisagem. Assumir que todo dispositivo mobile é potente.
