#!/usr/bin/env bash
set -euo pipefail

APP_DIR=${APP_DIR:-/opt/watcher}
PUBLIC_DIR=${PUBLIC_DIR:-/var/www/html/watcher}

mkdir -p "$PUBLIC_DIR"
cp -f "$APP_DIR/output/"*.json "$PUBLIC_DIR/" 2>/dev/null || true
cp -f "$APP_DIR/output/"*.csv "$PUBLIC_DIR/" 2>/dev/null || true

echo "Published Watcher output to $PUBLIC_DIR"
