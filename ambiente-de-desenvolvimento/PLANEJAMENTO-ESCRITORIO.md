# A Sede da OverCore — planejamento do ambiente de produção vivo

> **Decisão do dono:** OverCore é **a empresa**. A cena é a sede dela; os agentes são o time contratado.

> **Visão:** uma cena 3D (no navegador — dentro do VS Code via Simple Browser ou fora dele)
> mostrando o escritório do OverCore com os agentes trabalhando. Quando um agente é acionado
> de verdade no projeto (skill, subagente, gate), o personagem correspondente **age na cena**.
> Não é decoração: é telemetria com alma.

---

## 1. Como o real liga no virtual (a ponte técnica)

```
Claude Code (trabalho real)
   │  hooks: PreToolUse (Task/Skill), SubagentStart/Stop, UserPromptSubmit, Stop
   ▼
~/.claude/overcore-events.log   ← JÁ EXISTE (overcore-event.py grava JSONL)
   │  tail
   ▼
servidor local (python stdlib, ~80 linhas — mesmo padrão da Fila do Curador)
   │  GET /api/eventos  (polling 1s ou SSE)
   ▼
escritorio.html (Three.js do vendor/)
   → mapeia evento → personagem → ação
```

- **F0 pronta:** o hook de eventos já grava skill/subagente em JSONL.
- **Mapeamento evento→personagem:** por heurística de conteúdo:
  skills `safegate-*`/security → SafeGate · skills de design/verbos do Atelier → Atelier ·
  `contribution`/judge → Curator · git/test/build → Validação · plan mode → Plan ·
  edição de código → Code · prompt do usuário → Router acende · fetch externo/research → Researcher.
- **Onde ver:** navegador normal, ou painel do VS Code (Simple Browser aponta pro localhost).

## 2. O cenário — a sede da OverCore

