from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "RedShield AI Engine"
    ENVIRONMENT: str = "development"
    PORT: int = 8000
    DATABASE_URL: str = "sqlite:///./redshield.db"
    GITHUB_WEBHOOK_SECRET: str = "my_super_secret_key_123"

    class Config:
        env_file = ".env"

settings = Settings()