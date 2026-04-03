from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Final

DEFAULT_OUTPUT_DIR: Final = Path("./datasets")
DEFAULT_DATASET_NAME: Final[str] = "Actuele10mindataKNMIstations"
DEFAULT_DATASET_VERSION: Final[str] = "2"
DEFAULT_MAX_CONCURRENT: Final[int] = 10
DEFAULT_TIME_WINDOW: Final[timedelta] = timedelta(hours=1, minutes=30)


def get_default_date_range() -> tuple[datetime, datetime]:
    """Return the default query window as UTC, matching the KNMI API (+00:00)."""
    end = datetime.now(timezone.utc)
    start = end - DEFAULT_TIME_WINDOW
    return start, end
