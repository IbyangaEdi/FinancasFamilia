# Finanças da Família

Sistema de gestão financeira da família: contas a pagar e receber, vencimentos e avisos,
saúde financeira, sugestões de corte, grupos compartilhados, bancos PF e PJ, investimentos
e Open Finance via Pluggy.

- Protótipo navegável: `prototipo.html`
- Destino: `dividazero.berluc.com.br` (GitHub Pages) + Supabase (login, dados, tarefas agendadas)

## Fases
0. Contas e acessos ✅ (ver `FASE0.md`)
1. Validação da Pluggy / Meu Pluggy — ⏸️ pausada: a Pluggy exige formalização do cadastro (contrato empresarial). Seguimos com importação de arquivos
2. Base: banco de dados, regras de acesso, login
3. Telas com dados reais
4. Publicação em dividazero.berluc.com.br
5. Avisos (e-mail e celular)
6. Investimentos com dados reais
7. Importação de extratos e faturas (OFX, CSV, PDF) ← **caminho principal**
8. Open Finance (Pluggy ou outro agregador) — só se surgir opção viável para uso familiar
9. Teste com a família
10. No ar

Segredos ficam só em `.env` (fora do Git) e, em produção, nos "Secrets" das Edge Functions do Supabase.
