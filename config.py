# ============================================================
#  config.py — Loads database config from .env
#  Risk Management System  ·  by Sasindu Dilshara
# ============================================================

import os
from pathlib import Path
from dotenv import load_dotenv

# Locate the .env file relative to this file's directory
_BASE_DIR = Path(__file__).resolve().parent
_ENV_PATH = _BASE_DIR / ".env"

if not _ENV_PATH.exists():
    raise FileNotFoundError(
        f"\n  [CONFIG ERROR] .env file not found at: {_ENV_PATH}\n"
        f"  → Copy .env.example to .env and fill in your MySQL credentials.\n"
    )

load_dotenv(dotenv_path=_ENV_PATH)

def _require(key: str) -> str:
    """Read a required env variable, raise a clear error if missing."""
    val = os.getenv(key)
    if val is None:
        raise EnvironmentError(
            f"\n  [CONFIG ERROR] Required variable '{key}' is missing from .env\n"
        )
    return val

DB_CONFIG = {
    "host":       os.getenv("DB_HOST",    "localhost"),
    "port":       int(os.getenv("DB_PORT", "3306")),
    "user":       _require("DB_USER"),
    "password":   os.getenv("DB_PASSWORD", ""),
    "database":   _require("DB_NAME"),
    "charset":    os.getenv("DB_CHARSET",  "utf8mb4"),
    "autocommit": True,
}
