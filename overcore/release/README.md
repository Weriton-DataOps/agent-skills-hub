# Overcore — Release candidate (PRB-016)

Snapshot **consumível pelo Studio**: o atualizador do Agent-SDK baixa este diretório por SHA de
commit exato, valida integralmente (manifesto, checksums, schema, resolução) e o instala no cache
versionado (`<userData>/overcore/versions/<sha>/`). Gerado de forma **determinística** a partir do
catálogo canônico (`overcore/catalog/`).

## Conteúdo

```
manifest.json            manifesto do release (SEM campo commit; NÃO se auto-hasheia)
catalog.json             catálogo PROMOVIDO (status draft → active) para uso em produção
catalog.schema.json      schema canônico (cópia)
skill-dependencies.json  projeção de dependências (cópia)
skills-meta.json         índice PODADO: só as skills referenciadas, com risco/runtime
skills/<id>/SKILL.md      cada SKILL.md referenciado pelo catálogo
```

## Manifesto

- `manifestFormatVersion`, `name`, `version` (0.3.0), `channel`, `minStudioVersion`;
- `catalog`/`catalogSchema`/`dependencies`/`skillsIndex`: caminhos relativos;
- `declarative[]`: todos os arquivos; `executable[]`: **vazio** (rejeitado na ativação);
- `checksums`: SHA-256 de **cada** arquivo declarativo (o manifesto **não** entra na própria tabela);
- `publishedAt`: **fixo** (determinismo); a identidade autoritativa do snapshot é o **SHA Git**.

## Geração / verificação

```bash
python gen_release.py           # (re)gera o release determinístico
python gen_release.py --check    # verifica sem escrever (!=0 se desatualizado)
python test_release.py           # testes do release/manifesto
```

## Promoção draft → active

O catálogo canônico (`overcore/catalog/catalog.json`) permanece `draft` (PRB-017A congelada). A
promoção para `active` acontece **apenas** neste release, após todas as validações — o resolvedor de
produção recusa uma entrada `draft` como agente ativo. A promoção é determinística e documentada;
não altera o catálogo de desenvolvimento.

## Publicação

Este release ainda **não está no remoto**. O atualizador só o consome quando o commit que o contém
existir no ref configurado (`stable → main`), em `overcore/release/manifest.json`. Até lá, a ativação
real fica gated (`canActivate=false`). Ver `Oracle/arquitetura/REGISTRO_PROBLEMAS.md` (PRB-016).

## Projeção de dependências podada (2026-07-30)

`skill-dependencies.json` do release é **podado** para as skills do release + suas dependências
transitivas (não é cópia do canônico). Cada entrada carrega o SHA-256 do `SKILL.md` incluído; o
atualizador confere presença + hash interno + transitivas e **falha fechado** em divergência. Para o
catálogo atual (skills-folha), a projeção é vazia — sem referência pendente a skills fora do release.
