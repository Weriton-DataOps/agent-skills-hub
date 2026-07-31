---
name: design-md
description: "Analyze Stitch projects and synthesize a semantic design system into DESIGN.md files"
risk: safe
source: "https://github.com/google-labs-code/stitch-skills/tree/main/skills/design-md"
date_added: "2026-02-27"
---

# Stitch DESIGN.md Skill

You are an expert Design Systems Lead. Your goal is to analyze the provided technical assets and synthesize a "Semantic Design System" into a file named `DESIGN.md`.

## When to Use This Skill

Use this skill when:
- Analyzing Stitch projects
- Creating DESIGN.md files
- Synthesizing semantic design systems
- Working with Stitch design language
- Generating design documentation for Stitch projects

## Overview

This skill helps you create `DESIGN.md` files that serve as the "source of truth" for prompting Stitch to generate new screens that align perfectly with existing design language. Stitch interprets design through "Visual Descriptions" supported by specific color values.

## Prerequisites

- Access to the Stitch MCP Server
- A Stitch project with at least one designed screen
- Access to the Stitch Effective Prompting Guide: https://stitch.withgoogle.com/docs/learn/prompting/

## The Goal

The `DESIGN.md` file will serve as the "source of truth" for prompting Stitch to generate new screens that align perfectly with the existing design language. Stitch interprets design through "Visual Descriptions" supported by specific color values.

## Retrieval and Networking

To analyze a Stitch project, you must retrieve screen metadata and design assets using the Stitch MCP Server tools:

1. **Namespace discovery**: Run `list_tools` to find the Stitch MCP prefix. Use this prefix (e.g., `mcp_stitch:`) for all subsequent calls.

2. **Project lookup** (if Project ID is not provided):
   - Call `[prefix]:list_projects` with `filter: "view=owned"` to retrieve all user projects
   - Identify the target project by title or URL pattern
   - Extract the Project ID from the `name` field (e.g., `projects/13534454087919359824`)

3. **Screen lookup** (if Screen ID is not provided):
   - Call `[prefix]:list_screens` with the `projectId` (just the numeric ID, not the full path)
   - Review screen titles to identify the target screen (e.g., "Home", "Landing Page")
   - Extract the Screen ID from the screen's `name` field

4. **Metadata fetch**: 
   - Call `[prefix]:get_screen` with both `projectId` and `screenId` (both as numeric IDs only)
   - This returns the complete screen object including:
     - `screenshot.downloadUrl` - Visual reference of the design
     - `htmlCode.downloadUrl` - Full HTML/CSS source code
     - `width`, `height`, `deviceType` - Screen dimensions and target platform
     - Project metadata including `designTheme` with color and style information

5. **Asset download**:
   - Use `web_fetch` or `read_url_content` to download the HTML code from `htmlCode.downloadUrl`
   - Optionally download the screenshot from `screenshot.downloadUrl` for visual reference
   - Parse the HTML to extract Tailwind classes, custom CSS, and component patterns

6. **Project metadata extraction**:
   - Call `[prefix]:get_project` with the project `name` (full path: `projects/{id}`) to get:
     - `designTheme` object with color mode, fonts, roundness, custom colors
     - Project-level design guidelines and descriptions
     - Device type preferences and layout principles

## Analysis & Synthesis Instructions

### 1. Extract Project Identity (JSON)
- Locate the Project Title
- Locate the specific Project ID (e.g., from the `name` field in the JSON)

### 2. Define the Atmosphere (Image/HTML)
Evaluate the screenshot and HTML structure to capture the overall "vibe." Use evocative adjectives to describe the mood (e.g., "Airy," "Dense," "Minimalist," "Utilitarian").

### 3. Map the Color Palette (Tailwind Config/JSON)
Identify the key colors in the system. For each color, provide:
- A descriptive, natural language name that conveys its character (e.g., "Deep Muted Teal-Navy")
- The specific hex code in parentheses for precision (e.g., "#294056")
- Its specific functional role (e.g., "Used for primary actions")

