---
name: design-critique
description: "Crítica de design pontuada: rubrica Nielsen 0-40 com âncoras por heurística, checklist de carga cognitiva, personas de teste e severidade P0-P3, com tendência de score entre execuções. Use quando precisar de avaliação honesta, comparável e acionável de uma interface."
risk: safe
source: "pbakaus/impeccable (Apache-2.0, modificado)"
date_added: "2026-07-02"
origin: impeccable
upstream: https://github.com/pbakaus/impeccable
attribution: "Derivado de skill/reference/critique.md — traduzido para PT-BR e adaptado ao pipeline do Atelier/OverCore. Arquivo modificado (Apache-2.0 §4b)."
---

# Crítica de design pontuada

## Quando usar

- Antes ou depois do gate de revisão do Atelier (`/varrer`), quando a pergunta não é "quais regras violou?" mas **"quão bom isso é, e o que atacar primeiro?"**.
- Para medir progresso: a mesma rubrica aplicada em execuções sucessivas produz uma tendência de score comparável.
- Em interface herdada (não nascida no wizard) que precisa de diagnóstico antes de qualquer redesign.

Não use para auditoria de regra determinística pura — isso é o `/varrer`. A crítica **consome** o resultado do `/varrer` como evidência, mas o produto dela é julgamento pontuado + plano priorizado.

---

## Método: duas avaliações independentes

O viés de ancoragem é o inimigo. Rode duas avaliações que **não veem o resultado uma da outra** antes da síntese:

- **Avaliação A — revisão de design**: julgamento de diretor de arte sobre o alvo (fonte + página renderizada quando houver navegador). Cobre slop, hierarquia, heurísticas, carga cognitiva, jornada emocional, personas.
- **Avaliação B — evidência determinística**: as regras anti-slop do registro (`/varrer`: A1–A18 + contraste calculado + checklist de estados), com contagens e localização peça→regra. Se houver navegador, inspecione a página real — screenshot não lido não conta.

Regras duras:

1. A Avaliação A fecha **antes** de qualquer achado determinístico entrar no contexto da síntese. Evidência determinística é confiável, mas ancora o julgamento.
2. Se houver ferramenta de subagente, rode A e B como dois subagentes isolados e paralelos. Sem subagentes, rode sequencial: termine e registre A, depois rode B.
3. Rodou tudo num contexto só? A **primeira linha** do relatório declara: `⚠️ DEGRADADO: contexto único (<motivo>)`. Crítica degradada silenciosa é crítica falhada.
4. Alvo visualizável exige inspeção renderizada quando houver navegador disponível. Prefira caminho de fonte a URL de dev-server quando ambos identificam a mesma tela — portas mudam, paths não.
5. Pular a Avaliação B só é aceitável se não houver como executá-la; registre o motivo concreto.

### O que a Avaliação A devolve

- Veredito de AI-slop: alguém acreditaria "IA fez isso" de imediato? (estética geral, mesmice de layout, composição genérica, personalidade desperdiçada)
- Score 0–4 nas 10 heurísticas de Nielsen (rubrica abaixo)
- Falhas do checklist de carga cognitiva + pontos de decisão com >4 opções visíveis
- Jornada emocional: regra pico-fim, vales emocionais, reasseguramento em momentos de risco
- 2–3 pontos fortes, 3–5 problemas prioritários, red flags por persona, observações menores, perguntas provocativas

### O que a Avaliação B devolve

- Violações peça→regra com contagens e localização em arquivo
- Falsos positivos identificados
- Passos de inspeção pulados/falhados com o motivo concreto

Na síntese, **não concatene**: teça os achados — onde A e B concordam, o que o determinístico pegou que o julgamento perdeu, e quais achados determinísticos são falsos positivos.

---

## Rubrica Nielsen — 10 heurísticas, 0–4 cada

Seja honesto: **4 significa genuinamente excelente**, não "bom o suficiente". A maioria das interfaces reais pontua 20–32.

