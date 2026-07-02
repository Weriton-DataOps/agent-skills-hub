# Ambiente de Desenvolvimento

O laboratório do OverCore: aqui as peças **nascem e são testadas** antes de entrar no
catálogo oficial (`agents/design/showcase/`). Nada aqui é promessa; tudo aqui é protótipo.

## Experimentos

| # | Experimento | O que é |
|---|---|---|
| 001 | **Core** (`index.html`) | O personagem 3D do OverCore: um núcleo metálico com olhos de lima que seguem o cursor, piscam e reagem ao clique; anel-órbita com satélite (o "over" do Core). 100% procedural em Three.js — zero modelo externo. |

## Regras do laboratório
- Código autocontido (o Three.js vem de `../agents/design/showcase/vendor/`).
- Mesma disciplina do catálogo: fallback digno, `prefers-reduced-motion` respeitado.
- Experimento que provar valor **sobe pro catálogo** (e pode virar skill via `/cristalizar`).
