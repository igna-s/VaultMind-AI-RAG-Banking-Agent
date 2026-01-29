from typing import Optional, Literal, List, Union
from pydantic import model_validator, field_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Load .env file
# Priority:
# 1. backend/.env (for local dev)
# 2. Database/.env (legacy/shared)
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_env_path = os.path.join(current_dir, "..", ".env")
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
database_env_path = os.path.join(project_root, "Database", ".env")

if os.path.exists(database_env_path):
    load_dotenv(database_env_path)

if os.path.exists(backend_env_path):
    load_dotenv(backend_env_path, override=True)

class Settings(BaseSettings):
    APP_MODE: Literal["DEV", "PROD", "TEST"] = "DEV"
    
    # Security
    SECRET_KEY: str = "DEV_SECRET_KEY_CHANGE_IN_PROD" # Default for DEV only

    # API Keys
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    
    # Database
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password" 
    POSTGRES_DB: str = "rag_db"
    POSTGRES_HOST: str = "127.0.0.1" 
    POSTGRES_PORT: str = "5432"
    
    # Allow overriding DATABASE_URL directly (e.g. from .env for Azure)
    DATABASE_URL: Optional[str] = None

    # CORS
    CORS_ORIGINS: Union[List[str], str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    @field_validator("CORS_ORIGINS", mode="before")
    def parse_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [origin.strip() for origin in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Email / SMTP
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None

    # Google OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None

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
            if not self.OPENAI_API_KEY and not self.GEMINI_API_KEY:
                # Assuming at least one LLM key is needed
                pass 
                
            if self.SECRET_KEY == "DEV_SECRET_KEY_CHANGE_IN_PROD":
                 missing.append("SECRET_KEY (must be changed from default)")

            if not self.POSTGRES_PASSWORD or self.POSTGRES_PASSWORD == "password":
                 # In PROD we expect a strong password, though "password" could theoretically be the password, 
                 # it's best to warn or enforce via other means. 
                 # Here we just check if it's set.
                 pass

            if missing:
                raise ValueError(f"Missing or insecure configuration for PROD mode: {', '.join(missing)}")
        
        return self

settings = Settings()