### 1. Visibilidade do status do sistema
Verifique: indicador de loading em operações assíncronas; confirmação de ações (salvar, enviar, excluir); progresso em fluxos multi-etapa; localização atual na navegação; validação de formulário inline (não só no submit).

| Score | Critério |
|-------|----------|
| 0 | Nenhum feedback; usuário adivinha o que aconteceu |
| 1 | Feedback raro; a maioria das ações não produz resposta visível |
| 2 | Parcial; alguns estados comunicados, lacunas grandes |
| 3 | Bom; a maioria das operações dá feedback claro, lacunas menores |
| 4 | Excelente; toda ação confirma, progresso sempre visível |

### 2. Correspondência com o mundo real
Verifique: terminologia familiar (sem jargão inexplicado); ordem de informação natural; ícones e metáforas reconhecíveis; linguagem adequada ao público do PRODUCT.md; fluxo de leitura natural.

| Score | Critério |
|-------|----------|
| 0 | Jargão técnico puro, alienígena para o usuário |
| 1 | Majoritariamente confuso; exige expertise de domínio |
| 2 | Misto; linguagem simples com vazamentos de jargão |
| 3 | Quase natural; termo ocasional precisa de contexto |
| 4 | Fala a língua do usuário fluentemente, do início ao fim |

### 3. Controle e liberdade do usuário
Verifique: undo/redo; botão cancelar em formulários e modais; navegação de volta clara; limpar filtros/busca/seleções fácil; escape de processos longos.

| Score | Critério |
|-------|----------|
| 0 | Usuário fica preso; só sai com refresh |
| 1 | Saídas difíceis; caminhos obscuros para escapar |
| 2 | Algumas saídas; fluxo principal escapa, casos de borda não |
| 3 | Bom controle; sai e desfaz a maioria das ações |
| 4 | Controle total; undo, cancelar, voltar e escape em tudo |

### 4. Consistência e padrões
Verifique: terminologia consistente; mesma ação → mesmo resultado em todo lugar; convenções de plataforma; consistência visual (cor, tipografia, espaçamento — os tokens do DESIGN.md); padrões de interação uniformes.

| Score | Critério |
|-------|----------|
| 0 | Inconsistente em tudo; parece produtos diferentes costurados |
| 1 | Muitas inconsistências; coisas similares se comportam diferente |
| 2 | Parcial; fluxos principais batem, detalhes divergem |
| 3 | Quase consistente; desvio ocasional, nada confuso |
| 4 | Totalmente consistente; sistema coeso, comportamento previsível |

### 5. Prevenção de erros
Verifique: confirmação antes de ação destrutiva; restrições que impedem input inválido (date picker, dropdown); defaults inteligentes; rótulos que previnem mal-entendido; autosave/recuperação de rascunho.

| Score | Critério |
|-------|----------|
| 0 | Errar é fácil; nenhuma proteção |
| 1 | Poucas salvaguardas; pouca validação de input |
| 2 | Prevenção parcial; erros comuns pegos, bordas escapam |
| 3 | Boa prevenção; maioria dos caminhos de erro bloqueados |
| 4 | Excelente; erro quase impossível via restrições inteligentes |

### 6. Reconhecimento em vez de memorização
Verifique: opções visíveis (não enterradas em menus); ajuda contextual (tooltip, dica inline); itens recentes/histórico; autocomplete; rótulos em ícones (nunca navegação icon-only).

| Score | Critério |
|-------|----------|
| 0 | Memorização pesada; usuário decora caminhos e comandos |
| 1 | Quase tudo por recall; features escondidas, poucas pistas |
| 2 | Alguns auxílios; ações principais visíveis, secundárias ocultas |
| 3 | Bom reconhecimento; quase tudo descobrível |
| 4 | Tudo descobrível; usuário nunca precisa decorar |

