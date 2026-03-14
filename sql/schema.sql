-- Optional future Postgres schema for Watcher
create table if not exists watcher_state_log (
  timestamp_utc timestamptz primary key,
  price double precision not null,
  rsi_15m double precision,
  rsi_1h double precision,
  rsi_1d double precision,
  rsi_1w double precision,
  funding_latest double precision,
  open_interest double precision,
  price_vs_oi text,
  regime text,
  bias text,
  breakout_risk text,
  flush_risk text,
  support_state text,
  watcher_verdict text
);

create table if not exists watcher_signal_log (
  id bigserial primary key,
  timestamp_utc timestamptz not null,
  signal_type text not null,
  signal_text text not null
);
