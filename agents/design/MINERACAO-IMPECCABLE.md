# Mineração do Impeccable — plano de extração

## 1. Veredito geral

O Impeccable não substitui o Atelier — nosso wizard com gates humanos e artesãos por etapa é estruturalmente equivalente ao pipeline deles (shape→craft) e não precisa de transplante. O valor real está em três camadas que nos faltam: **(a)** a dimensão de **registro brand vs product**, que nenhum dos nossos 18 titulares carrega e que expõe um bug nosso (A1-A18 aplicadas cegas a um dashboard produzem slop invertido); **(b)** ~12 tells de AI-slop com thresholds numéricos que as A1-A18 não cobrem, prontos para virar A19+; **(c)** quatro buracos dos nossos 14 fechados ou semeados de graça (onboarding, navegação responsiva, robustez de produção, ilustração/hero). O resto — distill, optimize, extract — é restate do que já temos. Colheita: 9 imports, ~18 enxertos, 2 descartes.

## 2. IMPORTAR como skills novas

| Arquivo | Skill no hub | Buraco/valor | Prioridade |
|---|---|---|---|
| `reference/brand.md` + `reference/product.md` | `design-register` (par único — o fork É o valor) | Dimensão registro ausente em todos os titulares; ban list de 23 fontes-reflexo; permissões de produto (Inter/densidade) que nossas regras negariam | **Alta** |
| `reference/harden.md` | `hardening-ui` | Robustez de produção — dimensão inteira ausente do /varrer (i18n, overflow, matriz HTTP→UI, duplo-submit); semeia formulários complexos e páginas de erro | **Alta** |
| `reference/onboard.md` | `onboarding-first-run` | Buraco direto nosso, sem artesão nenhum; anatomia de empty states em 5 tipos | **Alta** |
| `reference/critique.md` | `design-critique` | Avaliação pontuada que o /varrer não faz: rubrica Nielsen 0-40 com âncoras, personas, P0-P3, tendência entre runs; desacoplar dos scripts .mjs | **Alta** |
| `reference/interaction-design.md` | `modern-interaction` | react-ui-patterns tem ZERO cobertura de popover/inert/anchor-positioning/roving-tabindex; resolve o dropdown clipado — bug recorrente de código gerado | **Alta** |
| `reference/adapt.md` | `responsive-adaptation` | Buraco navegação responsiva (nav 3 estágios, tabela→cards, pointer/hover queries) + seção email vira embrião do artesão email HTML | Média |
| `reference/overdrive.md` | `high-impact-moments` | Semeia ilustração/hero, tabelas densas e data-viz via APIs modernas com disciplina de fallback; gate de 2-3 direções encaixa nativo no wizard | Média |
| `agents/impeccable-asset-producer.md` | `asset-producer` (com nota de dependência de imagegen) | Metade faltante de ilustração/hero: da direção aprovada ao asset no build (buckets produce/direct/semantic, manifest com QA) | Média |

## 3. ABSORVER no Atelier/skills nossas

| Fonte | Destino | Insights a enxertar |
|---|---|---|
| `SKILL.src.md` | Atelier CLAUDE.md + /varrer | Tetos numéricos (hero ≤6rem, tracking ≥-0.04em, 65-75ch, `text-wrap:balance`); teste anti-reflexo de 2ª ordem (se categoria+anti-referências ainda predizem a estética, é slop); reveal-safety (nunca condicionar visibilidade a transição por classe) |
| `reference/shape.md` + `reference/init.md` | Wizard etapas herança/direção | Assert-then-confirm em vez de menu; scene sentence (1 frase física decide dark vs light); referências NOMEADAS, nunca adjetivos; anti-referências como campo obrigatório; "nunca sintetize o doc só do prompt" |
| `reference/craft.md` + `reference/codex.md` | Wizard (gates e croqui) | "Comprimir gates é o modo de falha dominante"; Step 0 de fundação (framework/ícones existentes, nunca escrever em dist/); paleta-primeiro como contrato; inventário de fidelidade do mock pós-aprovação; "screenshot não lido não conta" |
| `reference/colorize.md` | Atelier + semente do artesão dark-mode | Receita construtiva de dark (3 degraus de lightness de superfície com hue da marca, chroma reduzido, peso ~350); neutros tintados 0.005-0.015 rumo ao hue; "alpha pesado = paleta incompleta" |
| `reference/typeset.md` | design-taste-frontend | Compensação dark em 3 eixos (leading/tracking/peso); fallback metric-matched; ALL-CAPS exige tracking 0.05-0.12em; clamp bounded ≤2.5x; body sempre fixo |
| `reference/layout.md` | baseline-ui + A9 refinada | Escala 4pt justificada; gap>margin; container queries; margin -0.05em óptico; hit-area 44px via pseudo-element |
| `reference/animate.md` + `reference/optimize.md` | fixing-motion-performance + loading-states | Refinar A12: ban é layout props, não "só transform/opacity" — blur/clip-path bounded ok; tabela 100/300/500ms, saída = 75% da entrada; stagger cap 500ms; limiar de 80ms percebido; aspect-ratio contra CLS |
| `reference/polish.md` + `reference/audit.md` | baseline-ui/redesign + /varrer | Taxonomia de causa-raiz (token-faltante / one-off / desalinhamento conceitual → fix diferente); drift de IA/fluxo contra vizinhos; mecânica de score /20 + P0-P3 + re-medição; "script limpo nunca é prova" |
| `reference/bolder.md` + `reference/quieter.md` | design-taste-frontend + redesign | Design-System Lock (token novo exige aprovação nominal); amplificar via hierarquia/proporção dentro do sistema; dessaturação 70-85% + acento em 10%; "quiet ≠ genérico" |
| `reference/delight.md` + `reference/distill.md` + `reference/clarify.md` | ux-copy + loading-states | Blacklist de loading copy de IA ("Herding pixels"); registro brand=distribuído vs product=momentos ganhos; tabela de expansão i18n (+30% alemão); templates de erro; "Cancel"→"Keep editing"; undo > confirmação |
| `reference/document.md` | design-md | Seed mode (5 perguntas para projeto vazio — caminho que não temos); Named Rules citáveis; anti-referência verbatim nos Don'ts; ordem de scan de tokens |
| `reference/hooks.md` | Desenho do futuro hook do /varrer | Enforcement contínuo pós-edit; política ignore-value > ignore-file > ignore-rule com --reason; hook nunca escreve ignore sozinho |

