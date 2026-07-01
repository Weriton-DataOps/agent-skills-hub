# Atribuição e Deduplicação

A biblioteca do **OverCore** reúne skills próprias e skills de terceiros. As de terceiros
**mantêm a licença e a autoria originais** — a atribuição por skill vive no campo `source`
de cada item em [`skills_index.json`](indices/skills_index.json), e os textos-base das
licenças estão em [`licenses/`](licenses/). Ver também o [`NOTICE.md`](../NOTICE.md) na raiz.

## Política de deduplicação

As skills podiam se sobrepor por nome. Resolução aplicada para que **cada skill apareça
uma única vez**:

1. **Originais ganham.** Onde o mesmo nome existia em mais de uma origem, ficou a versão
   original mantida (upstream ativo), não a cópia agregada.
2. **Total de duplicatas resolvidas:** 27.

## O que ficou de fora (e por quê)

| Excluído | Motivo |
|---|---|
| Bundles que copiam as mesmas skills | pura redundância — os agrupamentos viraram índice em [`indices/marketplace.json`](indices/marketplace.json), sem duplicar conteúdo. |
| Código de empacotamento (apps/tools/scripts de sites) | não é skill/agente. |
| `node_modules/`, `*.zip`, `.git/` das origens | peso/lixo. |
| O orquestrador (Pipeline Studio) | projeto separado, com git próprio, não a biblioteca. |

## Índices

- [`indices/skills_index.json`](indices/skills_index.json) — índice machine-readable
  (descoberta pelo orquestrador; traz `source`, `risk`, `category`, `targets` por skill).
- [`indices/marketplace.json`](indices/marketplace.json) — agrupamentos em bundles, sem duplicar conteúdo.
- [`indices/CATALOG.md`](indices/CATALOG.md) — catálogo legível.
