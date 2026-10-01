import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "FitBuddy")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./data/fitbuddy.db",
    )

    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "").strip()

    GEMINI_WORKOUT_MODEL: str = os.getenv(
        "GEMINI_WORKOUT_MODEL",
        "gemini-2.5-pro",
    )

    GEMINI_TIP_MODEL: str = os.getenv(
        "GEMINI_TIP_MODEL",
        "gemini-2.5-flash-lite",
    )

    ADMIN_USERNAME: str = os.getenv(
        "ADMIN_USERNAME",
        "admin",
    )

    ADMIN_PASSWORD: str = os.getenv(
        "ADMIN_PASSWORD",
        "fitbuddy123",
    )


settings = Settings()