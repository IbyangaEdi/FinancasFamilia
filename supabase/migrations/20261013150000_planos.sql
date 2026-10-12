-- DividaZero v2: o planejamento de cada pessoa (saldo, receitas, despesas fixas, cartões,
-- assinaturas e empréstimos) fica num único registro por usuário.
-- As tabelas do sistema anterior continuam no banco, sem uso, como histórico.
create table if not exists public.planos (
  user_id uuid primary key default auth.uid() references auth.users(id) on delete cascade,
  dados jsonb not null default '{}'::jsonb,
  criado_em timestamptz not null default now(),
  atualizado_em timestamptz not null default now()
);

alter table public.planos enable row level security;

create policy planos_ver on public.planos for select using (user_id = auth.uid());
create policy planos_criar on public.planos for insert with check (user_id = auth.uid());
create policy planos_editar on public.planos for update using (user_id = auth.uid()) with check (user_id = auth.uid());
create policy planos_apagar on public.planos for delete using (user_id = auth.uid());