## 4. Regras determinísticas a adotar no /varrer

- **A19 — gray-on-color**: texto cinza sobre fundo cromático; fix é shade escura da própria cor ou transparência. (A regra mais citada da mineração: aparece em colorize, quieter, polish e no detector.)
- **A20 — side-stripe**: borda colorida ≥2px num só lado de card/callout — "o tell mais reconhecível de UI gerada".
- **A21 — fontes-reflexo**: blacklist nominal (Inter*, Roboto, Fraunces, Playfair, Space Grotesk, DM Sans, Plus Jakarta, Geist, Outfit…) — A7 limita quantidade, não proíbe as manjadas. *Inter isenta em registro product.
- **A22 — scaffold editorial**: eyebrow/kicker uppercase repetido por seção + marcadores numerados 01/02/03.
- **A23 — templates decorativos**: hero-metric sem dado real; grid de cards idênticos (ícone+título+texto ×N); icon-tile acima de heading.
- **A24 — ghost-card**: borda hairline 1px + sombra blur ≥16px no mesmo elemento; e radius ≥32px em card.
- **A25 — cream-palette default**: fundo creme/bege como "tasteful default" (OKLCH L 0.84-0.97, C<0.06, hue 40-100; tokens `--paper/--cream/--sand` como tell) — estende A2, que só cobre roxo.
- **A26 — easing proibido**: bounce/elastic/spring nomeado ou cubic-bezier com y fora de [-0.1, 1.1]; + fade-and-rise em toda seção scrollada — complementa A12, que cobre propriedades mas não curvas.
- **A27 — dark-glow**: box-shadow colorido difuso (chroma alto, blur >4px) sobre fundo escuro — A14 só cobre #000/#FFF puros.
- **A28 — copy-cadence de IA**: >2 travessões por bloco, "X. No Y." repetido 3+, loading/empty com clichê de IA — vai além do A10 (verbo-hype).
- **A29 — micro-tipografia**: linha >80ch, leading <1.3, texto <12px, all-caps sem tracking, justified sem hyphens.
- **A30 — defeitos renderizados**: tooltip/menu clipado por `overflow:hidden`, `min-width:0` faltante em flex/grid, texto na borda do viewport, heading pulado, broken image.

## 5. PULAR

- `reference/extract.md` — extração para design system é fluxo genérico que qualquer modelo executa; nada proprietário.
- `agents/impeccable-manual-edit-applier.md` — acoplado ao protocolo live/lease do CLI deles; sem a feature, é peso morto.
- (Do resto do `optimize.md` e `distill.md`, além dos enxertos pontuais da seção 3: conhecimento genérico ou restate literal de A13/A15/A16.)

## 6. Atribuição

Apache-2.0 é permissivo mas não invisível: no `NOTICE.md` do hub devemos (1) creditar `pbakaus/impeccable` com link e copyright original em cada skill importada ou derivada (design-register, hardening-ui, onboarding-first-run, design-critique, modern-interaction, responsive-adaptation, high-impact-moments, asset-producer), (2) incluir cópia ou link da licença Apache-2.0, e (3) declarar que os arquivos foram **modificados** — traduzidos, desacoplados dos scripts `.mjs` e adaptados ao pipeline do Atelier (exigência da cláusula 4b: arquivos alterados devem carregar aviso de alteração). Regras absorvidas como A19-A30 e enxertos em skills nossas são derivação suficientemente transformada, mas uma linha de crédito coletivo no NOTICE ("regras anti-slop parcialmente derivadas de pbakaus/impeccable, Apache-2.0") é barata e elegante — pagamos.