### 7. Flexibilidade e eficiência de uso
Verifique: atalhos de teclado; elementos customizáveis; recentes/favoritos; ações em lote; recursos avançados que não complicam o básico.

| Score | Critério |
|-------|----------|
| 0 | Um caminho rígido; sem atalhos ou alternativas |
| 1 | Flexibilidade limitada; poucas alternativas |
| 2 | Alguns atalhos; teclado básico, lote limitado |
| 3 | Bons aceleradores; navegação por teclado, alguma customização |
| 4 | Altamente flexível; múltiplos caminhos, power features |

### 8. Design estético e minimalista
Verifique: só o necessário visível em cada passo; hierarquia visual clara; cor e ênfase com propósito; sem clutter decorativo competindo por atenção; layouts focados.

| Score | Critério |
|-------|----------|
| 0 | Esmagador; tudo compete por atenção igualmente |
| 1 | Poluído; muito ruído, difícil achar o que importa |
| 2 | Algum clutter; conteúdo principal claro, periferia ruidosa |
| 3 | Quase limpo; design focado, ruído visual menor |
| 4 | Perfeitamente mínimo; cada elemento merece seu pixel |

### 9. Reconhecer, diagnosticar e recuperar de erros
Verifique: mensagens em linguagem simples (sem código de erro para usuário); problema apontado com precisão ("Email sem @", não "Input inválido"); sugestão acionável de recuperação; erro exibido perto da origem; tratamento não-bloqueante (não apagar o formulário).

| Score | Critério |
|-------|----------|
| 0 | Erros crípticos; código, jargão ou mensagem nenhuma |
| 1 | Erros vagos; "algo deu errado" sem direção |
| 2 | Claro mas inútil; nomeia o problema, não o conserto |
| 3 | Claro com sugestão; identifica e oferece próximo passo |
| 4 | Recuperação perfeita; aponta, sugere e preserva o trabalho |

### 10. Ajuda e documentação
Verifique: ajuda buscável; ajuda contextual (tooltip, dica inline, tour); organização por tarefa (não por feature); conteúdo conciso e escaneável; acesso sem sair do contexto.

| Score | Critério |
|-------|----------|
| 0 | Nenhuma ajuda disponível |
| 1 | Ajuda existe mas é difícil de achar ou irrelevante |
| 2 | Básica; FAQ/docs existem, não contextual |
| 3 | Boa documentação; buscável, orientada a tarefa |
| 4 | Ajuda contextual excelente; a informação certa na hora certa |

### Faixas do score total (máx. 40)

| Faixa | Classificação | Significado |
|-------|---------------|-------------|
| 36–40 | Excelente | Só polimento; pode lançar |
| 28–35 | Bom | Atacar áreas fracas; fundação sólida |
| 20–27 | Aceitável | Melhorias significativas antes de usuários felizes |
| 12–19 | Ruim | Overhaul de UX; experiência central quebrada |
| 0–11 | Crítico | Redesign; inutilizável no estado atual |

---

## Severidade por problema — P0–P3

Todo problema individual do relatório recebe uma etiqueta:

| Prioridade | Nome | Descrição | Ação |
|-----------|------|-----------|------|
| **P0** | Bloqueante | Impede completar a tarefa | Corrigir imediatamente; showstopper |
| **P1** | Grave | Dificuldade ou confusão significativa | Corrigir antes do release |
| **P2** | Menor | Incômodo, mas há contorno | Corrigir na próxima passada |
| **P3** | Polimento | Bom corrigir, sem impacto real | Se sobrar tempo |

**Desempate**: "o usuário abriria chamado no suporte por isso?" Se sim, é no mínimo P1.

---

## Carga cognitiva

Três tipos: **intrínseca** (a tarefa em si — estruture com passos, defaults e divulgação progressiva, não dá pra eliminar), **extrínseca** (design ruim — **elimine sem dó**, é puro desperdício) e **germânica** (esforço de aprendizado — carga *boa*, apoie com padrões consistentes e feedback).

### Checklist (8 itens)

