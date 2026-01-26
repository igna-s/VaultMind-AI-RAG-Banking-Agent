from typing import Optional, Literal
from pydantic import model_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Explicitly load .env from Database folder
# Current file: /workspace/TheDefinitiveProyect/backend/app/config.py
# Target: /workspace/TheDefinitiveProyect/Database/.env
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
env_path = os.path.join(project_root, "Database", ".env")

if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    # Fallback or maybe we are in a different structure (e.g. docker)
    pass

class Settings(BaseSettings):
    APP_MODE: Literal["DEV", "PROD", "TEST"] = "DEV"
    
    # API Keys
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    # Database
    # Switched to PostgreSQL (Host Machine)
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password" # Please update this!
    POSTGRES_DB: str = "rag_db"
    POSTGRES_HOST: str = "127.0.0.1" # Access local container DB
    POSTGRES_PORT: str = "5432"
    
    # Allow overriding DATABASE_URL directly (e.g. from .env for Azure)
    DATABASE_URL: Optional[str] = None

    @model_validator(mode='after')
    def compute_database_url(self) -> 'Settings':
        if not self.DATABASE_URL:
             self.DATABASE_URL = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        return self
    
    # Flags
    USE_MOCK_LLM: bool = False

    @model_validator(mode='after')
    def check_settings(self) -> 'Settings':
        # Automatically enable Mock LLM in TEST mode
        if self.APP_MODE == "TEST":
            self.USE_MOCK_LLM = True
            
        # Validate required keys in PROD mode
        if self.APP_MODE == "PROD":
            missing = []
            if not self.OPENAI_API_KEY:
                missing.append("OPENAI_API_KEY")
            if not self.GEMINI_API_KEY:
                missing.append("GEMINI_API_KEY")
            if not self.POSTGRES_PASSWORD:
                missing.append("POSTGRES_PASSWORD")
            
            if missing:
                raise ValueError(f"Missing required fields for PROD mode: {', '.join(missing)}")
        
        return self

settings = Settings()
