import os
from pathlib import Path


def get_data_dir() -> Path:
    """Get data directory from environment variable or use default."""
    data_dir = os.getenv("KANBAN_DATA_DIR", "data")
    return Path(data_dir)


def get_data_file() -> Path:
    """Get the JSON data file path."""
    return get_data_dir() / "kanban.json"