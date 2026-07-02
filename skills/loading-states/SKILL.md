---
name: loading-states
description: "O ofício das telas de carregamento: escolha o padrão pelo TEMPO da espera (<300ms nada, 300ms–3s skeleton fiel, >3s progresso determinado com escape), herde os tokens do projeto e nunca transforme loading em slop."
risk: safe
source: overcore:atelier
date_added: "2026-07-02"
origin: pipeline-studio:atelier
author: "Atelier (artesã efêmera cristalizada)"
contributed_via: https://github.com/Weriton-DataOps/agent-skills-hub/issues/7
---

# Loading States — o ofício das telas de carregamento

## Quando usar
Sempre que uma interface espera por algo: boot de app, fetch de lista, ação de botão,
importação longa. Esta skill decide **qual** padrão de loading usar, **como** desenhá-lo
e **o que nunca fazer** — loading não é enfeite, é **contrato de expectativa**.

## As 5 regras do ofício

1. **Nunca minta a forma.** Skeleton tem a geometria **exata** do conteúdo que vem —
   mesma grade, mesmos tamanhos, mesmas posições. Skeleton genérico que não bate com o
   layout real é pior que spinner: promete uma coisa e entrega outra. E a forma é
   **reservada de verdade**: toda imagem/vídeo/embed no skeleton tem `aspect-ratio`
   (ou width/height explícitos), e nada é injetado acima de conteúdo já renderizado —
   a troca skeleton→conteúdo real acontece com **zero layout shift** (alvo CLS < 0.1).
2. **Respeite os tempos.** O padrão é escolhido pelo tempo estimado da espera:
   - **< 300ms** → **nada aparece.** Flash de spinner é pior que nada.
   - **300ms – 3s** → **skeleton fiel.**
   - **> 3s** → **progresso determinado** (barra real) + mensagem honesta do que está
     acontecendo ("Conectando…", "Importando 240 registros…"). Copy de loading diz
     **o que** está acontecendo — específico do produto, nunca gracinha genérica de espera.
3. **Um ritmo só.** Mesma duração/easing em toda a tela; shimmer atravessa numa direção
   única; animação **apenas** com `transform`/`opacity` — nunca anime layout.
4. **Palco da marca, não circo.** Um elemento de identidade no splash é suficiente.
   Logo não pulsa gigante, não gira, não explode em partículas.
5. **Sempre uma saída.** Passou de ~8s: mostre "continuar esperando / tentar de novo".
   Loading sem escape é beco sem saída.

## Os 3 padrões

| Padrão | Janela | Onde | Como |
|---|---|---|---|
| **Skeleton fiel** | 300ms–3s | listas, cards, perfis, tabelas | a página "já chegou", só falta a tinta; shimmer sutil unidirecional |
| **Splash determinado** | > 3s | boot, importação, build | marca discreta + barra de progresso real + status honesto + escape aos 8s |
| **Inline / local** | esperas curtas contextuais | botões, linhas de tabela, refetch | a ação carrega **onde foi disparada**; o resto da UI continua vivo |

## Anti-slop específico de loading
- Sem glow colorido, glass ou gradiente decorativo no splash (salvo estilo eleito no DESIGN.md).
- Progresso **indeterminado** (spinner infinito) só para esperas curtas e locais — nunca
  como tela cheia de duração desconhecida.
- Todos os valores visuais (cor, raio, ritmo) vêm dos **tokens herdados** do projeto.
- **Blacklist de copy de IA** — reprovação automática no `/varrer`: "Herding pixels…",
  "Teaching robots to dance…", "Consulting the magic 8-ball…", "Counting backwards from
  infinity…" e as traduções fofas equivalentes ("Domando os pixels…", "Consultando o
  oráculo…"). São assinatura instantânea de copy gerada por máquina. A mensagem certa
  nomeia a operação real: "Sincronizando alterações do time…", "Preparando seu
  dashboard…", "Verificando atualizações desde ontem…".
- **Zero CLS na troca**: skeleton e conteúdo real ocupam exatamente o mesmo espaço —
  dimensões reservadas via `aspect-ratio` ou width/height em toda mídia e embed;
  animação de loading nunca causa layout shift (só `transform`/`opacity`, como na regra 3).

## Exemplo vivo
Demo com os 3 padrões animados: `agents/design/demo/artesao-loading.html` (repo OverCore).

---
*Enxertos derivados de pbakaus/impeccable (Apache-2.0, modificado).*
