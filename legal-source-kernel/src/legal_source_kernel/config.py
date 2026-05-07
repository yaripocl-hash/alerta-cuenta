"""Configuration — all paths and settings resolved here, never inline."""

from pathlib import Path
import os


DEFAULT_DB_PATH = Path.home() / ".legal_source_kernel" / "kernel.db"


def get_db_path() -> Path:
    """Return the active DB path from env or default."""
    env_path = os.environ.get("LEGAL_KERNEL_DB")
    if env_path:
        return Path(env_path)
    return DEFAULT_DB_PATH


def get_data_dir() -> Path:
    """Return the directory that contains the DB file."""
    return get_db_path().parent
