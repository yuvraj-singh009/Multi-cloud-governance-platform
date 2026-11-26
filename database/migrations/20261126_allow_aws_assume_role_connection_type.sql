-- The existing cloud_accounts connection_type CHECK constraint rejects
-- the new cross-account AWS connection type (aws_assume_role).
-- Drop the legacy restriction; the API validates supported connection types.
alter table public.cloud_accounts
  drop constraint if exists cloud_accounts_connection_type_check;