- [ ] **Foco único**: a tarefa principal completa sem distração de elementos concorrentes?
- [ ] **Chunking**: informação em grupos digeríveis (≤4 itens por grupo)?
- [ ] **Agrupamento**: itens relacionados agrupados visualmente (proximidade, borda, fundo)?
- [ ] **Hierarquia visual**: o mais importante da tela é óbvio de imediato?
- [ ] **Uma coisa por vez**: uma decisão de cada vez antes da próxima?
- [ ] **Escolhas mínimas**: ≤4 opções visíveis em cada ponto de decisão?
- [ ] **Memória de trabalho**: o usuário precisa lembrar algo de uma tela anterior para agir na atual?
- [ ] **Divulgação progressiva**: complexidade revelada só quando necessária?

**Pontuação**: conte as falhas. 0–1 = carga baixa (bom). 2–3 = moderada (atacar em breve). 4+ = alta (correção crítica).

### Regra da memória de trabalho (≤4 itens)

Humanos seguram ≤4 itens na memória de trabalho (Miller revisado por Cowan, 2001). Em cada ponto de decisão, conte opções/ações/informações simultâneas: **≤4** ok; **5–7** no limite — agrupe ou revele progressivamente; **8+** sobrecarga — usuário pula, erra clique ou abandona.

Aplicações práticas: navegação ≤5 itens de topo; ≤4 campos visíveis por grupo de formulário; 1 botão primário + 1–2 secundários (resto em menu — coerente com a A16 do `/varrer`); ≤4 métricas-chave visíveis sem scroll em dashboard; ≤3 tiers de preço.

### Violações comuns

| Violação | Problema | Fix |
|----------|----------|-----|
| Muro de opções | 10+ escolhas de uma vez, sem hierarquia | Categorizar, destacar recomendada, revelar progressivamente |
| Ponte de memória | Lembrar do passo 1 para completar o passo 3 | Manter contexto visível ou repetir onde é usado |
| Navegação oculta | Usuário constrói mapa mental do sistema | Mostrar sempre a localização (breadcrumb, estado ativo, progresso) |
| Barreira de jargão | Linguagem técnica força tradução | Linguagem simples; termo de domínio inevitável se define inline |
| Piso de ruído visual | Tudo com o mesmo peso; nada se destaca | 1 elemento primário, 2–3 secundários, resto silenciado |
| Padrão inconsistente | Ações similares funcionam diferente em lugares diferentes | Padronizar: mesmo tipo de ação = mesmo tipo de UI |
| Demanda multitarefa | Ler + decidir + navegar simultaneamente | Sequenciar; uma coisa por vez |
| Troca de contexto | Pular entre telas/abas para uma decisão só | Co-locar a informação de cada decisão |

---

## Personas de teste

Selecione **2–3 personas** conforme o tipo de interface (tabela abaixo). Percorra a ação principal do usuário como cada persona e reporte red flags **específicos** — nomeie o elemento e a interação que falhou, nunca descrição genérica.

**Alex — power user impaciente.** Expert em produtos similares; pula onboarding, procura atalhos, abandona o que parece lento ou paternalista.
- Testes: completa a tarefa central em <60 segundos? Há atalhos de teclado? Onboarding é pulável? Modal fecha com Esc? Existe caminho power (lote, atalhos)?
- Red flags: tutorial forçado; sem navegação por teclado nas ações primárias; animação lenta não pulável; fluxo um-item-por-vez onde lote seria natural; confirmação redundante em ação de baixo risco.

**Jordan — iniciante confuso.** Nunca usou esse tipo de produto; lê tudo, hesita antes de clicar, interpreta rótulos ao pé da letra, abandona em vez de decifrar.
- Testes: a primeira ação é óbvia em 5 segundos? Todo ícone tem rótulo? Há ajuda contextual nos pontos de decisão? A terminologia pressupõe conhecimento prévio? Há "voltar"/"desfazer" em cada passo?
- Red flags: navegação icon-only; jargão técnico sem explicação; nenhuma ajuda visível; próximo passo ambíguo após concluir ação; nenhuma confirmação de sucesso.

