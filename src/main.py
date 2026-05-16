"""
ArcaneVision – Entry Point
===========================
Run from project root:
    python -m src.main
or:
    python src/main.py   (with arcanevision/ as CWD)
"""

from __future__ import annotations
import sys
import os

# Ensure project root is on PYTHONPATH when running as script
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from src.core.engine import Engine
from src.utils.logger import get_logger

log = get_logger("arcanevision")


def main() -> None:
    log.info("=" * 60)
    log.info("  ArcaneVision – AI Magical Hand Gesture System")
    log.info("=" * 60)
    try:
        engine = Engine()
        engine.run()
    except RuntimeError as exc:
        log.error("Fatal error: %s", exc)
        sys.exit(1)
    except KeyboardInterrupt:
        log.info("Interrupted by user.")
        sys.exit(0)


if __name__ == "__main__":
    main()
