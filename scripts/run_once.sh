#!/usr/bin/env bash
set -e
cd /root/watcher_runtime_clean/watcher_v1
source .venv/bin/activate
python -m watcher.main
