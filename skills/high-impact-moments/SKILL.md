---
name: high-impact-moments
description: "Cria momentos de alto impacto na interface (hero, data-viz, tabelas densas, transições cinematográficas) usando APIs modernas do browser com disciplina de fallback. Exige gate de 2-3 direções aprovadas antes de escrever qualquer código."
risk: safe
source: "pbakaus/impeccable (Apache-2.0, modificado)"
date_added: "2026-07-02"
origin: impeccable
upstream: https://github.com/pbakaus/impeccable
attribution: "Derivado de skill/reference/overdrive.md — traduzido para PT-BR e adaptado ao pipeline do Atelier/OverCore. Arquivo modificado (Apache-2.0 §4b)."
---

# Momentos de alto impacto

Levar uma parte da interface além do limite convencional. Não é só efeito visual: é usar o poder completo do browser para tornar uma peça extraordinária — uma tabela que aguenta um milhão de linhas, um dialog que morfa a partir do botão que o abriu, um formulário que valida em tempo real com feedback contínuo, uma transição de página que parece cinematográfica.

## Quando usar

- Ao refinar a peça de maior peso de uma tela: hero de landing, data-viz de dashboard, tabela densa de operação.
- Quando o usuário pede explicitamente algo "impressionante", "premium" ou "além do comum" numa peça específica.
- No fluxo do Atelier: dentro da etapa peça-a-peça, como artesão da peça de destaque — nunca como passe geral sobre a tela inteira.
- **Não usar** para mascarar fundamentos fracos de design (hierarquia, espaçamento, contraste). Corrija isso primeiro com `/polir`, `/tipografar`, `/cor` — ambição técnica sobre base ruim só amplifica o problema.

**REGRA CENTRAL DE CONTEXTO**: o contexto determina o que "extraordinário" significa. Um sistema de partículas num portfólio criativo impressiona. O mesmo sistema numa página de configurações constrange. Mas uma página de configurações com salvamento otimista instantâneo e transições de estado animadas? Isso também é extraordinário. Entenda a personalidade e o objetivo do projeto (PRODUCT.md + registro da tela) antes de decidir o que cabe.

## Gate de direções — proposta antes de código (inegociável)

Esta é a peça com maior potencial de tiro no pé. NUNCA pule direto para implementação:

1. **Pense 2-3 direções diferentes**: técnicas distintas, níveis de ambição distintos, abordagens estéticas distintas. Para cada direção, descreva brevemente como o resultado vai parecer e *sentir*.
2. **Apresente as direções ao usuário** com trade-offs explícitos: suporte de browser, custo de performance, complexidade. Este é um gate humano do wizard — mesma mecânica de `croqui_aprovado`.
3. **Só prossiga com a direção confirmada.**

Pular esse gate arrisca construir algo constrangedor que vai para o lixo.

## Iterar com verificação visual

Efeitos tecnicamente ambiciosos quase nunca funcionam de primeira. Use automação de browser para renderizar, verificar visualmente e iterar — nunca assuma que o efeito ficou bom, confira. Espere múltiplas rodadas de refinamento. A distância entre "funciona tecnicamente" e "parece extraordinário" se fecha com iteração visual, não com código. Screenshot não olhado não conta.

## O que "extraordinário" significa por tipo de superfície

Antes de escolher técnica, pergunte: **o que faria um usuário DESTA interface dizer "uau, que bom"?** Cruze com o registro declarado da tela:

| Superfície (registro) | Onde mora o "uau" | Exemplos |
|---|---|---|
| Visual/marketing (LANDING) | Sensorial | Reveal dirigido por scroll, fundo com shader, transição cinematográfica de página, arte generativa que reage ao cursor |
| UI funcional (APP) | Em como *sente* | Dialog que morfa do botão via View Transitions, tabela renderizando 100k linhas a 60fps via virtual scrolling, formulário com validação contínua que parece instantânea, drag-and-drop com física de mola |
| Performance crítica (APP) | Invisível mas percebido | Busca que filtra 50k itens sem piscar, formulário complexo que nunca trava a main thread, editor de imagem quase em tempo real — a interface simplesmente nunca hesita |
| Dados densos (APP/dashboard) | Fluidez | Render acelerado por GPU (Canvas/WebGL) para datasets massivos, transições animadas entre estados de dados, grafos force-directed que assentam naturalmente |

**O fio comum**: algo na implementação vai além do que usuários esperam de uma interface web. A técnica serve à experiência, nunca o contrário. Em registro APP, o extraordinário é funcional — decoração continua proibida (regra A12 do `/varrer` segue valendo; motion usa tokens do DESIGN.md).

## Caixa de ferramentas — organizada por objetivo, não por tecnologia

### Transições cinematográficas
- **View Transitions API** (mesmo documento: todos os browsers; entre documentos: sem Firefox): morphing de elemento compartilhado entre estados. Item de lista expandindo em página de detalhe; botão morfando em dialog. O mais próximo de animação FLIP nativa.
- **`@starting-style`** (todos os browsers): animar de `display: none` para visível só com CSS, incluindo keyframes de entrada.
- **Física de mola**: movimento natural com massa, tensão e amortecimento em vez de cubic-bezier. Bibliotecas: motion (ex-Framer Motion), GSAP, ou solver próprio.