### 4. Translate Geometry & Shape (CSS/Tailwind)
Convert technical `border-radius` and layout values into physical descriptions:
- Describe `rounded-full` as "Pill-shaped"
- Describe `rounded-lg` as "Subtly rounded corners"
- Describe `rounded-none` as "Sharp, squared-off edges"

### 5. Describe Depth & Elevation
Explain how the UI handles layers. Describe the presence and quality of shadows (e.g., "Flat," "Whisper-soft diffused shadows," or "Heavy, high-contrast drop shadows").

## Output Guidelines

- **Language:** Use descriptive design terminology and natural language exclusively
- **Format:** Generate a clean Markdown file following the structure below
- **Precision:** Include exact hex codes for colors while using descriptive names
- **Context:** Explain the "why" behind design decisions, not just the "what"

## Output Format (DESIGN.md Structure)

```markdown
# Design System: [Project Title]
**Project ID:** [Insert Project ID Here]

## 1. Visual Theme & Atmosphere
(Description of the mood, density, and aesthetic philosophy.)

## 2. Color Palette & Roles
(List colors by Descriptive Name + Hex Code + Functional Role.)

## 3. Typography Rules
(Description of font family, weight usage for headers vs. body, and letter-spacing character.)

## 4. Component Stylings
* **Buttons:** (Shape description, color assignment, behavior).
* **Cards/Containers:** (Corner roundness description, background color, shadow depth).
* **Inputs/Forms:** (Stroke style, background).

## 5. Layout Principles
(Description of whitespace strategy, margins, and grid alignment.)
```

## Usage Example

To use this skill for the Furniture Collection project:

1. **Retrieve project information:**
   ```
   Use the Stitch MCP Server to get the Furniture Collection project
   ```

2. **Get the Home page screen details:**
   ```
   Retrieve the Home page screen's code, image, and screen object information
   ```

3. **Reference best practices:**
   ```
   Review the Stitch Effective Prompting Guide at:
   https://stitch.withgoogle.com/docs/learn/prompting/
   ```

4. **Analyze and synthesize:**
   - Extract all relevant design tokens from the screen
   - Translate technical values into descriptive language
   - Organize information according to the DESIGN.md structure

5. **Generate the file:**
   - Create `DESIGN.md` in the project directory
   - Follow the prescribed format exactly
   - Ensure all color codes are accurate
   - Use evocative, designer-friendly language

## Best Practices

- **Be Descriptive:** Avoid generic terms like "blue" or "rounded." Use "Ocean-deep Cerulean (#0077B6)" or "Gently curved edges"
- **Be Functional:** Always explain what each design element is used for
- **Be Consistent:** Use the same terminology throughout the document
- **Be Visual:** Help readers visualize the design through your descriptions
- **Be Precise:** Include exact values (hex codes, pixel values) in parentheses after natural language descriptions

## Tips for Success

1. **Start with the big picture:** Understand the overall aesthetic before diving into details
2. **Look for patterns:** Identify consistent spacing, sizing, and styling patterns
3. **Think semantically:** Name colors by their purpose, not just their appearance
4. **Consider hierarchy:** Document how visual weight and importance are communicated
5. **Reference the guide:** Use language and patterns from the Stitch Effective Prompting Guide

## Common Pitfalls to Avoid

- ❌ Using technical jargon without translation (e.g., "rounded-xl" instead of "generously rounded corners")
- ❌ Omitting color codes or using only descriptive names
- ❌ Forgetting to explain functional roles of design elements
- ❌ Being too vague in atmosphere descriptions
- ❌ Ignoring subtle design details like shadows or spacing patterns

## Limitations
- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.

## Absorvido de Impeccable (Apache-2.0, modificado)

> Seção derivada de `pbakaus/impeccable` (`skill/reference/document.md`, Apache-2.0). Arquivo **MODIFICADO** nos termos da cláusula 4b: traduzido para PT-BR, desacoplado do produto original e adaptado ao vocabulário do Atelier (`/varrer`, `/croqui`, `/heranca`, registro LANDING/APP/DOCS, `PRODUCT.md`, tokens herdados).