**Sam — usuário dependente de acessibilidade.** Leitor de tela (VoiceOver/NVDA), navegação só por teclado; pode ter baixa visão, limitação motora, zoom até 200%.
- Testes: fluxo principal completo só no teclado? Elementos interativos focáveis com indicador de foco visível? Imagens com alt significativo? Contraste WCAG AA (4.5:1 em texto — a A11 do `/varrer` mede)? Leitor de tela anuncia mudanças de estado (loading, sucesso, erro)?
- Red flags: interação só por clique; foco invisível; significado só por cor (vermelho=erro); campo/botão sem rótulo; ação com limite de tempo sem extensão; componente custom que quebra o leitor de tela.

**Riley — estressador deliberado.** Metódico; testa bordas (0 itens, 1000 itens, strings longas), inputs inesperados (emoji, RTL, colar do Excel), refresh no meio do fluxo, múltiplas abas.
- Testes: o que acontece nas bordas? Estado de erro recupera ou quebra a UI? Refresh no meio do fluxo preserva estado? Alguma feature parece funcionar mas produz resultado quebrado?
- Red flags: falha silenciosa; erro que expõe detalhe técnico ou deixa a UI quebrada; empty state inútil ("Sem resultados" sem orientação); perda de dados em refresh/navegação; comportamento inconsistente entre interações similares.

**Casey — mobile distraído.** Uma mão, polegar só, interrompido o tempo todo, conexão possivelmente lenta; digita o mínimo.
- Testes: ações primárias na zona do polegar (metade inferior)? Estado preservado ao sair e voltar? Funciona em 3G? Formulários com autocomplete e defaults? Alvos de toque ≥44×44pt?
- Red flags: ação importante no topo (fora do polegar); sem persistência de estado; input de texto grande onde seleção resolveria; assets pesados sem lazy loading; alvos minúsculos ou colados.

### Seleção por tipo de interface (alinhe ao registro da tela)

| Tipo de interface | Personas primárias | Por quê |
|-------------------|--------------------|---------|
| Landing / marketing (registro LANDING) | Jordan, Riley, Casey | Primeira impressão, confiança, mobile |
| Dashboard / admin (registro APP) | Alex, Sam | Power users, acessibilidade |
| E-commerce / checkout | Casey, Riley, Jordan | Mobile, bordas, clareza |
| Fluxo de onboarding | Jordan, Casey | Confusão, interrupção |
| Dados densos / analytics (registro APP) | Alex, Sam | Eficiência, teclado |
| Formulários / wizard (registro DOCS/FORM) | Jordan, Sam, Casey | Clareza, acessibilidade, mobile |

Se o PRODUCT.md descreve um público que nenhuma das 5 cobre, derive 1–2 personas do projeto (perfil em 2–3 características, 3–4 comportamentos, 3–4 red flags que alienariam esse usuário). Não invente detalhes de audiência sem dado real; sem contexto, fique nas 5.

---

## Estrutura do relatório

A resposta no chat é a entrega principal — relatório completo, não resumo com link. Ordem:

