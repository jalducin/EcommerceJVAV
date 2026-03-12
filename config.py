from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # App
    ENVIRONMENT: str = "development"
    FRONTEND_URL: str = "http://localhost:8000"

    # Base de datos
    DATABASE_URL: str = "sqlite+aiosqlite:///./metalshop.db"

    # JWT
    SECRET_KEY: str = "cambia-esto-en-produccion-usa-openssl-rand-hex-32"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAILS_FROM: str = "noreply@metalshop.com"


settings = Settings()
