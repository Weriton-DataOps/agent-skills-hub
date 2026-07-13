# Método de Construção — o mandato de todo agente do OverCore

> Isto é o que o passo 2 da montagem de qualquer agente injeta (ver `docs/ORQUESTRACAO.md`):
> o **gate duro** que todo papel obedece, do croqui à validação. A `ORQUESTRACAO.md` descreve
> *a máquina* (como o agente é montado, roteado e qual modelo puxa); este documento descreve
> *o mandato* — como se constrói, com quais gates, e as regras que não se negociam.
>
> Regra-mãe: **o código é a etapa mais cara. Por isso é a penúltima, nunca a primeira.**

---

## 1. O gate duro (não-negociável)

Todo trabalho atravessa a mesma sequência. Cada 👤 **para e espera o "ok" humano** —
nenhum papel avança o `gate_state` sozinho.

```
  ideia
    → croqui        (simples, descartável)      👤  gate_state = croqui_aprovado
    → refinado      (alta fidelidade, mockup)   👤  gate_state = refinado_aprovado
    → código        (só depois do refinado)         em worktree, nunca no main
    → validação     (roda de verdade)               verdict: PASS | HUMAN_REVIEW | FAIL
    → PR                                         👤  merge é sempre humano
```

Pular da **ideia** direto para o **código** é a falha proibida. Quem constrói UI gera o
mockup, mostra, e só codifica depois do refinado aprovado.

---

## 2. As etapas (papel · skills · modelo · gate · evidência)

Os papéis, skills e tiers abaixo são os do roster canônico em `docs/ORQUESTRACAO.md`.
Skill = pasta `skills/<id>/SKILL.md`, descoberta pelo índice (nunca o hub inteiro; **N≤6**).

### 0 · Roteamento — **Router / Supervisor**
Única porta de entrada. Classifica o pedido em uma de 6 rotas (`design`, `codigo`,
`validacao`, `research`, `curate`, `contribuir`), monta o agente-alvo e é o **dono do
`gate_state`**. Não faz trabalho de domínio.
· **Modelo:** `claude-sonnet-4-6` → `claude-opus-4-8` só em ambiguidade/conflito de verdicts.
· **Evidência:** `runs/<id>/router.jsonl` com `{route, model_tier, skills[], gate_state}`.

### 1 · Descoberta & Plano — **Plan** (e **Researcher** para descoberta externa)
Entender antes de mexer; decompor tarefa grande em plano antes de executar.
· **Skills:** `writing-plans` (tarefas bite-sized, caminhos exatos, zero placeholder),
`brainstorming` quando o problema ainda é aberto (uma pergunta por vez, 2-3 abordagens + recomendação).
· **Saída:** plano em checkbox; nada de código ainda.

### 2 · Croqui — **Design (Atelier, modo croqui)**  👤
Esboço tosco: só estrutura, hierarquia e navegação. Serve para alinhar a ideia; joga-se
fora de graça. **Aqui se erra barato.**
· **Skills:** `brainstorming`, `frontend-design`.
· **Modelo:** `claude-haiku-4-5` (descartável). · **Verbos:** `/croqui`.
· **Gate:** aprovação humana → `gate_state = croqui_aprovado`.

### 3 · Refinado — **Design (Atelier, modo refinado)**  👤
O mesmo papel reentra em alta fidelidade: tipografia, cor, espaçamento, estado, animação.
Ainda é mockup (HTML/render no tema real), ainda não é o app. Passa pelas **30 verificações
anti-"cara de IA"**.
· **Skills:** `ui-ux-pro-max`, `frontend-design`, `theme-factory`.
· **Modelo:** `claude-sonnet-4-6`. · **Verbos:** `/refinar`, `/tipografar`, `/cor`, `/animar`,
`/polir`, e o par crítico `/criticar` + `/endurecer`.
· **Gate:** aprovação humana → `gate_state = refinado_aprovado`.

### 4 · Código — **Código**
Implementa **só** com `gate_state == refinado_aprovado`; recebe o `refinado.html` aprovado
como contexto fixo. Herda a stack do projeto.
· **Skills:** `test-driven-development` (o teste que falha primeiro), `clean-code`,
`writing-plans` + skills de stack por `category` (ex.: `react-best-practices`).
· **Modelo:** `claude-sonnet-4-6` → `claude-opus-4-8` se o Router marcar alto-risco.
· **Onde:** sempre em **worktree/branch**, nunca no `main`.

