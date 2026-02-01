from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    """
    Central typed configuration.
    - Reads from env vars
    - Reads .env automatically in local dev
    - Extra env keys ignored (safe in CI)
    """
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    app_name: str = Field(default="Enterprise AI Knowledge Assistant", alias="APP_NAME")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # LLM/RAG
    llm_provider: str = Field(default="openai", alias="LLM_PROVIDER")
    rag_min_score: float = Field(default=0.05, alias="RAG_MIN_SCORE")

    # Security/ops
    api_key: str | None = Field(default=None, alias="API_KEY")
    disable_rate_limit: bool = Field(default=False, alias="DISABLE_RATE_LIMIT")
    require_api_key: bool = Field(default=False, alias="REQUIRE_API_KEY")

    # Web
    cors_origins: str = Field(default="http://localhost:3000", alias="CORS_ORIGINS")
    trusted_hosts: str = Field(default="localhost,127.0.0.1,testserver", alias="TRUSTED_HOSTS")

settings = Settings()