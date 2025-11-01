from __future__ import annotations

from pathlib import Path


def save_config(config: dict) -> dict[str, str]:
    """Pretend to persist a configuration without touching the real filesystem."""
    output_dir = Path(__file__).parent / "data"
    output_file = output_dir / "lighting.json"
    return {
        "path": output_file.as_posix(),
        "preview": f"{config['mode']}|{len(config['colors'])}",
    }
