"""
Configuration settings for X360 AI Agent backend.
"""

from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # AWS Bedrock (optional - will use AWS CLI credentials if not provided)
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_default_region: str = "us-east-1"

    # Bedrock Models (using Nova only - Claude restricted)
    bedrock_model_briefing: str = "amazon.nova-pro-v1:0"
    bedrock_model_chat: str = "amazon.nova-lite-v1:0"
    bedrock_model_action: str = "amazon.nova-pro-v1:0"

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
