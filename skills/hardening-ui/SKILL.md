---
name: hardening-ui
description: "Endurece a UI contra o mundo real: expansão de texto/i18n, overflow, matriz HTTP→UI, duplo-submit e estados extremos. Aplicar antes do gate final do /varrer em qualquer tela que consuma dados de rede ou input de usuário."
risk: safe
source: "pbakaus/impeccable (Apache-2.0, modificado)"
date_added: "2026-07-02"
origin: impeccable
upstream: https://github.com/pbakaus/impeccable
attribution: "Derivado de skill/reference/harden.md — traduzido para PT-BR e adaptado ao pipeline do Atelier/OverCore. Arquivo modificado (Apache-2.0 §4b)."
---

# Hardening de UI — robustez de produção

Design que só funciona com dados perfeitos não está pronto para produção. Esta skill endurece a interface contra os inputs, erros, idiomas e condições de rede que usuários reais vão jogar nela. É a dimensão que o `/varrer` estético não cobre: a tela pode passar nas regras anti-slop e ainda quebrar no primeiro nome com 100 caracteres.

## Quando usar

- Como dimensão extra do `/varrer` (etapa 5 do Atelier), antes do gate `refinado_aprovado` — especialmente em registro **APP/DASHBOARD**, onde dados de rede e formulários são a regra.
- Ao revisar qualquer peça que renderize conteúdo dinâmico: listas, tabelas, cards com texto de usuário, formulários, telas dependentes de API.
- Antes de internacionalizar ou de lançar para produção. Se a resposta a "o que acontece quando a API cai?" for silêncio, rode esta skill.

## 1. Diagnóstico — onde a interface quebra

Teste sistematicamente três frentes antes de corrigir qualquer coisa:

**Inputs extremos:**
- Texto muito longo (nomes, descrições, títulos)
- Texto muito curto (vazio, um único caractere)
- Caracteres especiais (emoji, texto RTL, acentos)
- Números grandes (milhões, bilhões)
- Muitos itens (1000+ itens de lista, 50+ opções)
- Nenhum dado (empty states)

**Cenários de erro:**
- Falhas de rede (offline, lenta, timeout)
- Erros de API (400, 401, 403, 404, 500)
- Erros de validação
- Erros de permissão
- Rate limiting
- Operações concorrentes

**Internacionalização:**
- Traduções longas (alemão costuma ser ~30% mais longo que inglês)
- Idiomas RTL (árabe, hebraico)
- Conjuntos de caracteres (chinês, japonês, coreano, emoji)
- Formatos de data/hora
- Formatos de número (1,000 vs 1.000)
- Símbolos de moeda

**CRÍTICO:** endureça contra a realidade, não contra o dado de demonstração do croqui.

## 2. Overflow e quebra de texto

**Texto longo — três estratégias, escolha por peça:**

```css
/* Linha única com reticências */
.truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Multilinha com clamp */
.line-clamp {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Permitir quebra */
.wrap {
  word-wrap: break-word;
  overflow-wrap: break-word;
  hyphens: auto;
}
```

**Overflow em flex/grid** — a causa nº 1 de layout estourado com conteúdo real:

```css
/* Itens flex: permitir encolher abaixo do tamanho do conteúdo */
.flex-item {
  min-width: 0;
  overflow: hidden;
}

/* Itens grid: idem, nos dois eixos */
.grid-item {
  min-width: 0;
  min-height: 0;
}
```

**Texto responsivo:**
- Use `clamp()` para tipografia fluida — sempre dentro da escala do DESIGN.md (regra A8)
- Tamanho mínimo legível: **14px no mobile**
- Teste com zoom de texto a **200%**
- Containers devem expandir com o texto, nunca cortá-lo

## 3. Internacionalização (i18n)

**Expansão de texto:**
- Reserve **30–40% de espaço extra** para traduções
- Use flexbox/grid que se adapta ao conteúdo
- Teste com o idioma mais longo (geralmente alemão)
- Nunca largura fixa em container de texto

```jsx
// ❌ Ruim: assume texto curto em inglês
<button className="w-24">Enviar</button>

// ✅ Bom: adapta-se ao conteúdo
<button className="px-4 py-2">Enviar</button>
```

