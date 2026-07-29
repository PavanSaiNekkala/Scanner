"""
Shared project paths.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DATA = ROOT / "data"

REPORTS = ROOT / "reports"

EXPORTS = ROOT / "exports"

LOGS = ROOT / "logs"