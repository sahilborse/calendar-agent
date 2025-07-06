import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    GEMINI_API_KEY: str
    GOOGLE_CALENDAR_SERVICE_ACCOUNT_JSON: str
    CALENDAR_ID: str = "primary" # Or your test calendar ID

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
# print("Settings loaded successfully:")
# print(f"GEMINI_API_KEY: {settings.GEMINI_API_KEY}")
# print(f"GOOGLE_CALENDAR_SERVICE_ACCOUNT_JSON: {settings.GOOGLE_CALENDAR_SERVICE_ACCOUNT_JSON}")
# print(f"CALENDAR_ID: {settings.CALENDAR_ID}")