**Suporte RTL (right-to-left):**

```css
/* Propriedades lógicas em vez de físicas */
margin-inline-start: 1rem;   /* não margin-left */
padding-inline: 1rem;        /* não padding-left/right */
border-inline-end: 1px solid; /* não border-right */

/* Ou via atributo dir */
[dir="rtl"] .arrow { transform: scaleX(-1); }
```

**Conjuntos de caracteres:**
- UTF-8 em tudo
- Teste com caracteres CJK (chinês/japonês/coreano)
- Teste com emoji (ocupam 2–4 bytes)
- Considere scripts diferentes (latino, cirílico, árabe etc.)

**Data, hora e número — sempre via Intl:**

```javascript
new Intl.DateTimeFormat('pt-BR').format(date); // 15/01/2024
new Intl.DateTimeFormat('de-DE').format(date); // 15.1.2024

new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: 'BRL'
}).format(1234.56); // R$ 1.234,56
```

**Pluralização:**

```javascript
// ❌ Ruim: assume regra de plural do português/inglês
`${count} ite${count !== 1 ? 'ns' : 'm'}`

// ✅ Bom: biblioteca de i18n com regras de plural por idioma
t('items', { count })
```

## 4. Matriz HTTP → UI

Cada status de API tem uma resposta de interface obrigatória. "Ocorreu um erro" genérico é reprovação.

| Status | Resposta na UI |
|---|---|
| 400 | Mostrar erros de validação campo a campo |
| 401 | Redirecionar para login |
| 403 | Estado de permissão negada, com explicação do porquê |
| 404 | Estado de "não encontrado" com próxima ação |
| 429 | Mensagem de rate limit (quando tentar de novo) |
| 500 | Erro genérico + caminho de suporte/retry |

**Erros de rede:**
- Mensagem clara do que aconteceu
- Botão de retry sempre presente
- Tratar timeout explicitamente
- Modo offline quando fizer sentido

```jsx
// Estado de erro com recuperação
{error && (
  <ErrorMessage>
    <p>Falha ao carregar os dados. {error.message}</p>
    <button onClick={retry}>Tentar novamente</button>
  </ErrorMessage>
)}
```

**Erros de formulário:**
- Erro inline, junto do campo
- Mensagem específica, com sugestão de correção
- Nunca descartar o que o usuário digitou ao errar
- Não bloquear a submissão sem necessidade

**Degradação graciosa:**
- Funcionalidade central sobrevive sem JavaScript
- Toda imagem tem alt text
- Progressive enhancement; fallback para features não suportadas
- Erro em um componente nunca derruba a interface inteira

## 5. Estados extremos

**Empty states** — cada um com próxima ação clara:
- Lista sem itens
- Busca sem resultados
- Nenhuma notificação
- Nenhum dado a exibir

**Loading states:**
- Carga inicial, paginação e refresh são estados distintos
- Diga *o que* está carregando ("Carregando seus projetos…")
- Estimativa de tempo em operações longas

**Datasets grandes:**
- Paginação ou virtual scrolling — nunca renderize 10.000 itens de uma vez
- Busca/filtro disponíveis
- Teste com **1000+ itens**, não com os 5 do mock

**Operações concorrentes (duplo-submit):**
- Desabilite o botão enquanto a requisição roda — é a defesa mínima contra duplo-submit
- Trate race conditions
- Update otimista só com rollback previsto
- Resolução de conflito quando dois clientes editam o mesmo dado

**Estados de permissão:**
- Sem permissão para ver / sem permissão para editar / modo somente-leitura
- Sempre com explicação clara do motivo

**Compatibilidade de navegador:**
- Feature detection, nunca browser detection
- Fallback para CSS não suportado; polyfill quando indispensável
- Teste nos navegadores-alvo do projeto

## 6. Validação de input

**Client-side (experiência):**
- Campos obrigatórios, formato (email, telefone, URL), limites de tamanho, pattern

**Server-side (segurança — sempre):**
- Nunca confie só no client
- Valide e sanitize todo input; proteja contra injeção; rate limiting

