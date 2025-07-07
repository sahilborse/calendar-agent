import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    GEMINI_API_KEY: str
    GOOGLE_CALENDAR_SERVICE_ACCOUNT_JSON: str
    CALENDAR_ID: str = "primary" # Or your test calendar ID

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
# print("Google Calendar Service Account JSON:", settings.GOOGLE_CALENDAR_SERVICE_ACCOUNT_JSON)