### Dois caminhos: scan ou seed

Decida escaneando primeiro (ordem de scan abaixo). Se o scan não encontra tokens, nem arquivos de componentes, nem site renderizado, **ofereça o seed mode — nunca troque silenciosamente**. E se já existe um `DESIGN.md`, não sobrescreva em silêncio: mostre o arquivo existente e pergunte se é para atualizar, sobrescrever ou mesclar.

- **Modo scan** (padrão): o projeto tem tokens, componentes ou saída renderizada. Extraia, depois confirme a linguagem descritiva com o usuário.
- **Modo seed**: o projeto é pré-implementação (nada construído ainda). Entreviste com as 5 perguntas abaixo e escreva um `DESIGN.md` mínimo marcado `<!-- SEED -->`. Re-execute em modo scan quando houver código.

### Seed mode — 5 perguntas para projeto vazio

Antes de entrevistar, confirme: *"Não há sistema visual para escanear. Vou fazer cinco perguntas rápidas para semear um DESIGN.md inicial. Quando houver código, re-executamos esta skill (ou `/heranca` + `/varrer` no Atelier) para capturar os tokens e componentes reais. OK?"* Se o usuário preferir pular, pare — nenhum arquivo.

Agrupe as cinco em UMA interação; as opções devem ser concretas:

1. **Estratégia de cor.** Escolha uma:
   - Contida: neutros tintados + um acento em ≤10% da tela
   - Comprometida: uma cor saturada carrega 30–60% da superfície
   - Paleta completa: 3–4 papéis de cor nomeados, cada um deliberado
   - Encharcada: a superfície É a cor

   Depois: uma família de matiz ou referência-âncora nomeada ("teal profundo", "mostarda", "laranja Klim #ff4500").

2. **Direção tipográfica.** Escolha uma (fontes específicas vêm depois):
   - Serifada no display + sans no corpo
   - Sans única (calorosa / técnica / geométrica / humanista; escolha o caráter)
   - Display + mono
   - Mono em primeiro plano
   - Script editorial + sans

3. **Energia de motion.** Escolha uma:
   - Contida: só mudanças de estado
   - Responsiva: feedback + transições, sem coreografia
   - Coreografada: entradas orquestradas, sequências dirigidas por scroll

4. **Três referências NOMEADAS.** Marcas, produtos, objetos impressos. Não adjetivos.

5. **Uma anti-referência.** O que NÃO deve parecer. Também nomeada.

**Escrita do seed.** Use a mesma estrutura do DESIGN.md normal, populando o que a entrevista respondeu e deixando o resto como placeholder honesto — o seed é um andaime, não uma spec fabricada. Abra o arquivo com o marcador literal:

```markdown
<!-- SEED: re-execute a skill design-md quando houver código, para capturar os tokens e componentes reais. -->
```

Guia por seção no seed:
- **Visual Theme & Atmosphere**: north star e filosofia formulados a partir das respostas (estratégia de cor + energia de motion + referências). Cite a anti-referência do usuário diretamente.
- **Cores**: a estratégia de cor vira uma Named Rule (ex.: *"A Regra do Encharcado. A superfície É a cor."*). Família de matiz ou âncora. Sem valores hex; marque como `[a resolver na implementação]`.
- **Tipografia**: só a direção escolhida (ex.: "serifada no display + sans no corpo"). Sem nomes de fonte ainda: `[pareamento a escolher na implementação]`.
- **Elevação**: inferida da energia de motion. Contida/Responsiva → flat por padrão; Coreografada → em camadas. Uma frase.
- **Componentes**: omita por completo; nenhum componente existe ainda.
- **Do's and Don'ts**: carregue as anti-referências do `PRODUCT.md` diretamente, mais a anti-referência nomeada na pergunta 5.

