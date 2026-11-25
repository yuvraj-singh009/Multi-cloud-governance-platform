-- Preserve existing cloud_accounts columns.
alter table public.cloud_accounts
  add column if not exists connection_status text not null default 'pending',
  add column if not exists role_arn text,
  add column if not exists external_id_encrypted text,
  add column if not exists verified_at timestamptz;

alter table public.cloud_accounts drop constraint if exists cloud_accounts_connection_status_check;
alter table public.cloud_accounts add constraint cloud_accounts_connection_status_check
  check (connection_status in ('pending','connected','disconnected','error'));

alter table public.cloud_accounts enable row level security;
drop policy if exists "Users can view their own cloud accounts" on public.cloud_accounts;
create policy "Users can view their own cloud accounts" on public.cloud_accounts
  for select using (auth.uid() = user_id);

drop policy if exists "Users can insert their own cloud accounts" on public.cloud_accounts;
drop policy if exists "Users can update their own cloud accounts" on public.cloud_accounts;
drop policy if exists "Users can delete their own cloud accounts" on public.cloud_accounts;
-- Backend writes use the Supabase server key only after explicit owner checks.
