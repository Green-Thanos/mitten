from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Enviducate"
    
    # Database (for future use)
    DATABASE_URL: str = "sqlite:///./enviducate.db"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Enviducate-specific settings
    MAX_QUERY_LENGTH: int = 1000
    MIN_QUERY_LENGTH: int = 1
    
    # API Keys
    GEMINI_API_KEY: str = "your-gemini-api-key-here"
    
    # Static files
    STATIC_DIR: str = "static"
    IMAGES_DIR: str = "static/images"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
