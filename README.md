# OverCore

> **Orquestrador multi-agente + hub vivo de skills de desenvolvimento.**
> O núcleo que fica acima de todos os agentes e unifica a inteligência deles num só padrão.

O **OverCore** reúne uma biblioteca curada de **1473 skills** e **agentes**, e um ciclo
que a mantém **viva**: cada bug resolvido, atalho ou jeito eficiente de trabalhar que um
agente ou dev descobre pode virar uma skill-padrão, reutilizável por todo mundo.

Dois consumidores leem o mesmo hub:

- **Pipeline Studio** (o sistema orquestrador / Agent-SDK) — monta agentes em runtime.
- **VS Code** — instale o plugin e use **`/overcore`** em qualquer projeto.

## Instalar (plugin do Claude Code)

No Claude Code, em qualquer projeto:

```
/plugin marketplace add Weriton-DataOps/agent-skills-hub
/plugin install overcore@overcore-hub
```

Depois, em qualquer projeto:

| Comando | O que faz |
|---|---|
| `/overcore usar <tarefa>` | descobre e aplica skills do hub na sua tarefa |
| `/overcore contribuir <texto>` | registra um fix/atalho → vira skill após revisão |
| `/overcore status` | mostra as contribuições pendentes |

> Requer o repositório **público**. Contribuir usa a **sua própria conta** do GitHub
> (`gh auth login`) — nenhum token compartilhado é distribuído.

## Como funciona (visão de 10 segundos)

```
descobre um fix/atalho  →  Issue (texto bruto, label: contribution)
        →  Curator avalia + deduplica + rascunha SKILL.md  →  abre PR
        →  VOCÊ faz o merge  →  vira padrão  →  volta pros dois consumidores
```

Ninguém recebe acesso de escrita ao git — quem escreve é um token-robô. **Merge é sempre humano.**
Arquitetura completa em [`docs/ORQUESTRACAO.md`](docs/ORQUESTRACAO.md).

## Estrutura

```
skills/            # 1473 skills; cada uma uma pasta com SKILL.md
agents/
  researcher/      # agente de descoberta externa (papers, posts → skills)
  curator/         # agente de descoberta interna (contribuições → skills)  [o "OverCore Forge"]
docs/
  ORQUESTRACAO.md        # como agentes × skills × instruções × modelos de IA se orquestram
  CONTRIBUTING-INTAKE.md # como uma contribuição entra (Issues → curador → PR)
  indices/
    skills_index.json    # índice machine-readable (descoberta pelo orquestrador)
    marketplace.json     # agrupações em bundles
    CATALOG.md           # catálogo legível
  licenses/              # licenças-base das skills de terceiros (atribuição)
METODO-CONSTRUCAO.md     # o método croqui → refinado → código → validação (gate humano)
NOTICE.md                # atribuições de terceiros (discreto)
```

## Como o orquestrador usa

- `skills/<nome>/SKILL.md` — cada skill é autocontida; descoberta por nome ou pelo
  `docs/indices/skills_index.json` (que traz `risk`, `category` e `targets` de IA por skill).
- `agents/curator/` — o motor que transforma contribuição bruta em skill-padrão
  (ver [`agents/curator/README.md`](agents/curator/README.md)).
- `METODO-CONSTRUCAO.md` — o método de construção seguido pelos agentes.

## Deduplicação

As skills que compõem a biblioteca podiam se sobrepor por nome. Regra aplicada: **cada
skill aparece uma única vez** — versões originais mantidas têm precedência sobre cópias
agregadas, e agrupamentos/bundles ficaram só como índice em `docs/indices/marketplace.json`
(sem duplicar conteúdo). Detalhes em [`docs/FONTES.md`](docs/FONTES.md).

## Licença

- **Código e ferramentas do OverCore:** MIT — ver [`LICENSE`](LICENSE).
- **Conteúdo original do OverCore** (skills/métodos/docs próprios): CC BY-SA 4.0 —
  ver [`LICENSE-CONTENT`](LICENSE-CONTENT).
- **Skills de terceiros:** mantêm licença e autoria originais — ver [`NOTICE.md`](NOTICE.md)
  e `docs/licenses/`.
