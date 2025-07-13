"""
Application configuration management
"""
from dotenv import load_dotenv
load_dotenv()

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""

    # Database
    DATABASE_URL: str = Field(default="postgresql://postgres:password@localhost:5432/smart_home_agent")
    DB_HOST: str = Field(default="localhost")
    DB_PORT: int = Field(default=5432)
    DB_NAME: str = Field(default="smart_home_agent")
    DB_USER: str = Field(default="postgres")
    DB_PASSWORD: str = Field(default="password")

    # OpenAI
    # OPENAI_API_KEY: str = Field(default="")

    # OpenRouter
    OPENROUTER_API_KEY: str = Field(default="")


    # Application
    DEBUG: bool = Field(default=True)
    LOG_LEVEL: str = Field(default="INFO")
    SECRET_KEY: str = Field(default="change-this-in-production")

    # API
    API_PREFIX: str = Field(default="/api/v1")
    CORS_ORIGINS: List[str] = Field(default=["http://localhost:3000", "http://localhost:8080", "http://localhost:5173"])

    # Agent
    AGENT_MODEL: str = Field(default="deepseek/deepseek-r1:free")
    AGENT_TEMPERATURE: float = Field(default=0.1)
    MAX_CONVERSATION_HISTORY: int = Field(default=50)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",  # Optional, but recommended
        case_sensitive=True
    )
    
# Global settings instance
settings = Settings()
