# Fontes e Atribuição

Este repositório consolida três coleções públicas de skills/agentes. Todo o conteúdo
mantém a licença original de cada fonte (ver `docs/licenses/`).

## As três fontes

| Fonte | Repo original | Skills | Licença |
|---|---|---|---|
| **superpowers** | `obra/superpowers` (superpowers-main) | 14 | `licenses/superpowers-LICENSE` |
| **Agent-Skills** | Agent-Skills-for-Context-Engineering | 15 | `licenses/Agent-Skills-LICENSE` |
| **antigravity** | antigravity-awesome-skills | ~1449 | `licenses/antigravity-LICENSE` (+ `-CONTENT`) |

> Os repos foram baixados como zip e extraídos em `OneDrive/Agentes AI/extracted/`.
> Atualize os nomes/links acima se quiser apontar para os upstreams exatos.

## O que entrou (1451 skills)

- **superpowers**: 14 skills (todas).
- **Agent-Skills**: 15 skills (todas) + o agente `researcher/`.
- **antigravity**: 1422 skills (as que sobraram depois de remover as duplicadas por nome).

## Política de deduplicação (cuidando da redundância)

As fontes se sobrepõem por nome. Resolução:

1. **Originais ganham.** Onde o mesmo nome existia em mais de uma fonte, ficou a
   versão de `superpowers` / `Agent-Skills` (upstreams mantidos), não a cópia da
   antigravity.
   - `superpowers ∩ antigravity`: 14 nomes → ficou a do superpowers.
   - `Agent-Skills ∩ antigravity`: 13 nomes → ficou a do Agent-Skills.
   - (`superpowers ∩ Agent-Skills`: nenhum.)
2. Total de duplicatas resolvidas: **27**.

## O que ficou DE FORA (e por quê)

| Excluído | Motivo |
|---|---|
| `antigravity/plugins/` (132 MB) | bundles que **copiam** as mesmas skills — pura redundância. As agrupações viraram índice em `docs/indices/marketplace.json`. |
| `antigravity/apps/`, `tools/`, `scripts/` | código de empacotamento do site, não é skill/agente. |
| `node_modules/`, `*.zip`, `.git/` das fontes | peso/lixo. |
| `pipeline-studio/` | é o **orquestrador** (projeto separado, com git próprio), não a biblioteca. |

## Índices preservados

- `docs/indices/CATALOG.md` — catálogo legível das skills da antigravity.
- `docs/indices/skills_index.json` — índice machine-readable (descoberta pelo orquestrador).
- `docs/indices/marketplace.json` — as agrupações em bundles, **sem** o conteúdo duplicado.
