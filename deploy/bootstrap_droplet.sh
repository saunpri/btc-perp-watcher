#!/usr/bin/env bash
set -euo pipefail

APP_DIR=${APP_DIR:-/opt/watcher}
APP_USER=${APP_USER:-watcher}
REPO_URL=${REPO_URL:-}
BRANCH=${BRANCH:-main}

if [[ -z "$REPO_URL" ]]; then
  echo "Set REPO_URL to your GitHub repo URL before running."
  exit 1
fi

sudo useradd --system --create-home --home-dir "$APP_DIR" --shell /bin/bash "$APP_USER" 2>/dev/null || true
sudo mkdir -p "$APP_DIR"
sudo chown -R "$APP_USER":"$APP_USER" "$APP_DIR"

if [[ ! -d "$APP_DIR/.git" ]]; then
  sudo -u "$APP_USER" git clone --branch "$BRANCH" "$REPO_URL" "$APP_DIR"
else
  sudo -u "$APP_USER" bash -lc "cd '$APP_DIR' && git fetch origin '$BRANCH' && git checkout '$BRANCH' && git pull --ff-only origin '$BRANCH'"
fi

sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip git

sudo -u "$APP_USER" bash -lc "cd '$APP_DIR' && python3 -m venv .venv && .venv/bin/pip install --upgrade pip && .venv/bin/pip install -r requirements.txt"

if [[ ! -f "$APP_DIR/config.json" ]]; then
  sudo cp "$APP_DIR/config.example.json" "$APP_DIR/config.json"
fi
if [[ ! -f "$APP_DIR/.env" ]]; then
  sudo cp "$APP_DIR/.env.example" "$APP_DIR/.env"
fi

sudo cp "$APP_DIR/deploy/systemd/watcher.service" /etc/systemd/system/watcher.service
sudo cp "$APP_DIR/deploy/systemd/watcher.timer" /etc/systemd/system/watcher.timer
sudo systemctl daemon-reload
sudo systemctl enable --now watcher.timer
sudo systemctl start watcher.service

echo "Watcher deployed. Check status with: systemctl status watcher.timer watcher.service"
