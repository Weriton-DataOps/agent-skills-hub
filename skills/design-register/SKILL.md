---
name: design-register
description: "Declara o registro da tela (LANDING/brand vs APP/product) e recalibra o peso de cada regra de design por registro: ban list nominal de fontes-reflexo (com isenções em product), permissões de densidade e o limite entre decoração intencional e sabotagem."
risk: safe
source: "pbakaus/impeccable (Apache-2.0, modificado)"
date_added: "2026-07-02"
origin: impeccable
upstream: https://github.com/pbakaus/impeccable
attribution: "Derivado de skill/reference/brand.md + skill/reference/product.md — traduzido para PT-BR e adaptado ao pipeline do Atelier/OverCore. Arquivo modificado (Apache-2.0 §4b)."
---

# Registro de design — brand vs product

## Quando usar

Antes de qualquer `/croqui`, ao declarar o registro da tela (`/registro landing|app|docs`), e durante o `/varrer`, para pesar cada regra pelo registro certo. A tese: **a mesma regra muda de peso conforme o tipo de interface**. Aplicar regra de brand num dashboard (ou vice-versa) produz slop invertido — a decoração que é voz numa landing é sabotagem num app, e a familiaridade que é virtude num app é invisibilidade numa landing.

Mapeamento para o registro do Atelier:

- **LANDING** ≈ registro *brand*: o design É o produto. Sites de marca, landing pages, superfícies de marketing, páginas de campanha, portfólios, conteúdo longo, páginas "sobre". A impressão do visitante é a coisa sendo feita.
- **APP/DASHBOARD** ≈ registro *product*: o design SERVE o produto. UIs de app, dashboards administrativos, painéis de configuração, tabelas de dados, ferramentas, superfícies autenticadas — o usuário está no meio de uma tarefa.
- **DOCS/FORM** herda majoritariamente o lado *product* (contenção, consistência), com a régua de leitura acima de tudo: largura de linha 60–75ch e hierarquia tipográfica primeiro.

O registro brand atravessa todos os gêneros — tech (Stripe, Linear, Vercel), luxo (hotel, casa de moda), consumo (restaurante, viagem, embalagem), estúdio criativo, página de álbum de banda. Todos compartilham a postura (*comunicar, não transacionar*) e divergem violentamente em estética. Não colapse tudo num visual só.

## Os dois testes de slop

**Teste brand (LANDING).** Se alguém consegue olhar e dizer "IA fez isso" sem hesitar, reprovou. A barra é distintividade: o visitante deve perguntar "como isso foi feito?", não "qual IA fez isso?". Brand não é registro neutro — landing pages geradas por IA inundaram a internet e o "mediano" deixou de ser encontrável. **Contenção sem intenção agora lê como medíocre, não como refinado.** Superfície de marca precisa de ponto de vista, público específico e disposição a arriscar estranheza.

- **Segundo teste (lane estética):** antes de cometer os movimentos, nomeie a referência. Uma página estilo espécime da Klim é uma lane; Stripe-minimal é outra; maximalismo-ácido Liquid Death é outra. Não derive para estética de revista editorial num brief que não é editorial — marca de trilha com drop caps em Cormorant itálico é o registro errado *dentro* do registro.
- **Teste inverso:** descreva em uma frase o que vai construir, do jeito que um concorrente descreveria o dele. Se a frase serve para a landing page modal da categoria, recomece.

**Teste product (APP).** Não é "alguém diria que IA fez isso" — familiaridade aqui costuma ser feature. O teste é: um usuário fluente nas melhores ferramentas da categoria (Linear, Figma, Notion, Raycast, Stripe) sentaria e **confiaria** nesta interface, ou pausaria a cada componente sutilmente errado? O modo de falha do product não é a chatice, é a **estranheza sem propósito**: botões superdecorados, controles de formulário desencontrados, motion gratuito, fonte display onde deveria haver label, affordances inventadas para tarefas padrão. A barra é a familiaridade conquistada — a ferramenta deve desaparecer dentro da tarefa.

## Tabela mestre — a mesma dimensão, peso por registro

