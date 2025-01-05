from pathlib import Path
from datetime import datetime, timedelta

# Default output directory
DEFAULT_OUTPUT_DIR = Path("./datasets")

# Default dataset name
DEFAULT_DATASET_NAME = "Actuele10mindataKNMIstations"

# Default dataset version
DEFAULT_DATASET_VERSION = "2"

# Default maximum number of concurrent downloads
DEFAULT_MAX_CONCURRENT = 10

# Default date range
def get_default_date_range() -> tuple[datetime, datetime]:
    """Get the default date range (now - 1 hour and 30 minutes to now)."""
    end = datetime.now()
    start = end - timedelta(hours=1, minutes=30)
    return start, end