### 5 · Revisão dupla — **Código** (self) + especialistas  👤
Primeiro **bate com a spec** (nem a mais, nem a menos), depois **qualidade**. Só passa
quando as duas estão ✓.
· **Skills:** `differential-review`, `code-review-checklist`, `architect-review`, `code-reviewer`.
· **Segurança:** quando toca auth/input/endpoints, entra o **SafeGate** —
`backend-security-coder`, `security-auditor`, `api-security-best-practices`.
· **Regra dura — gerador ≠ juiz:** o modelo que escreveu (Sonnet) nunca julga a própria
saída; o juiz é `claude-opus-4-8`. Modelo barato nunca emite REJECT terminal — vira `HUMAN_REVIEW`.

### 6 · Validação — **Validação**
**Roda de verdade.** Executa app/teste, captura evidência (screenshot/log/exit-code), emite verdict.
"Passou nos testes" ≠ "o app funciona".
· **Skills:** `verification-before-completion`, `webapp-testing`, `code-review-checklist`.
· **Modelo:** `claude-sonnet-4-6` → `claude-opus-4-8` (+ `differential-review`,
`backend-security-coder`) quando toca segurança.
· **Evidência:** `runs/<id>/validation/`. · **Verdict:** `PASS | HUMAN_REVIEW | FAIL`.

### 7 · Fechamento — **PR**
O agente **prepara** o PR; **o merge é sempre humano**. Nenhum auto-merge, em lugar nenhum.

### 8 · Curadoria viva — **Curator** (o Forge)
Aprendizado reutilizável não morre no chat: vira skill-padrão. `/overcore contribuir <texto>`
→ Issue `contribution` → o Curator avalia pela rubric (gates **C1–C5**: acionável, genérico,
não-duplicado, seguro, formatado), rascunha o `SKILL.md` e abre PR → **você faz o merge**.
Fonte única: espelha o `agents/researcher/` e reusa `novelty_check.py`.

---

## 3. Regras de ouro (acima de qualquer skill)

Valem da primeira à última decisão, em todo papel:

1. **Decidir e mostrar > perguntar.** Recomende uma opção e **mostre** (mockup/resultado);
   pergunte só o que for genuinamente do usuário. Nada de lista de perguntas.
2. **Honestidade > otimismo.** Resultado negativo é resultado. Linguagem direta, sem maquiar.
3. **Evidência antes de alegação.** Não existe "pronto/passando" sem ter rodado e visto a saída.
4. **Qualidade desde a raiz.** Checar a entrada em todo nível desde o início, com **fonte única**
   de verdade — não empurrar para o fim.
5. **O que vai a produção só olha o passado.** Nada de vazamento do futuro no que decide ao vivo.
6. **Núcleo sagrado / aditivo.** Não invadir o que funciona — **envolver**, não reescrever.
   Mudança reversível.
7. **Modelo por tarefa (degraus duros).** Haiku (mecânico) → Sonnet (execução/refinado) →
   Opus (julgamento). Sobe só com gatilho concreto registrado no run; nunca "por segurança".
8. **Aprende com a própria produção.** Bug resolvido, atalho, jeito eficiente → registra
   (causa-raiz + correção) e reinjeta via curadoria. É o que mantém o hub vivo.
9. **Visualizar antes de construir.** O croqui→refinado não é enfeite; é o gate que troca
   retrabalho caro por iteração barata.
10. **Esgotar antes de trocar.** Fecha a tarefa com veredito honesto e só então abre a próxima.

---

## 4. Descoberta de skills (resumo)

A montagem nunca despeja as 1.400+ skills no contexto. Duas fases sobre
`docs/indices/skills_index.json`, sem gastar LLM: **(1)** filtro determinista por
`plugin.targets` (runtime) + `risk`; **(2)** seleção por `category` exata ou ranking lexical.
O agente carrega **no máximo 6**: as de papel-fixo + as que a tarefa pedir. Detalhe completo
em `docs/ORQUESTRACAO.md` → *Descoberta de skills*.

---

## 5. Por que este método funciona

Mexer num croqui custa segundos; refazer uma tela codada custa horas — então erra-se cedo e
barato. Separa-se **o quê** (estrutura, no croqui) do **como** (estética, no refinado): misturar
os dois é a origem do retrabalho. A validação roda de verdade, então "funciona" quer dizer
funciona. E cada lição volta pro hub — o sistema fica mais afiado a cada entrega, em vez de
repetir o mesmo erro no próximo projeto.
