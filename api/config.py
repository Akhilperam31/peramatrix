import os
import logging
from typing import List, Optional
from functools import lru_cache
from pydantic import model_validator
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    ENVIRONMENT: str = "development" # development, production
    SECRET_KEY: str = "dev-secret-key-change-in-prod"
    ALLOWED_HOSTS: List[str] = ["*"]
    CORS_ORIGINS: List[str] = ["*"]
    
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    DB_PATH: str = os.getenv('DB_PATH', "peramatrix.db") 
    
    # SMTP Config
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_TO: str = ""

    # Uploads
    UPLOAD_FOLDER: str = "uploads"
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024

    model_config = {
        "env_file": ".env",
        "extra": "ignore",
        "case_sensitive": True
    }

    @model_validator(mode='after')
    def validate_production_security(self):
        if self.ENVIRONMENT == "production":
            if self.SECRET_KEY == "dev-secret-key-change-in-prod":
                raise ValueError("SECRET_KEY must be changed in production!")
            if self.CORS_ORIGINS == ["*"]:
                logger.warning("CORS_ORIGINS set to '*' in production. This is insecure!")
        return self

    @model_validator(mode='after')
    def set_default_email_to(self):
        if not self.EMAIL_TO and self.SMTP_USER:
            self.EMAIL_TO = self.SMTP_USER
        return self

@lru_cache()
def get_settings():
    return Settings()
