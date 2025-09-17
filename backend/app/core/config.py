import os
from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "UAE Multi-Business POS & Invoice API"
    environment: str = os.getenv("ENV", "development")
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-change-me")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    algorithm: str = "HS256"

    # Database: default to SQLite file in workspace
    database_url: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./data.db",
    )

    # File storage directory
    upload_dir: str = os.getenv("UPLOAD_DIR", "./uploads")


settings = Settings()

os.makedirs(settings.upload_dir, exist_ok=True)
