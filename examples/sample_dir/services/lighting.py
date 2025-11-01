from __future__ import annotations

from typing import Any

from utils.io import save_config
from utils.validation import ensure_colors


def configure_lighting(colors: list[dict[str, str]]) -> dict[str, Any]:
    ensure_colors(colors)
    payload = {"colors": colors, "mode": "ambient"}
    storage_info = save_config(payload)
    return {**payload, "storage": storage_info}