Uma **plataforma flutuante dark-premium** (paleta da casa: grafite #0b0d12–#171b26, acentos lima),
vista isométrica-orbital (câmera arrastável, como no experimento 001). Estações:

| Estação | Do que é feita | Vida ambiente (idle) |
|---|---|---|
| **Torre do Router** (centro) | balcão circular + 3 monitores flutuantes | monitores piscam suave; radar varre |
| **Ateliê** | cavalete + mesa de luz + potes de tinta | telas encostadas trocam de "quadro" |
| **Cofre do SafeGate** | porta de cofre + scanner de esteira | luz de ronda varre o chão em ciclos |
| **Biblioteca do Curator** | estantes de "skills" (caixinhas lima) + esteira de entrada + carimbo | caixinhas chegam de vez em quando na esteira |
| **Bancada do Code** | mesa + 2 monitores com "código" (shader de linhas rolando) | cursor pisca no monitor |
| **Quadro do Plan** | quadro branco + post-its flutuantes | post-it reorganiza sozinho |
| **Bancada da Validação** | bancada com semáforo verde/vermelho + prensa de teste | semáforo em amarelo repousando |
| **Observatório do Researcher** | telescópio/parabólica na borda, apontado "pra fora" | parabólica gira devagar procurando sinal |
| **Núcleo central** | um cristal de energia (o "core" da empresa) pulsando | pulso lento; acende com atividade geral |
| **Letreiro da empresa** | "OverCore" em 3D no alto da sede + contador de skills do hub (dado real) | contador vivo; letreiro com brilho sutil |

## 3. Os personagens — a família do Core

Todos **variações procedurais do DNA do Core** (experimento 001): corpo metálico escuro,
olhos de lima, antena. Diferem em silhueta, acessório e **um acento de cor próprio**
(paleta neutra do catálogo — nada de marca):

| Personagem | Papel | Silhueta/acessório | Acento | Personalidade (micro-idle) |
|---|---|---|---|---|
| **Core** | Router/Supervisor — o maestro | o original; anel-órbita com satélite | lima `#c8ff3d` | olha pra quem chega; aponta estações |
| **Tinta** | Atelier (design) | boina achatada + pincel na antena | rosa `#f472b6` | inclina a cabeça "avaliando" as telas |
| **Trava** | SafeGate (segurança) | corpo mais quadrado, visor único, escudo nas costas | vermelho `#f87171` | faz ronda; para e "escaneia" algo |
| **Tomo** | Curator (curadoria) | alto e fino, óculos retangulares, carimbo no cinto | azul `#60a5fa` | folheia caixinhas; ajeita a estante |
| **Byte** | Code (código) | compacto, visor largo tipo terminal | cyan `#22d3ee` | digita no ar mesmo sem tarefa |
| **Pauta** | Plan (planejamento) | prancheta acoplada ao braço | violeta `#a78bfa` | reordena post-its no quadro |
| **Prova** | Validação | lupa no lugar de um olho, checklist | verde `#4ade80` | carimba ✓/✗ em itens imaginários |
| **Faro** | Researcher (descoberta) | parabólica mini na cabeça | teal `#2dd4bf` | aponta a antena pra direções aleatórias |

*(Nomes são proposta — gate do dono. Alternativa: nomes em inglês ou sem nome, só o papel.)*

## 4. As ações — o vocabulário de animação

Máquina de estados por personagem (transições suaves, nada de teleporte):

| Estado | Gatilho (evento real) | O que se vê |
|---|---|---|
| **idle** | sem eventos | micro-idles de personalidade + respiração/piscada |
| **acordar** | evento chega pro papel | antena acende, endireita o corpo, olhos abrem |
| **trabalhar** | durante a tarefa | **loop próprio por papel** (abaixo) |
| **entregar** | tarefa termina | leva um **cubo brilhante** (o artefato) até a Torre do Core |
| **gate humano** | fluxo parado esperando aprovação | sino âmbar pisca na Torre até o humano responder |
| **erro** | tool falha / exceção | flash vermelho curto, balança a cabeça, volta ao trabalho |
| **dormir** | idle > 10 min | luzes da estação baixam, olhos em meia-lua, "zZ" de partículas |

**Loops de trabalho por personagem:**
- **Tinta:** pinceladas numa tela do cavalete — a tela ganha formas de cor a cada passada.
- **Byte:** digita; linhas de "código" rolam no monitor; às vezes estala os dedos.
- **Trava:** feixe de scanner varre um documento; carimbo VERDE (ok) ou trava VERMELHA (achado).
- **Tomo:** caixinha entra na esteira → ele examina com os óculos → **carimbo do juiz** →
  caixinha aprovada sobe pra estante (cristalização ao vivo!) ou cai na lixeira (rejeitada).
- **Pauta:** desenha fluxo no quadro; post-its se organizam em colunas.
- **Prova:** aciona a prensa de teste; semáforo fica verde (passou) ou vermelho (falhou) — cor real do resultado.
- **Faro:** telescópio estica, aponta, "puxa" um pacotinho de luz de fora da plataforma.
- **Core:** recebe entregas, acende o monitor correspondente, e quando o usuário manda prompt,
  ergue a batuta (a antena vira batuta por 1s).

**Eventos globais:**
- **Prompt do usuário** → luz geral sobe 10%, Core acorda todo mundo que for precisar.
- **Skill cristalizada (merge)** → mini-celebração: satélite do Core dá 3 voltas rápidas, estante ganha caixinha nova com brilho.
- **Fim de sessão** → luzes baixam em sequência, cada um volta pra estação.

## 5. Fases de entrega

| Fase | Entrega | Esforço |
|---|---|---|
| **F0** ✅ | hook gravando eventos em JSONL (já existe: `overcore-event.py`) | feito |
| **F1 — MVP** | servidor de eventos (stdlib) + cena com **4 personagens** (Core, Tinta, Byte, Trava) + 4 estados (idle/acordar/trabalhar/entregar) + placar real | 1 sessão boa |
| **F2** | roster completo (8), mapeamento fino evento→papel, gate humano com sino, erro, esteira do Tomo | 1-2 sessões |
| **F3** | polimento: câmera cinematográfica com auto-enquadre em quem trabalha, modo compacto (janelinha PiP pro canto do VS Code), tema claro, sons opcionais | depois |
| **F4 — ponte WarRoom** | escritório do TIME: cada dev com seu andar/sala, agregados históricos (a visão do WarRoom vira o prédio) | visão |

## 6. Decisões em aberto (gates do dono)

1. **Nomes dos personagens** — Tinta/Trava/Tomo/Byte/Pauta/Prova/Faro, ou outra família?
2. **Core = Router** (maestro na torre) ou Core = mascote livre circulando (e o Router é outro)?
3. **Som** — desligado por padrão com toggle, ou sem som nunca?
4. **Tom visual** — sóbrio-premium (como o 001) ou mais cartoon (olhos maiores, squash forte)?
5. ~~Nome do produto~~ — **decidido: a sede da OverCore** (OverCore é a empresa; a cena é o QG dela).

## 7. Regras herdadas (inegociáveis)
- Código no repo, Three.js do `vendor/`, zero CDN.
- Fallback digno (sem WebGL → painel 2D de status com os mesmos eventos).
- `prefers-reduced-motion` → cena estática + lista de eventos.
- Genérico: nenhuma marca de empresa na cena (princípio da camada 1).
