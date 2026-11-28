
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Library360"
    APP_VERSION: str = "1.0.0"

    GOOGLE_CLOUD_PROJECT: str = "floci-local"

    FIRESTORE_EMULATOR_HOST: str = "localhost:4588"
    STORAGE_EMULATOR_HOST: str = "http://localhost:4588"

    GCS_BUCKET_NAME: str = "library360-digital-books"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()
