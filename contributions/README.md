# contributions/ — drop-zone de sugestões

Pasta onde **agentes** (o Pipeline Studio, ou o Claude trabalhando neste repo) largam
melhorias que descobrem, em **texto bruto**. Depois o **curador** (na máquina do mantenedor)
avalia com o juiz Opus e, se aprovar, vira skill válida pra todo mundo que usa o plugin.

```
agente acha melhoria  →  escreve .md em contributions/inbox/
        →  mantenedor roda o ciclo do curador  →  juiz Opus avalia  →  PR  →  merge  →  skill nova pra todos
```

## Como um agente contribui (o drop)

Escreva um arquivo `.md` em [`inbox/`](inbox/). Formato flexível:

```markdown
# Título curto da melhoria
origin: pipeline-studio:<nome-do-agente>
tags: nextjs, cache, deploy

<texto bruto: contexto, causa, como diagnosticar, como resolver, lição>
```

- A **primeira linha** vira o título; `origin:` e `tags:` são opcionais.
- **Não** coloque segredos/tokens/senhas — o curador barra, mas nem tente.

## Como o mantenedor processa

```
python agents/curator/scripts/run_cycle.py          # dry (inspeciona)
python agents/curator/scripts/run_cycle.py --live    # materializa skill + abre PR
```

O `run_cycle` ingere daqui **e** das GitHub Issues, roda triagem/dedup/juiz, e move os
arquivos processados para `processed/`.

## Dois canais, um curador

- **Esta pasta** — pros agentes que **têm o repo** (seu Pipeline Studio, sua máquina).
- **GitHub Issues** (label `contribution`) — pros usuários do plugin que **não têm o repo**.

Os dois caem no mesmo curador → mesmo juiz → mesmo merge humano.
