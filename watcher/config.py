from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_PATH = BASE_DIR / "config.json"
EXAMPLE_CONFIG_PATH = BASE_DIR / "config.example.json"


def load_config() -> Dict[str, Any]:
    env_path = os.getenv("WATCHER_CONFIG")
    if env_path:
        path = Path(env_path).expanduser().resolve()
    else:
        path = DEFAULT_CONFIG_PATH if DEFAULT_CONFIG_PATH.exists() else EXAMPLE_CONFIG_PATH
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
