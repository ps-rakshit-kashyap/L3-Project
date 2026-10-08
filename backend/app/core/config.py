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

    # Supabase Configuration
    SUPABASE_URL: str | None = None
    SUPABASE_PUBLISHABLE_KEY: str | None = None
    SUPABASE_SECRET_KEY: str | None = None
    SUPABASE_ANON_KEY: str | None = None
    SUPABASE_SERVICE_ROLE_KEY: str | None = None
    SUPABASE_STORAGE_BUCKET: str = "resumes"
    MAX_UPLOAD_SIZE_MB: int = 10

    @property
    def effective_supabase_key(self) -> str | None:
        """Returns the secret / service role key for backend administration."""
        return self.SUPABASE_SECRET_KEY or self.SUPABASE_SERVICE_ROLE_KEY

    # Initial Bootstrap Admin
    INITIAL_ADMIN_EMAIL: str | None = None

    # LLM & Screening Agent Configuration
    LLM_PROVIDER: str = "groq"  # "groq", "openai", "custom", "mock"
    LLM_MODEL: str = "llama-3.3-70b-versatile"
    LLM_API_KEY: str | None = None
    GROQ_API_KEY: str | None = None
    OPENAI_API_KEY: str | None = None
    LLM_BASE_URL: str | None = None
    LLM_TEMPERATURE: float = 0.1

    @property
    def effective_llm_api_key(self) -> str | None:
        """Returns the configured LLM API key based on provider preference or general key."""
        if self.LLM_PROVIDER == "groq" and self.GROQ_API_KEY:
            return self.GROQ_API_KEY
        if self.LLM_PROVIDER == "openai" and self.OPENAI_API_KEY:
            return self.OPENAI_API_KEY
        return self.LLM_API_KEY or self.GROQ_API_KEY or self.OPENAI_API_KEY

    @property
    def effective_llm_base_url(self) -> str:
        """Returns the base URL for OpenAI-compatible chat completion endpoints."""
        if self.LLM_BASE_URL:
            return self.LLM_BASE_URL
        if self.LLM_PROVIDER == "groq":
            return "https://api.groq.com/openai/v1"
        return "https://api.openai.com/v1"

    LANGFUSE_PUBLIC_KEY: str | None = None
    LANGFUSE_SECRET_KEY: str | None = None
    LANGFUSE_BASE_URL: str = "https://cloud.langfuse.com"

    # Embeddings Configuration
    EMBEDDING_API_KEY: str | None = None
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_BASE_URL: str = "https://api.openai.com/v1"

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
