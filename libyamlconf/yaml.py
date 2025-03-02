"""Load and merge YAMl configuration."""

from pathlib import Path
from typing import Any

import yaml


def load_yaml(file: Path) -> dict[str, Any]:
    with open(file, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
