from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # DATABASE_URL: legacy del monolito; opcional durante la migración a DynamoDB.
    DATABASE_URL: str = "sqlite+aiosqlite:///./metalshop.db"
    SECRET_KEY: str = "dev-local-insecure-key-change-me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ENVIRONMENT: str = "development"
    FRONTEND_URL: str = "http://localhost:8000"

    # DynamoDB (arquitectura serverless)
    DYNAMODB_TABLE: str = "metalshop"
    AWS_REGION: str = "us-east-2"
    # Endpoint local opcional (DynamoDB Local); None = AWS real
    DYNAMODB_ENDPOINT_URL: str | None = None

    # Email settings
    SMTP_HOST: str | None = None
    SMTP_PORT: int | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