1. **Proveniência** (primeira linha): `Método: dual-agent (A: <id> · B: <id>)` ou `⚠️ DEGRADADO: contexto único (<motivo>)`.
2. **Score de saúde**: tabela das 10 heurísticas (`# | Heurística | Score | Problema-chave`), com total `??/40` e a faixa de classificação. Heurística sólida recebe "n/a" no problema-chave.
3. **Veredito anti-padrões** (comece por aqui): parece gerado por IA? Julgamento próprio (estética, mesmice, personalidade) + resumo da varredura determinística com contagens e localizações, marcando o que o determinístico pegou a mais e os falsos positivos.
4. **Impressão geral**: reação sincera — o que funciona, o que não, e a maior oportunidade única.
5. **O que está funcionando**: 2–3 acertos, com o porquê específico.
6. **Problemas prioritários**: os 3–5 mais impactantes, em ordem. Para cada um: `[P?] O quê` (nomeie claro) / `Por que importa` (dano ao usuário ou ao objetivo) / `Fix` (concreto) / `Comando sugerido` (do vocabulário do Atelier).
7. **Red flags por persona**: para cada persona selecionada, o que quebrou na ação principal — elementos exatos, não descrição de persona.
8. **Observações menores**: notas rápidas.
9. **Tendência** (ver abaixo).
10. **Perguntas a considerar**: provocações que destravam soluções melhores ("e se a ação primária fosse mais proeminente?", "isso precisa parecer tão complexo?", "como seria uma versão confiante disso?").

---

## Tendência entre execuções

O score só vale se for comparável. Após finalizar o relatório:

1. Persista um snapshot em `criticas/<slug-do-alvo>-<data>.md` junto aos artefatos do run (ao lado de `croquis/` e `refinados/`), com frontmatter mínimo: `target`, `date`, `total_score`, `p0_count`, `p1_count`, e o corpo do relatório (itens 2–8; sem as perguntas ao usuário).
2. Leia os snapshots anteriores do mesmo slug e acrescente uma linha ao relatório:
   > **Tendência de `<slug>` (últimas 5 execuções): 24 → 28 → 32 → 29 → 32**
   Primeira execução? Diga: "Primeira execução para este alvo, sem tendência ainda."
3. Isso é fire-and-forget: falha na persistência não bloqueia a crítica — registre o erro e siga.
4. Se existir uma lista de exclusões acordada com o usuário (achados aceitos como intencionais — ex.: escolha de estilo registrada no DESIGN.md), suprima esses achados silenciosamente. Escolha deliberada da etapa de direção não é slop.

Re-rode a crítica depois das correções para ver o score se mover — é a régua do progresso.

---

## Perguntas ao usuário e plano de ação

Depois do relatório, faça **2–4 perguntas no máximo**, todas ancoradas nos achados reais (nunca "quem é seu público?" genérico), cada uma com 2–3 opções concretas:

1. **Prioridade**: "achei problemas de hierarquia visual, uso de cor e sobrecarga de informação — qual atacamos primeiro?"
2. **Intenção**: se houve desencontro tonal, pergunte se foi intencional ("a interface está clínica e corporativa — é o tom desejado, ou deveria ser mais quente/ousada?").
3. **Escopo**: "achei N problemas — tudo, top 3 ou só os críticos?"
4. **Restrições** (só se relevante): "alguma seção fica como está?"

Achados óbvios (1–2 problemas claros)? Pule as perguntas e vá direto ao plano.

Com as respostas, entregue o **plano priorizado** mapeando cada problema a um comando do Atelier: `/tipografar` (escala/ritmo), `/cor` (paleta/contraste), `/polir` (alinhamento/espaçamento/estados), `/baixar` ou `/subir` (hierarquia), `/animar` (motion), `/refinar <peça>` (retrabalho da peça), `/varrer` (re-medição final). Ordene pelas prioridades do usuário, depois por impacto; pule comando que não resolve nada; respeite escopo e áreas intocáveis; feche sempre com re-medição.

---

## Do's & don'ts do crítico

- Seja direto: feedback vago desperdiça o tempo de todos.
- Seja específico: "o botão de enviar", não "alguns elementos".
- Diga o que está errado **e** por que importa para o usuário.
- Sugestão concreta sempre; corte "considere explorar…" por inteiro.
- Priorize sem dó: se tudo é importante, nada é.
- Não amacie a crítica: honestidade é o que faz o design melhorar.
- Não infle o score: 4 é excelência genuína; a maioria das interfaces reais vive entre 20 e 32.
- Não reporte achado que o usuário já declarou intencional no DESIGN.md.
