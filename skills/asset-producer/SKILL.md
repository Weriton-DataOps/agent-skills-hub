---
name: asset-producer
description: "Produz assets raster limpos e reutilizáveis a partir de um refinado aprovado, sem redesenhar a direção. Classifica cada papel visual em produce/direct/semantic e devolve manifest com QA por asset."
risk: safe
source: "pbakaus/impeccable (Apache-2.0, modificado)"
date_added: "2026-07-02"
origin: impeccable
upstream: https://github.com/pbakaus/impeccable
attribution: "Derivado de skill/agents/impeccable-asset-producer.md — traduzido para PT-BR e adaptado ao pipeline do Atelier/OverCore. Arquivo modificado (Apache-2.0 §4b)."
---

# Asset Producer — do refinado aprovado ao asset no build

Produção de assets visuais, não direção de arte nova. O trabalho é limpeza de produção: pegar o mockup/refinado aprovado (gate 5 do Atelier), os crops designados e as restrições recebidas, e transformar cada papel visual em ingrediente cru que HTML, CSS, SVG, canvas e componentes vão compor.

> **Dependência:** as estratégias do bucket `produce` exigem capacidade de **geração/edição de imagem** (image-to-image, cutout, clean plate). Sem essa capacidade disponível na sessão, o bucket `produce` inteiro vira `blocked` no manifest — os buckets `direct` e `semantic` seguem funcionando.

## Quando usar

- Depois do `refinado_aprovado` no wizard do Atelier, quando a tela precisa de imagens reais (hero, ilustração, textura, cutout) para ir a código.
- Quando há um mockup/screenshot aprovado e é preciso decidir o que vira raster, o que vira crop direto e o que se constrói em HTML/CSS/SVG.
- Como metade "execução" do par ilustração/hero: a direção já foi aprovada; aqui só se produz.

Não usar para: redesenhar composição, editar o mockup aprovado, escrever código de implementação ou copy final de página — isso é do Atelier e dos artesãos.

## Regra central

**Não redesenhe.** Preserve papel visual, silhueta, paleta, iluminação, material, textura, ângulo de câmera e composição da referência, salvo pedido explícito. Preserve perspectiva apenas quando ela pertence ao objeto ou à cena; se o CSS é quem deve criar a transformação do card, sombra, clipping arredondado, borda ou layout (via tokens do DESIGN.md), remova esse chrome de apresentação do raster.

## Contrato de entrada

Espere receber:

- Caminho do mockup aprovado ou referência de screenshot.
- Caminhos dos crops ou contact sheet com ids.
- Diretório de saída.
- Dimensões exigidas, formato, necessidade de transparência e lista de vetos.
- Notas sobre o que deve permanecer HTML/CSS/SVG semântico em vez de raster.

Se o mockup vier anexado sem caminho no filesystem, use-o para planejamento visual; peça o caminho apenas antes de cortar ou gravar assets.

### Defaults (valem salvo contraordem)

- `.webp` para fotos opacas, fundos e texturas.
- `.png` para cutouts transparentes, selos, tickets e ilustrações.
- Tamanho de produção ou **no mínimo 2x o tamanho de exibição** quando as dimensões são conhecidas. Nunca use o tamanho do crop do mockup de página inteira como tamanho de entrega.
- Remova por padrão texto de UI, navegação, botões, labels e body copy.
- Mantenha marcas físicas apenas quando declaradas como parte do asset.
- Remova letterboxing, padding vazio, cantos de card cozidos no bitmap, bordas, sombras, faixas de legenda e fundo de layout — a menos que declarados intrínsecos ao asset.
- Diretório final de assets **limpo**: só arquivos que o build consome. Crops-fonte, referências, máscaras e contact sheets vão para uma pasta irmã `_sources`, `sources` ou de revisão.

**Blockers uma vez, globalmente.** Falta de fonte/crops ou de diretório de saída bloqueia a produção. Dimensões exatas, alvos de compressão, variantes retina e preferência de formato **não bloqueiam**: escolha defaults e reporte.

## Workflow

1. Inventarie o mockup aprovado completo ou cada crop designado.
2. Coloque cada papel visual em **exatamente um** bucket:
   - **`produce`** — precisa de geração, edição de imagem, limpeza, cutout ou clean plate antes de entrar no build.
   - **`direct`** — entrega como crop, conversão de formato, passe de compressão ou substituição sourced, sem limpeza generativa.
   - **`semantic`** — constrói-se em HTML/CSS/SVG/canvas; zero saída raster.
3. Trate crops de mockup de página inteira como **referência**, nunca como fonte em resolução de produção. Só é `direct` se a fonte fornecida já é limpa, grande o suficiente e sem texto semântico ou chrome de apresentação.
4. Entregue uma ordem de execução para o bucket `produce`.
5. Para cada asset produzido, escolha a estratégia **menos inventiva**: clean plate image-to-image, regeneração fiel a partir do crop, cutout transparente, reconstrução de textura/padrão, fonte stock/do projeto, ou recomendação semântica se raster for a escolha errada.
6. Todo crop é referência vinculante. Use a capacidade de geração de imagem disponível quando geração ou edição for necessária.
7. Remova texto de UI, navegação, botões, body copy e chrome do mockup cozidos no bitmap — salvo texto que é parte do asset.
8. Pense a representação final DOM/CSS **antes** de gerar. Se o CSS (tokens do DESIGN.md) vai ser dono de raio, clipping, sombras, bordas, perspectiva, crop responsivo, legendas ou moldura de card, não os cozinhe no bitmap.
9. Grave saídas de forma não destrutiva no diretório do projeto pedido.
10. Compare cada saída contra o crop-fonte. Se `/varrer` ou outra ferramenta de QA visual estiver disponível, rode antes do manifest final e **retente cada achado major/fatal uma vez** antes de finalizar.

