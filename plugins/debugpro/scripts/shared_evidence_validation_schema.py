from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = PLUGIN_ROOT / "skills/debugpro/references/shared-evidence.v1.schema.json"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))