**Restrições declaradas no próprio campo:**

```html
<input
  type="text"
  maxlength="100"
  pattern="[A-Za-z0-9]+"
  required
  aria-describedby="username-hint"
/>
<small id="username-hint">
  Somente letras e números, até 100 caracteres
</small>
```

## 7. Resiliência de acessibilidade

Complementa a regra A11 do Atelier (contraste calculado) — aqui o foco é sobreviver a modos de uso não-padrão:

- **Teclado:** toda funcionalidade acessível sem mouse; tab order lógico; foco gerenciado em modais; skip links em conteúdo longo.
- **Leitor de tela:** ARIA correto; mudanças dinâmicas anunciadas via live regions; HTML semântico.
- **Sensibilidade a movimento:**

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

- **Alto contraste:** teste no modo de alto contraste do Windows; nunca dependa só de cor — dê pista visual alternativa.

## 8. Resiliência de performance

- **Conexão lenta:** skeleton screens, carregamento progressivo de imagem, UI otimista, offline via service worker quando o produto pedir.
- **Vazamento de memória:** limpe event listeners, cancele subscriptions, limpe timers e aborte requests pendentes no unmount.
- **Throttle/debounce:**

```javascript
const debouncedSearch = debounce(handleSearch, 300); // busca
const throttledScroll = throttle(handleScroll, 100); // scroll
```

## 9. Como testar

**Manual:**
- Dados extremos (muito longo, muito curto, vazio)
- Idiomas diferentes
- Offline e conexão lenta (throttle para 3G)
- Leitor de tela e navegação só por teclado
- Navegadores antigos do alvo do projeto

**Automatizado:**
- Testes unitários para edge cases
- Testes de integração para cenários de erro
- E2E nos caminhos críticos
- Regressão visual
- Acessibilidade (axe, WAVE)

**IMPORTANTE:** hardening é esperar o inesperado. Usuários reais fazem coisas que ninguém imaginou.

## 10. NUNCA

- Assumir input perfeito (valide tudo)
- Ignorar i18n (projete para o mundo)
- Deixar mensagem de erro genérica ("Ocorreu um erro")
- Esquecer o cenário offline
- Confiar só em validação client-side
- Usar largura fixa para texto
- Assumir texto do tamanho do inglês
- Bloquear a interface inteira quando um componente falha

## 11. Checklist de verificação

Marque cada linha antes de liberar o gate:

- [ ] **Texto longo** — nomes com 100+ caracteres não estouram nada
- [ ] **Emoji** — emoji em todos os campos de texto renderiza sem quebrar
- [ ] **RTL** — testado com árabe ou hebraico
- [ ] **CJK** — testado com chinês/japonês/coreano
- [ ] **Rede** — internet desligada e conexão throttled não deixam a tela muda
- [ ] **Volume** — 1000+ itens sem colapso de layout ou performance
- [ ] **Duplo-submit** — clicar em enviar 10 vezes seguidas gera UMA operação
- [ ] **Erros** — todos os status da matriz HTTP→UI forçados e verificados
- [ ] **Vazio** — todos os empty states vistos com dados zerados

## Integração com o Atelier

- Rode como dimensão extra do `/varrer` na etapa 5; violações entram na mesma lista peça→regra, e peça reprovada volta ao artesão sem incomodar o humano.
- Peso por **registro**: em APP/DASHBOARD, tudo aqui é bloqueante; em LANDING, priorize i18n/overflow e a matriz HTTP dos formulários (contato, signup); em DOCS/FORM, priorize validação e estados de erro inline.
- Estados de erro, loading e empty usam exclusivamente tokens do DESIGN.md — cor semântica de erro nunca vira decoração (regra A13) e valor novo só entra como token aprovado (A18).
- Coberto o checklist, siga para `/polir` — o passe final de alinhamento e estados.

---

*Derivado de `skill/reference/harden.md` do projeto [pbakaus/impeccable](https://github.com/pbakaus/impeccable) (Apache-2.0). Este arquivo foi modificado: traduzido para PT-BR e adaptado ao pipeline do Atelier/OverCore.*
