from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

SESSION_PATH = Path(__file__).resolve().parents[1] / ".session.json"


def save_session(data: Dict[str, Any]) -> None:
    SESSION_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_session() -> Optional[Dict[str, Any]]:
    if not SESSION_PATH.exists():
        return None
    try:
        return json.loads(SESSION_PATH.read_text(encoding="utf-8"))
    except Exception:
        return None


def clear_session() -> None:
    if SESSION_PATH.exists():
        SESSION_PATH.unlink()
