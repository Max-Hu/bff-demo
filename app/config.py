import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    api_title: str = "CI/CD Scan API"
    api_version: str = "1.0.0"
    api_description: str = "API service for triggering Jenkins pipelines and managing scan results"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # Security
    api_key: str = "your-secret-api-key-here"
    
    # Jenkins Configuration
    jenkins_url: str = "http://localhost:8080"
    jenkins_username: str = ""	
    jenkins_password: str = ""
    jenkins_token: str = ""
    
    # Database Configuration (Oracle)
    oracle_host: str = "localhost"
    oracle_port: int = 1521
    oracle_service: str = "XE"
    oracle_username: str = "system"
    oracle_password: str = "oracle"
    
    # Logging
    log_level: str = "DEBUG"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings() 