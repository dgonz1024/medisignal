from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = "MediSignal"
    environment: str = "development"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/medisignal"
    clinical_trials_base_url: str = "https://clinicaltrials.gov/api/v2/studies"
    request_timeout_seconds: int = 30
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_prefix="MEDISIGNAL_",
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def normalized_database_url(self) -> str:
        if self.database_url.startswith("postgres://"):
            return self.database_url.replace("postgres://", "postgresql+psycopg://", 1)

        if self.database_url.startswith("postgresql://") and "+psycopg" not in self.database_url:
            return self.database_url.replace("postgresql://", "postgresql+psycopg://", 1)

        return self.database_url


@lru_cache
def get_settings() -> Settings:
    return Settings()
