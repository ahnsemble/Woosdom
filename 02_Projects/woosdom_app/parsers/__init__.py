import sys
import os
from pathlib import Path


def get_vault_root() -> Path:
    """Return Woosdom_Brain vault root, handling both dev and frozen environments."""
    if getattr(sys, 'frozen', False):
        return Path(os.environ.get(
            "WOOSDOM_VAULT",
            os.path.expanduser("~/Desktop/Dev/Woosdom_Brain"),
        ))
    # 개발 환경: parsers/ → woosdom_app/ → 02_Projects/ → Woosdom_Brain/
    return Path(__file__).resolve().parent.parent.parent.parent
