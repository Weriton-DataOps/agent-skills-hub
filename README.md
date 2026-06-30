# agent-skills-hub

Biblioteca consolidada de **agentes** e **skills** para alimentar um orquestrador
multi-agente (ex.: o `Agent-SDK` / Pipeline Studio). Reúne, em um só lugar e **sem
redundância**, o conteúdo de três coleções públicas de skills.

## Estrutura

```
skills/        # 1451 skills únicas (deduplicadas por nome)
agents/
  researcher/  # agente de pesquisa (harness completo: discovery → rubrics → reports)
docs/
  FONTES.md            # de onde veio cada coisa + política de deduplicação
  METODO-CONSTRUCAO.md (na raiz) # método "visualização simples → avançada"
  indices/
    CATALOG.md         # catálogo das skills da antigravity
    skills_index.json  # índice machine-readable (para descoberta pelo orquestrador)
    marketplace.json   # agrupações em bundles/plugins (sem duplicar conteúdo)
  licenses/            # licenças das três fontes (atribuição)
```

## Política de deduplicação

As três fontes têm skills com o mesmo nome. Regra aplicada:

1. **Originais ganham.** As skills de `superpowers` e `Agent-Skills` (repos upstream
   mantidos) têm precedência sobre as cópias agregadas pela `antigravity`.
2. **antigravity preenche o resto** — só entram dela as skills cujo nome ainda não
   existia.
3. **Bundles/plugins da antigravity ficaram de fora** porque eram *cópias* das mesmas
   skills agrupadas (132 MB de redundância). As agrupações foram preservadas como
   índice em `docs/indices/marketplace.json` — sem duplicar o conteúdo.

Resultado: cada skill aparece **uma vez**.

## Como o orquestrador usa

- `skills/<nome>/SKILL.md` — cada skill é uma pasta autocontida; o orquestrador
  descobre pelo nome ou pelo `docs/indices/skills_index.json`.
- `agents/researcher/` — exemplo de agente completo (templates, rubrics, runbooks).
- `METODO-CONSTRUCAO.md` — o método de construção a ser seguido pelos agentes.

## Fontes e licenças

Conteúdo de terceiros — ver `docs/FONTES.md` e `docs/licenses/`. Repositório
**privado**; cada fonte mantém sua licença original.
