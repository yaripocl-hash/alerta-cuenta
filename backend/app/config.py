from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pathlib import Path

# .env está en la raíz del proyecto (un nivel arriba de backend/)
_ENV_FILE = Path(__file__).parent.parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(_ENV_FILE), env_file_encoding="utf-8", extra="ignore")

    app_env: str = "local"
    app_name: str = "alerta-cuenta"
    app_secret: str = ""

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-6"

    groq_api_key: str = ""

    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    supabase_db_url: str = ""
    supabase_storage_bucket: str = "evidence"

    cors_origins: str = "http://localhost:5500,http://127.0.0.1:5500"

    email_provider: str = "console"
    smtp_host: str = ""
    smtp_port: str = ""
    smtp_user: str = ""
    smtp_password: str = ""

    log_level: str = "INFO"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
