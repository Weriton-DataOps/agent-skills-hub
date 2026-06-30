# Método de Construção — Visualização Simples → Avançada

> O jeito de construir software (e qualquer artefato visual) que deu certo no Pipeline Studio.
> Registrado aqui para ser reaproveitado pelo orquestrador e pelos agentes.

## Princípio

**Ver o visual antes de codar.** Nunca se implementa direto. Primeiro mostra-se o
resultado em baixo custo (mockup), aprova-se, e só então se gasta esforço de código.
Isso troca retrabalho caro (código) por iteração barata (croqui).

## As duas etapas da visualização

1. **Simples (croqui).** Um esboço rápido e tosco da tela/fluxo — só estrutura,
   hierarquia e navegação. Objetivo: alinhar a ideia, não impressionar. Baratíssimo
   de jogar fora. Aqui se erra de graça.
2. **Avançada (refinado).** Depois que o croqui é aprovado, evolui-se para o mockup
   de alta fidelidade — tipografia, cor, espaçamento, estados, animação. Ainda é
   mockup (HTML/render), ainda não é o app, mas já é o "como vai ficar".

Só depois do refinado aprovado é que o código entra.

## O loop (HARD-GATE)

```
ideia
  → croqui (simples)            ← mostra, ajusta, aprova
  → refinado (avançado)         ← mostra, ajusta, aprova
  → implementação (código)      ← só aqui se escreve o app
  → validação (roda de verdade) ← confere que funciona, não só que "passa nos testes"
```

Regra dura: **não pular do "ideia" para "implementação"**. O agente que constrói UI
deve gerar o mockup, renderizar para aprovação humana, e esperar o "ok" antes de
codar. É o gate de qualquer trabalho visual.

## Por que funciona

- **Erro barato no começo.** Mexer num croqui custa segundos; refazer uma tela
  codada custa horas.
- **Aprovação explícita por etapa.** Cada passo tem um "ok" humano — o agente nunca
  corre solto na direção errada.
- **Croqui → refinado separa decisões.** Primeiro decide-se *o quê* (estrutura),
  depois *como* (estética). Misturar os dois é o que gera retrabalho.
- **Validação real no fim.** Aprovar o visual não basta: o artefato roda e é
  observado funcionando.

## Como o orquestrador aplica

- Agente de **Design**: produz croqui → refinado (mockups HTML, tela por tela), com
  esquema de telas, árvore de navegação e histórico de versões.
- **Gate humano** entre design e código: o pipeline pausa e espera aprovação.
- Agente de **Código**: só recebe a tarefa depois do refinado aprovado.
- Agente de **Validação**: roda o resultado e confirma o comportamento.
