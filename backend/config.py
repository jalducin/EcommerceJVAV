from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
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

    # Remitente para correos transaccionales (Amazon SES)
    EMAILS_FROM: str | None = None

    # Documentación OpenAPI: protegida con Basic auth. Si DOCS_PASSWORD está vacío,
    # los docs quedan deshabilitados (404) — seguro por defecto.
    DOCS_USER: str = "jvmarket"
    DOCS_PASSWORD: str = ""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
