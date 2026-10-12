-- Finanças da Família — estrutura inicial
-- Cada tabela é uma "planilha". As regras de acesso (RLS) garantem que cada pessoa
-- só enxerga o que é dela ou o que foi compartilhado com um grupo do qual participa.

create extension if not exists pgcrypto;

-- ---------- pessoas e grupos ----------
create table public.perfis (
  id uuid primary key references auth.users(id) on delete cascade,
  nome text not null default '',
  email text not null default '',
  criado_em timestamptz not null default now()
);

create table public.grupos (
  id uuid primary key default gen_random_uuid(),
  nome text not null,
  criado_por uuid not null default auth.uid() references auth.users(id) on delete cascade,
  criado_em timestamptz not null default now()
);

create table public.grupo_membros (
  grupo_id uuid not null references public.grupos(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  papel text not null default 'membro' check (papel in ('admin', 'membro')),
  primary key (grupo_id, user_id)
);

create table public.convites (
  grupo_id uuid not null references public.grupos(id) on delete cascade,
  email text not null check (email = lower(email)),
  criado_em timestamptz not null default now(),
  primary key (grupo_id, email)
);

-- ---------- dinheiro ----------
create table public.contas (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
  compartilhado boolean not null default true,
  tipo text not null check (tipo in ('conta', 'cartao')),
  pessoa text not null default 'pf' check (pessoa in ('pf', 'pj')),
  banco text not null,
  apelido text,
  cor text,
  saldo numeric(14,2) not null default 0,
  data_saldo date,
  limite numeric(14,2),
  fecha smallint check (fecha between 1 and 31),
  venc smallint check (venc between 1 and 31),
  paga_com uuid references public.contas(id) on delete set null,
  empresa text,
  cnpj text,
  criado_em timestamptz not null default now()
);

create table public.lancamentos (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
  tipo text not null check (tipo in ('despesa', 'receita')),
  descricao text not null,
  valor numeric(14,2) not null check (valor >= 0),
  venc date not null,
  compra date,
  conta_id uuid references public.contas(id) on delete set null,
  categoria text not null,
  essencial boolean not null default true,
  pago boolean not null default false,
  pago_em date,
  compartilhado boolean not null default true,
  parcela text,
  fitid text,
  origem text not null default 'manual',
  criado_em timestamptz not null default now()
);
create index lancamentos_owner_venc on public.lancamentos (owner_id, venc);
create index lancamentos_conta on public.lancamentos (conta_id);
-- a mesma transação de banco não entra duas vezes na mesma conta
create unique index lancamentos_fitid_unico on public.lancamentos (conta_id, fitid) where fitid is not null;

create table public.investimentos (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
  compartilhado boolean not null default true,
  tipo text not null check (tipo in ('rf', 'tesouro', 'rv', 'fundo')),
  classe text, ticker text, qtd numeric(18,6), pm numeric(14,4),
  data date not null default current_date,
  titulo text, ano smallint, indexador text, taxa numeric(10,4), aplicado numeric(14,2),
  produto text, emissor text, cnpj text, nome text,
  criado_em timestamptz not null default now()
);

create table public.importacoes (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
  conta_id uuid references public.contas(id) on delete cascade,
  arquivo text, data date not null default current_date,
  novos int not null default 0, casados int not null default 0, faturas int not null default 0, regras int not null default 0,
  criado_em timestamptz not null default now()
);

-- preferências de cada pessoa: avisos, regras de categoria aprendidas, colunas de CSV, premissas
create table public.preferencias (
  user_id uuid primary key default auth.uid() references auth.users(id) on delete cascade,
  dados jsonb not null default '{}'::jsonb,
  atualizado_em timestamptz not null default now()
);

-- ---------- funções de apoio às regras de acesso ----------
create or replace function public.e_membro(g uuid) returns boolean
language sql security definer stable set search_path = public as $$
  select exists (select 1 from grupo_membros where grupo_id = g and user_id = auth.uid())
$$;

create or replace function public.e_admin(g uuid) returns boolean
language sql security definer stable set search_path = public as $$
  select exists (select 1 from grupo_membros where grupo_id = g and user_id = auth.uid() and papel = 'admin')
$$;

-- a pessoa u participa de algum grupo comigo (ou sou eu)?
create or replace function public.compartilha_grupo(u uuid) returns boolean
language sql security definer stable set search_path = public as $$
  select u = auth.uid() or exists (
    select 1 from grupo_membros a join grupo_membros b on a.grupo_id = b.grupo_id
    where a.user_id = auth.uid() and b.user_id = u)
$$;

create or replace function public.meu_email() returns text
language sql stable as $$ select lower(coalesce(auth.jwt() ->> 'email', '')) $$;

-- ---------- perfil criado automaticamente no cadastro ----------
create or replace function public.novo_usuario() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  insert into perfis (id, nome, email)
  values (new.id, coalesce(nullif(new.raw_user_meta_data ->> 'nome', ''), split_part(new.email, '@', 1)), lower(new.email))
  on conflict (id) do nothing;
  return new;
end $$;

create trigger ao_criar_usuario after insert on auth.users
for each row execute function public.novo_usuario();

-- ---------- regras de acesso (RLS) ----------
alter table public.perfis enable row level security;
alter table public.grupos enable row level security;
alter table public.grupo_membros enable row level security;
alter table public.convites enable row level security;
alter table public.contas enable row level security;
alter table public.lancamentos enable row level security;
alter table public.investimentos enable row level security;
alter table public.importacoes enable row level security;
alter table public.preferencias enable row level security;

create policy perfis_ver on public.perfis for select using (compartilha_grupo(id));
create policy perfis_editar on public.perfis for update using (id = auth.uid()) with check (id = auth.uid());

create policy grupos_ver on public.grupos for select using (
  e_membro(id) or criado_por = auth.uid()
  or exists (select 1 from convites c where c.grupo_id = grupos.id and c.email = meu_email()));
create policy grupos_criar on public.grupos for insert with check (criado_por = auth.uid());
create policy grupos_editar on public.grupos for update using (e_admin(id));
create policy grupos_apagar on public.grupos for delete using (e_admin(id));

create policy membros_ver on public.grupo_membros for select using (e_membro(grupo_id));
create policy membros_entrar on public.grupo_membros for insert with check (
  e_admin(grupo_id)
  or (user_id = auth.uid() and exists (select 1 from grupos g where g.id = grupo_membros.grupo_id and g.criado_por = auth.uid()))
  or (user_id = auth.uid() and papel = 'membro' and exists (select 1 from convites c where c.grupo_id = grupo_membros.grupo_id and c.email = meu_email())));
create policy membros_editar on public.grupo_membros for update using (e_admin(grupo_id));
create policy membros_sair on public.grupo_membros for delete using (e_admin(grupo_id) or user_id = auth.uid());

create policy convites_ver on public.convites for select using (e_membro(grupo_id) or email = meu_email());
create policy convites_criar on public.convites for insert with check (e_admin(grupo_id));
create policy convites_apagar on public.convites for delete using (e_admin(grupo_id) or email = meu_email());

create policy contas_ver on public.contas for select using (owner_id = auth.uid() or (compartilhado and compartilha_grupo(owner_id)));
create policy contas_criar on public.contas for insert with check (owner_id = auth.uid());
create policy contas_editar on public.contas for update using (owner_id = auth.uid()) with check (owner_id = auth.uid());
create policy contas_apagar on public.contas for delete using (owner_id = auth.uid());

create policy lanc_ver on public.lancamentos for select using (owner_id = auth.uid() or (compartilhado and compartilha_grupo(owner_id)));
create policy lanc_criar on public.lancamentos for insert with check (owner_id = auth.uid());
-- quem é do grupo pode marcar como pago um lançamento compartilhado (ex.: pagar a fatura da família)
create policy lanc_editar on public.lancamentos for update
  using (owner_id = auth.uid() or (compartilhado and compartilha_grupo(owner_id)))
  with check (owner_id = auth.uid() or (compartilhado and compartilha_grupo(owner_id)));
create policy lanc_apagar on public.lancamentos for delete using (owner_id = auth.uid());

create policy inv_ver on public.investimentos for select using (owner_id = auth.uid() or (compartilhado and compartilha_grupo(owner_id)));
create policy inv_criar on public.investimentos for insert with check (owner_id = auth.uid());
create policy inv_editar on public.investimentos for update using (owner_id = auth.uid()) with check (owner_id = auth.uid());
create policy inv_apagar on public.investimentos for delete using (owner_id = auth.uid());

create policy imp_tudo on public.importacoes for all using (owner_id = auth.uid()) with check (owner_id = auth.uid());
create policy pref_tudo on public.preferencias for all using (user_id = auth.uid()) with check (user_id = auth.uid());