| Dimensão | LANDING (brand) | APP/DASHBOARD (product) |
|---|---|---|
| Barra de qualidade | Distintividade ("como fizeram isso?") | Familiaridade conquistada (confiança à primeira vista) |
| Famílias tipográficas | 2 famílias só se a voz pedir; 1 família com contraste comprometido é mais forte que um par tímido | 1 família quase sempre basta; uma sans bem ajustada carrega heading, botão, label, corpo e dado |
| Escala tipográfica | Modular, fluida com `clamp()` em headings, razão ≥1.25 entre degraus (1.1× lê como não-comprometido) | rem fixo, nunca fluido; razão 1.125–1.2 — há mais elementos de tipo, contraste exagerado vira ruído |
| Largura de linha | Prosa 65–75ch | Prosa 65–75ch; dados e UI compacta podem ser mais densos — tabela a 120ch+ é ok |
| Estratégia de cor | Committed, Full palette e Drenched liberadas — cor espalhada num hero é voz, não excesso | Restrained é o piso; uma superfície pode merecer Committed (relatório carregado por 1 cor de categoria, welcome de onboarding drenched) |
| Fontes-reflexo | Ban list nominal vale integralmente | Inter, SF Pro e stacks `system-ui` são **permissão**, não violação |
| Responsividade | Espaçamento fluido com `clamp()` que respira em viewports maiores; assimetria intencional | Estrutural: colapsar sidebar, tabela responsiva, colunas por breakpoint — nunca tipografia fluida |
| Motion | 1 page-load bem orquestrado pode ser a voz (e pular motion de entrada também pode ser) | 150–250 ms na maioria das transições; motion comunica estado, nada mais; zero sequência de load |
| Densidade | Dobras de propósito único: 1 ideia dominante por viewport, scroll longo, ritmo deliberado | Densidade é permissão: tabelas com muitas linhas, painéis com muitos labels, informação densa quando o usuário precisa |
| Decoração | Gosto — se intencional, nomeada e registrada no DESIGN.md | Sabotagem — acento só em ação primária, seleção atual e indicadores de estado |
| Imagem | Obrigatória quando o brief implica (restaurante, hotel, viagem, moda, fotografia): zero imagem é bug, não escolha | Screenshot de produto, data-viz e conteúdo real; sem exigência de hero fotográfico |
| Consistência | Direção de arte por seção é permitida se a narrativa exigir; consistência de **voz** vence consistência de tratamento | Mesma vocabulário visual tela a tela é virtude; delícia é para momentos, não para páginas |

## Tipografia

### Procedimento de seleção de fonte (LANDING — todo projeto, nunca pule)

1. Leia o brief. Escreva **três palavras concretas de voz de marca**. Não "moderno" ou "elegante": "quente, mecânico e opinativo", "calmo, clínico e cuidadoso". Palavras de objeto físico.
2. Liste as três fontes que você pegaria por reflexo. Se qualquer uma está na ban list abaixo, rejeite — são defaults de training data e criam monocultura.
3. Navegue um catálogo real (Google Fonts, Pangram Pangram, Future Fonts, Adobe Fonts, ABC Dinamo, Klim, Velvetyne) com as três palavras em mente. Procure a fonte da marca como **objeto físico**: legenda de museu, manual de terminal dos anos 70, etiqueta de tecido, livro infantil de jornal barato, pôster de show, recibo de lanchonete mid-century. Rejeite a primeira coisa que "parece designzuda".
4. Cross-check: "elegante" não é necessariamente serifada; "técnico" não é necessariamente sans; "quente" não é Fraunces. Se a escolha final coincide com o reflexo original, recomece.

### Ban list nominal — fontes-reflexo

Defaults de training data. Em registro **LANDING**, reprovação direta no `/varrer`; procure adiante:

> Fraunces · Newsreader · Lora · Crimson · Crimson Pro · Crimson Text · Playfair Display · Cormorant · Cormorant Garamond · Syne · IBM Plex Mono · IBM Plex Sans · IBM Plex Serif · Space Mono · Space Grotesk · Inter · DM Sans · DM Serif Display · DM Serif Text · Outfit · Plus Jakarta Sans · Instrument Sans · Instrument Serif

**Isenções:**

- **Registro APP/DASHBOARD:** fontes de sistema e sans familiares (Inter, SF Pro, stacks `system-ui`) são permissão explícita do registro product — a familiaridade é o ponto. A ban list não se aplica.
- **Herança:** a ban list vale para **decisão greenfield**. Se a marca já se comprometeu com uma fonte ou lane como identidade, preservação de identidade vence — variante de superfície existente não questiona o que já está no ar. No Atelier, isso é a regra de herança: token herdado no DESIGN.md nunca é sobrescrito por esta lista.

### Lanes estéticas-reflexo (o reflexo de segunda ordem)

Paralelo à lista de fontes: famílias estéticas saturadas que inundaram superfícies de marca. Se o brief cai numa dessas lanes **sem uma razão de registro que a exija** (uma revista literal, um terminal literal, sinalização industrial literal), é o reflexo um nível mais fundo que escolher Fraunces:

- **Editorial-tipográfica.** Serifada display (geralmente itálica) + pequenos labels mono + separadores em régua + contenção monocromática. Afetação de capa de revista, influência Klim. A impressão digital: três colunas separadas por réguas, headline itálica em Fraunces/Recoleta/Newsreader, metadata minúscula com tracking, zero imagem. Em 2026, toda marca Stripe-adjacente e Notion-adjacente já pousou aqui.

A lista de lanes atualiza na mesma cadência da lista de fontes (brutalist-utility e acid-maximalism entram quando saturarem; entradas saem quando caírem abaixo da saturação).

### Pareamento, escala e ritmo

- **Distintivo + refinado** é a meta em LANDING. A forma específica depende da marca, não da categoria da marca — "restaurante", "dev tool", "fintech" **não é receita**; tratar como receita é o reflexo de primeira ordem.
- Duas famílias no mínimo só quando a voz precisa. Uma família única bem escolhida com contraste comprometido de peso/tamanho é mais forte que um par display+body tímido.
- **LANDING:** escala modular, `clamp()` fluido nos headings, razão ≥1.25 entre degraus. Escala achatada (degraus a 1.1×) lê como não-comprometida.
- **APP:** escala rem **fixa** — o usuário vê em DPI consistente, e um h1 fluido que encolhe numa sidebar fica pior, não melhor. Razão 1.125–1.2.
- **Texto claro sobre fundo escuro:** some 0.05–0.1 ao line-height. Tipo claro lê como peso mais leve e precisa de mais respiro.
- Fonte display em label, botão ou dado de UI é banida em APP, sempre.

## Cor

**LANDING** tem permissão para as estratégias Committed, Full palette e Drenched — use. Uma única cor saturada espalhada num hero não é excesso, é voz. Landing bege-com-cinza-apagado ignora o registro.

- Nomeie uma referência real antes de escolher estratégia: "laranja #ff4500 drenched da Klim", "contenção roxo-sobre-branco da Stripe", "full palette verde-ácido da Liquid Death", "full palette amarela do Mailchimp", "contenção navy do Condé Nast Traveler", "monocromo preto puro da Vercel". **Ambição sem nome vira bege.**
- Paleta É voz: uma marca calma e uma marca inquieta não devem compartilhar mecânica de paleta. Não convirja entre projetos — cada superfície de marca se diferencia da anterior.
- Estratégia Committed ou Drenched: a cor carrega a marca. Não proteja as bordas com neutros. Comprometa.
- Quando a paleta de símbolo cultural é o puxão óbvio, passe por cima: deixe a leitura cultural vir de tipografia, imagem e copy, não da paleta.

**APP** tem Restrained como piso.

- Vocabulário semântico rico em estados, padronizado: hover, focus, active, disabled, selected, loading, error, warning, success, info.
- Acento **só** em ação primária, seleção atual e indicadores de estado — nunca decoração. Cores semânticas nunca viram enfeite (coerente com a A13 do `/varrer`).
- Uma **segunda camada neutra** para sidebars, toolbars e painéis: levemente mais fria ou mais quente que a superfície de conteúdo.
- Acento pesado ou saturação cheia em estado **inativo** é ban.

## Layout, densidade e imagem

**LANDING:**

- Composição assimétrica é opção legítima; quebre o grid de propósito para ênfase.
- Espaçamento fluido com `clamp()` que respira em viewports maiores; varie para ritmo — separações generosas, agrupamentos apertados.
- Brief guiado por imagem (hotel, restaurante, revista, fotografia): hero full-bleed com menu sobreposto e headline centralizada é movimento canônico — deixe a fotografia ser o design.
- Quando card É a affordance certa: `grid-template-columns: repeat(auto-fit, minmax(280px, 1fr))` para responsividade sem breakpoint.
- **Imagem é obrigatória quando o brief implica imagem.** Zero imagens é bug, não escolha de design; "contenção" não é desculpa. Retângulo colorido onde ia o hero é pior que um stock representativo. Sem assets locais, Unsplash é o default (`https://images.unsplash.com/photo-{id}?auto=format&fit=crop&w=1600&q=80`) — **verifique as URLs antes de referenciar**: ID chutado 404-eia e vira imagem quebrada em produção. Sem caminho de verificação, prefira menos fotos confirmadas a mais fotos chutadas; nunca substitua por `<div>` colorido.
- Busque o **objeto físico da marca**, não a categoria genérica: "massa artesanal sobre mesa de madeira riscada" bate "comida italiana"; "ciprestes sobre fachada de hotel em calcário ao entardecer" bate "hotel de luxo". **Uma foto decisiva bate cinco medianas.** Alt text é parte da voz: "fettuccine da costa, cortado à mão, servido no terraço" bate "prato de massa".
- "Imagem" é mais amplo que stock: screenshot de produto, data-viz customizada, SVG gerado, cena canvas/WebGL contam. Página só-texto onde a tipografia carrega todo o peso visual é o modo de falha.

