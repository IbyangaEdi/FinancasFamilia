# Fase 0 — Contas e acessos

| # | Item | Quem | Status |
|---|---|---|---|
| 0.1 | Projeto no Supabase "DividaZero" (São Paulo, PostgreSQL 17 — chaves e senha testadas) | Edval | ✅ |
| 0.2 | Conta na Pluggy + Application (chaves testadas; MeuPluggy e bancos PF/PJ disponíveis) | Edval | ✅ |
| 0.3 | Conta no Resend + API key | Edval | ⬜ |
| 0.4 | Token da brapi.dev (testado: cotação real ok) | Edval | ✅ |
| 0.5 | Repositório privado no GitHub (github.com/IbyangaEdi/FinancasFamilia) | Claude | ✅ |
| 0.6 | Chaves preenchidas no `.env` | Edval | ⬜ |
| 0.7 | Conferência das chaves (sem expor valores) | Claude | ⬜ |

Regra: o Client Secret da Pluggy e a chave secreta do Supabase **não** são colados no chat.
Eles vão direto no arquivo `.env` desta pasta.

Para conferir as chaves a qualquer momento (não mostra os valores):

    python3 scripts/verificar_chaves.py
