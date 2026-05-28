"""
Application configuration
"""
from pydantic_settings import BaseSettings
from pydantic import model_validator
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Satryawiguna API"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "satryawiguna_db"
    
    # JWT — JWT_SECRET_KEY has no default; it MUST be set in the environment.
    # Generate a strong key with: python -c "import secrets; print(secrets.token_hex(64))"
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Swagger Auth
    SWAGGER_USERNAME: str = "admin"
    SWAGGER_PASSWORD: str = "admin123"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001", "http://localhost:8000"]
    
    # DigitalOcean Spaces (S3-compatible storage)
    SPACES_ACCESS_KEY: str = ""
    SPACES_SECRET_KEY: str = ""
    SPACES_BUCKET_NAME: str = "satryawiguna-bucket"
    SPACES_REGION: str = "sgp1"
    SPACES_ENDPOINT_URL: str = "https://sgp1.digitaloceanspaces.com"
    SPACES_ORIGIN_ENDPOINT: str = "https://satryawiguna-bucket.sgp1.digitaloceanspaces.com"

    # Brevo SMTP
    SMTP_HOST: str = "smtp-relay.brevo.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "noreply@satryawiguna.me"
    SMTP_FROM_NAME: str = "Satrya Wiguna"
    BREVO_API_KEY: str = ""
    
    @property
    def SPACES_UPLOAD_FOLDER(self) -> str:
        """Determine upload folder based on environment: 'dev' for local/dev, 'prod' for production"""
        if self.APP_ENV == "production":
            return "prod"
        return "dev"
    
    @property
    def DATABASE_URL(self) -> str:
        """Sync database URL — used by Alembic migrations and CLI seeders"""
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        """Async database URL — used by the FastAPI application"""
        return f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @model_validator(mode="after")
    def validate_secrets(self) -> "Settings":
        known_weak = {
            "your-secret-key-change-this-in-production",
            "secret",
            "changeme",
            "change-this",
        }
        if self.JWT_SECRET_KEY.lower() in known_weak or len(self.JWT_SECRET_KEY) < 32:
            raise ValueError(
                "JWT_SECRET_KEY is insecure. "
                "Set a strong random value (>=32 chars) in your .env file. "
                "Generate one with: python -c \"import secrets; print(secrets.token_hex(64))\""
            )
        return self

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
