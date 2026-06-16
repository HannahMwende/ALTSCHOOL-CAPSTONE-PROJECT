-- 02_staging.sql
-- Stage 2: clean, typed, deduplicated staging copies of source tables.

-- 1. stg_customers
-- Standardise customer names, normalise email, default missing country to Nigeria,
-- and cast to a proper timestamp for created_at.
create view if not exists stg_customers as
select
  customer_id::int as customer_id,
  initcap(name) as name,
  lower(email) as email,
  coalesce(country, 'Nigeria') as country,
  created_at::timestamp as created_at
from customers;

-- 2. stg_billing
-- Remove duplicate transaction_id values by keeping only the most recent record.
-- Replace NULL amount values with zero and cast transaction_date to timestamp.
create view if not exists stg_billing as
with ranked as (
  select
    transaction_id::int as transaction_id,
    customer_id::int as customer_id,
    coalesce(amount, 0)::numeric(18,2) as amount,
    currency,
    transaction_date::timestamp as transaction_date,
    row_number() over (
      partition by transaction_id
      order by transaction_date desc nulls last
    ) as rn
  from billings_transactions
)
select
  transaction_id,
  customer_id,
  amount,
  currency,
  transaction_date
from ranked
where rn = 1;

-- 3. stg_sessions
-- Cast start_time and end_time to timestamps, replace NULL data_used_mb with zero,
-- and derive session_duration_sec as the positive session length in seconds.
create view if not exists stg_sessions as
select
  session_id::int as session_id,
  customer_id::int as customer_id,
  start_time::timestamp as start_time,
  end_time::timestamp as end_time,
  coalesce(data_used_mb, 0)::numeric(18,2) as data_used_mb,
  greatest(extract(epoch from (end_time::timestamp - start_time::timestamp)), 0) as session_duration_sec
from networks_sessions;