**APP:**

- Responsividade é **estrutural** (colapsar sidebar, tabela responsiva, colunas por breakpoint), não tipografia fluida.
- Densidade é permissão do registro: tabela com muitas linhas, painel com muitos labels, informação densa quando o usuário precisa dela.

## Componentes (APP) — checklist de estados

Todo componente interativo tem: **default, hover, focus, active, disabled, loading, error**. Não entregue com metade — é o mesmo checklist do gate 5 do Atelier (`/varrer`).

- Loading = **skeleton**, não spinner no meio do conteúdo.
- Empty state **ensina a interface**, não diz "nada aqui".
- Affordances consistentes na superfície inteira: mesma forma de botão, mesmo vocabulário de form control, mesmo estilo de ícone. Se o botão "salvar" é diferente em dois lugares, um deles está errado.

## Motion — quando decoração é gosto e quando é sabotagem

**LANDING (gosto, se intencional):** um page-load bem orquestrado vale mais que micro-interações espalhadas — *quando a marca convida*. Algumas marcas pulam motion de entrada por completo; a contenção é a voz. O que não é voz: fade-on-scroll em toda seção por hábito.

**APP (sabotagem):**

- **150–250 ms** na maioria das transições. O usuário está em fluxo; não o faça esperar coreografia.
- Motion comunica **estado**: mudança de estado, feedback, loading, reveal. Nada além disso.
- **Zero sequência orquestrada de page-load.** Product carrega para dentro de uma tarefa; ninguém quer assistir o app carregar.

No Atelier isso já é lei parcial (A12: animação decorativa proibida em registro APP); esta skill dá os números e o racional.

## Bans por registro (somam-se aos bans absolutos do `/varrer`)

**LANDING:**

1. Monospace como atalho preguiçoso para "técnico/developer" — se a marca não é técnica, mono é fantasia.
2. Ícone grande de canto arredondado acima de cada heading — grita template.
3. Página de família única escolhida por reflexo, não por voz (família única deliberada é ok).
4. Body em all-caps — caps só em labels curtos e headings.
5. Paleta tímida e layout mediano — seguro = invisível.
6. Zero imagem em brief que implica imagem; bloco colorido onde ia a foto de hero.
7. Estética editorial-revista como default (serifada display + itálico + drop caps + grid de broadsheet) em brief que não tem forma de revista — editorial é UMA lane, não o default de marca.
8. Kicker minúsculo uppercase com tracking repetido acima de toda seção — um kicker forte pode ser voz; repetido como gramática de seção é andaime de IA, salvo sistema de marca deliberado e nomeado.

**APP:**

1. Motion decorativo que não comunica estado.
2. Vocabulário de componente inconsistente entre telas.
3. Fonte display em label, botão ou dado.
4. Reinventar affordance padrão por tempero: scrollbar customizada, form control esquisito, modal fora do padrão.
5. Cor pesada ou acento em saturação cheia em estado inativo.
6. **Modal como primeiro pensamento.** Modal costuma ser preguiça; esgote alternativas inline/progressivas antes.

## Permissões por registro

**LANDING pode (product não):** motion ambicioso de primeiro load (reveals e coreografia tipográfica que se pagam); viewports de propósito único (uma ideia dominante por dobra, scroll longo); estratégias de cor inesperadas; direção de arte por seção quando a narrativa exige — consistência de voz vence consistência de tratamento.

**APP pode (brand não):** fontes de sistema e sans familiares (Inter, SF Pro, `system-ui`); padrões de navegação padrão (top bar + side nav, breadcrumbs, tabs, command palette); densidade; **consistência acima de surpresa** — o mesmo vocabulário visual tela a tela é virtude, delícia é para momentos, não páginas.

## Integração com o Atelier

- Declare o registro **antes** do `/croqui` (`/registro landing|app|docs`) — é o que decide o peso de cada regra desta skill no `/varrer`.
- **Intencionalidade registrada não é slop:** escolha deliberada gravada no DESIGN.md (uma fonte da ban list como identidade herdada, um drenched eleito na direção) libera a regra correspondente. O que a ban list barra é o *default não-escolhido*.
- Herança vence ban list: token existente no projeto nunca é sobrescrito por esta skill.

---

*Derivado de `skill/reference/brand.md` e `skill/reference/product.md` de [pbakaus/impeccable](https://github.com/pbakaus/impeccable) (Apache-2.0). Este arquivo foi modificado: traduzido para PT-BR, fundido num único documento e adaptado ao vocabulário do Atelier/OverCore (Apache-2.0 §4b).*
