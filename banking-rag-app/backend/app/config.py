from typing import Optional, Literal
from pydantic import model_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_MODE: Literal["DEV", "PROD", "TEST"] = "DEV"
    
    # API Keys
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    # Database
    # Switched to SQLite for immediate availability in Codespaces without Docker
    # Database
    # Switched to MySQL (Host Machine)
    MYSQL_USER: str = "admin"
    MYSQL_PASSWORD: str = "password" # Please update this!
    MYSQL_DB: str = "banking_db"
    MYSQL_HOST: str = "127.0.0.1" # Access local container DB
    MYSQL_PORT: str = "3306"
    
    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+aiomysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"
    
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
            if not self.DB_PASSWORD:
                missing.append("DB_PASSWORD")
            
            if missing:
                raise ValueError(f"Missing required fields for PROD mode: {', '.join(missing)}")
        
        return self

settings = Settings()