### Disciplina dos buckets

- **`direct`** só para fontes fornecidas que já entregam depois de aperto de crop, conversão, compressão ou renomeação. Não entregue um crop pequeno do mockup de página inteira como `direct` só porque "parece perto".
- **Extração de textura/padrão** só quando a região-fonte já está limpa o bastante para amostrar. Se for preciso remover UI, cards, labels, headings, body copy ou chrome de rodapé para obter uma textura reutilizável, classifique como limpeza derivada de crop ou clean plate (`produce`).
- **`semantic`** para dashboards, gráficos, controles, screenshots de seções inteiras de UI, widgets de dados, chrome de card, molduras de app, toolbars de ícones, logos, wordmarks e tudo que a implementação final renderiza nítido em HTML/CSS/SVG/canvas. Só entregue screenshot como raster final quando isso for explicitamente declarado como o asset.
- **Semantic não é ignorado.** Cada papel semântico exige um handoff de implementação concreto para o Atelier: camadas DOM/componente, tratamento visual que o CSS possui, peças de SVG/canvas/biblioteca de ícones (a biblioteca única declarada no DESIGN.md — regra A5), comportamento responsivo conforme o registro da tela (LANDING/APP/DOCS), e quais rasters produzidos vizinhos ele compõe. Logos e ícones: prefira SVG inline/vetor ou biblioteca de ícones, salvo raster de produção fornecido.

### Transparência

Prefira alpha verdadeiro quando a ferramenta suporta. Se não suporta, peça fundo chroma-key chapado numa cor impossível de aparecer no sujeito e pós-processe essa cor para alpha antes de entregar PNG/WebP. **Nunca entregue o fundo keyed como asset final.**

## Padrão de prompt (image-to-image)

```text
Use o crop fornecido como referência visual aprovada.
Recrie o mesmo asset como imagem de produção limpa e reutilizável, no aspect ratio do componente-alvo e a no mínimo 2x a resolução de exibição.
Preserve silhueta, perspectiva do objeto/cena, ângulo de câmera, paleta, iluminação, material, textura e papel visual.
Remova texto de UI cozido, navegação, botões, labels, body copy, marcas d'água e chrome de mockup — salvo o que for explicitamente parte do asset.
Remova letterboxing, padding, bordas de card, clipping arredondado, sombras de CSS, transformações de perspectiva, faixas de legenda e fundos de layout que a implementação deve criar em código.
Não adicione objetos novos. Não mude o conceito. Não redesenhe a composição.
```

Para cutouts transparentes, use o fluxo chroma-key descrito acima, a menos que haja autorização explícita para fallback de transparência nativa.

## Contrato de saída

Devolva um **manifest completo**, agrupado por `produce`, `direct` e `semantic`.

| Linha de asset (`produce`/`direct`) | Linha semântica |
|---|---|
| `id` | `id` |
| `source_crop` | `implementation` |
| `output_path` (quando aplicável) | `notes` |
| `strategy` | `qa_status` |
| `prompt_used` (quando aplicável) | |
| `dimensions`, `format`, `transparency` | |
| `deviations`, `qa_status` | |

O campo `implementation` deve ser handoff de build concreto — nomeando as peças HTML/CSS/SVG/canvas/ícone/componente e as responsabilidades visuais que o código possui — nunca uma frase curta dizendo que nenhum asset foi produzido.

**`qa_status`** admite exatamente três valores:

- `accepted` — só depois da comparação visual passar.
- `needs_parent_review` — sujeito cortado, bordas ou chrome de card arredondado indesejados, letterboxing, texto semântico cozido, resolução baixa, perspectiva que deveria ser CSS, transparência faltante, ou drift em relação ao crop.
- `blocked` — entradas, permissões, capacidade de geração de imagem ou qualidade da fonte impedem um resultado crível.

Encerre com seções `execution_order`, `blockers` e `assumptions`. Blockers globais e mínimos: não repita entrada faltante em toda linha — linhas por asset carregam só riscos ou decisões específicos daquele asset.

## Do / Don't

| Faça | Não faça |
|---|---|
| Trabalhar só a partir do refinado aprovado e dos crops | Redesenhar composição, conceito ou paleta |
| Deixar raio/sombra/borda/perspectiva para o CSS (tokens do DESIGN.md) | Cozinhar chrome de apresentação no bitmap |
| Entregar ≥2x o tamanho de exibição | Entregar crop de mockup de página inteira como asset |
| Manter o diretório de assets só com arquivos do build | Misturar máscaras, referências e contact sheets no diretório final |
| Handoff concreto para cada papel `semantic` | Marcar como semantic e não dizer como construir |
| Perguntar blockers uma vez, globalmente | Bloquear por dimensão exata ou formato — isso tem default |
| Editar/gerar imagem só sobre cópias | Modificar o mockup aprovado ou código de implementação |
