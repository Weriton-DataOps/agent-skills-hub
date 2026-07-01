Contexto: uma API route do Next.js (App Router) funcionava em dev mas retornava
HTTP 500 em produção na Vercel. O log só mostrava "Internal Server Error" sem stack.

Causa raiz: a rota lia `process.env.DATABASE_URL`, que estava definida no `.env.local`
(dev) mas NÃO estava cadastrada nas Environment Variables do projeto na Vercel para o
ambiente Production. Em produção a variável vinha `undefined`, o cliente do banco
estourava na inicialização e o handler morria antes de logar.

Como diagnosticar:
- Rodar `vercel env ls` e conferir se a var existe no ambiente `production` (não só `development`).
- Adicionar um guard no topo do handler: se a env var essencial for `undefined`, retornar 500
  com uma mensagem explícita e logar o nome da var faltando (sem logar o valor).
- Conferir os logs em Vercel > Deployment > Functions; um crash na init do módulo aparece como
  invocação que falha sem log de request.

Como resolver:
- Cadastrar a var no ambiente correto: `vercel env add DATABASE_URL production`.
- Fazer um novo deploy (env vars só entram em builds novos): `vercel --prod`.
- Opcional: validar todas as envs obrigatórias no boot com um schema (ex.: zod) e falhar
  o build cedo, em vez de falhar em runtime.

Lição: variável que existe em dev não existe automaticamente em produção; separar por
ambiente e validar no boot evita 500 silencioso.