### Animação amarrada ao scroll
- **Scroll-driven animations** (`animation-timeline: scroll()`): só CSS, zero JS. Parallax, barras de progresso, sequências de reveal dirigidas pela posição do scroll. (Chrome/Edge/Safari; Firefox só atrás de flag; **sempre** forneça fallback estático.)

### Renderizar além do CSS
- **WebGL** (todos os browsers): shaders, pós-processamento, partículas. Bibliotecas: Three.js, OGL (leve), regl. Use para efeitos que CSS não expressa.
- **WebGPU** (Chrome/Edge; Safari parcial; Firefox só flag): GPU compute de próxima geração. Mais potente que WebGL, suporte limitado. **Sempre** caia para WebGL2.
- **Canvas 2D / OffscreenCanvas**: render custom, manipulação de pixel, ou tirar render pesado da main thread via Web Workers + OffscreenCanvas.
- **Cadeias de filtro SVG**: displacement maps, turbulence, morphology para distorção orgânica. Animáveis por CSS.

### Dados vivos
- **Virtual scrolling**: renderizar só as linhas visíveis em tabelas/listas com dezenas de milhares de itens. Casos simples dispensam biblioteca; TanStack Virtual para os complexos.
- **Gráficos acelerados por GPU**: data-viz em Canvas ou WebGL para datasets grandes demais para SVG/DOM. Bibliotecas: deck.gl, renderers custom sobre regl.
- **Transições animadas de dados**: morfar entre estados do gráfico em vez de substituir. `transition()` do D3, ou View Transitions para gráficos baseados em DOM.

### Animar propriedades complexas
- **`@property`** (todos os browsers): registrar custom properties CSS com tipo, habilitando animação de gradientes, cores e valores que o CSS normalmente não interpola.
- **Web Animations API** (todos os browsers): animação dirigida por JavaScript com performance de CSS. Componível, cancelável, reversível — a fundação de coreografia complexa.

### Empurrar o limite de performance
- **Web Workers**: computação fora da main thread — processamento pesado de dados, manipulação de imagem, indexação de busca; tudo que causaria jank.
- **OffscreenCanvas**: render numa thread de Worker; a main thread fica livre enquanto o visual pesado renderiza ao fundo.
- **WASM**: performance quase nativa para features de computação pesada — processamento de imagem, simulação física, codecs.

### Interagir com o dispositivo
- **Web Audio API**: áudio espacial, visualização audio-reativa, feedback sonoro. Exige gesto do usuário para iniciar.
- **APIs de dispositivo**: orientação, luz ambiente, geolocalização. Com parcimônia e sempre com permissão do usuário.

**NOTA**: esta skill melhora como a interface *sente*, não o que o produto *faz*. Colaboração em tempo real, suporte offline ou capacidades novas de backend são decisões de produto, não de UI. O foco é fazer features existentes parecerem extraordinárias.

## Disciplina de implementação

### Progressive enhancement é inegociável

Toda técnica precisa degradar com graça. A experiência SEM o aprimoramento ainda tem de ser boa.

```css
@supports (animation-timeline: scroll()) {
  .hero { animation-timeline: scroll(); }
}
```

```javascript
if ('gpu' in navigator) { /* WebGPU */ }
else if (canvas.getContext('webgl2')) { /* fallback WebGL2 */ }
/* o fallback só-CSS ainda precisa ficar bonito */
```

### Regras de performance

- Alvo: **60fps**. Se cair abaixo de **50**, simplifique.
- Respeite `prefers-reduced-motion`, **sempre**. Forneça alternativa estática bonita.
- Inicialize recursos pesados (contextos WebGL, módulos WASM) de forma lazy, só quando perto do viewport.
- Pause render fora de tela. Mate o que não está visível.
- Teste em dispositivos intermediários reais, não só na sua máquina de desenvolvimento.

### O polimento é a diferença

A distância entre "legal" e "extraordinário" está nos últimos 20% de refino: a curva de easing de uma animação de mola, o offset de timing num reveal escalonado, o movimento secundário sutil que faz uma transição parecer física. Não entregue a primeira versão que funciona; entregue a versão que parece inevitável.

**NUNCA**:
- Ignorar `prefers-reduced-motion` — requisito de acessibilidade, não sugestão.
- Entregar efeito que causa jank em dispositivo intermediário.
- Usar API de ponta sem fallback funcional.
- Adicionar som sem opt-in explícito do usuário.
- Usar ambição técnica para mascarar fundamentos fracos de design; conserte-os primeiro com os outros comandos do Atelier.
- Empilhar múltiplos momentos extraordinários concorrentes. Foco cria impacto; excesso cria ruído — um momento de alto impacto por tela.

## Verificação do resultado

Checklist antes de considerar a peça pronta (encaixa no `/varrer` como verificação adicional da peça):

- **Teste do uau**: mostre a alguém que não viu antes. A pessoa reage?
- **Teste da remoção**: tire o efeito. A experiência empobrece, ou ninguém nota?
- **Teste de dispositivo**: rode num celular, num tablet, num Chromebook. Continua fluido?
- **Teste de acessibilidade**: ative reduced motion. Continua bonito?
- **Teste de contexto**: isso faz sentido para ESTA marca e ESTE público (PRODUCT.md + registro)?

"Tecnicamente extraordinário" não é usar a API mais nova. É fazer a interface realizar algo que o usuário não achava que um site pudesse fazer.
