"""Configuration settings for the payroll agent system."""

import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class EmailConfig:
    """Email configuration settings."""
    username: str
    password: str
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    use_tls: bool = True


@dataclass
class OpenAIConfig:
    """OpenAI API configuration."""
    api_key: str
    model: str = "gpt-4o-mini"
    temperature: float = 0.7


@dataclass
class AppConfig:
    """Application configuration."""
    environment: str = "development"
    log_level: str = "INFO"
    csv_data_path: str = "data/timesheets.csv"
    anomaly_threshold_hours: int = 8  # Flag if less than 8 hours per day


class Settings:
    """Main settings class that aggregates all configuration."""
    
    def __init__(self):
        self.email = self._load_email_config()
        self.openai = self._load_openai_config()
        self.app = self._load_app_config()
    
    def _load_email_config(self) -> EmailConfig:
        """Load email configuration from environment variables."""
        return EmailConfig(
            username=os.getenv("EMAIL_USERNAME", "abdulrehman@clickchain.com"),
            password=os.getenv("EMAIL_PASSWORD", "jayx tamp jmcj yrnf"),
            smtp_server=os.getenv("SMTP_SERVER", "smtp.gmail.com"),
            smtp_port=int(os.getenv("SMTP_PORT", "587"))
        )
    
    def _load_openai_config(self) -> OpenAIConfig:
        """Load OpenAI configuration from environment variables."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        return OpenAIConfig(
            api_key=api_key,
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        )
    
    def _load_app_config(self) -> AppConfig:
        """Load application configuration."""
        return AppConfig(
            environment=os.getenv("ENVIRONMENT", "development"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            csv_data_path=os.getenv("CSV_DATA_PATH", "data/timesheets.csv"),
            anomaly_threshold_hours=int(os.getenv("ANOMALY_THRESHOLD_HOURS", "8"))
        )


# Singleton instance
settings = Settings()
