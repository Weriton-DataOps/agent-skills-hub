# NOTICE — Atribuições

O **OverCore** inclui skills de terceiros, cada uma sob a sua licença original.
Este arquivo consolida, de forma discreta, as atribuições exigidas por essas licenças.

## Conteúdo original do OverCore

Código e ferramentas: **MIT** © 2026 Weriton — GR Group (ver [`LICENSE`](LICENSE)).
Conteúdo (skills/métodos/docs criados para o projeto): **CC BY-SA 4.0** © 2026
Weriton — GR Group (ver [`LICENSE-CONTENT`](LICENSE-CONTENT)).

## Skills de terceiros

Parte das skills desta biblioteca foi originada de projetos open-source de terceiros e
**mantém a licença e a autoria originais**. Essas atribuições são preservadas assim:

- **Por skill:** o campo `source` de cada item em
  [`docs/indices/skills_index.json`](docs/indices/skills_index.json) registra a origem/autoria.
- **Licenças-base:** os textos completos estão em [`docs/licenses/`](docs/licenses/), que
  preservam os avisos de copyright exigidos (MIT / CC BY 4.0).

## Tipos de licença de terceiros presentes

- **MIT License** — ver `docs/licenses/`
- **Creative Commons Attribution 4.0 (CC BY 4.0)** — conteúdo não-código
- **Apache License 2.0** — algumas skills

## Three.js (MIT)

O catálogo do Atelier embarca `three.min.js` r147 (`agents/design/showcase/vendor/`) —
Copyright 2010-2022 Three.js Authors, MIT License — usado na galeria orbital 3D.

## Derivação de magic.css (MIT)

A seção "Efeitos" do catálogo do Atelier (`agents/design/showcase/catalogo.html`) inclui
keyframes derivados de [`magic.css`](https://github.com/miniMAC/magic)
(Copyright © Christian Pucci, MIT License), adaptados ao palco do catálogo.

## Derivações de pbakaus/impeccable (Apache-2.0)

Parte do agente **Atelier** e um conjunto de skills derivam de
[`pbakaus/impeccable`](https://github.com/pbakaus/impeccable) (Copyright Paul Bakaus,
Apache License 2.0 — texto em https://www.apache.org/licenses/LICENSE-2.0). Os arquivos
foram **modificados** (Apache-2.0 §4b): traduzidos para PT-BR, desacoplados dos scripts
e comandos do produto original, e adaptados ao pipeline do Atelier/OverCore.

- Skills derivadas: `design-register`, `hardening-ui`, `onboarding-first-run`,
  `design-critique`, `modern-interaction`, `responsive-adaptation`,
  `high-impact-moments`, `asset-producer` (atribuição também no frontmatter de cada uma).
- Enxertos derivados (seção "Absorvido de Impeccable" ou crédito em rodapé):
  `agents/design/CLAUDE.md` (regras A19–A30 e refinamentos), `design-taste-frontend`,
  `baseline-ui`, `fixing-motion-performance`, `loading-states`, `ux-copy`, `design-md`,
  `redesign-existing-projects`.

> Nenhuma atribuição de autor foi removida: ela vive no `source` de cada skill e nos
> textos em `docs/licenses/`. O OverCore rebranda apenas a sua própria identidade,
> preservando o crédito de quem escreveu cada skill de terceiros.
