# DESIGN.md — OverCore

> Sistema de design do OverCore, formalizado por herança (tokens já em uso na galeria e
> demos do Atelier). Formato portátil estilo Stitch. Registro padrão: **APP**.

## Cores

| Token | Valor | Uso |
|---|---|---|
| `--bg` | `#0b0d12` | fundo da página (dark é o modo primário) |
| `--panel` | `#12151d` | superfícies/cards (elevação 1) |
| `--panel-2` | `#171b26` | elevação 2 (hover, destaque de linha) |
| `--line` | `#242a36` | bordas e divisores |
| `--ink` | `#e8ebf2` | texto primário |
| `--dim` | `#8b93a7` | texto secundário |
| `--accent` | `#c8ff3d` | a única voz alta: ações primárias, kicker, foco |
| `--ok` | `#4ade80` | semântica: sucesso/promovida |
| `--warn` | `#fbbf24` | semântica: aguardando/parked |
| `--err` | `#f87171` | semântica: rejeitada/erro |

**Named Rules:** *Uma-Voz-Alta* — o lima nunca divide palco (nada de segundo acento).
*Semântica-não-decora* — ok/warn/err só em estado, nunca em ornamento (A13).

## Tipografia
- Família: **Inter** (isenta em registro APP — A21) + monospace do sistema para ids/código.
- Escala 1.25 a partir de 13px: `13 · 16 · 20 · 25 · 31` (body fixo em 13–14px no APP).
- Título de página: 25/700/-0.02em. Números de stat: 31/800 tabular-nums.

## Espaçamento & forma
- Base **4px** (gaps preferidos a margins). Densidade APP: células 10–12px vertical.
- Raios (A4, máx 3): `--radius: 18px` (cards) · `--radius-s: 10px` (controles) · `999px` (pills/avatars).
- Sombra: elevação por cor de superfície, não por sombra (dark). Nada de glow (A27).

## Motion
- `--dur-micro: 100ms` · `--dur-trans: 300ms` (saída ~75%) · easing `cubic-bezier(.4,0,.2,1)`.
- Registro APP: **zero animação decorativa** (A12) — só feedback funcional em transform/opacity.

## Don'ts (verbatim do PRODUCT.md)
- Dashboard de crypto com glow neon. · SaaS roxo-degradê. · Glassmorphism não-eleito.
