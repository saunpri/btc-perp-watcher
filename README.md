# Watcher v1

Watcher v1 is a public-market BTC monitoring pipeline that:
- fetches public BTC market data
- calculates indicators and interpreted state
- stores append-only history
- exports public-readable files for later investigation
- produces an EX bridge summary

## What it collects
- Binance BTCUSDT spot klines (15m, 1h, 1d, 1w)
- Binance futures funding rate history (BTCUSDT)
- Binance futures open interest (BTCUSDT)
- Derived RSI values (15m, 1h, 1d, 1w)
- Interpreted state: bias, regime, price-vs-OI state, breakout risk, flush risk

## Outputs
The script writes four files into `output/`:
- `current_state.json`
- `state_log.csv`
- `signal_log.csv`
- `ex_bridge.json`

## Repo layout
- `watcher/` - main Python package
- `deploy/systemd/` - droplet service and timer units
- `deploy/bootstrap_droplet.sh` - first-time droplet setup script
- `deploy/publish_output.sh` - optional helper to copy output into a public web directory
- `sql/schema.sql` - starter database schema for later migration

## Quick start
1. Create a Python 3.11+ environment.
2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy config and env templates:
   ```bash
   cp config.example.json config.json
   cp .env.example .env
   ```
4. Run once:
   ```bash
   python -m watcher.main
   ```

## Droplet deployment
1. Push this repo to GitHub.
2. SSH into the droplet.
3. Run:
   ```bash
   export REPO_URL=https://github.com/<you>/<repo>.git
   curl -fsSL https://raw.githubusercontent.com/<you>/<repo>/main/deploy/bootstrap_droplet.sh -o bootstrap_droplet.sh
   bash bootstrap_droplet.sh
   ```
   Or clone the repo manually and run `deploy/bootstrap_droplet.sh`.
4. Check status:
   ```bash
   systemctl status watcher.timer watcher.service
   ```
5. Run an immediate snapshot manually when needed:
   ```bash
   sudo systemctl start watcher.service
   ```

## Public-readable output
To let me inspect Watcher later, publish `output/` somewhere public-readable.
Two simple paths:
1. Copy files into a small Nginx web directory with `deploy/publish_output.sh`
2. Sync the files to object storage or a public gist-like endpoint

Example after publishing:
- `https://watcher.example.com/current_state.json`
- `https://watcher.example.com/state_log.csv`
- `https://watcher.example.com/signal_log.csv`
- `https://watcher.example.com/ex_bridge.json`

## Notes
- This starter uses flat files by default so it is easy to test.
- The code is structured so you can swap storage later for Supabase/Postgres.
- No private API keys are required for the current data sources.
- `WATCHER_CONFIG` can point to a custom config file path if you do not want `config.json` in the repo root.

## Suggested next steps
- Add SPX proxy data
- Add Fear & Greed
- Add Supabase/Postgres storage
- Publish `output/` to a public web location for investigation
- Map old Watcher verdict language into the new state model