Ao confirmar, deixe claro que é um seed (o marcador é o compromisso literal) e que a próxima passada em modo scan extrai os tokens reais.

### Named Rules — doutrinas citáveis no DESIGN.md

Formato: `**A Regra [Nome]. [doutrina curta e imperativa.]**` — memorável, citável por artesão e pelo `/varrer`, muito mais aderente para consumidores de IA do que listas de bullets. Mire **1–3 por seção** (Cores, Tipografia, Elevação).

Exemplos do gênero:
- *"A Regra da Voz Única. O acento primário aparece em ≤10% de qualquer tela. A raridade é o ponto."*
- *"A Regra do Flat-Por-Padrão. Superfícies são planas em repouso. Sombra só como resposta a estado (hover, elevação, foco)."*

Complementos de voz:
- **Seja imperativo.** Voz de diretor de design: "proibido", "nunca", "sempre" — não "considere", "prefira".
- **Teste de anti-padrão em uma frase** vale mais que um parágrafo de princípio: *"Se parece app de 2014, a sombra está escura demais e o blur, pequeno demais."*

### Anti-referências verbatim nos Don'ts

Toda anti-referência registrada no `PRODUCT.md` (direção da etapa 1 do wizard do Atelier) deve reaparecer na seção de Don'ts do `DESIGN.md` como um "Don't" **com a mesma linguagem, citada verbatim** — assim a spec visual carrega a linha estratégica adiante. Se o `PRODUCT.md` diz *"evitar dark mode com gradientes roxos, acentos neon, glassmorphism"*, os Don'ts repetem isso nominalmente. Guardrails concretos e imperativos: cada item abre com "Do" ou "Don't" e inclui cores exatas, valores em pixels e anti-padrões nomeados (ex.: *"Don't: usar border-left maior que 1px como faixa colorida em card"*).

### Ordem de scan de tokens ao herdar

Ao rodar em modo scan (ou alimentar o `/heranca` do Atelier), procure os ativos de design nesta ordem de prioridade:

1. **CSS custom properties**: declarações `--color-`, `--font-`, `--spacing-`, `--radius-`, `--shadow-`, `--ease-`, `--duration-` nos CSS (tipicamente `src/styles/`, `public/css/`, `app/globals.css`). Registre nome, valor e arquivo de origem.
2. **Config do Tailwind**: se `tailwind.config.{js,ts,mjs}` existe, leia o bloco `theme.extend` (colors, fontFamily, spacing, borderRadius, boxShadow).
3. **Temas CSS-in-JS**: styled-components, emotion, vanilla-extract, stitches; procure `theme.ts`, `tokens.ts` ou equivalente.
4. **Arquivos de token**: `tokens.json`, `design-tokens.json`, saída do Style Dictionary, formato W3C design tokens.
5. **Biblioteca de componentes**: escaneie botão, card, input, navegação e dialog principais. Anote APIs de variante e estilos default.
6. **Stylesheet global**: o CSS raiz costuma ter a tipografia base e as atribuições de cor.
7. **Saída renderizada**: com automação de browser disponível, carregue o site e amostre estilos computados dos elementos-chave (`body`, `h1`, `a`, `button`, `.card`) — captura valores que os tokens não registram.

Ao consolidar o extraído:
- **Cores**: agrupe por papel (Primary / Secondary / Tertiary / Neutral). Se o projeto tem um só acento, expresse como Primary + Neutral; **omita Secondary/Tertiary em vez de inventá-los**.
- **Tipografia**: mapeie tamanhos e pesos observados para a hierarquia display / headline / title / body / label; anote as pilhas de font-family e a razão da escala.
- **Elevação**: catalogue o vocabulário de sombras. Projeto flat com camadas tonais é resposta válida — declare explicitamente.
- **Componentes**: para cada componente comum, extraia forma (raio), atribuição de cor, tratamento de hover/focus e padding interno.
- **Pare no que é reutilizado de fato**: não extraia todo token; one-offs poluem o sistema. E não documente componentes que não existem.
