from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    app_name: str = "toyagent-backend"
    app_version: str = "0.1.0"
    debug: bool = False
    app_env: str = "development"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True

    # Database
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "toyagent"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"

    @property
    def database_url(self) -> str:
        """Construct async PostgreSQL connection URL."""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def database_url_sync(self) -> str:
        """Construct sync PostgreSQL connection URL (for Alembic)."""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # Azure OpenAI
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_deployment: str = ""
    azure_openai_api_version: str = "2024-02-15-preview"

    # Email (Exchange)
    email_server: str = ""
    email_username: str = ""  # RWTH account: ab123456@rwth-aachen.de
    email_primary_smtp_address: str = ""  # Email address: name@institution.rwth-aachen.de
    email_password: str = ""

    # Temporal
    temporal_host: str = "localhost"
    temporal_port: int = 7233
    temporal_namespace: str = "default"

    @property
    def temporal_address(self) -> str:
        """Construct Temporal server address."""
        return f"{self.temporal_host}:{self.temporal_port}"

    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:3001"
    cors_allow_credentials: bool = True

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    # Agent
    agent_timeout: int = 300
    agent_max_iterations: int = 10


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
