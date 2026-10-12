-- Liga os lançamentos de uma mesma série: parcelas de uma compra ou meses de uma assinatura.
-- Permite "excluir este e os próximos" e evita lançar o mesmo mês futuro duas vezes.
alter table public.lancamentos add column if not exists serie uuid;
create index if not exists lancamentos_serie on public.lancamentos (serie) where serie is not null;
