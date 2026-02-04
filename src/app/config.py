"""Application configuration from environment."""
import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root (src/ or parent)
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/contentflow",
)
