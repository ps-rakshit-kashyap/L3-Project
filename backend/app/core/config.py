from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "TalentForge API"
    VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/talentforge"

    # CORS
    CORS_ORIGINS: list[str] | str = ["http://localhost:3000", "http://127.0.0.1:3000"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            if not v.strip():
                return []
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, tuple)):
            return [str(i) for i in v]
        return []

    # Future integration placeholders (Phase 1 placeholders)
    LLM_API_KEY: str | None = None
    LANGFUSE_PUBLIC_KEY: str | None = None
    LANGFUSE_SECRET_KEY: str | None = None

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
