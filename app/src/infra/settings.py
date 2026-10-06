"""Configurações da aplicação carregadas das variáveis de ambiente."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


DEFAULT_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    """Configuração central da aplicação."""

    DATABASE_URL: str = "sqlite:///./vehicle-core.db"
    POSTGRES_DB: str = "vehicle_core"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = ""
    AWS_DEFAULT_REGION: str = "us-east-1"
    DEBUG: bool = False

    model_config = SettingsConfigDict(
        env_file=DEFAULT_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
