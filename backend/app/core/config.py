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
    GOOGLE_SEARCH_API_KEY: str = "your-google-search-api-key-here"
    GOOGLE_SEARCH_ENGINE_ID: str = "your-search-engine-id-here"
    
    # Google Earth Engine
    GEE_SERVICE_ACCOUNT_EMAIL: str = "your-service-account@project.iam.gserviceaccount.com"
    GEE_PRIVATE_KEY_PATH: str = "path/to/your/private-key.json"
    
    # Static files
    STATIC_DIR: str = "static"
    IMAGES_DIR: str = "static/images"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra environment variables


settings = Settings()
