from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "Mitten API"
    APP_ENV: str = "dev"
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-pro"  # This is the correct model name

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()